from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from linkedin_app.models import CustomUser, Post

# Register your models here.
UserAdmin.fieldsets += ('extra info', {'fields': ('name', 'bio', 'image', 'following')}),
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Post)
