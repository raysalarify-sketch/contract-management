from django.db import models


class InsuranceApplication(models.Model):
    """보증보험 가입 신청"""

    class Provider(models.TextChoices):
        HUG = 'hug', 'HUG (주택도시보증공사)'
        SGI = 'sgi', 'SGI (서울보증보험)'

    class Status(models.TextChoices):
        PENDING = 'pending', '신청 대기'
        APPLIED = 'applied', '신청 완료'
        REVIEWING = 'reviewing', '심사 중'
        APPROVED = 'approved', '승인'
        REJECTED = 'rejected', '거절'
        ACTIVE = 'active', '가입 완료'
        EXPIRING = 'expiring', '만기 임박'
        EXPIRED = 'expired', '만기'
        RENEWED = 'renewed', '갱신'

    contract = models.ForeignKey('contracts.Contract', on_delete=models.CASCADE, related_name='insurance_apps')
    provider = models.CharField(max_length=10, choices=Provider.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # 보험 정보
    coverage_amount = models.BigIntegerField(verbose_name='보장 금액')
    premium = models.BigIntegerField(default=0, verbose_name='보험료')
    premium_rate = models.FloatField(default=0.00128, verbose_name='보험료율')

    start_date = models.DateField(null=True, blank=True, verbose_name='보험 시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='보험 종료일')
    policy_number = models.CharField(max_length=50, blank=True, verbose_name='증권번호')

    applied_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '보증보험'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_provider_display()} - {self.get_status_display()}"


class NotaryApplication(models.Model):
    """공증 신청"""

    class Status(models.TextChoices):
        PENDING = 'pending', '신청 대기'
        MATCHED = 'matched', '공증사무소 매칭'
        SCHEDULED = 'scheduled', '일정 확정'
        COMPLETED = 'completed', '공증 완료'
        CANCELLED = 'cancelled', '취소'

    contract = models.ForeignKey('contracts.Contract', on_delete=models.CASCADE, related_name='notary_apps')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notary_office = models.CharField(max_length=100, blank=True, verbose_name='공증사무소')
    scheduled_date = models.DateTimeField(null=True, blank=True)
    fee = models.BigIntegerField(default=0, verbose_name='공증 비용')
    document = models.FileField(upload_to='notary/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '공증 신청'


class MortgageApplication(models.Model):
    """근저당 설정 신청"""

    class Status(models.TextChoices):
        PENDING = 'pending', '신청 대기'
        LAWYER_MATCHED = 'lawyer_matched', '법무사 매칭'
        PROCESSING = 'processing', '처리 중'
        REGISTERED = 'registered', '설정 완료'
        RELEASED = 'released', '말소 완료'
        CANCELLED = 'cancelled', '취소'

    contract = models.ForeignKey('contracts.Contract', on_delete=models.CASCADE, related_name='mortgage_apps')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    amount = models.BigIntegerField(verbose_name='설정 금액')
    lawyer_name = models.CharField(max_length=50, blank=True, verbose_name='법무사명')
    lawyer_phone = models.CharField(max_length=20, blank=True)
    fee = models.BigIntegerField(default=0, verbose_name='설정 비용')
    registered_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '근저당 설정'
