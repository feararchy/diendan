from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên Chuyên Mục")
    description = models.TextField(verbose_name="Mô tả", blank=True)
    def __str__(self): return self.name

class Topic(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics', verbose_name="Chuyên mục")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Tác giả")
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    content = models.TextField(verbose_name="Nội dung bài viết")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Comment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Bình luận")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Bình luận của {self.author.username}"
