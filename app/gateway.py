import random
import time
from typing import Tuple

class PaymentResult:
    def __init__(self, success: bool, payment_id: str = None, reason: str = None):
        self.success = success
        self.payment_id = payment_id
        self.reason = reason

class RefundResult:
    def __init__(self, success: bool, refund_id: str = None, reason: str = None):
        self.success = success
        self.refund_id = refund_id
        self.reason = reason

class BaseGateway:
    async def capture_payment(self, amount: float, currency: str, metadata: dict) -> PaymentResult:
        raise NotImplementedError

    async def refund_payment(self, gateway_payment_id: str, amount: float) -> RefundResult:
        raise NotImplementedError

class MockGateway(BaseGateway):
    async def capture_payment(self, amount: float, currency: str, metadata: dict) -> PaymentResult:
        time.sleep(0.5)
        if random.random() < 0.8:
            return PaymentResult(True, payment_id=f"mock_{int(time.time()*1000)}")
        else:
            return PaymentResult(False, reason='Insufficient funds (mock)')

    async def refund_payment(self, gateway_payment_id: str, amount: float) -> RefundResult:
        time.sleep(0.2)
        return RefundResult(True, refund_id=f"refund_{int(time.time()*1000)}")

class YooMoneyGateway(BaseGateway):
    async def capture_payment(self, amount: float, currency: str, metadata: dict) -> PaymentResult:
        raise NotImplementedError('YooMoney integration not implemented in demo')

    async def refund_payment(self, gateway_payment_id: str, amount: float) -> RefundResult:
        raise NotImplementedError('YooMoney integration not implemented in demo')
