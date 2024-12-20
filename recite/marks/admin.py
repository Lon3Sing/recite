from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Mark, Tag, Administrator
# Register your models here.

admin.site.register(User)
admin.site.register(Mark)
admin.site.register(Tag)

# 自定义 Administrator 管理员界面
class AdministratorAdmin(UserAdmin):
    model = Administrator
    list_display = ['username', 'email', 'is_mark_manager', 'is_tag_manager']
    list_filter = ['is_mark_manager', 'is_tag_manager']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_mark_manager', 'is_tag_manager')}),
    )

admin.site.register(Administrator, AdministratorAdmin)