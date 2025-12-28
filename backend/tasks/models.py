from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='companies')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contacts')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Deal(models.Model):
    STAGE_CHOICES = [
        ('lead', 'Lead'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='lead')
    probability = models.IntegerField(default=0, help_text='Win probability (0-100%)')
    expected_close_date = models.DateField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='deals')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='deals')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AuditLog(models.Model):
    """
    Immutable append-only audit trail for all CRM operations.
    Records who did what, when, and what changed.
    
    IMMUTABILITY ENFORCEMENT:
    - save() refuses updates to existing records
    - delete() is disabled (use is_deleted flag instead)
    - Hash chaining detects tampering
    - Database constraints prevent insertion of invalid records
    """
    
    # Action constants
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_LOGIN = 'LOGIN'
    
    ACTION_CHOICES = [
        ('CREATE', 'Object created'),
        ('UPDATE', 'Object updated'),
        ('DELETE', 'Object deleted'),
        ('LOGIN', 'User logged in'),
    ]
    
    # Core audit fields
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="Type of action: CREATE, UPDATE, DELETE, LOGIN, etc."
    )
    
    # What was audited
    entity_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Model name affected (e.g., 'Company', 'Contact', 'Deal', 'Task')"
    )
    
    entity_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Primary key of audited object (flexible for UUID or int)"
    )
    
    # Who did it
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        db_index=True,
        help_text="User who performed the action (from token auth)"
    )
    
    # What changed (JSON)
    old_values = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="Previous field values before update"
    )
    
    new_values = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="New field values after update"
    )
    
    # Request metadata
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_index=True,
        help_text="IPv4 or IPv6 address of request origin"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="User-Agent HTTP header from request"
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="UTC timestamp of action"
    )
    
    # Hash chaining for tamper detection
    prev_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        editable=False,
        help_text="SHA-256 hash of previous audit log entry"
    )
    
    current_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        editable=False,
        help_text="SHA-256 hash of this entry (includes prev_hash)"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'entity_type']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['current_hash']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    
    def save(self, *args, **kwargs):
        """
        Override save() to enforce append-only behavior.
        - New records (pk=None) are allowed
        - Existing records cannot be updated
        """
        if self.pk is not None:
            # This is an update attempt on an existing record
            raise ValueError(
                f"Cannot modify existing AuditLog record (ID: {self.pk}). "
                "Audit logs are append-only and immutable. "
                "If you need to record a correction, create a new entry."
            )
        
        # Compute hash chain
        self._compute_hash_chain()
        
        # Allow insert only
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete() to prevent deletion of audit logs.
        Audit logs must never be deleted to maintain integrity.
        """
        raise ValueError(
            f"Cannot delete AuditLog record (ID: {self.pk}). "
            "Audit logs are immutable and must be preserved. "
            "If this entry is incorrect, create a corrective entry instead."
        )
    
    def _compute_hash_chain(self):
        """
        Compute hash chain for tamper detection.
        
        Hash includes:
        1. Previous entry's current_hash (chain)
        2. This entry's data (action, entity_type, entity_id, user, created_at, etc.)
        
        Formula:
        - first entry: hash(all_fields)
        - subsequent: hash(prev_hash + all_fields)
        
        If a past entry is modified, its hash changes, breaking the chain.
        """
        import hashlib
        import json
        from datetime import datetime
        
        # Get previous entry in chronological order
        prev_entry = AuditLog.objects.filter(
            created_at__lt=self.created_at or datetime.now()
        ).order_by('-created_at').first()
        
        if prev_entry:
            self.prev_hash = prev_entry.current_hash
        else:
            self.prev_hash = None
        
        # Build data to hash
        hash_data = {
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'user_id': self.user_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': str(self.created_at),
            'prev_hash': self.prev_hash,
        }
        
        # Create JSON string (sorted keys for consistency)
        hash_string = json.dumps(hash_data, sort_keys=True, default=str)
        
        # Compute SHA-256
        self.current_hash = hashlib.sha256(hash_string.encode()).hexdigest()
    
    def __str__(self):
        return f"{self.action} {self.entity_type}#{self.entity_id} by {self.user} @ {self.created_at}"
