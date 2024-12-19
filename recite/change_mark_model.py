import os
import django

# 设置环境变量，指定你的 settings 模块路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recite.settings')  # 替换为你的项目 settings 路径

# 初始化 Django 环境
django.setup()

# 使用 Django shell 创建所有 Category 数据
from marks.models import Category, Mark
existing_categories = Mark.objects.values('category').distinct()

# 遍历 Mark 表中的所有不同的 category 值
for category in existing_categories:
    Category.objects.get_or_create(name=category['category'])

# 将 Mark 表中的 category 字段更新为 Category 外键
for mark in Mark.objects.all():
    category_obj = Category.objects.get(name=mark.category)  # 获取对应的 Category 对象
    mark.category = category_obj  # 设置外键
    mark.save()  # 保存更新后的 mark
