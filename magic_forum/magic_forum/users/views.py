from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from magic_forum.users.forms import UserRegisterForm, UserProfileForm, UserUpdateForm
from magic_forum.users.models import UserProfile
from magic_forum.posts.models import Post


def not_authenticated(user):
    return not user.is_authenticated


# Prevents already logged in users to access the register page
@user_passes_test(not_authenticated, login_url='/', redirect_field_name=None)
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)  # Automatically log in after registration
            messages.success(request, f'Welcome to the forum, {user.username}!')
            return redirect('post-list')
    else:
        form = UserRegisterForm()
    return render(request, 'forum/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)

    # Get user's posts
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')

    context = {
        'form': form,
        'user_posts': user_posts
    }
    return render(request, 'forum/profile.html', context)


@login_required
def settings(request):
    user_form = UserUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'update_info' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your account information has been updated!')
                return redirect('settings')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated!')
                return redirect('settings')
            else:
                messages.error(request, 'Please correct the errors below.')

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'forum/settings.html', context)


class CustomLoginView(LoginView):
    template_name = 'forum/login.html'

    # Prevents already logged in users to access the login page
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('post-list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        return response

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('post-list')


class CustomLogoutView(LogoutView):
    template_name = 'forum/logout.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            # messages.info(request, 'You have been logged out successfully.')
            return super().dispatch(request, *args, **kwargs)
        return redirect('post-list')
