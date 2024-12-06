from django.views.generic import ListView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from magic_forum.posts.models import Post
from magic_forum.comments.models import Comment


@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(ListView):
    model = Post
    template_name = 'forum/admin_dashboard.html'
    context_object_name = 'pending_posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(is_approved=False).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.count()
        context['pending_comments'] = Comment.objects.filter(is_approved=False).count()
        # Removed the notes access by the admins in their dashboard for privacy reasons
        return context


@staff_member_required
def approve_post(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=pk)
        post.is_approved = True
        post.save()
        messages.success(request, 'Post has been approved.')
        return redirect('admin-dashboard')
    return redirect('admin-dashboard')


@method_decorator(staff_member_required, name='dispatch')
class AdminCommentsView(ListView):
    model = Comment
    template_name = 'forum/admin_dashboard_comments.html'
    context_object_name = 'pending_comments'
    paginate_by = 10

    def get_queryset(self):
        return Comment.objects.filter(is_approved=False).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_comments'] = Comment.objects.count()
        return context


@staff_member_required
def approve_comment(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_approved = True
        comment.save()
        messages.success(request, 'Comment has been approved.')
        return redirect('admin-dashboard-comments')
    return redirect('admin-dashboard-comments')


@staff_member_required
def reject_comment(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()
        messages.success(request, 'Comment has been rejected and deleted.')
        return redirect('admin-dashboard-comments')
    return redirect('admin-dashboard-comments')
