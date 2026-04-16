"""
WSGI config for internshiptracker project.
"""

import os

from django.core.wsgi import get_wsgi_application
from config.wsgi_wrapper import AllowVercelDomainsMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Wrap with WSGI middleware to allow Vercel domains
application = AllowVercelDomainsMiddleware(application)
