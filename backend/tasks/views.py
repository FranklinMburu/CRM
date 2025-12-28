from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.utils import timezone
from .models import Company, Contact, Deal, Task, AuditLog
from .serializers import (
    CompanySerializer, ContactSerializer, DealSerializer,
    TaskSerializer, UserSerializer, AuditLogSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'})


@api_view(['GET'])
def dashboard_stats(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    stats = {
        'total_contacts': Contact.objects.count(),
        'total_companies': Company.objects.count(),
        'total_deals': Deal.objects.count(),
        'total_tasks': Task.objects.count(),
        'deals_by_stage': list(Deal.objects.values('stage').annotate(count=Count('id'))),
        'total_deal_value': Deal.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'won_deals_value': Deal.objects.filter(stage='won').aggregate(total=Sum('amount'))['total'] or 0,
        'pending_tasks': Task.objects.filter(status='pending').count(),
        'overdue_tasks': Task.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count() if 'timezone' in dir() else 0,
    }
    return Response(stats)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AuditLogPagination(PageNumberPagination):
    """
    Pagination for AuditLog entries.
    50 entries per page by default.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for AuditLog.
    Exposes immutable audit trail via REST API.
    
    Supports:
    - Listing all audit entries (paginated, 50 per page)
    - Filtering by action, entity_type, user, date range
    - Searching by entity_id, user__username
    - Ordering by created_at (descending by default)
    
    Does NOT support:
    - Create (POST)
    - Update (PUT/PATCH)
    - Delete (DELETE)
    
    All operations are append-only and immutable.
    
    Examples:
    GET /api/audit-logs/
    GET /api/audit-logs/?action=CREATE&user=demo
    GET /api/audit-logs/?entity_type=Company&created_at__gte=2025-01-01
    GET /api/audit-logs/?search=company_123
    GET /api/audit-logs/?page=2&page_size=100
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AuditLogPagination
    ordering = ['-created_at']
    
    # Filter backend configuration
    filter_backends = [DjangoFilterBackend, SearchFilter]
    
    # Filter by these fields
    filterset_fields = {
        'action': ['exact'],
        'entity_type': ['exact', 'icontains'],
        'user': ['exact'],
        'created_at': ['gte', 'lte', 'date__gte', 'date__lte'],
        'ip_address': ['exact'],
    }
    
    # Search by these fields
    search_fields = ['entity_id', 'user__username', 'ip_address']
    
    def list(self, request, *args, **kwargs):
        """
        List audit log entries with filtering, searching, and pagination.
        
        Query Parameters:
        - action: Filter by action type (CREATE, UPDATE, DELETE, LOGIN)
        - entity_type: Filter by entity type (Company, Contact, Deal, Task)
        - user: Filter by user ID
        - user__username: Filter by username (via search)
        - created_at__gte: Filter by start date (YYYY-MM-DD)
        - created_at__lte: Filter by end date (YYYY-MM-DD)
        - ip_address: Filter by IP address
        - search: Search by entity_id or username
        - page: Page number (default 1)
        - page_size: Entries per page (default 50, max 1000)
        - ordering: Order by field (e.g., -created_at for descending)
        """
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single audit log entry (read-only).
        """
        return super().retrieve(request, *args, **kwargs)
    
    # Explicitly disable write operations
    def create(self, request, *args, **kwargs):
        return Response(
            {'error': 'Audit logs are read-only. Cannot create new entries via API.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    def update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Audit logs are immutable. Cannot modify entries.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Audit logs are immutable. Cannot modify entries.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    def destroy(self, request, *args, **kwargs):
        return Response(
            {'error': 'Audit logs are permanent. Cannot delete entries.'},
            status=status.HTTP_403_FORBIDDEN
        )
