from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Property(models.Model):
    """매물 정보"""

    class PropertyType(models.TextChoices):
        APARTMENT = 'apartment', '아파트'
        VILLA = 'villa', '빌라'
        MULTI_FAMILY = 'multi_family', '다세대'
        OFFICETEL = 'officetel', '오피스텔'
        MIXED_USE = 'mixed_use', '주상복합'

    class RiskGrade(models.TextChoices):
        A_PLUS = 'A+', 'A+'
        A = 'A', 'A'
        B_PLUS = 'B+', 'B+'
        B = 'B', 'B'
        C = 'C', 'C'
        D = 'D', 'D'

    # 기본 정보
    name = models.CharField(max_length=200, verbose_name='매물명')
    address = models.TextField(verbose_name='주소')
    address_detail = models.CharField(max_length=200, blank=True, verbose_name='상세주소')
    property_type = models.CharField(max_length=20, choices=PropertyType.choices, verbose_name='매물유형')
    size_sqm = models.FloatField(verbose_name='면적 (㎡)')
    floor = models.CharField(max_length=20, verbose_name='층수')
    built_year = models.IntegerField(verbose_name='건축년도')

    # 위치
    latitude = models.FloatField(verbose_name='위도')
    longitude = models.FloatField(verbose_name='경도')

    # 계약 조건
    deposit = models.BigIntegerField(verbose_name='보증금 (원)')
    monthly_rent = models.BigIntegerField(default=0, verbose_name='월세 (원)')

    # 리스크 판정
    risk_grade = models.CharField(
        max_length=5, choices=RiskGrade.choices, blank=True, verbose_name='리스크 등급'
    )
    risk_score = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='안전도 점수'
    )
    is_insurable = models.BooleanField(default=False, verbose_name='보증보험 가입 가능')

    # 임대인
    landlord = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='properties', verbose_name='임대인'
    )

    # 상태
    is_available = models.BooleanField(default=True, verbose_name='계약 가능')
    is_active = models.BooleanField(default=True, verbose_name='활성 매물')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '매물'
        verbose_name_plural = '매물 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_risk_grade_display()})"

    @property
    def deposit_display(self):
        """보증금 표시 (억/만원 단위)"""
        if self.deposit >= 100_000_000:
            return f"{self.deposit / 100_000_000:.1f}억"
        return f"{self.deposit / 10_000:.0f}만원"

    @property
    def rent_type(self):
        return '전세' if self.monthly_rent == 0 else '월세'


class PropertyImage(models.Model):
    """매물 이미지"""
    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RiskScan(models.Model):
    """물건지 리스크 스캔 결과"""

    class ItemStatus(models.TextChoices):
        SAFE = 'safe', '안전'
        WARNING = 'warning', '주의'
        DANGER = 'danger', '위험'

    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='risk_scans')
    scanned_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='scans'
    )
    scanned_at = models.DateTimeField(auto_now_add=True)

    # 판정 결과
    overall_grade = models.CharField(max_length=5, choices=Property.RiskGrade.choices)
    overall_score = models.IntegerField(default=0)

    # 등기부등본 분석
    mortgage_status = models.CharField(max_length=10, choices=ItemStatus.choices, default='safe')
    mortgage_detail = models.TextField(blank=True)

    ownership_status = models.CharField(max_length=10, choices=ItemStatus.choices, default='safe')
    ownership_detail = models.TextField(blank=True)

    seizure_status = models.CharField(max_length=10, choices=ItemStatus.choices, default='safe')
    seizure_detail = models.TextField(blank=True)

    # 전세가율
    jeonse_ratio = models.FloatField(default=0, verbose_name='전세가율 (%)')
    jeonse_status = models.CharField(max_length=10, choices=ItemStatus.choices, default='safe')

    # 임대인 정보
    landlord_multi_house = models.IntegerField(default=0, verbose_name='임대인 보유주택 수')
    landlord_status = models.CharField(max_length=10, choices=ItemStatus.choices, default='safe')

    tax_delinquency_status = models.CharField(max_length=10, choices=ItemStatus.choices, default='safe')
    tax_delinquency_detail = models.TextField(blank=True)

    # 보증보험
    hug_available = models.BooleanField(default=False, verbose_name='HUG 가입 가능')
    sgi_available = models.BooleanField(default=False, verbose_name='SGI 가입 가능')
    loan_available = models.BooleanField(default=False, verbose_name='전세대출 가능')

    # 깡통전세 위험도
    empty_house_risk = models.CharField(max_length=10, choices=ItemStatus.choices, default='safe')
    empty_house_detail = models.TextField(blank=True)

    class Meta:
        verbose_name = '리스크 스캔'
        verbose_name_plural = '리스크 스캔 목록'
        ordering = ['-scanned_at']

    def __str__(self):
        return f"{self.property.name} 스캔 ({self.overall_grade})"


class PropertyTag(models.Model):
    """매물 태그 (HUG가능, SGI가능 등)"""
    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='tags')
    label = models.CharField(max_length=50)
    tag_type = models.CharField(
        max_length=20,
        choices=[('positive', '긍정'), ('warning', '경고'), ('danger', '위험')],
        default='positive'
    )
