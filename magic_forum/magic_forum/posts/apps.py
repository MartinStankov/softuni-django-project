from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_groups(sender, **kwargs):
    from .admin import setup_groups
    setup_groups()


class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'magic_forum.posts'

    def ready(self):
        post_migrate.connect(create_groups, sender=self)
        from magic_forum.signals import update_user_staff_status
