from django.contrib.auth import login, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm, PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.http import HttpResponseNotFound, JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, F, Func
from django.core.paginator import Paginator
from .forms import SignUpForm, PostForm, ContactForm, CommentForm, LoginForm, EditProfileForm
from .models import Post, Comment, Like, Notification, User
import datetime
from decouple import config






def get_api_key(request):
    return JsonResponse({'google_api_key': config('API_KEY')})

def welcome(request):
    form = SignUpForm()
    login_form = LoginForm()
    # Sign Up
    if request.method == 'POST':
        if 'signup' in request.POST:
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('webapp:home')
        elif 'login' in request.POST:
            login_form = LoginForm(data=request.POST)
            if login_form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('webapp:home')
                else:
                    messages.error(request, 'Invalid login or password.')
        else:
            messages.error(request, 'Invalid form submission.')
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
            return redirect('webapp:user_profile_own')
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, f"{field.capitalize()}: {error}")
            return redirect('webapp:user_profile_own')
    else:
        form = PasswordChangeForm(request.user)
        return redirect('webapp:user_profile_own')

@login_required   
def create_a_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.published_date = timezone.now()
            new_post.latitude = form.cleaned_data['latitude']
            new_post.longitude = form.cleaned_data['longitude']
            new_post.save()
            form.save_m2m() 
            messages.success(request, 'Post created successfully!')
            return redirect('webapp:home')
    else:
        form = PostForm()
    
    form.fields['include_time'].widget.attrs['onchange'] = 'toggleTimeOption()'

    context = {
        'form': form,
        'API_KEY': settings.GOOGLE_API_KEY
    }
    return render(request, 'webapp/create_a_post.html', context)

#Story Posts
@login_required
def home(request):
    most_liked_posts_list = Post.objects.all().order_by('-likes_count')
    followed_users = request.user.profile.following.all()
    followed_posts_list = Post.objects.filter(user__in=followed_users)

    paginator_followed_posts = Paginator(followed_posts_list, 5) 
    page_number_followed_posts = request.GET.get('page_followed_posts')
    followed_posts = paginator_followed_posts.get_page(page_number_followed_posts)

    paginator_most_liked = Paginator(most_liked_posts_list, 5)
    page_number_most_liked = request.GET.get('page_most_liked')
    most_liked_posts = paginator_most_liked.get_page(page_number_most_liked)

    current_user = request.user
    context = {
        'most_liked_posts': most_liked_posts,
        'current_user': current_user, 
        'followed_posts': followed_posts, 
    }
  
    return render(request, 'webapp/home.html', context)

