"""
WSGI middleware wrapper to handle dynamic Vercel domains.
Allows any *.vercel.app domain by modifying the request before Django validates it.
"""
import os
from django.conf import settings


class AllowVercelDomainsMiddleware:
    """
    WSGI middleware that allows any Vercel domain by adding it to ALLOWED_HOSTS
    before the request reaches Django's host validation.
    """
    
    def __init__(self, application):
        self.application = application
    
    def __call__(self, environ, start_response):
        # Get the HTTP_HOST from the WSGI environ
        http_host = environ.get('HTTP_HOST', '')
        
        # Extract just the hostname (without port)
        hostname = http_host.split(':')[0]
        
        # Check if it's a Vercel domain
        if '.vercel.app' in hostname or 'vercel.dev' in hostname:
            # Add it to ALLOWED_HOSTS if not already there
            if hostname not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(hostname)
        
        # Continue with the request
        return self.application(environ, start_response)
