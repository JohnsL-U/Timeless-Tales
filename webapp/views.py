from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from .forms import SignUpForm, PostForm, ContactForm, CommentForm, LoginForm, EditProfileForm
from .models import Post, Comment, Like, Notification, UserProfile
from django.http import HttpResponseNotFound






#Welcome Page!
def welcome(request):
    #Sign Up
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('webapp:user_profile')
    else:
        form = SignUpForm()
    login_form = LoginForm()
    context = {
        'form': form,
        'login_form': login_form
    }
    
    return render(request, 'webapp/welcome.html', context)

#Password Change
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('webapp:user_profile')
    else:
        messages.error(request, 'Please correct the error below.')
    return redirect('webapp:user_profile')
    


#Story Posts
@login_required
def home(request):
    user_posts = Post.objects.filter(user=request.user)
    followed_users = request.user.profile.following.all()
    followed_posts = Post.objects.filter(user__in=followed_users)
    current_user = request.user
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            form.save_m2m() 
            messages.success(request, 'Post created successfully!')
            return redirect('webapp:home')
    else:
        form = PostForm()
    return render(request, 'webapp/home.html', {'posts': user_posts, 'form': form, 'followed_posts': followed_posts, 'current_user': request.user})



#Search Page
def post_search(request):
    chosen_categories = request.GET.getlist('category')
    search_query = request.GET.get('search')

    if chosen_categories:
        posts = Post.objects.filter(
            Q(published_date__lte=timezone.now()) & Q(category__in=chosen_categories)
        ).order_by('published_date')
    else:
        posts = Post.objects.filter(
            published_date__lte=timezone.now()
        ).order_by('published_date')

    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    recent_posts = Post.objects.filter(
        published_date__lte=timezone.now()
    ).order_by('-published_date')[:5]

    context = {
        'posts': posts,
        'chosen_categories': chosen_categories,
        'categories': Post.CATEGORY_CHOICES,
        'recent_posts': recent_posts,
    }
    return render(request, 'webapp/post_search.html', context)

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post).order_by('created_date')
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'webapp/post_detail.html', context)

# Comment, Like
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()

            # Create a notification for the post author
            notification = Notification(
                user=post.user,
                text=f"{request.user.username} commented on your post.",
                post=post
            )
            notification.save()

            return redirect('webapp:post_detail', post_id=post.id)
    else:
        form = CommentForm()

    return redirect("webapp:post_detail", post_id=post_id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.user:
        comment.delete()
    return redirect("webapp:post_detail", post_id=comment.post_id)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        # The user already liked this post, so this request is for unliking it
        like.delete()
        post.likes_count -= 1
    else:
        post.likes_count += 1
        # Create a notification for the post author
        notification = Notification(
            user=post.user,
            text=f"{request.user.username} liked your post.",
            post=post
        )
        notification.save()
    post.save()
    return redirect("webapp:post_detail", post_id=post_id)


#User Profile
@login_required
def user_profile(request, username=None):
    current_user = request.user
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseNotFound("User not found")
    else:
        user = current_user
    my_posts = Post.objects.filter(user=current_user)
    notifications = Notification.objects.filter(user=current_user)
    comments = Comment.objects.filter(user=request.user).order_by('-created_date')

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=current_user.profile)
        if form.is_valid():
            print("Form is valid")
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('webapp:user_profile')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = EditProfileForm(instance=current_user.profile)

    context = {
        'current_user': current_user,
        'user': user,
        'my_posts': my_posts,
        'notifications': notifications,
        'comments': comments,
        'messages': messages.get_messages(request),
        'form': form
    }
    return render(request, 'webapp/user_profile.html', context)

@login_required
def follow(request, user_id):
    user_to_follow = User.objects.get(pk=user_id)
    request.user.profile.following.add(user_to_follow)
    return redirect('webapp:user_profile')

@login_required
def unfollow(request, user_id):
    user_to_unfollow = User.objects.get(pk=user_id)
    request.user.profile.following.remove(user_to_unfollow)
    return redirect('webapp:user_profile')

#Contact Page
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send the email
            subject = f'Contact message from {name}'
            message = f'From: {name} <{email}>\n\n{message}'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)

            # Redirect to a success page
            return redirect('webapp:contact_success')
    else:
        form = ContactForm()

    return render(request, 'webapp/contact.html', {'form': form})

##Contact Page Form Sent
def contact_success(request):
    return render(request, 'webapp/contact_success.html')

#About Us Page
def about(request):
    return render(request, 'webapp/about.html')

#User Agreement
def user_agreement(request):
    return render(request, 'webapp/user_agreement.html')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'webapp/password_reset.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'webapp/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'webapp/password_reset_confirm.html'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'webapp/password_reset_complete.html'



    