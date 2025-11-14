from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.models import SessionLocal, Subscription, Payment
from app.gateway import MockGateway, YooMoneyGateway
from app.notifier import notifier
from app.config import SCHEDULER_INTERVAL_SECONDS, RETRY_DELAY, GATEWAY_MODE
import asyncio

if GATEWAY_MODE == 'yoomoney':
    gateway = YooMoneyGateway()
else:
    gateway = MockGateway()

async def process_due_payments():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        subs = db.query(Subscription).filter(Subscription.active == True, Subscription.next_run <= now).all()
        for s in subs:
            print('Processing subscription', s.id)
            p = Payment(subscription_id=s.id, amount=s.amount, currency=s.currency)
            db.add(p)
            db.commit()
            db.refresh(p)

            res = await gateway.capture_payment(p.amount, p.currency, {"subscription_id": s.id})
            p.attempts += 1
            if res.success:
                p.status = 'succeeded'
                p.gateway_payment_id = res.payment_id
                s.next_run = now + timedelta(days=s.interval_days)
                db.add(s)
                db.add(p)
                db.commit()
                notifier.send(f"Payment succeeded for subscription {s.id}, payment_id={res.payment_id}")
            else:
                p.status = 'failed'
                p.failure_reason = res.reason
                db.add(p)
                s.next_run = now + timedelta(seconds=RETRY_DELAY)
                db.add(s)
                db.commit()
                notifier.send(f"Payment FAILED for subscription {s.id}. Reason: {res.reason}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(process_due_payments()), 'interval', seconds=SCHEDULER_INTERVAL_SECONDS)
    scheduler.start()
    print('Scheduler started (interval seconds=', SCHEDULER_INTERVAL_SECONDS,')')
