from django.db import models
from django.contrib.auth.models import AbstractUser

# 用户模型
class User(AbstractUser):
    # 自定义字段
    bio = models.TextField(blank=True, null=True, verbose_name="用户简介")
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="头像")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

# 固定 Mark 模型
class Mark(models.Model):
    CATEGORY_CHOICES = [
        ('poem', 'Poem'),
        ('math', 'Math'),
        ('science', 'Science'),
        ('english', 'English'),
    ]
    title = models.CharField(max_length=255)  # 标题
    content = models.TextField()  # 条目内容
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # 分类
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return f"{self.title} ({self.category})"

class UserMark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_marks')  # 收藏用户
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE, related_name='user_marks')  # 被收藏条目
    note = models.TextField(blank=True, null=True)  # 用户对条目的备注
    preference_level = models.IntegerField(default=0)  # 用户喜好等级（0~5）
    created_at = models.DateTimeField(auto_now_add=True)  # 收藏时间
    updated_at = models.DateTimeField(auto_now=True)  # 笔记更新时间

    class Meta:
        unique_together = ('user', 'mark')  # 确保同一用户不能重复收藏同一条目

    def __str__(self):
        return f"{self.user.username} -> {self.mark.title}"