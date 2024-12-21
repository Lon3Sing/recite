from rest_framework import serializers
from .models import Mark, UserMark, Tag
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserCollection, CollectionMark

class UserCollectionSerializer(serializers.ModelSerializer):
    # 这个字段表示该收藏夹中所有的条目
    marks_count = serializers.IntegerField(source='marks.count', read_only=True)

    class Meta:
        model = UserCollection
        fields = ['id', 'name', 'created_at', 'updated_at', 'marks_count']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

# 固定 Mark 序列化器
class MarkSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True) 
    class Meta:
        model = Mark
        fields = ['id', 'title', 'content', 'category', 'created_at', 'tags']
    
    def update(self, instance, validated_data):
        # 提取 tags 字段的数据
        tags_data = validated_data.pop('tags', None)

        # 更新 Mark 对象的其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新 tags
        if tags_data is not None:
            # 更新标签，如果标签存在则获取 ID，不存在则创建新标签
            for tag_data in tags_data:
                tag_name = tag_data.get('name')
                tag = Tag.objects.filter(name=tag_name).first()
                if tag is None:
                    tag = Tag.objects.create(name=tag_name)
                # 更新 tags 关联（可以根据需要处理多个标签的逻辑）
                instance.tags.add(tag)

        return instance

# 用户收藏序列化器
class UserMarkSerializer(serializers.ModelSerializer):
    mark = MarkSerializer()  # 这里嵌套 Mark 序列化器
    class Meta:
        model = UserMark
        fields = ['id', 'mark', 'note', 'preference_level', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'password2', 'email']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords must match.")
        return attrs

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email'),
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email']  # 只允许更新这些字段

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("The new passwords must match.")
        return attrs
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user  # 获取登录的用户

        # 如果是管理员角色（假设管理员使用 is_mark_manager 标识）
        if user.is_superuser or user.is_mark_manager:
            data['is_admin'] = True  # 返回给前端是否为管理员
        else:
            data['is_admin'] = False

        return data
    

