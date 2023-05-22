from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Post, Comment, UserProfile
from django.forms import DateInput, TimeInput
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
    memory_date = forms.DateTimeField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )
    include_time = forms.BooleanField(required=False, initial=False)
    time = forms.TimeField(required=False, widget=TimeInput(attrs={'type': 'time'}), input_formats=['%H:%M'])
    latitude = forms.DecimalField(widget=forms.HiddenInput(), required=True)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), required=True)
    tags = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Separate multiple tags with commas'}),
    )
    

    class Meta:
        model = Post
        fields = ['title', 'description', 'location', 'category', 'tags', 'memory_date', 'include_time', 'time', 'season', 'decade', 'year']
        widgets = {'location': forms.TextInput(attrs={'id': 'location'})}

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['time'].widget.attrs['disabled'] = 'disabled'

    def clean(self):
        cleaned_data = super().clean()
        include_time = cleaned_data.get('include_time', False)
        time_optional = cleaned_data.get('time')

        if include_time and not time_optional:
            self.add_error('time', "Please enter a valid time.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        tags = self.cleaned_data['tags']

        if tags:
            categories_list = [cat.strip() for cat in tags.split(',') if cat.strip()]
            instance.tags = ', '.join(categories_list)

        if commit:
            instance.save()

        return instance
    
    
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

