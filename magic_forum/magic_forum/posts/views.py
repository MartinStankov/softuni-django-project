from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms

from magic_forum.comments.forms import CommentForm
from magic_forum.comments.models import CommentModeration
from magic_forum.posts.forms import PostForm
from magic_forum.posts.models import Post


class PostListView(ListView):
    model = Post
    template_name = 'forum/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        base_queryset = Post.objects.filter(is_approved=True)

        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                # Staff can see all posts
                queryset = base_queryset
            else:
                # Regular users can only see approved posts and their own posts
                queryset = base_queryset.filter(
                    Q(is_approved=True) |
                    Q(author=self.request.user)
                )
        else:
            # Non-logged in users can only see approved posts
            queryset = base_queryset.filter(is_approved=True, is_anonymous=True)

        queryset = queryset.order_by('-created_at')

        # Handles search and category filtering
        query = self.request.GET.get('query')
        category_id = self.request.GET.get('category')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )
        if category_id:
            queryset = queryset.filter(category=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = Post.category.field.choices
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'forum/post_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff


class PostDetailView(DetailView):
    model = Post
    template_name = 'forum/post_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # Check if user can view this post
        if not obj.is_approved:
            if not self.request.user.is_authenticated:
                raise PermissionDenied
            if not (self.request.user.is_staff or self.request.user == obj.author):
                raise PermissionDenied

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        comments = self.object.comments.filter(is_approved=True)
        context['comments'] = comments.order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object

            # Set author if user is logged in
            if request.user.is_authenticated:
                comment.author = request.user
                # If user is logged in and chooses to post anonymously
                if form.cleaned_data.get('is_anonymous'):
                    comment.is_anonymous = True
                    comment.is_approved = False
                    comment.save()
                    CommentModeration.objects.create(comment=comment)
                    messages.info(request, 'Your anonymous comment has been submitted for moderation.')
                else:
                    # Non-anonymous comment by logged-in user
                    comment.is_anonymous = False
                    comment.is_approved = True
                    comment.save()
                    messages.success(request, 'Your comment has been posted successfully.')
            else:
                # Non-logged in users' comments are always anonymous and need approval
                comment.is_anonymous = True
                comment.is_approved = False
                comment.save()
                CommentModeration.objects.create(comment=comment)
                messages.info(request, 'Your anonymous comment has been submitted for moderation.')

        return redirect('post-detail', pk=self.object.pk)


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'forum/post_form.html'
    success_url = reverse_lazy('post-list')

    def dispatch(self, request, *args, **kwargs):
        """Handle authentication check before view execution"""
        post_type = request.GET.get('type')

        # If it's not an anonymous post and user is not authenticated the permission to create personal post is removed
        if post_type != 'anonymous' and not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to create personal posts.')
            return redirect('login')

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        post_type = self.request.GET.get('type')

        # Sets initial value for is_anonymous based on post type
        if post_type == 'anonymous':
            form.initial['is_anonymous'] = True

        # Always hide the is_anonymous field
        form.fields['is_anonymous'].widget = forms.HiddenInput()

        return form

    def form_valid(self, form):
        post_type = self.request.GET.get('type')

        # Set anonymous and approval status
        if post_type == 'anonymous':
            form.instance.is_anonymous = True
            form.instance.is_approved = False
            if self.request.user.is_authenticated:
                form.instance.author = self.request.user
            messages.info(self.request, 'Your anonymous post has been submitted for moderation.')
        else:
            if not self.request.user.is_authenticated:
                messages.error(self.request, 'You must be logged in to create personal posts.')
                return redirect('login')
            form.instance.author = self.request.user
            form.instance.is_approved = True
            messages.success(self.request, 'Your post has been created successfully!')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_type = self.request.GET.get('type')
        context['is_anonymous_post'] = (post_type == 'anonymous')
        context['categories'] = Post.category.field.choices
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post-list')
    template_name = 'forum/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        # Allows both author and admin to delete
        return self.request.user == post.author or self.request.user.is_staff
