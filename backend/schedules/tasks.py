"""
Celery tasks - 비동기 알림/스케줄 관리
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_notification(user_id, channel, title, content, contract_id=None):
    """알림 발송 (알림톡/SMS/이메일)"""
    from schedules.models import Notification
    from accounts.models import User

    user = User.objects.get(id=user_id)
    notification = Notification.objects.create(
        user=user,
        channel=channel,
        title=title,
        content=content,
        related_contract_id=contract_id,
    )

    if channel == 'kakao':
        # TODO: 카카오 알림톡 API 연동
        # from workd_project.kakao import send_alimtalk
        # send_alimtalk(user.phone, template_code, variables)
        pass
    elif channel == 'sms':
        # TODO: SMS API 연동
        pass

    notification.status = 'sent'
    notification.sent_at = timezone.now()
    notification.save()
    return notification.id


@shared_task
def check_rent_due_dates():
    """매일 실행: 월세 납부일 확인 및 알림 발송"""
    from schedules.models import RentSchedule

    today = timezone.now().date()
    three_days_later = today + timedelta(days=3)

    # 3일 전 알림
    upcoming = RentSchedule.objects.filter(
        due_date=three_days_later,
        status='pending',
        reminder_3days_sent=False
    )
    for schedule in upcoming:
        contract = schedule.contract
        send_notification.delay(
            user_id=contract.tenant_id,
            channel='kakao',
            title='월세 납부 안내',
            content=f'{schedule.due_date} 월세 {schedule.amount:,}원 납부 예정입니다.',
            contract_id=contract.id,
        )
        schedule.reminder_3days_sent = True
        schedule.status = 'upcoming'
        schedule.save()

    # 당일 알림
    due_today = RentSchedule.objects.filter(
        due_date=today,
        status='upcoming',
        reminder_dueday_sent=False
    )
    for schedule in due_today:
        contract = schedule.contract
        send_notification.delay(
            user_id=contract.tenant_id,
            channel='kakao',
            title='월세 납부일 알림',
            content=f'오늘 월세 {schedule.amount:,}원 납부일입니다.',
            contract_id=contract.id,
        )
        schedule.reminder_dueday_sent = True
        schedule.save()

    # 미납 알림 (3일 경과)
    overdue_date = today - timedelta(days=3)
    overdue = RentSchedule.objects.filter(
        due_date=overdue_date,
        status='upcoming',
        overdue_reminder_sent=False
    )
    for schedule in overdue:
        contract = schedule.contract
        schedule.status = 'overdue'
        schedule.overdue_reminder_sent = True
        schedule.save()

        # 임차인 알림
        send_notification.delay(
            user_id=contract.tenant_id,
            channel='kakao',
            title='월세 미납 알림',
            content=f'{schedule.due_date} 월세 {schedule.amount:,}원이 미납 상태입니다.',
            contract_id=contract.id,
        )
        # 임대인 알림
        send_notification.delay(
            user_id=contract.landlord_id,
            channel='kakao',
            title='월세 미납 안내',
            content=f'{contract.tenant.get_full_name()} 임차인의 월세가 미납 상태입니다.',
            contract_id=contract.id,
        )


@shared_task
def check_contract_expiry():
    """매일 실행: 계약 만기 확인 및 알림"""
    from contracts.models import Contract

    today = timezone.now().date()
    three_months = today + timedelta(days=90)
    one_month = today + timedelta(days=30)

    # 3개월 전 알림
    expiring_3m = Contract.objects.filter(
        end_date=three_months,
        status='active'
    )
    for contract in expiring_3m:
        for user_id in [contract.tenant_id, contract.landlord_id]:
            send_notification.delay(
                user_id=user_id,
                channel='kakao',
                title='계약 만기 안내 (3개월 전)',
                content=f'{contract.property.name} 계약이 {contract.end_date}에 만료됩니다.',
                contract_id=contract.id,
            )
        contract.status = 'expiring'
        contract.save()

    # 1개월 전 알림
    expiring_1m = Contract.objects.filter(
        end_date=one_month,
        status='expiring'
    )
    for contract in expiring_1m:
        for user_id in [contract.tenant_id, contract.landlord_id]:
            send_notification.delay(
                user_id=user_id,
                channel='kakao',
                title='계약 만기 안내 (1개월 전)',
                content=f'{contract.property.name} 계약 만료 1개월 전입니다. 갱신 여부를 결정해주세요.',
                contract_id=contract.id,
            )


@shared_task
def check_insurance_expiry():
    """매일 실행: 보증보험 만기 확인"""
    from insurance.models import InsuranceApplication

    today = timezone.now().date()
    two_months = today + timedelta(days=60)

    expiring = InsuranceApplication.objects.filter(
        end_date=two_months,
        status='active'
    )
    for app in expiring:
        contract = app.contract
        send_notification.delay(
            user_id=contract.tenant_id,
            channel='kakao',
            title='보증보험 만기 안내',
            content=f'보증보험이 {app.end_date}에 만료됩니다. 갱신이 필요합니다.',
            contract_id=contract.id,
        )
        app.status = 'expiring'
        app.save()


@shared_task
def generate_rent_schedules(contract_id, payment_type='prepaid'):
    """계약 서명 완료 후 월세 스케줄 자동 생성"""
    from contracts.models import Contract
    from schedules.models import RentSchedule
    from dateutil.relativedelta import relativedelta

    contract = Contract.objects.get(id=contract_id)
    if contract.monthly_rent == 0:
        return  # 전세는 스케줄 불필요

    current = contract.start_date
    while current < contract.end_date:
        if payment_type == 'prepaid':
            due_date = current.replace(day=1)
        else:
            import calendar
            last_day = calendar.monthrange(current.year, current.month)[1]
            due_date = current.replace(day=last_day)

        RentSchedule.objects.create(
            contract=contract,
            payment_type=payment_type,
            due_date=due_date,
            amount=contract.monthly_rent,
        )
        current += relativedelta(months=1)


@shared_task
def create_post_management_events(contract_id):
    """계약 서명 완료 후 사후관리 이벤트 자동 생성"""
    from contracts.models import Contract
    from schedules.models import ContractEvent

    contract = Contract.objects.get(id=contract_id)

    events = [
        {
            'event_type': 'expiry_alert',
            'title': '계약 만기 안내 (3개월 전)',
            'scheduled_date': contract.end_date - timedelta(days=90),
        },
        {
            'event_type': 'expiry_alert',
            'title': '계약 만기 안내 (1개월 전)',
            'scheduled_date': contract.end_date - timedelta(days=30),
        },
        {
            'event_type': 'deposit_return',
            'title': '보증금 반환 프로세스 시작',
            'scheduled_date': contract.end_date - timedelta(days=30),
        },
    ]

    for event_data in events:
        ContractEvent.objects.create(contract=contract, **event_data)
