"""
계약서 업로드 및 관리 API
"""
import json`nimport logging
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.conf import settings
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


# ===== Contract Registration Serializer =====
class ContractRegistrationSerializer(serializers.Serializer):
    # 계약 정보
    contract_type = serializers.ChoiceField(choices=["전세", "월세"])
    deposit = serializers.IntegerField(help_text="보증금 (원)")
    monthly_rent = serializers.IntegerField(default=0, help_text="월세 (원)")
    rent_day = serializers.IntegerField(default=25, help_text="월세 납부일")
    start_date = serializers.DateField(help_text="계약 시작일")
    end_date = serializers.DateField(help_text="계약 종료일")
    address = serializers.CharField(help_text="물건지 주소")

    # 임대인 정보
    landlord_name = serializers.CharField(help_text="임대인 이름")
    landlord_phone = serializers.CharField(help_text="임대인 연락처")
    landlord_bank = serializers.CharField(required=False, default="", help_text="입금 은행")
    landlord_account = serializers.CharField(required=False, default="", help_text="입금 계좌")

    # 계약서 파일
    contract_file = serializers.FileField(required=False)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def register_contract(request):
    """
    계약 등록 API
    - 계약 정보 저장
    - 월세 스케줄 자동 생성
    - 알림 스케줄 자동 생성
    - 등록 완료 알림 발송
    """
    data = request.data.copy()

    # Parse JSON fields if sent as form data
    for field in ['deposit', 'monthly_rent', 'rent_day']:
        if field in data and isinstance(data[field], str):
            data[field] = int(data[field])

    serializer = ContractRegistrationSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    d = serializer.validated_data

    # 1. 계약 저장
    from contracts.models import Contract, ContractAgreement
    from accounts.models import User
    from django.contrib.auth.hashers import make_password

    # 사용자 처리 (익명 등록 지원)
    current_user = request.user
    token_data = None

    if not current_user.is_authenticated:
        tenant_name = d.get('landlord_name') # This was the landlord, we need tenant data
        # Actually, in anonymous mode, we expect tenant_name, tenant_phone, pin in the body
        tenant_name = request.data.get('tenant_name')
        tenant_phone = request.data.get('tenant_phone')
        pin = request.data.get('pin')

        if not tenant_name or not tenant_phone or not pin:
            return Response({'error': '성함, 연락처, 그리고 6자리 비밀번호가 필요합니다.'}, status=400)

        # 사용자 생성 또는 가져오기
        username = tenant_phone.replace("-", "")
        current_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': tenant_name,
                'phone': tenant_phone,
                'role': 'tenant'
            }
        )
        # PIN(비밀번호) 설정
        current_user.set_password(pin)
        current_user.save()
        
        # 가입 완료 후 토큰 발급
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(current_user)
        token_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'first_name': current_user.first_name,
            }
        }

    # 임대인 정보 저장 (간이)
    contract_data = {
        'tenant': current_user,
        'deposit': d['deposit'],
        'monthly_rent': d['monthly_rent'],
        'start_date': d['start_date'],
        'end_date': d['end_date'],
        'move_in_date': d['start_date'],
        'status': 'active',
        'special_terms': json.dumps({
            'contract_type': d['contract_type'],
            'rent_day': d['rent_day'],
            'address': d['address'],
            'landlord_name': d['landlord_name'],
            'landlord_phone': d['landlord_phone'],
            'landlord_bank': d.get('landlord_bank', ''),
            'landlord_account': d.get('landlord_account', ''),
        }, ensure_ascii=False),
    }

    # 계약서 파일 저장
    if 'contract_file' in request.FILES:
        contract_data['contract_document'] = request.FILES['contract_file']

    # Get or create a dummy landlord and property for FK requirements
    from properties.models import Property
    landlord, _ = User.objects.get_or_create(
        username=f"landlord_{d['landlord_phone'].replace('-','')[-4:]}",
        defaults={
            'first_name': d['landlord_name'][1:] if len(d['landlord_name']) > 1 else d['landlord_name'],
            'last_name': d['landlord_name'][0] if d['landlord_name'] else '임',
            'role': 'landlord',
            'phone': d['landlord_phone'],
        }
    )

    prop, _ = Property.objects.get_or_create(
        address=d['address'],
        landlord=landlord,
        defaults={
            'name': d['address'][:50],
            'property_type': 'apartment',
            'size_sqm': 0,
            'floor': '-',
            'built_year': 2020,
            'latitude': 37.5,
            'longitude': 127.0,
            'deposit': d['deposit'],
            'monthly_rent': d['monthly_rent'],
            'is_insurable': True,
            'risk_grade': 'B',
            'risk_score': 70,
        }
    )

    # Create agreement stub
    agreement = ContractAgreement.objects.create(
        related_property=prop,
        tenant=current_user,
        landlord=landlord,
        agreed_deposit=d['deposit'],
        agreed_rent=d['monthly_rent'],
        agreed_start_date=d['start_date'],
        agreed_end_date=d['end_date'],
        agreed_move_in_date=d['start_date'],
        deposit_agreed=True,
        period_agreed=True,
        landlord_agreed=True,
        tenant_agreed=True,
        status='both_agreed',
    )

    contract = Contract.objects.create(
        agreement=agreement,
        related_property=prop,
        landlord=landlord,
        **contract_data,
    )

    # 2. 월세 스케줄 생성
    schedules_created = 0
    if d['monthly_rent'] > 0:
        schedules_created = _create_rent_schedules(
            contract, d['start_date'], d['end_date'],
            d['monthly_rent'], d['rent_day']
        )

    # 3. 사후관리 이벤트 생성
    events_created = _create_management_events(contract)

    # 4. 등록 완료 알림 발송
    _send_registration_notification(current_user, contract, d)

    return Response({
        'success': True,
        'contract_id': contract.id,
        'message': '계약이 등록되었습니다',
        'schedules_created': schedules_created,
        'events_created': events_created,
        'contract_info': {
            'type': d['contract_type'],
            'deposit': d['deposit'],
            'monthly_rent': d['monthly_rent'],
            'start_date': str(d['start_date']),
            'end_date': str(d['end_date']),
            'address': d['address'],
            'landlord_name': d['landlord_name'],
        },
        'token': token_data
    }, status=status.HTTP_201_CREATED)


def _create_rent_schedules(contract, start_date, end_date, monthly_rent, rent_day):
    """월세 납부 스케줄 자동 생성"""
    from schedules.models import RentSchedule
    import calendar

    count = 0
    current = start_date
    while current <= end_date:
        # 해당 월의 납부일 계산
        last_day = calendar.monthrange(current.year, current.month)[1]
        actual_day = min(rent_day, last_day)
        due_date = current.replace(day=actual_day)

        # 시작일 이전이면 건너뛰기
        if due_date >= start_date:
            RentSchedule.objects.create(
                contract=contract,
                payment_type='prepaid',
                due_date=due_date,
                amount=monthly_rent,
                status='paid' if due_date < date.today() else 'pending',
            )
            count += 1

        # 다음 달로
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)

    return count


def _create_management_events(contract):
    """사후관리 이벤트 자동 생성"""
    from schedules.models import ContractEvent

    events = []

    # 만기 3개월 전
    d_3m = contract.end_date - timedelta(days=90)
    if d_3m > date.today():
        events.append(ContractEvent(
            contract=contract,
            event_type='expiry_alert',
            title='계약 만료 3개월 전 안내',
            description='계약 갱신 여부를 결정해주세요.',
            scheduled_date=d_3m,
        ))

    # 만기 1개월 전
    d_1m = contract.end_date - timedelta(days=30)
    if d_1m > date.today():
        events.append(ContractEvent(
            contract=contract,
            event_type='expiry_alert',
            title='계약 만료 1개월 전 안내',
            description='계약이 곧 만료됩니다.',
            scheduled_date=d_1m,
        ))

    ContractEvent.objects.bulk_create(events)
    return len(events)


def _send_registration_notification(user, contract, data):
    """계약 등록 완료 알림 발송"""
    try:
        from schedules.notification_service import send_notification_to_user
        # 비동기 처리가 권장되지만, 현재는 동기 발송 후 예외 처리 강화
        send_notification_to_user(
            user=user,
            template_id="JEONSE_REGISTERED",
            variables={
                "tenant_name": user.first_name,
                "address": data['address'][:20],
                "contract_type": data['contract_type'],
                "start_date": str(data['start_date']),
                "end_date": str(data['end_date']),
                "deposit": f"{data['deposit']:,}",
            }
        )
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logging.getLogger(__name__).error(f"Registration notification failed:\n{error_msg}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_contracts(request):
    """내 계약 목록 조회"""
    from contracts.models import Contract
    from django.db.models import Q

    contracts = Contract.objects.filter(
        Q(tenant=request.user) | Q(landlord=request.user)
    ).order_by('-created_at')

    result = []
    for c in contracts:
        info = json.loads(c.special_terms) if c.special_terms else {}
        result.append({
            'id': c.id,
            'contract_type': info.get('contract_type', ''),
            'deposit': c.deposit,
            'monthly_rent': c.monthly_rent,
            'start_date': str(c.start_date),
            'end_date': str(c.end_date),
            'address': info.get('address', ''),
            'landlord_name': info.get('landlord_name', ''),
            'landlord_phone': info.get('landlord_phone', ''),
            'landlord_bank': info.get('landlord_bank', ''),
            'landlord_account': info.get('landlord_account', ''),
            'rent_day': info.get('rent_day', 25),
            'status': c.status,
            'days_until_expiry': c.days_until_expiry,
            'created_at': str(c.created_at),
        })
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contract_schedules(request, contract_id):
    """계약의 월세 납부 스케줄 조회"""
    from schedules.models import RentSchedule
    schedules = RentSchedule.objects.filter(
        contract_id=contract_id,
        contract__tenant=request.user
    ).order_by('due_date')

    result = [{
        'id': s.id,
        'due_date': str(s.due_date),
        'amount': s.amount,
        'status': s.status,
        'paid_date': str(s.paid_date) if s.paid_date else None,
    } for s in schedules]
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_rent_paid(request, schedule_id):
    """월세 납부 완료 처리"""
    from schedules.models import RentSchedule
    try:
        schedule = RentSchedule.objects.get(
            id=schedule_id,
            contract__tenant=request.user
        )
        schedule.status = 'paid'
        schedule.paid_date = date.today()
        schedule.paid_amount = schedule.amount
        schedule.save()
        return Response({'success': True, 'status': 'paid'})
    except RentSchedule.DoesNotExist:
        return Response({'error': 'Schedule not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contract_notifications(request, contract_id):
    """계약 관련 알림 내역 조회"""
    from schedules.models import Notification
    notifications = Notification.objects.filter(
        user=request.user,
        related_contract_id=contract_id,
    ).order_by('-created_at')[:20]

    result = [{
        'id': n.id,
        'channel': n.channel,
        'status': n.status,
        'title': n.title,
        'content': n.content,
        'sent_at': str(n.sent_at) if n.sent_at else None,
    } for n in notifications]
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_notification(request):
    """테스트 알림 발송 (진단 정보 포함)"""
    try:
        from schedules.notification_service import send_notification_to_user
        template = request.data.get('template', 'PAYMENT_REMINDER_D3')
        variables = request.data.get('variables', {
            'tenant_name': request.user.first_name or request.user.username,
            'payment_type': '월세',
            'address': '서울시 강남구 삼성동 123',
            'due_date': str(date.today()),
            'amount': '800,000',
            'bank': '국민은행',
            'account': '123-456-789',
            'landlord_name': '이임대',
        })

        result_obj, raw_res = send_notification_to_user(
            user=request.user,
            template_id=template,
            variables=variables,
        )

        if result_obj:
            return Response({
                'success': True,
                'notification_id': result_obj.id,
                'channel': result_obj.channel,
                'status': result_obj.status,
                'raw_result': raw_res
            })
        return Response({'success': False, 'error': 'No notification result returned', 'raw_result': raw_res}, status=400)
    except Exception as e:
        import traceback
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        print(f"Notification Test Error: {error_msg}")
        return Response({
            'success': False, 
            'error': f'알림 발송 실패: {error_msg}',
            'detail': stack_trace if settings.DEBUG else None
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def update_profile(request):
    """사용자 프로필(연락처) 업데이트 (진단 정보 포함)"""
    phone = request.data.get('phone')
    if not phone:
        return Response({'success': False, 'error': 'Phone number is required'}, status=400)
    
    try:
        user = request.user
        user.phone = phone
        user.save()
        
        return Response({
            'success': True,
            'message': '프로필이 업데이트되었습니다',
            'phone': user.phone
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        print(f"Profile Update Error: {error_msg}")
        return Response({
            'success': False, 
            'error': f'서버 내부 오류: {error_msg}',
            'detail': stack_trace if settings.DEBUG else None
        }, status=500)
