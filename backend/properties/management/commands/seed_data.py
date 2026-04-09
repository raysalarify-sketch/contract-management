"""
?œë“œ ?°ì´???ì„± ì»¤ë§¨??python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from accounts.models import User, Company, LandlordProfile, AgentProfile
from properties.models import Property, PropertyTag


SEED_PROPERTIES = [
    {"name":"?˜ë????¼ìŠ¤?°ì? 102??1203??,"addr":"?œìš¸ ?œì´ˆêµ?ë°˜í¬??19-1","type":"apartment","deposit":1_200_000_000,"rent":0,"grade":"A+","score":97,"lat":37.5085,"lng":127.0005,"size":84,"floor":"12/28ì¸?,"year":2009,"insurable":True,"tags":["HUGê°€??,"SGIê°€??,"?„ì„¸?€ì¶œê???]},
    {"name":"?€?ŒíŒ°ë¦¬ìŠ¤ 3ì°?2506??,"addr":"?œìš¸ ê°•ë‚¨êµ??„ê³¡??467","type":"mixed_use","deposit":1_500_000_000,"rent":0,"grade":"A+","score":99,"lat":37.4895,"lng":127.0455,"size":165,"floor":"25/69ì¸?,"year":2004,"insurable":True,"tags":["HUGê°€??,"SGIê°€??,"?„ì„¸?€ì¶œê???]},
    {"name":"??‚¼ ?„ì´?Œí¬ 805??,"addr":"?œìš¸ ê°•ë‚¨êµ???‚¼??702-10","type":"apartment","deposit":650_000_000,"rent":0,"grade":"A","score":91,"lat":37.5005,"lng":127.0365,"size":112,"floor":"8/25ì¸?,"year":2017,"insurable":True,"tags":["HUGê°€??,"SGIê°€??,"?„ì„¸?€ì¶œê???]},
    {"name":"? ì‹¤ ?˜ìŠ¤ 106??503??,"addr":"?œìš¸ ?¡íŒŒêµ?? ì‹¤??40","type":"apartment","deposit":900_000_000,"rent":0,"grade":"A+","score":98,"lat":37.5115,"lng":127.0815,"size":119,"floor":"5/35ì¸?,"year":2008,"insurable":True,"tags":["HUGê°€??,"SGIê°€??,"?„ì„¸?€ì¶œê???]},
    {"name":"?¼í˜„??ë¹Œë¼ 301??,"addr":"?œìš¸ ê°•ë‚¨êµ??¼í˜„??245-3","type":"villa","deposit":350_000_000,"rent":500_000,"grade":"B+","score":76,"lat":37.5175,"lng":127.0285,"size":59,"floor":"3/4ì¸?,"year":2015,"insurable":True,"tags":["SGIê°€??,"ê³µì¦ê¶Œì¥"]},
    {"name":"?€ì¹˜ë™ ?¤ì„¸?€ 201??,"addr":"?œìš¸ ê°•ë‚¨êµ??€ì¹˜ë™ 906-5","type":"multi_family","deposit":280_000_000,"rent":400_000,"grade":"B","score":71,"lat":37.4975,"lng":127.0625,"size":46,"floor":"2/4ì¸?,"year":2008,"insurable":True,"tags":["SGIê°€??,"?„ì„¸ê°€?¨ì£¼??]},
    {"name":"ë°©ë°°??ë¹Œë¼ 102??,"addr":"?œìš¸ ?œì´ˆêµ?ë°©ë°°??794-2","type":"villa","deposit":180_000_000,"rent":600_000,"grade":"D","score":35,"lat":37.4815,"lng":126.9925,"size":33,"floor":"1/3ì¸?,"year":2001,"insurable":False,"tags":["ë³´ì¦ë³´í—˜ë¶ˆê?","ê¹¡í†µ?„í—˜"]},
    {"name":"ì²?‹´ ?ì´ 1802??,"addr":"?œìš¸ ê°•ë‚¨êµ?ì²?‹´??134-10","type":"apartment","deposit":1_000_000_000,"rent":0,"grade":"A","score":90,"lat":37.5205,"lng":127.0505,"size":99,"floor":"18/24ì¸?,"year":2016,"insurable":True,"tags":["HUGê°€??,"SGIê°€??]},
]

LANDLORD_NAMES = ["ê¹€?ìˆ˜","ë°•ì¬??,"?´ì •ë¯?,"?•ìˆ˜??,"?œë???,"?¡ë???,"?„ì¬??,"?¤í˜„??]


class Command(BaseCommand):
    help = '?Œí¬???œë“œ ?°ì´???ì„±'

    def handle(self, *args, **options):
        self.stdout.write("?œë“œ ?°ì´???ì„± ?œì‘...")

        # ?Œì‚¬
        company, _ = Company.objects.get_or_create(
            business_number='123-45-67890',
            defaults={
                'name': '?ŒìŠ¤??ì£¼ì‹?Œì‚¬',
                'representative': '?€?œì´??,
                'address': '?œìš¸??ê°•ë‚¨êµ??ŒìŠ¤?¸ë¡œ 1',
                'loan_budget': 10_000_000_000,
                'loan_used': 9_700_000_000,
            }
        )

        # ê´€ë¦¬ì
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@workd.kr', 'admin1234', role='admin')

        # ?„ì°¨??(ì§ì›)
        tenant, _ = User.objects.get_or_create(
            username='tenant01',
            defaults={
                'email': 'tenant@workd.kr',
                'first_name': 'ì§ì›',
                'last_name': 'ê¹€',
                'role': 'tenant',
                'phone': '010-1234-5678',
                'is_verified': True,
                'company': company,
            }
        )
        if not tenant.has_usable_password():
            tenant.set_password('test1234')
            tenant.save()

        # ì¤‘ê°œ??        agent, _ = User.objects.get_or_create(
            username='agent01',
            defaults={
                'email': 'agent@workd.kr',
                'first_name': 'ì¤‘ê°œ',
                'last_name': 'ë°?,
                'role': 'agent',
                'phone': '010-9999-0000',
                'is_verified': True,
            }
        )
        if not agent.has_usable_password():
            agent.set_password('test1234')
            agent.save()
        AgentProfile.objects.get_or_create(
            user=agent,
            defaults={
                'license_number': '11680-2024-00123',
                'office_name': '??‚¼ ë¶€?™ì‚°ì¤‘ê°œë²•ì¸',
                'office_address': '?œìš¸??ê°•ë‚¨êµ???‚¼ë¡?45, 1ì¸?,
                'office_phone': '02-555-1234',
            }
        )

        # ?„ë???+ ë§¤ë¬¼
        for i, prop_data in enumerate(SEED_PROPERTIES):
            landlord_name = LANDLORD_NAMES[i] if i < len(LANDLORD_NAMES) else f"?„ë???i}"
            username = f'landlord{i+1:02d}'

            landlord, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@test.com',
                    'first_name': landlord_name[1:],
                    'last_name': landlord_name[0],
                    'role': 'landlord',
                    'phone': f'010-****-{1000+i}',
                    'is_verified': prop_data['score'] > 70,
                }
            )
            if not landlord.has_usable_password():
                landlord.set_password('test1234')
                landlord.save()

            LandlordProfile.objects.get_or_create(
                user=landlord,
                defaults={
                    'response_rate': min(95, 60 + prop_data['score'] * 0.3),
                    'avg_response_minutes': max(30, 300 - prop_data['score'] * 2),
                }
            )

            prop, created = Property.objects.get_or_create(
                name=prop_data['name'],
                defaults={
                    'address': prop_data['addr'],
                    'property_type': prop_data['type'],
                    'size_sqm': prop_data['size'],
                    'floor': prop_data['floor'],
                    'built_year': prop_data['year'],
                    'latitude': prop_data['lat'],
                    'longitude': prop_data['lng'],
                    'deposit': prop_data['deposit'],
                    'monthly_rent': prop_data['rent'],
                    'risk_grade': prop_data['grade'],
                    'risk_score': prop_data['score'],
                    'is_insurable': prop_data['insurable'],
                    'landlord': landlord,
                }
            )

            if created:
                tag_type_map = {
                    'HUGê°€??: 'positive', 'SGIê°€??: 'positive', '?„ì„¸?€ì¶œê???: 'positive',
                    'ê³µì¦ê¶Œì¥': 'warning', '?„ì„¸ê°€?¨ì£¼??: 'warning', 'ê·¼ì??¹í™•?¸í•„??: 'warning',
                    'ë³´ì¦ë³´í—˜ë¶ˆê?': 'danger', 'ê¹¡í†µ?„í—˜': 'danger',
                }
                for tag_label in prop_data.get('tags', []):
                    PropertyTag.objects.create(
                        related_property=prop,
                        label=tag_label,
                        tag_type=tag_type_map.get(tag_label, 'positive')
                    )

        self.stdout.write(self.style.SUCCESS(
            f"?„ë£Œ! ë§¤ë¬¼ {len(SEED_PROPERTIES)}ê±? ?„ë???{len(LANDLORD_NAMES)}ëª??ì„±"
        ))