#Search Page
def post_search(request):
    chosen_categories = request.GET.getlist('category')
    search_query = request.GET.get('search')
    search_season = request.GET.get('season')
    search_decade = request.GET.get('decade')
    search_year = request.GET.get('year')
    search_daterange = request.GET.get('daterange')
    current_year = datetime.datetime.now().year

    decades = [decade for decade in range(1900, 2030, 10)]
    year_range = range(1900, current_year + 1)
    month_range = range(1, 13)
    day_range = range(1, 32)
    start_year = request.GET.get('start_year')
    start_month = request.GET.get('start_month')
    start_day = request.GET.get('start_day')
    end_year = request.GET.get('end_year')
    end_month = request.GET.get('end_month')
    end_day = request.GET.get('end_day')

    posts = Post.objects.all()
    all_posts = Post.objects.all()

    if search_query and len(search_query) > 3:
        posts = posts.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(user__username__icontains=search_query) | Q(tags__icontains=search_query) | Q(location__icontains=search_query))
    
    if search_decade:
        start_decade = int(search_decade)
        end_decade = start_decade + 9
        posts = posts.filter(Q(year__range=(start_decade, end_decade)) | Q(date__year__range=(start_decade, end_decade)))

    if search_year:
        posts = posts.filter(Q(year=search_year)| Q(date__year=search_year))
        
    if search_season:
        if search_season == 'Winter':
            posts = posts.filter(Q(season=search_season) | Q(date__month__in=[12, 1, 2]))
        elif search_season == 'Spring':
            posts = posts.filter(Q(season=search_season) | Q(date__month__in=[3, 4, 5]))
        elif search_season == 'Summer':
            posts = posts.filter(Q(season=search_season) | Q(date__month__in=[6, 7, 8]))
        elif search_season == 'Fall':
            posts = posts.filter(Q(season=search_season) | Q(date__month__in=[9, 10, 11]))


    if chosen_categories:
        posts = posts.filter(Q(category__in=chosen_categories)).order_by('date')
    else:
        posts = posts.order_by('date')
        

    if start_year or end_year:  
        if search_daterange == 'year':
            if start_year and end_year: 
                posts = posts.filter(
                    Q(year__range=(start_year, end_year)) | 
                    Q(end_year__range=(start_year, end_year)) |
                    Q(date__year__range=(start_year, end_year))
                )
            elif start_year:  
                posts = posts.filter(
                    Q(year__gte=start_year) | 
                    Q(end_year__gte=start_year) |
                    Q(date__year__gte=start_year)
                )
            elif end_year:  
                posts = posts.filter(
                    Q(year__lte=end_year) |
                    Q(end_year__lte=end_year) |
                    Q(date__year__lte=end_year)
                )
        else:  
            if start_year:
                start_date = datetime.date(int(start_year), int(start_month), int(start_day))
            else:
                start_date = None

            if end_year:
                end_date = datetime.date(int(end_year), int(end_month), int(end_day))
            else:
                end_date = None
            
            if start_date and end_date: 
                posts = posts.filter(Q(date__range=(start_date, end_date)) | 
                                 Q(end_date__range=(start_date, end_date))
                                )
            elif start_date: 
                posts = posts.filter(Q(date__gte=start_date) | 
                                    Q(end_date__gte=start_date)
                                    )
            elif end_date:  
                posts = posts.filter(Q(date__lte=end_date) | 
                                    Q(end_date__lte=end_date)
                                    )
                
    posts = posts.order_by('date')
    paginator = Paginator(posts, 4)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {
        'posts': posts,
        'all_posts': all_posts,
        'chosen_categories': chosen_categories,
        'categories': Post.CATEGORY_CHOICES,
        'decades': decades,
        'API_KEY': settings.GOOGLE_API_KEY,
        'year_range': year_range,
        'month_range': month_range,
        'day_range': day_range,
        'start_year': start_year,
        'start_month': start_month,
        'start_day': start_day,
        'end_year': end_year,
        'end_month': end_month,
        'end_day': end_day
    }
    return render(request, 'webapp/post_search.html', context)


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post).order_by('created_date')
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'API_KEY': settings.GOOGLE_API_KEY
    }
    return render(request, 'webapp/post_detail.html', context)

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.user != request.user:
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('webapp:post_detail', post_id=post.pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, 'Post updated successfully.')
            return redirect('webapp:post_detail', post_id=post.pk)
    else:
        form = PostForm(instance=post)
    context = {
        'post': post,
        'form': form,
        'API_KEY': settings.GOOGLE_API_KEY
    }
    return render(request, 'webapp/post_edit.html', context)


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
        like.delete()
        post.likes_count -= 1
    else:
        post.likes_count += 1
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

    if not current_user.is_authenticated:
        return redirect('webapp:home')
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseNotFound("User not found")
    else:
        user = current_user
    
    show_my_posts = user == current_user
    posts = Post.objects.filter(user=user)
    notifications = Notification.objects.filter(user=current_user)
    comments = Comment.objects.filter(user=request.user).order_by('-created_date')


    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=current_user.profile)
        if form.is_valid():
            print("Form is valid")
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('webapp:user_profile_own')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = EditProfileForm(instance=current_user.profile)

    context = {
        'current_user': current_user,
        'user': user,
        'posts': posts,
        'notifications': notifications,
        'comments': comments,
        'messages': messages.get_messages(request),
        'form': form,
        'show_my_posts': show_my_posts
    }
    return render(request, 'webapp/user_profile.html', context)

@login_required
def follow(request, user_id):
    user_to_follow = User.objects.get(pk=user_id)
    request.user.profile.following.add(user_to_follow)
    return redirect('webapp:user_profile_other', username=user_to_follow.username)

@login_required
def unfollow(request, user_id):
    user_to_unfollow = User.objects.get(pk=user_id)
    request.user.profile.following.remove(user_to_unfollow)
    return redirect('webapp:user_profile_other', username=user_to_unfollow.username)

#Contact Page
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            subject = f'Contact message from {name}'
            message = f'From: {name} <{email}>\n\n{message}'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)

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

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST['email']
        associated_users = User.objects.filter(Q(email=email))
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                email_template_name = "webapp/password_reset_email.txt"
                c = {
                "email":user.email,
                'domain':'127.0.0.1:8000',
                'site_name': 'Timeless Tales',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, 'admin@mywebsite.com' , [user.email], fail_silently=False)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return redirect ("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="webapp/password_reset.html", context={"password_reset_form":password_reset_form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            validlink = True
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    return redirect('password_reset_complete')
            else:
                form = SetPasswordForm(user)
        else:
            validlink = False
            form = None
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        validlink = False
        form = None
    return render(request, 'webapp/password_reset_confirm.html', {
        'form': form,
        'validlink': validlink,
    })

def password_reset_done(request):
    return render(request, 'webapp/password_reset_done.html')

def password_reset_complete(request):
    return render(request, 'webapp/password_reset_complete.html')