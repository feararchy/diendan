from django.contrib import admin
from .models import Category, Topic, Comment

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at')
    list_filter = ('category',)

admin.site.register(Category)
admin.site.register(Comment)
