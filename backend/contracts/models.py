from django.db import models


class Inquiry(models.Model):
    """임대인 문의 (채팅)"""

    class Status(models.TextChoices):
        ACTIVE = 'active', '진행중'
        VIEWING_SCHEDULED = 'viewing_scheduled', '방문예정'
        CLOSED = 'closed', '종료'

    related_property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='inquiries')
    tenant = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='inquiries_sent')
    landlord = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='inquiries_received')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    viewing_date = models.DateTimeField(null=True, blank=True, verbose_name='방문 일정')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '문의'
        ordering = ['-updated_at']


class InquiryMessage(models.Model):
    """문의 메시지"""

    class SenderType(models.TextChoices):
        TENANT = 'tenant', '임차인'
        LANDLORD = 'landlord', '임대인'
        SYSTEM = 'system', '시스템'

    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SenderType.choices)
    sender = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ContractAgreement(models.Model):
    """계약 진행 합의 (계약하기 단계)"""

    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        DEPOSIT_AGREED = 'deposit_agreed', '보증금 합의'
        PERIOD_AGREED = 'period_agreed', '기간 합의'
        LANDLORD_AGREED = 'landlord_agreed', '임대인 동의'
        TENANT_AGREED = 'tenant_agreed', '임차인 동의'
        BOTH_AGREED = 'both_agreed', '쌍방 합의'
        CANCELLED = 'cancelled', '취소'

    related_property = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    tenant = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='agreements_as_tenant')
    landlord = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='agreements_as_landlord')

    # 합의된 조건
    agreed_deposit = models.BigIntegerField(verbose_name='합의 보증금')
    agreed_rent = models.BigIntegerField(default=0, verbose_name='합의 월세')
    agreed_start_date = models.DateField(verbose_name='계약 시작일')
    agreed_end_date = models.DateField(verbose_name='계약 종료일')
    agreed_move_in_date = models.DateField(verbose_name='입주일')

    # 안전장치
    safety_insurance = models.BooleanField(default=False, verbose_name='보증보험')
    safety_notary = models.BooleanField(default=False, verbose_name='공증')
    safety_mortgage = models.BooleanField(default=False, verbose_name='근저당 설정')

    # 합의 상태
    deposit_agreed = models.BooleanField(default=False)
    period_agreed = models.BooleanField(default=False)
    landlord_agreed = models.BooleanField(default=False)
    landlord_agreed_at = models.DateTimeField(null=True, blank=True)
    tenant_agreed = models.BooleanField(default=False)
    tenant_agreed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '계약 합의'
        ordering = ['-created_at']


class Contract(models.Model):
    """표준 임대차계약서"""

    class Status(models.TextChoices):
        DRAFT = 'draft', '작성중'
        LANDLORD_CONFIRMED = 'landlord_confirmed', '임대인 확인'
        TENANT_CONFIRMED = 'tenant_confirmed', '임차인 확인'
        BOTH_CONFIRMED = 'both_confirmed', '쌍방 확인'
        AGENT_VERIFIED = 'agent_verified', '중개사 확인'
        SIGNED = 'signed', '서명 완료'
        ACTIVE = 'active', '계약 진행중'
        EXPIRING = 'expiring', '만기 임박'
        EXPIRED = 'expired', '만기'
        RENEWED = 'renewed', '갱신'
        TERMINATED = 'terminated', '해지'

    agreement = models.OneToOneField(ContractAgreement, on_delete=models.CASCADE, related_name='contract')
    related_property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='contracts')
    tenant = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='contracts_as_tenant')
    landlord = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='contracts_as_landlord')
    agent = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='contracts_as_agent', verbose_name='공인중개사'
    )

    # 계약 조건
    deposit = models.BigIntegerField(verbose_name='보증금')
    monthly_rent = models.BigIntegerField(default=0, verbose_name='월세')
    start_date = models.DateField(verbose_name='계약 시작일')
    end_date = models.DateField(verbose_name='계약 종료일')
    move_in_date = models.DateField(verbose_name='입주일')
    special_terms = models.TextField(blank=True, verbose_name='특약사항')

    # 상태
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # 확인/서명
    landlord_confirmed = models.BooleanField(default=False)
    landlord_confirmed_at = models.DateTimeField(null=True, blank=True)
    tenant_confirmed = models.BooleanField(default=False)
    tenant_confirmed_at = models.DateTimeField(null=True, blank=True)
    agent_verified = models.BooleanField(default=False)
    agent_verified_at = models.DateTimeField(null=True, blank=True)

    # 계약서 문서
    contract_document = models.FileField(upload_to='contracts/', blank=True, null=True)
    signed_document = models.FileField(upload_to='contracts/signed/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '계약서'
        verbose_name_plural = '계약서 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.related_property.name} 계약 ({self.get_status_display()})"

    @property
    def days_until_expiry(self):
        from django.utils import timezone
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return delta.days
        return None


class ESignature(models.Model):
    """전자서명"""

    class SignerRole(models.TextChoices):
        LANDLORD = 'landlord', '임대인'
        TENANT = 'tenant', '임차인'
        AGENT = 'agent', '공인중개사'

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='signatures')
    signer = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    signer_role = models.CharField(max_length=10, choices=SignerRole.choices)
    signature_data = models.TextField(verbose_name='서명 데이터 (base64)')
    ip_address = models.GenericIPAddressField(verbose_name='서명 IP')
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '전자서명'
        unique_together = ['contract', 'signer_role']

    def __str__(self):
        return f"{self.contract} - {self.get_signer_role_display()} 서명"


class AgentVerification(models.Model):
    """공인중개사 확인 항목"""
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='agent_verification')
    agent = models.ForeignKey('accounts.User', on_delete=models.CASCADE)

    contract_validity = models.BooleanField(default=False, verbose_name='계약서 적정성')
    property_status = models.BooleanField(default=False, verbose_name='물건지 현황')
    commission_calc = models.BooleanField(default=False, verbose_name='중개보수 산정')
    disclosure_form = models.BooleanField(default=False, verbose_name='확인·설명서')

    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = '중개사 확인'

    @property
    def is_complete(self):
        return all([
            self.contract_validity, self.property_status,
            self.commission_calc, self.disclosure_form
        ])
