"""
Management command to initialize groups and permissions.
Run this after creating the database: python manage.py setup_groups_permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from logging_app.models import HourLog
from reports.models import Report


class Command(BaseCommand):
    help = 'Create and configure user groups and permissions'

    def handle(self, *args, **options):
        self.stdout.write('Setting up groups and permissions...\n')

        # Create groups
        intern_group, created = Group.objects.get_or_create(name='Intern')
        supervisor_group, created = Group.objects.get_or_create(name='Supervisor')
        admin_group, created = Group.objects.get_or_create(name='Admin')

        self.stdout.write(self.style.SUCCESS('✓ Groups created'))

        # Get content types
        hourlog_ct = ContentType.objects.get_for_model(HourLog)
        report_ct = ContentType.objects.get_for_model(Report)

        # Define permissions
        permissions_to_create = [
            # HourLog permissions
            (hourlog_ct, 'log_hours', 'Can log hours'),
            (hourlog_ct, 'view_own_logs', 'Can view own hour logs'),
            (hourlog_ct, 'edit_own_logs', 'Can edit own draft logs'),
            (hourlog_ct, 'delete_own_logs', 'Can delete own draft logs'),
            (hourlog_ct, 'view_all_logs', 'Can view all hour logs'),
            (hourlog_ct, 'approve_logs', 'Can approve submitted logs'),
            (hourlog_ct, 'reject_logs', 'Can reject submitted logs'),
            
            # Report permissions
            (report_ct, 'generate_reports', 'Can generate reports'),
            (report_ct, 'view_own_reports', 'Can view own reports'),
            (report_ct, 'view_all_reports', 'Can view all reports'),
        ]

        # Create permissions
        created_count = 0
        for content_type, codename, name in permissions_to_create:
            permission, created = Permission.objects.get_or_create(
                content_type=content_type,
                codename=codename,
                defaults={'name': name}
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'✓ {created_count} permissions created'))

        # Assign permissions to groups
        
        # INTERN GROUP
        intern_permissions = Permission.objects.filter(
            codename__in=[
                'log_hours',
                'view_own_logs',
                'edit_own_logs',
                'delete_own_logs',
                'generate_reports',
                'view_own_reports',
            ]
        )
        intern_group.permissions.set(intern_permissions)

        # SUPERVISOR GROUP
        supervisor_permissions = Permission.objects.filter(
            codename__in=[
                'view_all_logs',
                'approve_logs',
                'reject_logs',
                'view_all_reports',
            ]
        )
        supervisor_group.permissions.set(supervisor_permissions)

        # ADMIN GROUP (all permissions)
        admin_permissions = Permission.objects.filter(
            codename__in=[
                'log_hours',
                'view_own_logs',
                'edit_own_logs',
                'delete_own_logs',
                'generate_reports',
                'view_own_reports',
                'view_all_logs',
                'approve_logs',
                'reject_logs',
                'view_all_reports',
            ]
        )
        admin_group.permissions.set(admin_permissions)

        self.stdout.write(self.style.SUCCESS('[CHECK] Permissions assigned to groups'))
        self.stdout.write(self.style.SUCCESS('\n[CHECK] Groups and permissions setup complete!\n'))
        
        self.stdout.write('Group Permissions Summary:')
        self.stdout.write('─' * 50)
        self.stdout.write('INTERN:')
        for perm in intern_group.permissions.all():
            self.stdout.write(f'  • {perm.name}')
        
        self.stdout.write('\nSUPERVISOR:')
        for perm in supervisor_group.permissions.all():
            self.stdout.write(f'  • {perm.name}')
        
        self.stdout.write('\nADMIN:')
        for perm in admin_group.permissions.all():
            self.stdout.write(f'  • {perm.name}')
