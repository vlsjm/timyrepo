"""
Custom middleware to handle ngrok domains in development.
"""
from django.conf import settings


class NgrokMiddleware:
    """
    Middleware to allow ngrok domains in development by adding them to ALLOWED_HOSTS.
    This runs before SecurityMiddleware to bypass host validation.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # In development, dynamically add ngrok domains to ALLOWED_HOSTS
        if settings.DEBUG:
            host = request.get_host().split(':')[0]  # Remove port if present
            
            # Check if it's an ngrok domain
            if any(domain in host for domain in [
                'ngrok-free.dev',
                'ngrok.io',
                'ngrok-free.app',
            ]):
                # Add it to ALLOWED_HOSTS if not already there
                if host not in settings.ALLOWED_HOSTS:
                    settings.ALLOWED_HOSTS.append(host)
        
        response = self.get_response(request)
        return response

