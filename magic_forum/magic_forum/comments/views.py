from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from magic_forum.comments.forms import CommentForm
from magic_forum.comments.models import CommentModeration
from magic_forum.posts.models import Post


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.is_anonymous = form.cleaned_data['is_anonymous']
            comment.save()

            if post.is_anonymous:
                # Creates moderation request for comments on anonymous posts
                CommentModeration.objects.create(comment=comment)
                messages.info(request, 'Your comment has been submitted for moderation.')
            else:
                messages.success(request, 'Your comment has been posted successfully.')

            return redirect('post-detail', pk=post.pk)
    return redirect('post-detail', pk=post.pk)
