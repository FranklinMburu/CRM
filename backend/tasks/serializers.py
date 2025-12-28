from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company, Contact, Deal, Task, AuditLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CompanySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    contacts_count = serializers.SerializerMethodField()
    deals_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'industry', 'website', 'phone', 'email', 'address',
                  'notes', 'created_at', 'updated_at', 'created_by', 'created_by_name',
                  'contacts_count', 'deals_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def get_contacts_count(self, obj):
        return obj.contacts.count()

    def get_deals_count(self, obj):
        return obj.deals.count()


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
                  'position', 'company', 'company_name', 'notes', 'created_at',
                  'updated_at', 'created_by', 'created_by_name']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'full_name']


class DealSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Deal
        fields = ['id', 'title', 'amount', 'stage', 'probability', 'expected_close_date',
                  'company', 'company_name', 'contact', 'contact_name', 'notes',
                  'created_at', 'updated_at', 'created_by', 'created_by_name']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class TaskSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    deal_title = serializers.CharField(source='deal.title', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'due_date',
                  'contact', 'contact_name', 'deal', 'deal_title', 'assigned_to',
                  'assigned_to_name', 'created_at', 'updated_at', 'created_by',
                  'created_by_name']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for AuditLog.
    Exposes audit trail with all metadata.
    No write operations allowed.
    """
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    ip_address = serializers.CharField(read_only=True, allow_null=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'action',
            'entity_type',
            'entity_id',
            'user',
            'user_username',
            'old_values',
            'new_values',
            'ip_address',
            'user_agent',
            'created_at',
            'prev_hash',
            'current_hash',
        ]
        read_only_fields = [
            'id',
            'action',
            'entity_type',
            'entity_id',
            'user',
            'user_username',
            'old_values',
            'new_values',
            'ip_address',
            'user_agent',
            'created_at',
            'prev_hash',
            'current_hash',
        ]
