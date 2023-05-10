from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from decouple import config
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from webapp.views import password_change, like_post, follow, get_api_key, create_a_post, post_search, home
from webapp.models import Post, Comment, Like
from datetime import timezone
from forms import ContactForm
from django.urls import reverse

class UserAuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_signup_with_valid_details(self):
        user_data = {
            'username': 'newuser',
            'password': 'newpassword123'
        }
        response = self.client.post('/signup/', user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=user_data['username']).exists())

    def test_signup_with_invalid_details(self):
        user_data = {
            'username': 'newuser',
            'password': 'short'
        }
        response = self.client.post('/signup/', user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=user_data['username']).exists())

    def test_login_with_valid_credentials(self):
        response = self.client.post('/login/', self.user_data, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_with_invalid_credentials(self):
        user_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/login/', user_data, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)


class CreatePostTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@gmail.com', password='top_secret')

    def test_create_post(self):
        request = self.factory.post('/create_a_post', {'title': 'Test Post', 'description': 'Test Description', 'category': 'Test Category', 'latitude': '0.0', 'longitude': '0.0'})
        request.user = self.user

        response = create_a_post(request)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, 'webapp:home')
        self.assertEqual(Post.objects.filter(title='Test Post').count(), 1)


class PostSearchTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@gmail.com', password='top_secret')
        self.post = Post.objects.create(title='Test Post', description='Test Description', user=self.user,
                                        created_date=timezone.now(), location='Test Location')

    def test_post_search_title(self):
        request = self.factory.get('/post_search', {'search': 'Test Post'})

        response = post_search(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['posts']), 1)
        self.assertEqual(response.context_data['posts'][0], self.post)

    def test_post_search_date(self):
        request = self.factory.get('/post_search', {'date_range': f'{timezone.now().date()} - {timezone.now().date()}'})

        response = post_search(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['posts']), 1)
        self.assertEqual(response.context_data['posts'][0], self.post)

    def test_post_search_location(self):
        request = self.factory.get('/post_search', {'search': 'Test Location'})

        response = post_search(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['posts']), 1)
        self.assertEqual(response.context_data['posts'][0], self.post)

class HomeTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@gmail.com', password='top_secret')
        self.client.login(username='jacob', password='top_secret')

    def test_home_view(self):
        request = self.factory.get('/home')
        request.user = self.user
        response = home(request)
        self.assertEqual(response.status_code, 200)

class AddCommentTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@gmail.com', password='top_secret')
        self.post = Post.objects.create(title='Test Post', description='Test Description', user=self.user)

    def test_add_comment(self):
        self.client.login(username='jacob', password='top_secret')
        response = self.client.post(f'/add_comment/{self.post.id}', {'text': 'Test comment'})
        self.assertEqual(response.status_code, 302) # Expecting a redirect
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().text, 'Test comment')

class DeleteCommentTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@gmail.com', password='top_secret')
        self.post = Post.objects.create(title='Test Post', description='Test Description', user=self.user)
        self.comment = Comment.objects.create(post=self.post, user=self.user, text='Great post!')

    def test_delete_comment(self):
        self.client.login(username='jacob', password='top_secret')
        response = self.client.post(f'/delete_comment/{self.comment.id}')
        self.assertEqual(response.status_code, 302) # Expecting a redirect
        self.assertEqual(Comment.objects.count(), 0)


class ContactTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_contact_form(self):
        form_data = {'name': 'Test User', 'email': 'testuser@gmail.com', 'message': 'Hello!'}
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact(self):
        form_data = {'name': 'Test User', 'email': 'testuser@gmail.com', 'message': 'Hello!'}
        response = self.client.post('/contact', form_data)
        self.assertEqual(response.status_code, 302) # Expecting a redirect


class LikePostTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username='jacob', email='jacob@gmail.com', password='top_secret')
        self.user2 = User.objects.create_user(username='mark', email='mark@gmail.com', password='top_secret')
        self.post = Post.objects.create(title='Test Post', description='Test Description', user=self.user2)

    def test_like_post(self):
        request = self.factory.post(f'/like_post/{self.post.id}')
        request.user = self.user1

        response = like_post(request, self.post.id)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'webapp:post_detail/{self.post.id}')
        self.assertEqual(Like.objects.filter(post=self.post, user=self.user1).count(), 1)

class UserProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        self.user_profile_url = reverse('user_profile_own')
        self.other_user_profile_url = reverse('user_profile_other', kwargs={'username': 'testuser2'})

    def test_authenticated_user_can_view_own_profile(self):
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser1')

    def test_authenticated_user_can_edit_own_profile(self):
            self.client.login(username='testuser1', password='testpass123')
            with open('path_to_profile_pic.jpg', 'rb') as profile_pic, open('path_to_background_pic.jpg', 'rb') as background_pic:
                response = self.client.post(self.user_profile_url, {
                    'username': 'newuser1', 
                    'email': 'newuser1@test.com',
                    'profile.profile_picture': profile_pic,
                    'profile.background_picture': background_pic,
                    'profile.about': 'This is a test about section.'
                })
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, self.user_profile_url)
            self.user1.refresh_from_db()
            self.assertEqual(self.user1.username, 'newuser1')
            self.assertEqual(self.user1.email, 'newuser1@test.com')
            self.assertEqual(self.user1.profile.about, 'This is a test about section.')

    def test_user_cannot_edit_someone_elses_profile(self):
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.post(self.other_user_profile_url, {'username': 'newuser2', 'email': 'newuser2@test.com'})
        self.assertEqual(response.status_code, 403)
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.username, 'testuser2')
        self.assertNotEqual(self.user2.email, 'newuser2@test.com')


class FollowUserTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username='jacob', email='jacob@gmail.com', password='top_secret')
        self.user2 = User.objects.create_user(username='mark', email='mark@gmail.com', password='top_secret')

    def test_follow_user(self):
        request = self.factory.post(f'/follow/{self.user2.id}')
        request.user = self.user1

        response = follow(request, self.user2.id)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'webapp:user_profile_other/{self.user2.username}')
        self.assertTrue(self.user2 in self.user1.profile.following.all())

class PasswordChangeTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@gmail.com', password='top_secret')

    def test_password_change(self):
        request = self.factory.post('/password_change', {'old_password': 'top_secret', 'new_password1': 'new_secret', 'new_password2': 'new_secret'})
        request.user = self.user

        response = password_change(request)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, 'webapp:user_profile_own')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_secret'))


class GetApiKeyTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_api_key(self):
        request = self.factory.get('/get_api_key')
        response = get_api_key(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content['google_api_key'], config('API_KEY'))

