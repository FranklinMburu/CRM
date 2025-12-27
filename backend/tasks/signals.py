"""
Django signals for automatic audit logging.

This module captures model changes and creates AuditLog entries automatically.
Supports CREATE, UPDATE, and DELETE operations for Company, Contact, Deal, and Task models.
"""

import threading
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction

from .models import AuditLog, Company, Contact, Deal, Task

# Thread-local storage for request context (user, IP, user-agent)
# Set by middleware or manually in Phase 3
_audit_context = threading.local()


def set_audit_context(user=None, ip_address=None, user_agent=None):
    """
    Set audit context for the current request.
    Called by middleware in Phase 3.
    
    Args:
        user: Django User instance or None
        ip_address: Client IP address string
        user_agent: HTTP User-Agent header
    """
    _audit_context.user = user
    _audit_context.ip_address = ip_address
    _audit_context.user_agent = user_agent


def get_audit_context():
    """
    Retrieve audit context for the current thread.
    Returns dict with user, ip_address, user_agent keys.
    """
    return {
        'user': getattr(_audit_context, 'user', None),
        'ip_address': getattr(_audit_context, 'ip_address', None),
        'user_agent': getattr(_audit_context, 'user_agent', None),
    }


def clear_audit_context():
    """Clear audit context for the current thread."""
    _audit_context.user = None
    _audit_context.ip_address = None
    _audit_context.user_agent = None


# Models to audit
AUDITED_MODELS = (Company, Contact, Deal, Task)

# Fields to exclude from change tracking
EXCLUDED_FIELDS = {'created_at', 'updated_at', 'id', 'pk'}


def get_model_field_values(instance):
    """
    Extract auditable field values from model instance.
    Excludes auto-managed and internal fields.
    
    Args:
        instance: Django model instance
    
    Returns:
        dict: Field names and values
    """
    values = {}
    for field in instance._meta.get_fields():
        # Skip excluded fields
        if field.name in EXCLUDED_FIELDS:
            continue
        
        # Skip reverse relations
        if field.many_to_one or field.one_to_one:
            # For FK, store the ID value
            if hasattr(field, 'many_to_one') and field.many_to_one:
                field_id = f"{field.name}_id"
                if hasattr(instance, field_id):
                    values[field.name] = getattr(instance, field_id)
        elif not field.many_to_many and not field.one_to_many:
            # Regular field
            try:
                values[field.name] = getattr(instance, field.name)
            except AttributeError:
                pass
    
    return values


def create_audit_log(action, instance, old_values=None, new_values=None):
    """
    Create an AuditLog entry.
    
    Args:
        action: 'CREATE', 'UPDATE', or 'DELETE'
        instance: Model instance
        old_values: dict of previous field values (for UPDATE/DELETE)
        new_values: dict of new field values (for CREATE/UPDATE)
    """
    try:
        context = get_audit_context()
        
        AuditLog.objects.create(
            action=action,
            entity_type=instance.__class__.__name__,
            entity_id=str(instance.pk),
            user=context.get('user'),
            old_values=old_values or {},
            new_values=new_values or {},
            ip_address=context.get('ip_address'),
            user_agent=context.get('user_agent') or '',
        )
    except Exception as e:
        # Log the error but don't break the transaction
        import logging
        logger = logging.getLogger('tasks.signals')
        logger.error(f"Failed to create audit log for {instance.__class__.__name__}: {str(e)}")


def get_changed_fields(old_values, new_values):
    """
    Compare old and new values, return only changed fields.
    
    Args:
        old_values: dict of previous values
        new_values: dict of new values
    
    Returns:
        dict: {field_name: {'old': old_val, 'new': new_val}} for changed fields only
    """
    changes = {}
    
    # Get all field names from both dicts
    all_fields = set(old_values.keys()) | set(new_values.keys())
    
    for field in all_fields:
        old_val = old_values.get(field)
        new_val = new_values.get(field)
        
        # Only track fields that actually changed
        if old_val != new_val:
            changes[field] = {
                'old': old_val,
                'new': new_val,
            }
    
    return changes


# Pre-save signal handler to capture old values for UPDATE operations
@receiver(pre_save, sender=Company)
@receiver(pre_save, sender=Contact)
@receiver(pre_save, sender=Deal)
@receiver(pre_save, sender=Task)
def audit_pre_save(sender, instance, **kwargs):
    """
    Capture instance state BEFORE save for UPDATE detection.
    Stores old values on instance._audit_old_values for post_save handler.
    """
    if instance.pk:  # Only for updates (existing instances have pk)
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._audit_old_values = get_model_field_values(old_instance)
        except sender.DoesNotExist:
            instance._audit_old_values = {}
    else:
        # New instance (CREATE)
        instance._audit_old_values = {}


# Post-save signal handler for CREATE and UPDATE
@receiver(post_save, sender=Company)
@receiver(post_save, sender=Contact)
@receiver(post_save, sender=Deal)
@receiver(post_save, sender=Task)
def audit_post_save(sender, instance, created, **kwargs):
    """
    Create audit log after save completes.
    Distinguishes between CREATE (new instance) and UPDATE (existing instance).
    """
    if created:
        # CREATE action
        new_values = get_model_field_values(instance)
        create_audit_log(
            action=AuditLog.ACTION_CREATE,
            instance=instance,
            old_values={},
            new_values=new_values,
        )
    else:
        # UPDATE action
        old_values = getattr(instance, '_audit_old_values', {})
        new_values = get_model_field_values(instance)
        
        # Only create audit log if something actually changed
        changes = get_changed_fields(old_values, new_values)
        if changes:
            # Store only the changes, not full values
            create_audit_log(
                action=AuditLog.ACTION_UPDATE,
                instance=instance,
                old_values=old_values,
                new_values=new_values,
            )


# Post-delete signal handler for DELETE
@receiver(post_delete, sender=Company)
@receiver(post_delete, sender=Contact)
@receiver(post_delete, sender=Deal)
@receiver(post_delete, sender=Task)
def audit_post_delete(sender, instance, **kwargs):
    """
    Create audit log after instance is deleted.
    Captures final state before deletion.
    """
    create_audit_log(
        action=AuditLog.ACTION_DELETE,
        instance=instance,
        old_values=get_model_field_values(instance),
        new_values={},
    )
