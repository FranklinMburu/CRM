from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import Contact, Company, AuditLog
from .signals import set_audit_context, clear_audit_context


class AuditLogCreateActionTest(TestCase):
    """Test that creating a Contact automatically creates an AuditLog with action='CREATE'"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.company = Company.objects.create(
            name='Test Company',
            created_by=self.user
        )
    
    def test_contact_creation_logs_audit_entry(self):
        """Creating a Contact should create an AuditLog entry with action='CREATE'"""
        set_audit_context(user=self.user, ip_address='127.0.0.1', user_agent='TestClient')
        
        try:
            initial_audit_count = AuditLog.objects.count()
            
            contact = Contact.objects.create(
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                company=self.company,
                created_by=self.user
            )
            
            self.assertEqual(AuditLog.objects.count(), initial_audit_count + 1)
            
            audit_entry = AuditLog.objects.latest('created_at')
            self.assertEqual(audit_entry.action, AuditLog.ACTION_CREATE)
            self.assertEqual(audit_entry.entity_type, 'Contact')
            self.assertEqual(audit_entry.entity_id, str(contact.id))
            self.assertEqual(audit_entry.user, self.user)
            self.assertIsNotNone(audit_entry.new_values)
            self.assertIn('first_name', audit_entry.new_values)
        finally:
            clear_audit_context()


class AuditLogUpdateActionTest(TestCase):
    """Test that updating a Contact automatically creates an AuditLog with action='UPDATE'"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.company = Company.objects.create(
            name='Test Company',
            created_by=self.user
        )
        set_audit_context(user=self.user, ip_address='127.0.0.1', user_agent='TestClient')
        self.contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            company=self.company,
            created_by=self.user
        )
        clear_audit_context()
        AuditLog.objects.all().delete()
    
    def test_contact_update_logs_audit_entry(self):
        """Updating a Contact should create an AuditLog entry with action='UPDATE'"""
        set_audit_context(user=self.user, ip_address='127.0.0.1', user_agent='TestClient')
        
        try:
            initial_audit_count = AuditLog.objects.count()
            
            self.contact.email = 'newemail@example.com'
            self.contact.save()
            
            self.assertEqual(AuditLog.objects.count(), initial_audit_count + 1)
            
            audit_entry = AuditLog.objects.latest('created_at')
            self.assertEqual(audit_entry.action, AuditLog.ACTION_UPDATE)
            self.assertEqual(audit_entry.entity_type, 'Contact')
            self.assertEqual(audit_entry.entity_id, str(self.contact.id))
            self.assertEqual(audit_entry.user, self.user)
            self.assertIsNotNone(audit_entry.old_values)
            self.assertIsNotNone(audit_entry.new_values)
            self.assertEqual(audit_entry.old_values.get('email'), 'john@example.com')
            self.assertEqual(audit_entry.new_values.get('email'), 'newemail@example.com')
        finally:
            clear_audit_context()


class AuditLogDeleteActionTest(TestCase):
    """Test that deleting a Contact automatically creates an AuditLog with action='DELETE'"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.company = Company.objects.create(
            name='Test Company',
            created_by=self.user
        )
        set_audit_context(user=self.user, ip_address='127.0.0.1', user_agent='TestClient')
        self.contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            company=self.company,
            created_by=self.user
        )
        clear_audit_context()
        AuditLog.objects.all().delete()
    
    def test_contact_deletion_logs_audit_entry(self):
        """Deleting a Contact should create an AuditLog entry with action='DELETE'"""
        set_audit_context(user=self.user, ip_address='127.0.0.1', user_agent='TestClient')
        
        try:
            contact_id = self.contact.id
            initial_audit_count = AuditLog.objects.count()
            
            self.contact.delete()
            
            self.assertEqual(AuditLog.objects.count(), initial_audit_count + 1)
            
            audit_entry = AuditLog.objects.latest('created_at')
            self.assertEqual(audit_entry.action, AuditLog.ACTION_DELETE)
            self.assertEqual(audit_entry.entity_type, 'Contact')
            self.assertEqual(audit_entry.entity_id, str(contact_id))
            self.assertEqual(audit_entry.user, self.user)
            self.assertIsNotNone(audit_entry.old_values)
            self.assertEqual(audit_entry.new_values, {})
        finally:
            clear_audit_context()


class AuditLogEndpointUnauthenticatedTest(APITestCase):
    """Test that unauthenticated users cannot access the audit logs endpoint"""
    
    def test_unauthenticated_user_cannot_access_audit_logs(self):
        """GET /api/audit-logs/ without authentication should return 401"""
        response = self.client.get('/api/audit-logs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuditLogEndpointAuthenticatedTest(APITestCase):
    """Test that authenticated users can successfully retrieve audit logs"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.company = Company.objects.create(
            name='Test Company',
            created_by=self.user
        )
        self.contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            company=self.company,
            created_by=self.user
        )
    
    def test_authenticated_user_can_retrieve_audit_logs(self):
        """GET /api/audit-logs/ with valid token should return 200 and audit logs"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/audit-logs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)
        self.assertGreater(len(response.data['results']), 0)
        
        audit_entry = response.data['results'][0]
        self.assertIn('id', audit_entry)
        self.assertIn('action', audit_entry)
        self.assertIn('entity_type', audit_entry)
        self.assertIn('entity_id', audit_entry)
        self.assertIn('user', audit_entry)
        self.assertIn('created_at', audit_entry)
