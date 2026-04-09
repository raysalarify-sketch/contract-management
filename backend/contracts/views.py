"""Contracts API - Serializers & Views"""
from django.utils import timezone
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import (
    Inquiry, InquiryMessage, ContractAgreement,
    Contract, ESignature, AgentVerification
)


# ===== Serializers =====

class InquiryMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)

    class Meta:
        model = InquiryMessage
        fields = ['id', 'sender_type', 'sender_name', 'content', 'is_read', 'created_at']
        read_only_fields = ['sender_type', 'sender_name', 'created_at']


class InquirySerializer(serializers.ModelSerializer):
    messages = InquiryMessageSerializer(many=True, read_only=True)
    landlord_name = serializers.CharField(source='landlord.get_full_name', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)

    class Meta:
        model = Inquiry
        fields = [
            'id', 'property', 'tenant', 'landlord', 'status',
            'viewing_date', 'messages', 'landlord_name', 'property_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['tenant', 'landlord', 'status']


class ContractAgreementSerializer(serializers.ModelSerializer):
    landlord_name = serializers.CharField(source='landlord.get_full_name', read_only=True)

    class Meta:
        model = ContractAgreement
        fields = '__all__'
        read_only_fields = ['tenant', 'landlord', 'status']


class ContractSerializer(serializers.ModelSerializer):
    days_until_expiry = serializers.ReadOnlyField()
    signatures_count = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'updated_at']

    def get_signatures_count(self, obj):
        return obj.signatures.count()


class ESignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESignature
        fields = ['id', 'signer_role', 'signed_at']
        read_only_fields = ['signed_at']


# ===== Views =====

class InquiryViewSet(viewsets.ModelViewSet):
    serializer_class = InquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Inquiry.objects.filter(
            models.Q(tenant=user) | models.Q(landlord=user)
        ).select_related('property', 'tenant', 'landlord')

    def perform_create(self, serializer):
        property_obj = serializer.validated_data['property']
        inquiry = serializer.save(
            tenant=self.request.user,
            landlord=property_obj.landlord
        )
        # 시스템 메시지 추가
        InquiryMessage.objects.create(
            inquiry=inquiry,
            sender_type='system',
            content=f'{property_obj.landlord.get_full_name()}님에게 문의를 보내보세요'
        )

    @action(detail=True, methods=['post'], url_path='send-message')
    def send_message(self, request, pk=None):
        inquiry = self.get_object()
        content = request.data.get('content', '')
        if not content:
            return Response({'error': '메시지를 입력하세요'}, status=400)

        sender_type = 'tenant' if request.user == inquiry.tenant else 'landlord'
        msg = InquiryMessage.objects.create(
            inquiry=inquiry,
            sender_type=sender_type,
            sender=request.user,
            content=content
        )
        inquiry.save()  # updated_at 갱신

        # TODO: 상대방에게 알림톡 발송
        return Response(InquiryMessageSerializer(msg).data, status=201)

    @action(detail=True, methods=['post'], url_path='schedule-viewing')
    def schedule_viewing(self, request, pk=None):
        inquiry = self.get_object()
        viewing_date = request.data.get('viewing_date')
        if not viewing_date:
            return Response({'error': '방문 일정을 선택하세요'}, status=400)

        inquiry.viewing_date = viewing_date
        inquiry.status = Inquiry.Status.VIEWING_SCHEDULED
        inquiry.save()

        InquiryMessage.objects.create(
            inquiry=inquiry,
            sender_type='system',
            content=f'📅 방문 일정이 확정되었습니다: {viewing_date}'
        )
        return Response({'status': 'scheduled', 'viewing_date': viewing_date})


from django.db import models as db_models


