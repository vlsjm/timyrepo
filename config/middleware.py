"""
Custom middleware to handle ngrok domains in development.
"""
from django.conf import settings


class NgrokMiddleware:
    """
    Middleware to allow ngrok and Vercel preview domains by adding them to ALLOWED_HOSTS.
    This runs before SecurityMiddleware to bypass host validation.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # Check if it's an ngrok domain (in development) or Vercel preview domain
        should_add = False
        
        # Always allow ngrok domains in development
        if settings.DEBUG:
            if any(domain in host for domain in [
                'ngrok-free.dev',
                'ngrok.io',
                'ngrok-free.app',
            ]):
                should_add = True
        
        # Allow Vercel preview and production domains
        if any(domain in host for domain in [
            '.vercel.app',
            'vercel.dev',
        ]):
            should_add = True
        
        # Add it to ALLOWED_HOSTS if not already there
        if should_add and host not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS.append(host)
        
        response = self.get_response(request)
        return response

