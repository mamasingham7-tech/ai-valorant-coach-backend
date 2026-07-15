from django.db import models

class User(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    email = models.EmailField(unique=True)
    hashed_password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'
        managed = False

    def __str__(self):
        return self.email

class Tenant(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tenants'
        managed = False

    def __str__(self):
        return self.name

class Subscription(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, to_field='id')
    plan_tier = models.CharField(max_length=20, default='FREE')
    credits_balance = models.FloatField(default=0.0)
    billing_cycle = models.CharField(max_length=20, default='MONTHLY')
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'subscriptions'
        managed = False

    def __str__(self):
        return f"{self.tenant.name} - {self.plan_tier}"

class BillingEvent(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, to_field='id')
    amount = models.FloatField()
    currency = models.CharField(max_length=10, default='USD')
    credits_added = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'billing_events'
        managed = False

class UsageMetric(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, to_field='id')
    api_calls_count = models.IntegerField(default=0)
    websocket_connections_count = models.IntegerField(default=0)
    inference_duration_seconds = models.FloatField(default=0.0)
    cost_credits = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usage_metrics'
        managed = False

class WorkflowDefinition(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, to_field='id')
    name = models.CharField(max_length=100)
    visual_steps = models.JSONField(default=dict)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow_definitions'
        managed = False

class WorkflowRun(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    workflow = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE, to_field='id')
    status = models.CharField(max_length=20, default='RUNNING')
    current_step = models.IntegerField(default=0)
    execution_logs = models.JSONField(default=list)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow_runs'
        managed = False

class FeatureFlag(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    rollout_percentage = models.IntegerField(default=100)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feature_flags'
        managed = False

class SecurityEvent(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, to_field='id')
    event_type = models.CharField(max_length=50)
    source_ip = models.CharField(max_length=45)
    threat_score = models.FloatField()
    action_taken = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'security_events'
        managed = False
