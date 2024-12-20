from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework import permissions

# 用户模型
class User(AbstractUser):
    # 自定义字段
    bio = models.TextField(blank=True, null=True, verbose_name="用户简介")
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="头像")
    is_mark_manager = models.BooleanField(default=False)  # 自定义字段，表示是否为管理员

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

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
    tags = models.ManyToManyField(Tag, related_name='marks')  # 多对多关系

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

# 定义自定义管理员类
class Administrator(AbstractUser):
    # 为防止与默认 User 模型发生冲突，添加 related_name
    is_mark_manager = models.BooleanField(default=True, help_text="Can manage Marks")
    is_tag_manager = models.BooleanField(default=True, help_text="Can manage Tags")

    # 修改 'groups' 和 'user_permissions' 的 related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='administrator_groups',  # 自定义反向关系
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='administrator_permissions',  # 自定义反向关系
        blank=True
    )

    def __str__(self):
        return self.username

# 可选: 为 Admin 用户赋予额外的权限
class Permission(models.Model):
    admin = models.ForeignKey(Administrator, on_delete=models.CASCADE)
    can_manage_marks = models.BooleanField(default=False)
    can_manage_tags = models.BooleanField(default=False)