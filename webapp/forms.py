from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Post, Comment, UserProfile
from django.forms import DateInput
from django_quill.forms import QuillFormField


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'login-username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'login-password'}))

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput)
    username = forms.CharField(max_length=30, required=True, widget=forms.TextInput)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password1
    
class PostForm(forms.ModelForm):
    description = QuillFormField()
    created_date = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Post
        fields = ['title', 'description', 'location', 'category', 'created_date']

    
class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100, required=True)
    email = forms.EmailField(label='Email', required=True)
    message = forms.CharField(label='Message', required=True, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': 'Comment',
        }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'comment-form'}),
        }

class EditProfileForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=False)
    background_pic = forms.ImageField(required=False)
    about = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = UserProfile
        fields = ('profile_pic', 'background_pic', 'about')