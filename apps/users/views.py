from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from apps.common.pagination import StandardResultsSetPagination
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import AdminListSerializer
from .permissions import IsAdmin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .filters import UserFilter
from .models import User
from .serializers import UserSerializer, RegisterSerializer
from apps.chat.serializers import ConversationUserSerializer

class TeacherOnlyUserListView(generics.ListAPIView):
    serializer_class = ConversationUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = StandardResultsSetPagination

    queryset = User.objects.exclude(phone_number='+998900748737').order_by('-created_at')

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserFilter
    ordering_fields = ['first_name', 'last_name', 'email', 'created_at']
    ordering = ['-created_at']


class AdminCreateUserAPIView(generics.CreateAPIView):
    """
    Admin foydalanuvchi qo'shish endpointi
    POST /users/add/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # Form data'dagi barcha qiymatlarni to'g'ri qayta ishlash
        data = {}
        
        for key, value in request.data.items():
            if key == 'group':
                # group fieldini groups array'ga o'zgartirish
                if value:
                    if isinstance(value, list):
                        value = value[0] if value else None
                    if value:
                        data['groups'] = [int(value)]
            else:
                # Boshqa fieldlar uchun - agar list bo'lsa, birinchi elementni olish
                if isinstance(value, list):
                    data[key] = value[0] if value else None
                else:
                    data[key] = value
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        photo = request.FILES.get('photo')
        if photo:
            user.photo = photo
            user.save(update_fields=['photo'])

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class AdminUserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = "pk"
    parser_classes = [MultiPartParser, FormParser]


class AdminChangeUserPasswordAPIView(APIView):
	"""
	Admin-only endpoint to change another user's password without old password.
	Student-only endpoint to change own password with old password.
	
	Admin case:
	POST /users/{user_id}/change-password/
	Body:
	{
	  "new_password": "newpass",
	  "confirm_password": "newpass"
	}
	
	Student case:
	POST /users/{user_id}/change-password/
	Body:
	{
	  "old_password": "oldpass",
	  "new_password": "newpass",
	  "confirm_password": "newpass"
	}
	"""
	permission_classes = [IsAuthenticated]

	def post(self, request, user_id, *args, **kwargs):
		current_user = request.user
		data = request.data or {}
		new_password = data.get("new_password")
		confirm_password = data.get("confirm_password")
		old_password = data.get("old_password")

		def _to_str(val):
			if isinstance(val, list):
				return val[0] if val else None
			if isinstance(val, bytes):
				try:
					return val.decode("utf-8")
				except Exception:
					return str(val)
			if val is None:
				return None
			return str(val)

		new_password = _to_str(new_password)
		confirm_password = _to_str(confirm_password)
		old_password = _to_str(old_password)

		target_user = get_object_or_404(User, id=user_id)
		errors = {}
		
		if current_user.role == 'student':
			if str(current_user.id) != str(user_id):
				return Response(
					{"detail": "Siz faqat o'zingizning parolingizni o'zgartira olasiz."},
					status=status.HTTP_403_FORBIDDEN
				)
			
			if not old_password:
				errors["old_password"] = ["Eski parolni jo'nating."]
			if not new_password:
				errors["new_password"] = ["Yangi parolni jo'nating."]
			if not confirm_password:
				errors["confirm_password"] = ["Parolni tasdiqlang."]
			
			if errors:
				return Response(errors, status=status.HTTP_400_BAD_REQUEST)
			
			if not current_user.check_password(old_password):
				return Response(
					{"old_password": ["Eski parol noto'g'ri."]},
					status=status.HTTP_400_BAD_REQUEST
				)
		
		elif current_user.role == 'admin':
			if not new_password:
				errors["new_password"] = ["buni jo'nating."]
			if not confirm_password:
				errors["confirm_password"] = ["buni jo'nating."]
			
			if errors:
				return Response(errors, status=status.HTTP_400_BAD_REQUEST)
		
		else:
			return Response(
				{"detail": "Sizda bu amalni bajarish huquqi yo'q."},
				status=status.HTTP_403_FORBIDDEN
			)

		if new_password != confirm_password:
			return Response(
				{"confirm_password": ["Parollar mos kelmadi."]},
				status=status.HTTP_400_BAD_REQUEST
			)

		target_user.set_password(new_password)
		target_user.save(update_fields=["password", "updated_at"])
		return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)


class AdminCheckUserAPIView(generics.ListAPIView):
    """
    Admin foydalanuvchi tekshirish endpointi
    GET /users/check/?uuid=...
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('uuid', None)
        if uuid is not None:
            return User.objects.filter(uuid=uuid)
        return User.objects.none()
    

class AdminsListView(generics.ListAPIView):
    """
    Admin foydalanuvchilar ro'yxati
    GET /users/admins/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AdminListSerializer

    def get_queryset(self):
        return User.objects.filter(role='admin').order_by('-created_at')
