from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from linkedin_app.models import CustomUser, Post, DirectMessage, Message

# Register your models here.
UserAdmin.fieldsets += ('extra info', {'fields': ('name', 'bio', 'image', 'following')}),
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Post)
admin.site.register(DirectMessage)
admin.site.register(Message)