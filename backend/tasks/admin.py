from django.contrib import admin
from .models import Company, Contact, Deal, Task, AuditLog


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'email', 'phone', 'created_at']
    list_filter = ['industry', 'created_at']
    search_fields = ['name', 'email', 'industry']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'company', 'position', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'amount', 'stage', 'probability', 'expected_close_date', 'created_at']
    list_filter = ['stage', 'created_at']
    search_fields = ['title', 'company__name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'due_date', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Read-only admin interface for audit logs.
    Audit logs are immutable and tamper-proof.
    No add/edit/delete operations allowed.
    """
    
    list_display = [
        'id',
        'action',
        'entity_type',
        'entity_id',
        'user',
        'ip_address',
        'created_at',
    ]
    
    list_filter = [
        'action',
        'entity_type',
        'user',
        'created_at',
    ]
    
    search_fields = [
        'entity_type',
        'entity_id',
        'user__username',
        'ip_address',
    ]
    
    readonly_fields = [
        'id',
        'action',
        'entity_type',
        'entity_id',
        'user',
        'old_values',
        'new_values',
        'ip_address',
        'user_agent',
        'created_at',
        'prev_hash',
        'current_hash',
    ]
    
    # Disable add form (create button)
    def has_add_permission(self, request):
        return False
    
    # Disable change form (edit button)
    def has_change_permission(self, request, obj=None):
        return False
    
    # Disable delete button
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Show all fields as readonly in detail view
    fields = readonly_fields
    
    ordering = ['-created_at']
