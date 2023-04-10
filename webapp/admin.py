from django.contrib import admin
from .models import Post
from .models import UserProfile
from .models import Tag

admin.site.register(Post)
admin.site.register(UserProfile)
admin.site.register(Tag)