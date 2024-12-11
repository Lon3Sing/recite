import os
import django

# 设置环境变量，指定你的 settings 模块路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recite.settings')  # 替换为你的项目 settings 路径

# 初始化 Django 环境
django.setup()

from django.db import connection

# 清理迁移记录
with connection.cursor() as cursor:
    cursor.execute("DELETE FROM django_migrations WHERE app='marks';")
    cursor.execute("DELETE FROM django_migrations WHERE app='admin';")

print("迁移记录已清理")
