import structlog
import uuid
from app.modules.enterprise.domain.entities.enterprise import Subscription, BillingEvent
from app.modules.enterprise.domain.repositories.enterprise_repository import EnterpriseRepository

logger = structlog.get_logger()

class BillingEngine:
    def __init__(self, repo: EnterpriseRepository):
        self.repo = repo

    async def deduct_usage_credits(self, tenant_id: str, credits: float) -> Subscription:
        """Subtracts cost credits from subscription balance, raising error on overdrafts."""
        logger.info("Deducting usage credits", tenant_id=tenant_id, credits=credits)
        sub = await self.repo.get_subscription(tenant_id)
        if not sub:
            # Default initialization
            sub = Subscription(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                plan_tier="FREE",
                credits_balance=100.0,
                billing_cycle="MONTHLY"
            )
            
        if sub.credits_balance < credits:
            raise ValueError(f"Insufficient credits balance for tenant {tenant_id}")
            
        sub.credits_balance -= credits
        await self.repo.save_subscription(sub)
        logger.info("Credits deducted", remaining=sub.credits_balance)
        return sub

    async def add_billing_credits(
        self,
        tenant_id: str,
        amount: float,
        credits: float
    ) -> BillingEvent:
        """Records payment invoice events and adds credits to balances."""
        logger.info("Adding billing credits", tenant_id=tenant_id, credits=credits)
        
        event = BillingEvent(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            amount=amount,
            credits_added=credits
        )
        await self.repo.save_billing_event(event)
        
        sub = await self.repo.get_subscription(tenant_id)
        if not sub:
            sub = Subscription(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                plan_tier="FREE",
                credits_balance=0.0,
                billing_cycle="MONTHLY"
            )
        sub.credits_balance += credits
        await self.repo.save_subscription(sub)
        
        return event
