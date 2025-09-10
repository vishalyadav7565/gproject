"""
WSGI config for gproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
sys.path.append('/home/username/your_project_folder')
sys.path.append('/home/username/your_project_folder/gproject')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gproject.settings')

application = get_wsgi_application()
