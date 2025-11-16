from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class UsernameOrPhoneBackend(ModelBackend):
    """
    Username yoki phone_number orqali login qilish uchun custom backend
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Avval username orqali qidiramiz
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                # Agar topilmasa phone_number orqali qidiramiz
                user = User.objects.get(phone_number=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None
