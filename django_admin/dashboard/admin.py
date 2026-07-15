from django.contrib import admin
from .models import (
    User,
    Tenant,
    Subscription,
    BillingEvent,
    UsageMetric,
    WorkflowDefinition,
    WorkflowRun,
    FeatureFlag,
    SecurityEvent
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_active', 'is_verified')
    search_fields = ('email',)
    list_filter = ('is_active', 'is_verified')

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'created_at')
    search_fields = ('name',)
    list_filter = ('status',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'plan_tier', 'credits_balance', 'billing_cycle', 'expires_at')
    search_fields = ('tenant__name',)
    list_filter = ('plan_tier', 'billing_cycle')

@admin.register(BillingEvent)
class BillingEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'amount', 'currency', 'credits_added', 'created_at')
    search_fields = ('tenant__name',)
    list_filter = ('currency',)

@admin.register(UsageMetric)
class UsageMetricAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tenant',
        'api_calls_count',
        'websocket_connections_count',
        'inference_duration_seconds',
        'cost_credits',
        'created_at'
    )
    search_fields = ('tenant__name',)

@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'name', 'version', 'created_at')
    search_fields = ('name', 'tenant__name')

@admin.register(WorkflowRun)
class WorkflowRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'workflow', 'status', 'current_step', 'started_at')
    search_fields = ('workflow__name', 'status')
    list_filter = ('status',)

@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rollout_percentage', 'is_enabled', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_enabled',)

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tenant',
        'event_type',
        'source_ip',
        'threat_score',
        'action_taken',
        'created_at'
    )
    search_fields = ('tenant__name', 'event_type', 'source_ip')
    list_filter = ('event_type', 'action_taken')
