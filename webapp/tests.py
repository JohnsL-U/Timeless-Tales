from django.test import TestCase, Client, SimpleTestCase
from django.contrib.auth.models import User
from . import views
from .models import Post, Comment, Like, Notification, UserProfile
from django.urls import reverse, resolve
from django.contrib.auth.views import LoginView, LogoutView


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.post = Post.objects.create(user=self.user, title='Test Post')
    
    def test_home_view(self):
        self.client.login(username='testuser', password='testpassword')  # Log in the test client
        response = self.client.get(reverse('webapp:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/home.html')

    def test_post_detail_view(self):
        self.client.login(username='testuser', password='testpassword')  # Log in the test client
        response = self.client.get(reverse('webapp:post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/post_detail.html')


    def test_add_comment_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('webapp:add_comment', args=[self.post.id]), {'content': 'Test Comment'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful comment submission

        comments = Comment.objects.filter(post=self.post)
        self.assertEqual(comments.count(), 1)
        self.assertEqual(comments[0].content, 'Test Comment')

    def test_like_post_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('webapp:like_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful like

        likes = Like.objects.filter(post=self.post)
        self.assertEqual(likes.count(), 1)

    def test_user_profile_view(self):
        response = self.client.get(reverse('webapp:user_profile_own'))
        self.assertEqual(response.status_code, 302)  # Redirect if user is not authenticated

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('webapp:user_profile_own'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/user_profile.html')


class UrlsTestCase(SimpleTestCase):
    def test_home_url_resolves(self):
        url = reverse('webapp:home')
        self.assertEqual(resolve(url).func, views.home)

    def test_welcome_url_resolves(self):
        url = reverse('webapp:welcome')
        self.assertEqual(resolve(url).func, views.welcome)

    def test_post_search_url_resolves(self):
        url = reverse('webapp:post_search')
        self.assertEqual(resolve(url).func, views.post_search)

    def test_create_a_post_url_resolves(self):
        url = reverse('webapp:create_a_post')
        self.assertEqual(resolve(url).func, views.create_a_post)

    def test_post_detail_url_resolves(self):
        url = reverse('webapp:post_detail', args=[1])
        self.assertEqual(resolve(url).func, views.post_detail)

    def test_add_comment_url_resolves(self):
        url = reverse('webapp:add_comment', args=[1])
        self.assertEqual(resolve(url).func, views.add_comment)

    def test_delete_comment_url_resolves(self):
        url = reverse('webapp:delete_comment', args=[1])
        self.assertEqual(resolve(url).func, views.delete_comment)

    def test_like_post_url_resolves(self):
        url = reverse('webapp:like_post', args=[1])
        self.assertEqual(resolve(url).func, views.like_post)

    def test_contact_url_resolves(self):
        url = reverse('webapp:contact')
        self.assertEqual(resolve(url).func, views.contact)

    def test_contact_success_url_resolves(self):
        url = reverse('webapp:contact_success')
        self.assertEqual(resolve(url).func, views.contact_success)

    def test_about_url_resolves(self):
        url = reverse('webapp:about')
        self.assertEqual(resolve(url).func, views.about)

    def test_user_profile_own_url_resolves(self):
        url = reverse('webapp:user_profile_own')
        self.assertEqual(resolve(url).func, views.user_profile)

    def test_user_profile_other_url_resolves(self):
        url = reverse('webapp:user_profile_other', args=['testuser'])
        self.assertEqual(resolve(url).func, views.user_profile)

    def test_follow_url_resolves(self):
        url = reverse('webapp:follow', args=[1])
        self.assertEqual(resolve(url).func, views.follow)

    def test_unfollow_url_resolves(self):
        url = reverse('webapp:unfollow', args=[1])
        self.assertEqual(resolve(url).func, views.unfollow)

    def test_login_url_resolves(self):
        url = reverse('webapp:login')
        self.assertEqual(resolve(url).func.view_class, LoginView)

    def test_logout_url_resolves(self):
        url = reverse('webapp:logout')
        self.assertEqual(resolve(url).func.view_class, LogoutView)

    def test_password_change_url_resolves(self):
        url = reverse('webapp:password_change')
        self.assertEqual(resolve(url).func, views.password_change)

    def test_password_reset_request_url_resolves(self):
        url = reverse('webapp:password_reset')
        self.assertEqual(resolve(url).func, views.password_reset_request)

    def test_password_reset_done_url_resolves(self):
        url = reverse('webapp:password_reset_done')
        self.assertEqual(resolve(url).func, views.password_reset_done)

    def test_password_reset_confirm_url_resolves(self):
        url = reverse('webapp:password_reset_confirm', args=['uidb64', 'token'])
        self.assertEqual(resolve(url).func, views.password_reset_confirm)

    def test_password_reset_complete_url_resolves(self):
        url = reverse('webapp:password_reset_complete')
        self.assertEqual(resolve(url).func, views.password_reset_complete)

    def test_user_agreement_url_resolves(self):
        url = reverse('webapp:user_agreement')
        self.assertEqual(resolve(url).func, views.user_agreement)

    def test_get_api_key_url_resolves(self):
        url = reverse('webapp:get_api_key')
        self.assertEqual(resolve(url).func, views.get_api_key)




class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_post_creation(self):
        post = Post.objects.create(user=self.user, title='Test Post')
        self.assertEqual(str(post), 'Test Post')

    def test_comment_creation(self):
        post = Post.objects.create(user=self.user, title='Test Post')
        comment = Comment.objects.create(post=post, user=self.user, content='Test comment content')
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'Test comment content')

    def test_like_creation(self):
        post = Post.objects.create(user=self.user, title='Test Post')
        like = Like.objects.create(post=post, user=self.user)
        self.assertEqual(like.post, post)
        self.assertEqual(like.user, self.user)

    def test_notification_creation(self):
        post = Post.objects.create(user=self.user, title='Test Post')
        notification = Notification.objects.create(
            user=self.user,
            text='Test notification text',
            post=post
        )
        self.assertEqual(str(notification), 'Test notification text')
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.text, 'Test notification text')
        self.assertEqual(notification.post, post)
        self.assertFalse(notification.read)

    def test_user_profile_creation(self):
        UserProfile.objects.filter(user=self.user).delete()
        user_profile = UserProfile.objects.create(user=self.user, about='Test user profile')
        self.assertEqual(str(user_profile), "testuser's Profile")
        self.assertEqual(user_profile.user, self.user)
        self.assertEqual(user_profile.about, 'Test user profile')

class APITestCase(TestCase):
    def test_get_api_key(self):
        response = self.client.get(reverse('webapp:get_api_key'))
        self.assertEqual(response.status_code, 200)
