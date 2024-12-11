from rest_framework import serializers
from .models import Mark, UserMark
from django.contrib.auth import get_user_model

# 固定 Mark 序列化器
class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = ['id', 'title', 'content', 'category', 'created_at']

# 用户收藏序列化器
class UserMarkSerializer(serializers.ModelSerializer):
    mark = MarkSerializer(read_only=True)  # 嵌套 Mark 信息
    mark_id = serializers.PrimaryKeyRelatedField(queryset=Mark.objects.all(), source='mark')  # 用于添加收藏时传递条目 ID

    class Meta:
        model = UserMark
        fields = ['id', 'user', 'mark', 'mark_id', 'note', 'created_at', 'updated_at']
        read_only_fields = ['user']

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