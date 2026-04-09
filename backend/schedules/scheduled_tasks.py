"""
자동 알림 스케줄러 - Celery Beat
매일 오전 9시에 실행되어 알림을 자동 발송합니다.
"""
from celery import shared_task
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def daily_rent_check():
    """
    매일 실행: 월세 납부 관련 알림
    - D-3: PAYMENT_D3
    - D-Day: PAYMENT_DDAY
    """
    from schedules.models import RentSchedule
    from schedules.notification_service import send_notification_to_user

    today = date.today()
    d3_later = today + timedelta(days=3)

    # ① D-3 알림
    upcoming = RentSchedule.objects.filter(
        due_date=d3_later,
        status='pending',
        reminder_3days_sent=False,
    ).select_related('contract', 'contract__tenant')

    for s in upcoming:
        c = s.contract
        u = c.tenant
        send_notification_to_user(
            user=u, template_id="PAYMENT_D3",
            variables={
                "tenant_name": u.first_name,
                "address": c.address[:20],
                "payment_type": "월세",
                "due_date": str(s.due_date),
                "amount": f"{s.amount:,}",
                "bank": c.landlord_bank or "-",
                "account": c.landlord_account or "-",
                "landlord_name": c.landlord_name or "-"
            }
        )
        s.reminder_3days_sent = True
        s.status = 'upcoming'
        s.save()

    # ② D-Day 알림
    due_today = RentSchedule.objects.filter(
        due_date=today,
        status__in=['pending', 'upcoming'],
        reminder_dueday_sent=False,
    ).select_related('contract', 'contract__tenant')

    for s in due_today:
        c = s.contract
        u = c.tenant
        send_notification_to_user(
            user=u, template_id="PAYMENT_DDAY",
            variables={
                "tenant_name": u.first_name,
                "address": c.address[:20],
                "payment_type": "월세",
                "amount": f"{s.amount:,}",
                "bank": c.landlord_bank or "-",
                "account": c.landlord_account or "-",
                "landlord_name": c.landlord_name or "-"
            }
        )
        s.reminder_dueday_sent = True
        s.save()

    return {"d3": upcoming.count(), "dday": due_today.count()}


@shared_task
def daily_contract_expiry_check():
    """
    매일 실행: 계약 만료 알림 (3개월 전, 1개월 전)
    """
    from contracts.models import Contract
    from schedules.models import ContractEvent
    from schedules.notification_service import send_notification_to_user

    today = date.today()
    events = ContractEvent.objects.filter(
        scheduled_date=today, status='scheduled', notification_sent=False
    ).select_related('contract', 'contract__tenant')

    for event in events:
        c = event.contract
        u = c.tenant
        days_left = (c.end_date - today).days
        # 3개월(약 90일) vs 1개월(약 30일) 구분
        template = "CONTRACT_EXPIRY_3M" if days_left > 45 else "CONTRACT_EXPIRY_1M"
        
        send_notification_to_user(
            user=u, template_id=template,
            variables={
                "tenant_name": u.first_name,
                "address": c.address[:20],
                "contract_type": c.contract_type,
                "start_date": str(c.start_date),
                "end_date": str(c.end_date),
                "deposit": f"{c.deposit:,}"
            }
        )
        event.notification_sent = True
        event.status = 'completed'
        event.save()

    return {"events": events.count()}