class ContractAgreementViewSet(viewsets.ModelViewSet):
    serializer_class = ContractAgreementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ContractAgreement.objects.filter(
            db_models.Q(tenant=user) | db_models.Q(landlord=user)
        )

    def perform_create(self, serializer):
        property_obj = serializer.validated_data['property']
        serializer.save(
            tenant=self.request.user,
            landlord=property_obj.landlord,
            status=ContractAgreement.Status.PENDING
        )

    @action(detail=True, methods=['post'])
    def agree(self, request, pk=None):
        """임대인/임차인 동의"""
        agreement = self.get_object()
        user = request.user

        if user == agreement.landlord:
            agreement.landlord_agreed = True
            agreement.landlord_agreed_at = timezone.now()
        elif user == agreement.tenant:
            agreement.tenant_agreed = True
            agreement.tenant_agreed_at = timezone.now()

        if agreement.landlord_agreed and agreement.tenant_agreed:
            agreement.status = ContractAgreement.Status.BOTH_AGREED

        agreement.save()
        return Response(ContractAgreementSerializer(agreement).data)


class ContractViewSet(viewsets.ModelViewSet):
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Contract.objects.filter(
            db_models.Q(tenant=user) | db_models.Q(landlord=user) | db_models.Q(agent=user)
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """임대인/임차인 확인"""
        contract = self.get_object()
        user = request.user

        if user == contract.landlord:
            contract.landlord_confirmed = True
            contract.landlord_confirmed_at = timezone.now()
        elif user == contract.tenant:
            contract.tenant_confirmed = True
            contract.tenant_confirmed_at = timezone.now()

        if contract.landlord_confirmed and contract.tenant_confirmed:
            contract.status = Contract.Status.BOTH_CONFIRMED

        contract.save()
        return Response(ContractSerializer(contract).data)

    @action(detail=True, methods=['post'], url_path='agent-verify')
    def agent_verify(self, request, pk=None):
        """공인중개사 확인"""
        contract = self.get_object()
        verification, _ = AgentVerification.objects.get_or_create(
            contract=contract, defaults={'agent': request.user}
        )

        for field in ['contract_validity', 'property_status', 'commission_calc', 'disclosure_form']:
            if field in request.data:
                setattr(verification, field, request.data[field])

        if verification.is_complete:
            verification.verified_at = timezone.now()
            contract.agent_verified = True
            contract.agent_verified_at = timezone.now()
            contract.status = Contract.Status.AGENT_VERIFIED
            contract.save()

        verification.save()
        return Response({'verified': verification.is_complete})

    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """전자서명"""
        contract = self.get_object()
        role = request.data.get('role')
        signature_data = request.data.get('signature_data', '')

        sig, created = ESignature.objects.get_or_create(
            contract=contract,
            signer_role=role,
            defaults={
                'signer': request.user,
                'signature_data': signature_data,
                'ip_address': request.META.get('REMOTE_ADDR', '0.0.0.0'),
            }
        )

        # 3자 서명 완료 확인
        total = contract.signatures.count()
        if total >= 3:
            contract.status = Contract.Status.SIGNED
            contract.save()

            # TODO: 계약서 1개 문서로 통합 후 업로드
            # TODO: 월세 스케줄 자동 생성
            # TODO: 사후관리 이벤트 생성

        return Response({
            'signed': True,
            'role': role,
            'total_signatures': total,
            'all_signed': total >= 3,
        })

    @action(detail=True, methods=['get'], url_path='post-management')
    def post_management(self, request, pk=None):
        """사후관리 대시보드 데이터"""
        contract = self.get_object()
        events = contract.events.all()
        schedules = contract.rent_schedules.all()[:6]

        return Response({
            'days_until_expiry': contract.days_until_expiry,
            'status': contract.status,
            'events': [{
                'type': e.event_type,
                'title': e.title,
                'status': e.status,
                'scheduled_date': e.scheduled_date,
            } for e in events],
            'upcoming_payments': [{
                'due_date': s.due_date,
                'amount': s.amount,
                'status': s.status,
            } for s in schedules],
        })
