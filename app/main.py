from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.models import init_db, SessionLocal, Subscription, Payment
from app.scheduler import start_scheduler
from app.notifier import notifier
from app.gateway import MockGateway, YooMoneyGateway
from app.config import GATEWAY_MODE

init_db()
app = FastAPI(title='Recurrent Payments Demo')
start_scheduler()

class SubscribeRequest(BaseModel):
    user_id: str
    amount: float
    currency: str = 'RUB'
    interval_days: int = 30

class RefundRequest(BaseModel):
    payment_id: int
    amount: float = None

@app.post('/subscribe')
async def subscribe(req: SubscribeRequest):
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        s = Subscription(user_id=req.user_id, amount=req.amount, currency=req.currency, interval_days=req.interval_days, next_run=now)
        db.add(s)
        db.commit()
        db.refresh(s)
        return {"subscription_id": s.id}
    finally:
        db.close()

@app.post('/refund')
async def refund(req: RefundRequest):
    db = SessionLocal()
    try:
        p = db.query(Payment).filter(Payment.id == req.payment_id).first()
        if not p:
            raise HTTPException(status_code=404, detail='Payment not found')
        if p.status != 'succeeded':
            raise HTTPException(status_code=400, detail='Only succeeded payments can be refunded')
        if GATEWAY_MODE == 'yoomoney':
            gateway = YooMoneyGateway()
        else:
            gateway = MockGateway()
        res = await gateway.refund_payment(p.gateway_payment_id, req.amount or p.amount)
        if res.success:
            p.status = 'refunded'
            db.add(p)
            db.commit()
            notifier.send(f"Refund succeeded for payment {p.id}, refund_id={res.refund_id}")
            return {"refund_id": res.refund_id}
        else:
            notifier.send(f"Refund FAILED for payment {p.id}. Reason: {res.reason}")
            raise HTTPException(status_code=400, detail=res.reason)
    finally:
        db.close()

@app.get('/status/{subscription_id}')
async def status(subscription_id: int):
    db = SessionLocal()
    try:
        s = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not s:
            raise HTTPException(status_code=404)
        payments = db.query(Payment).filter(Payment.subscription_id == s.id).all()
        return {
            "subscription": {
                "id": s.id,
                "user_id": s.user_id,
                "amount": s.amount,
                "currency": s.currency,
                "active": s.active,
                "next_run": s.next_run.isoformat()
            },
            "payments": [
                {"id": p.id, "status": p.status, "amount": p.amount, "failure_reason": p.failure_reason, "attempts": p.attempts} for p in payments
            ]
        }
    finally:
        db.close()

@app.get('/health')
async def health():
    return {"status": "ok"}
