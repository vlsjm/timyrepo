from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from logging_app.models import HourLog


class Command(BaseCommand):
    help = 'Initialize groups and permissions for the internship tracker'

    def handle(self, *args, **options):
        # Get or create groups
        intern_group, intern_created = Group.objects.get_or_create(name='Intern')
        supervisor_group, supervisor_created = Group.objects.get_or_create(name='Supervisor')
        admin_group, admin_created = Group.objects.get_or_create(name='Admin')

        # Get HourLog content type
        hourlog_ct = ContentType.objects.get_for_model(HourLog)

        # Define permissions using code names
        permissions_map = {
            'log_hours': 'Can log hours',
            'view_own_logs': 'Can view own logs',
            'edit_own_logs': 'Can edit own logs',
            'delete_own_logs': 'Can delete own logs',
            'submit_for_review': 'Can submit logs for review',
            'view_all_logs': 'Can view all hour logs',
            'approve_logs': 'Can approve hour logs',
            'reject_logs': 'Can reject hour logs',
            'generate_reports': 'Can generate reports',
        }

        # Create custom permissions
        for code, name in permissions_map.items():
            perm, created = Permission.objects.get_or_create(
                codename=code,
                content_type=hourlog_ct,
                defaults={'name': name}
            )

        # Get permissions
        log_hours = Permission.objects.get(codename='log_hours')
        view_own = Permission.objects.get(codename='view_own_logs')
        edit_own = Permission.objects.get(codename='edit_own_logs')
        delete_own = Permission.objects.get(codename='delete_own_logs')
        submit = Permission.objects.get(codename='submit_for_review')
        view_all = Permission.objects.get(codename='view_all_logs')
        approve = Permission.objects.get(codename='approve_logs')
        reject = Permission.objects.get(codename='reject_logs')
        gen_reports = Permission.objects.get(codename='generate_reports')

        # Assign permissions to Intern group
        intern_group.permissions.set([
            log_hours,
            view_own,
            edit_own,
            delete_own,
            submit,
            gen_reports,
        ])

        # Assign permissions to Supervisor group
        supervisor_group.permissions.set([
            view_all,
            approve,
            reject,
        ])

        # Assign all permissions to Admin group (including Django's default ones)
        admin_perms = Permission.objects.filter(
            content_type__app_label__in=['auth', 'logging_app', 'users', 'reports']
        )
        admin_group.permissions.set(admin_perms)

        self.stdout.write(self.style.SUCCESS('[CHECK] Groups and permissions created successfully'))
        self.stdout.write(f'   Intern group: {intern_group.permissions.count()} permissions')
        self.stdout.write(f'   Supervisor group: {supervisor_group.permissions.count()} permissions')
        self.stdout.write(f'   Admin group: {admin_group.permissions.count()} permissions')
