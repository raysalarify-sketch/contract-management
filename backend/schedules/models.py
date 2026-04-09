from django.db import models


class RentSchedule(models.Model):
    """월세 납부 스케줄"""

    class PaymentType(models.TextChoices):
        PREPAID = 'prepaid', '선불 (매월 초)'
        POSTPAID = 'postpaid', '후불 (매월 말)'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', '예정'
        UPCOMING = 'upcoming', '납부 예정'
        PAID = 'paid', '납부 완료'
        OVERDUE = 'overdue', '미납'

    contract = models.ForeignKey('contracts.Contract', on_delete=models.CASCADE, related_name='rent_schedules')
    payment_type = models.CharField(max_length=10, choices=PaymentType.choices, default=PaymentType.PREPAID)

    # 납부 정보
    due_date = models.DateField(verbose_name='납부일')
    amount = models.BigIntegerField(verbose_name='납부 금액')
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    paid_date = models.DateField(null=True, blank=True, verbose_name='실제 납부일')
    paid_amount = models.BigIntegerField(default=0, verbose_name='실제 납부 금액')

    # 알림
    reminder_3days_sent = models.BooleanField(default=False, verbose_name='3일 전 알림')
    reminder_dueday_sent = models.BooleanField(default=False, verbose_name='당일 알림')
    overdue_reminder_sent = models.BooleanField(default=False, verbose_name='미납 알림')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '납부 스케줄'
        ordering = ['due_date']


class ContractEvent(models.Model):
    """계약 사후관리 이벤트"""

    class EventType(models.TextChoices):
        EXPIRY_ALERT = 'expiry_alert', '만기 안내'
        RENEWAL = 'renewal', '계약 갱신'
        INFO_CHANGE = 'info_change', '정보 변경'
        INSURANCE_RENEWAL = 'insurance_renewal', '보증보험 갱신'
        MARKET_REPORT = 'market_report', '시세 리포트'
        MORTGAGE_RELEASE = 'mortgage_release', '근저당 말소'
        DEPOSIT_RETURN = 'deposit_return', '보증금 반환'
        DISPUTE = 'dispute', '분쟁 대응'

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', '예정'
        ACTIVE = 'active', '활성'
        COMPLETED = 'completed', '완료'
        CANCELLED = 'cancelled', '취소'

    contract = models.ForeignKey('contracts.Contract', on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_date = models.DateField(verbose_name='예정일')
    completed_date = models.DateField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '계약 이벤트'
        ordering = ['scheduled_date']


class Notification(models.Model):
    """알림 (알림톡/문자)"""

    class Channel(models.TextChoices):
        KAKAO = 'kakao', '알림톡'
        SMS = 'sms', '문자'
        EMAIL = 'email', '이메일'
        PUSH = 'push', '푸시'

    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        SENT = 'sent', '발송'
        DELIVERED = 'delivered', '수신'
        FAILED = 'failed', '실패'

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    channel = models.CharField(max_length=10, choices=Channel.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    title = models.CharField(max_length=200)
    content = models.TextField()
    related_contract = models.ForeignKey(
        'contracts.Contract', on_delete=models.SET_NULL, null=True, blank=True
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '알림'
        ordering = ['-created_at']
