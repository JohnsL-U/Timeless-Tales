from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView


app_name = 'webapp'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.welcome, name='welcome'),
    path('search/', views.post_search, name='post_search'),
    path('search/<str:search>/', views.post_search, name='post_search'),
    path('create/', views.create_a_post, name='create_a_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    path('about/', views.about, name='about'),
    path('user_profile/', views.user_profile, name='user_profile_own'),
    path('user_profile/<str:username>/', views.user_profile, name='user_profile_other'),
    path('follow/<int:user_id>/', views.follow, name='follow'),
    path('unfollow/<int:user_id>/', views.unfollow, name='unfollow'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(next_page='webapp:welcome'), name='logout'),
    path('password_change/', views.password_change, name='password_change'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('user_agreement/', views.user_agreement, name='user_agreement'),
    path('get_api_key/', views.get_api_key, name='get_api_key')
]
