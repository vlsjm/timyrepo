"""
Signals for automatic group assignment based on role.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Assign user to appropriate group based on their role.
    This runs every time a user is saved.
    """
    if not instance.is_superuser:  # Don't mess with superusers
        # Remove user from all groups first
        instance.groups.clear()
        
        # Assign to appropriate group based on role
        try:
            if instance.role == 'intern':
                group = Group.objects.get(name='Intern')
                instance.groups.add(group)
            elif instance.role == 'supervisor':
                group = Group.objects.get(name='Supervisor')
                instance.groups.add(group)
            elif instance.role == 'admin':
                group = Group.objects.get(name='Admin')
                instance.groups.add(group)
        except Group.DoesNotExist:
            # Groups haven't been created yet
            pass
