from django.contrib import admin
from .models import User, Mark, Tag
# Register your models here.

admin.site.register(User)
admin.site.register(Mark)
admin.site.register(Tag)