from django.db.models.signals import m2m_changed
from django.contrib.auth.models import User
from django.dispatch import receiver


@receiver(m2m_changed, sender=User.groups.through)
def update_user_staff_status(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove"]:
        admin_groups = instance.groups.filter(name__in=[
            'Administrator',
            'Comments Administrator',
            'Posts Administrator',
            'Moderator'
        ])
        instance.is_staff = admin_groups.exists()
        instance.save()
