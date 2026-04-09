from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """확장 사용자 모델"""

    class Role(models.TextChoices):
        LANDLORD = 'landlord', '임대인'
        TENANT = 'tenant', '임차인'
        AGENT = 'agent', '공인중개사'
        ADMIN = 'admin', '관리자'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TENANT)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False, verbose_name='본인인증 완료')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    company = models.ForeignKey(
        'Company', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='employees', verbose_name='소속 회사'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class Company(models.Model):
    """사내대출 연동 회사"""
    name = models.CharField(max_length=100, verbose_name='회사명')
    business_number = models.CharField(max_length=20, unique=True, verbose_name='사업자번호')
    representative = models.CharField(max_length=50, verbose_name='대표자명')
    address = models.TextField(verbose_name='회사 주소')
    loan_budget = models.BigIntegerField(default=0, verbose_name='대출 운용예산')
    loan_used = models.BigIntegerField(default=0, verbose_name='사용 금액')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '회사'
        verbose_name_plural = '회사 목록'

    def __str__(self):
        return self.name

    @property
    def usage_rate(self):
        if self.loan_budget == 0:
            return 0
        return round(self.loan_used / self.loan_budget * 100, 1)


class LandlordProfile(models.Model):
    """임대인 프로필 (응답률 등)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')
    response_rate = models.FloatField(default=0, verbose_name='응답률 (%)')
    avg_response_minutes = models.IntegerField(default=0, verbose_name='평균 응답시간 (분)')
    total_properties = models.IntegerField(default=0, verbose_name='등록 매물 수')
    total_contracts = models.IntegerField(default=0, verbose_name='완료 계약 수')

    class Meta:
        verbose_name = '임대인 프로필'

    def __str__(self):
        return f"{self.user.get_full_name()} 임대인 프로필"


class AgentProfile(models.Model):
    """공인중개사 프로필"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    license_number = models.CharField(max_length=30, verbose_name='등록번호')
    office_name = models.CharField(max_length=100, verbose_name='사무소명')
    office_address = models.TextField(verbose_name='사무소 주소')
    office_phone = models.CharField(max_length=20, verbose_name='사무소 전화')

    class Meta:
        verbose_name = '중개사 프로필'

    def __str__(self):
        return f"{self.office_name} ({self.user.get_full_name()})"
