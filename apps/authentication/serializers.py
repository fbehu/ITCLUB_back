from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username_or_phone = data.get("username_or_phone")
        password = data.get("password")

        user = authenticate(phone_number=username_or_phone, password=password)

        if not user:
            user = authenticate(username=username_or_phone, password=password)

        if not user:
            raise serializers.ValidationError("Login yoki parol noto'g'ri")

        data["user"] = user
        return data
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        user = instance.get('user')
        if user:
            refresh = RefreshToken.for_user(user)
            ret['access'] = str(refresh.access_token)
            ret['refresh'] = str(refresh)
        return ret
