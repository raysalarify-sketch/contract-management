import os
import django

# 환경 변수 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workd_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = '관리자'
password = '123456'

# 관리자 계정이 없으면 생성, 있으면 비밀번호 초기화
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password, email='admin@example.com')
    print(f"Superuser '{username}' created successfully!")
else:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"Superuser '{username}' password updated successfully!")
