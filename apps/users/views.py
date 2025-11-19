from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.common.pagination import StandardResultsSetPagination
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ChangePasswordSerializer, AdminListSerializer
from .permissions import IsAdmin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .filters import UserFilter
from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from django.db.models.query import QuerySet

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if not user.is_active:
            return Response(
                {"detail": "Sizning profilingiz aktiv emas. Admin tomonidan bloklangansiz."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Tizimdan muvaffaqiyatli chiqdingiz."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Noto'g'ri token yoki Qora ro'yxatga kiritilgan."}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response({"old_password": ["Eski parol noto'g'ri."]}, status=status.HTTP_400_BAD_REQUEST)

        # parolni o'zgartirish
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)



class TeacherOnlyUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = StandardResultsSetPagination

    queryset = User.objects.exclude(phone_number='+998900748737').order_by('-created_at')

    filterset_class = UserFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['first_name', 'last_name', 'email', 'created_at']
    ordering = ['-created_at'] 


class AdminCreateUserAPIView(generics.CreateAPIView):
    """
    Admin foydalanuvchi qo'shish endpointi
    POST /users/users/
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser, FormParser]  # Rasm fayllarini qabul qilish uchun

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # create() metodi RegisterSerializer da ishlaydi

        # Agar rasm fayli kelsa, saqlash
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
	POST /users/{user_id}/change-password/
	Body:
	{
	  "new_password": "newpass",
	  "confirm_password": "newpass"
	}
	"""
	permission_classes = [IsAuthenticated, IsAdmin]

	def post(self, request, user_id, *args, **kwargs):
		data = request.data or {}
		new_password = data.get("new_password")
		confirm_password = data.get("confirm_password")

		# normalize possible list inputs (e.g. ["pass"]) -> "pass"
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

		# Build DRF-style validation error dict
		errors = {}
		if not new_password:
			errors["new_password"] = ["buni jo'nating."]
		if not confirm_password:
			errors["confirm_password"] = ["buni jo'nating."]
		if errors:
			return Response(errors, status=status.HTTP_400_BAD_REQUEST)

		if new_password != confirm_password:
			return Response({"confirm_password": ["Passwords do not match."]}, status=status.HTTP_400_BAD_REQUEST)

		# Get target user
		target_user = get_object_or_404(User, id=user_id)
		# Set new password (ensure string passed)
		target_user.set_password(new_password)
		target_user.save(update_fields=["password", "updated_at"])
		return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)

class UserStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        data = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "user_level": user.level,
            "user_course": user.course,
            "user_coins": user.coins,
        }
        return Response(data, status=status.HTTP_200_OK)

class AdminCheckUserAPIView(generics.ListAPIView):
    """
    Admin foydalanuvchi tekshirish endpointi
    GET /users/check-users/?uuid=...
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
    