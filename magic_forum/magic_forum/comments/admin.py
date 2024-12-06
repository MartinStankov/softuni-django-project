from django.contrib import admin
from django.utils import timezone

from magic_forum.comments.models import Comment, CommentModeration


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'get_author', 'is_anonymous', 'is_approved', 'created_at')
    list_filter = ('is_anonymous', 'is_approved', 'created_at')
    search_fields = ('content', 'post__title')
    actions = ['approve_comments', 'reject_comments']

    def get_author(self, obj):
        return 'Anonymous' if obj.is_anonymous else obj.author.username

    get_author.short_description = 'Author'

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    approve_comments.short_description = "Approve selected comments"

    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)

    reject_comments.short_description = "Reject selected comments"


@admin.register(CommentModeration)
class CommentModerationAdmin(admin.ModelAdmin):
    list_display = ('comment', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status', 'submitted_at', 'reviewed_at')
    actions = ['approve_comments', 'reject_comments']

    def approve_comments(self, request, queryset):
        for moderation in queryset:
            moderation.status = 'approved'
            moderation.comment.is_approved = True
            moderation.comment.save()
            moderation.reviewed_at = timezone.now()
            moderation.save()

    def reject_comments(self, request, queryset):
        for moderation in queryset:
            moderation.status = 'rejected'
            moderation.comment.is_approved = False
            moderation.comment.save()
            moderation.reviewed_at = timezone.now()
            moderation.save()
