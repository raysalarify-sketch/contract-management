from rest_framework import serializers, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, LandlordProfile, AgentProfile
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'phone', 'is_verified', 'profile_image']
        read_only_fields = ['is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name', 'role', 'phone']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '비밀번호가 일치하지 않습니다'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.role == User.Role.LANDLORD:
            LandlordProfile.objects.create(user=user)
        elif user.role == User.Role.AGENT:
            AgentProfile.objects.create(user=user)

        return user


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SimpleLoginView(APIView):
    """성함 + 6자리 PIN 번호로 로그인"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        name = request.data.get('name')
        pin = request.data.get('pin')

        if not name or not pin:
            return Response({'error': '성함과 비밀번호를 모두 입력해주세요.'}, status=400)

        # 1. 성함으로 사용자 검색 (최신순 또는 고유 식별자 필요할 수 있음)
        # 여기선 간단히 성함(first_name)과 비밀번호가 맞는 사용자를 찾음
        users = User.objects.filter(first_name=name).order_by('-date_joined')
        
        target_user = None
        for user in users:
            if user.check_password(pin):
                target_user = user
                break
        
        if not target_user:
            return Response({'error': '정보가 일치하지 않습니다.'}, status=401)

        # 2. 토큰 생성
        refresh = RefreshToken.for_user(target_user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(target_user).data
        })
