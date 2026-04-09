"""Properties API - Serializers & Views"""
from rest_framework import serializers, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, PropertyImage, RiskScan, PropertyTag


# ===== Serializers =====

class PropertyTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyTag
        fields = ['label', 'tag_type']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_primary', 'caption']


class PropertyListSerializer(serializers.ModelSerializer):
    tags = PropertyTagSerializer(many=True, read_only=True)
    landlord_name = serializers.CharField(source='landlord.get_full_name', read_only=True)
    landlord_verified = serializers.BooleanField(source='landlord.is_verified', read_only=True)
    deposit_display = serializers.ReadOnlyField()
    rent_type = serializers.ReadOnlyField()

    class Meta:
        model = Property
        fields = [
            'id', 'name', 'address', 'property_type', 'size_sqm', 'floor',
            'built_year', 'latitude', 'longitude', 'deposit', 'deposit_display',
            'monthly_rent', 'rent_type', 'risk_grade', 'risk_score',
            'is_insurable', 'is_available', 'tags',
            'landlord_name', 'landlord_verified', 'created_at',
        ]


class PropertyDetailSerializer(PropertyListSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    landlord_response_rate = serializers.SerializerMethodField()
    landlord_response_time = serializers.SerializerMethodField()

    class Meta(PropertyListSerializer.Meta):
        fields = PropertyListSerializer.Meta.fields + [
            'address_detail', 'images',
            'landlord_response_rate', 'landlord_response_time',
        ]

    def get_landlord_response_rate(self, obj):
        profile = getattr(obj.landlord, 'landlord_profile', None)
        return profile.response_rate if profile else 0

    def get_landlord_response_time(self, obj):
        profile = getattr(obj.landlord, 'landlord_profile', None)
        if not profile:
            return "정보 없음"
        mins = profile.avg_response_minutes
        if mins < 60:
            return f"평균 {mins}분"
        return f"평균 {mins // 60}시간"


class RiskScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskScan
        fields = '__all__'
        read_only_fields = ['scanned_by', 'scanned_at']


class RiskScanResultSerializer(serializers.Serializer):
    """리스크 스캔 결과 요약"""
    overall_grade = serializers.CharField()
    overall_score = serializers.IntegerField()
    items = serializers.ListField()
    insurance_available = serializers.DictField()


# ===== Views =====

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(is_active=True).select_related('landlord')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'risk_grade', 'is_insurable', 'is_available']
    search_fields = ['name', 'address']
    ordering_fields = ['deposit', 'risk_score', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        return PropertyDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'insurable_map']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(landlord=self.request.user)

    @action(detail=False, methods=['get'], url_path='insurable-map')
    def insurable_map(self, request):
        """보증보험 가능 매물 지도 데이터"""
        properties = self.queryset.filter(is_insurable=True, is_available=True)
        property_type = request.query_params.get('type')
        if property_type:
            properties = properties.filter(property_type=property_type)

        serializer = PropertyListSerializer(properties, many=True)
        stats = {
            'total': self.queryset.filter(is_available=True).count(),
            'insurable': properties.count(),
            'grade_a': properties.filter(risk_grade__in=['A+', 'A']).count(),
        }
        return Response({'properties': serializer.data, 'stats': stats})

    @action(detail=True, methods=['post'], url_path='scan')
    def risk_scan(self, request, pk=None):
        """물건지 리스크 스캔 실행"""
        property_obj = self.get_object()

        # 실제로는 등기부등본 API, 임대인 조회 API 등과 연동
        # 여기서는 스캔 결과를 생성하는 로직
        scan = RiskScan.objects.create(
            property=property_obj,
            scanned_by=request.user,
            overall_grade=property_obj.risk_grade,
            overall_score=property_obj.risk_score,
            hug_available=property_obj.is_insurable,
            sgi_available=property_obj.is_insurable,
        )

        result = {
            'overall_grade': scan.overall_grade,
            'overall_score': scan.overall_score,
            'items': [
                {'label': '근저당권 설정', 'status': scan.mortgage_status, 'detail': scan.mortgage_detail or '근저당 없음'},
                {'label': '소유권 이전등기', 'status': scan.ownership_status, 'detail': scan.ownership_detail or '정상'},
                {'label': '압류/가압류', 'status': scan.seizure_status, 'detail': scan.seizure_detail or '해당사항 없음'},
                {'label': '전세가율', 'status': scan.jeonse_status, 'detail': f'시세 대비 {scan.jeonse_ratio}%'},
                {'label': '임대인 다주택', 'status': scan.landlord_status, 'detail': f'보유주택 {scan.landlord_multi_house}채'},
                {'label': '체납 이력', 'status': scan.tax_delinquency_status, 'detail': scan.tax_delinquency_detail or '없음'},
                {'label': '보증보험 가입', 'status': 'safe' if scan.hug_available else 'danger',
                 'detail': 'HUG/SGI 가입 가능' if scan.hug_available else '가입 불가'},
            ],
            'insurance_available': {
                'hug': scan.hug_available,
                'sgi': scan.sgi_available,
                'loan': scan.loan_available,
            }
        }
        return Response(result)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """매물 관련 임대인 리뷰 조회"""
        property_obj = self.get_object()
        from reviews.models import Review
        reviews = Review.objects.filter(
            reviewee=property_obj.landlord, is_visible=True
        ).order_by('-created_at')[:10]

        data = [{
            'author': r.reviewer.get_full_name(),
            'rating': r.rating,
            'content': r.content,
            'date': r.created_at.strftime('%Y.%m'),
        } for r in reviews]
        return Response(data)
