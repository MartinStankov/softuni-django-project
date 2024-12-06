from django.contrib import admin
from django.contrib.auth.models import Permission, Group, User
from django.db.models import Q
from magic_forum.comments.models import Comment
from magic_forum.posts.models import Post, Category


def setup_groups():
    # Create groups
    moderator_group, _ = Group.objects.get_or_create(name='Moderator')
    admin_group, _ = Group.objects.get_or_create(name='Administrator')
    comments_admin_group, _ = Group.objects.get_or_create(name='Comments Administrator')
    posts_admin_group, _ = Group.objects.get_or_create(name='Posts Administrator')

    # Moderator permissions - view only
    moderator_perms = Permission.objects.filter(
        Q(codename__startswith='view_')
    )
    moderator_group.permissions.set(moderator_perms)

    # Administrator permissions - full access
    admin_perms = Permission.objects.filter(
        content_type__app_label='forum'
    )
    admin_group.permissions.set(admin_perms)

    # Comments admin permissions
    comments_perms = Permission.objects.filter(
        Q(codename__startswith='view_') |
        Q(codename__in=[
            'add_comment',
            'change_comment',
            'delete_comment',
            'approve_comments',
            'reject_comments'
        ])
    )
    comments_admin_group.permissions.set(comments_perms)

    # Posts admin permissions
    posts_perms = Permission.objects.filter(
        Q(codename__startswith='view_') |
        Q(codename__in=[
            'add_post',
            'change_post',
            'delete_post',
            'approve_posts',
            'reject_posts'
        ])
    )
    posts_admin_group.permissions.set(posts_perms)

    # Update staff status
    User.objects.filter(
        groups__name__in=['Administrator', 'Comments Administrator', 'Posts Administrator', 'Moderator']
    ).update(is_staff=True)


class BaseAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name='Administrator').exists():
            return True
        if isinstance(obj, Comment):
            return request.user.groups.filter(name='Comments Administrator').exists()
        if isinstance(obj, Post):
            return request.user.groups.filter(name='Posts Administrator').exists()
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name='Administrator').exists():
            return True
        if isinstance(obj, Comment):
            return request.user.groups.filter(name='Comments Administrator').exists()
        if isinstance(obj, Post):
            return request.user.groups.filter(name='Posts Administrator').exists()
        return request.user.groups.filter(name='Moderator').exists()


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'is_anonymous', 'is_approved')
    list_filter = ('category', 'is_anonymous', 'is_approved', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
    actions = ['approve_posts', 'reject_posts']

    def approve_posts(self, request, queryset):
        queryset.update(is_approved=True)

    def reject_posts(self, request, queryset):
        queryset.update(is_approved=False)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name', 'description')
    search_fields = ('name', 'description')
