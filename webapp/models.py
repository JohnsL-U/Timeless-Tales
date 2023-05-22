from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_quill.fields import QuillField


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = QuillField()
    memory_date = models.DateField(blank=True, null=True)
    include_time = models.BooleanField(default=False)
    time = models.TimeField(blank=True, null=True)
    published_date = models.DateField(default=timezone.now)
    SEASONS = (
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
        ('Winter', 'Winter')
    )
    DECADES = [(str(i), str(i)) for i in range(1900, 2030, 10)]
    YEARS = [(str(i), str(i)) for i in range(1900, 2031)]
    season = models.CharField(max_length=10, choices=SEASONS, null=True, blank=True)
    decade = models.CharField(max_length=4, choices=DECADES, null=True, blank=True)
    year = models.CharField(max_length=4, choices=YEARS, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    CATEGORY_CHOICES = (
    ('military', 'Military'),
    ('social', 'Social'),
    ('political', 'Political'),
    ('economic', 'Economic'),
    ('technological', 'Technological'),
    ('intellectual', 'Intellectual'),
    ('environmental', 'Environmental'),
    ('medical', 'Medical'),
    ('artistic', 'Artistic'),
    ('religious', 'Religious'),
    ('sports', 'Sports')
)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    
    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
    
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateField(auto_now_add=True)

class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.text
    
    def save(self, *args, **kwargs):
        max_notifications = 5 
        notification_count = Notification.objects.filter(user=self.user).count()

        if notification_count >= max_notifications:
            notifications_to_delete = Notification.objects.filter(user=self.user).order_by('created_at')[:notification_count - max_notifications + 1]
            Notification.objects.filter(id__in=[notification.id for notification in notifications_to_delete]).delete()
        
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    about = models.CharField(max_length=500, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pictures/', default='images/default_profile_pic.png')
    background_pic = models.ImageField(upload_to='background_pictures/', null=True, blank=True)
    following = models.ManyToManyField(User, related_name='followers', blank=True)
    join_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @receiver(post_save, sender=User)
    def create_UserProfile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)
         
