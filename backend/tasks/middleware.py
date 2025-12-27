"""
Audit Context Injection Middleware for Django.

This middleware automatically captures request metadata (user, IP address, user-agent)
and stores it in thread-local context for signal handlers to use.

How it works:
1. On each request, extract user, IP, and user-agent
2. Store in thread-local context using set_audit_context()
3. Signal handlers (pre_save, post_save, post_delete) automatically use this context
4. On response, clear context to prevent cross-request contamination

Result: All model changes are automatically tagged with request metadata without
any modifications to views, serializers, or models.
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from tasks.signals import set_audit_context, clear_audit_context

logger = logging.getLogger('tasks.middleware')


def get_client_ip(request):
    """
    Extract client IP address from request.
    
    Checks in order:
    1. X-Forwarded-For header (for proxied requests)
    2. X-Real-IP header (alternative proxy header)
    3. REMOTE_ADDR (direct connection)
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        str: IP address (IPv4 or IPv6) or None if unable to determine
    """
    # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2, ...)
    # We want the first one (the actual client)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # Alternative proxy header
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip
    
    # Direct connection
    return request.META.get('REMOTE_ADDR')


class AuditContextMiddleware(MiddlewareMixin):
    """
    Middleware to inject audit context on every request.
    
    Captures request metadata (user, IP, user-agent) and stores in thread-local
    context so signal handlers can access it automatically.
    
    Usage:
    Add to MIDDLEWARE in settings.py:
        MIDDLEWARE = [
            ...
            'tasks.middleware.AuditContextMiddleware',
            ...
        ]
    
    The middleware should be placed relatively early in the middleware stack,
    after authentication middleware but before any middleware that may trigger
    model saves (e.g., session middleware, CSRF middleware).
    
    Context lifetime:
    - Set: At the beginning of request processing (process_request)
    - Used: By signal handlers during model operations
    - Cleared: At the end of response processing (process_response)
    
    Thread safety:
    Context uses threading.local() so each request thread has isolated storage.
    Safe for multi-threaded WSGI servers (gunicorn, uWSGI, etc.).
    """
    
    def process_request(self, request):
        """
        Called at the beginning of request processing.
        
        Extracts user, IP, and user-agent from request and stores in thread-local
        context for signal handlers to use during this request.
        
        Args:
            request: Django HttpRequest object
        
        Returns:
            None (always allows request to proceed)
        """
        try:
            # Get authenticated user (or None for anonymous)
            user = request.user if request.user.is_authenticated else None
            
            # Extract IP address (handles proxies)
            ip_address = get_client_ip(request)
            
            # Get user-agent header
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Store in thread-local context
            set_audit_context(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            
            # Optional: Log context setup (helpful for debugging)
            logger.debug(
                f"Audit context set: user={user}, ip={ip_address}, "
                f"path={request.path}, method={request.method}"
            )
        
        except Exception as e:
            # Log error but don't break request processing
            logger.error(f"Failed to set audit context: {str(e)}")
            # Continue anyway (context will be None/empty, but app still works)
        
        # Always return None to allow request processing to continue
        return None
    
    def process_response(self, request, response):
        """
        Called at the end of request processing (after view executes).
        
        Clears thread-local context to prevent cross-request contamination.
        Uses try/finally to ensure cleanup happens even if response processing fails.
        
        Args:
            request: Django HttpRequest object
            response: Django HttpResponse object
        
        Returns:
            HttpResponse: The response object (unchanged)
        """
        try:
            clear_audit_context()
            logger.debug("Audit context cleared")
        except Exception as e:
            # Log error but don't affect response
            logger.error(f"Failed to clear audit context: {str(e)}")
        
        return response
    
    def process_exception(self, request, exception):
        """
        Called when an exception occurs during request processing.
        
        Ensures context is cleared even if an exception happens.
        
        Args:
            request: Django HttpRequest object
            exception: The exception that occurred
        
        Returns:
            None (allows exception to be handled by other middleware/error handlers)
        """
        try:
            clear_audit_context()
            logger.debug(f"Audit context cleared after exception: {exception.__class__.__name__}")
        except Exception as e:
            logger.error(f"Failed to clear audit context in exception handler: {str(e)}")
        
        # Return None to allow other middleware/error handlers to process the exception
        return None
