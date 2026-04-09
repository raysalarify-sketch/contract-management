"""
NHN Cloud 알림 발송 서비스 v3
- 알림톡 + SMS 동시 발송
- 시점별 알림 템플릿 (카카오 변수 #{변수} 형식)
- 워크드 임직원 알림 발신프로필 사용
- 이미지: 00_로고형_알림서비스 (승인됨)
"""
import requests
import json
from django.utils import timezone
import logging
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)

# ============================================================
# 알림톡 템플릿 정의
# NHN Cloud 콘솔 → KakaoTalk Bizmessage → 템플릿 관리에서 등록
# 카카오 변수 형식: #{변수명}
# ============================================================

ALIMTALK_TEMPLATES = {

    # ─── 1. 계약 등록 완료 ───
    "JEONSE_REGISTERED": {
        "templateCode": "JEONSE_REGISTERED",
        "templateName": "임대차계약 등록 완료",
        "templateContent": (
            "#{tenant_name}님 안녕하세요.\n"
            "\n"
            "임대차계약이 등록되었습니다.\n"
            "-물건지: #{address}\n"
            "-계약유형: #{contract_type}\n"
            "-계약기간: #{start_date} ~ #{end_date}\n"
            "-보증금: #{deposit}원\n"
            "\n"
            "납부일 알림, 계약만료 안내를 자동으로 받으실 수 있습니다."
        ),
        "templateType": "BA",
    },

    # ─── 2. 계약 만료 3개월 전 ───
    "CONTRACT_EXPIRY_3M": {
        "templateCode": "CONTRACT_EXPIRY_3M",
        "templateName": "계약 만료 3개월 전 안내",
        "templateContent": (
            "#{tenant_name}님 안녕하세요.\n"
            "\n"
            "임대차계약 만료 3개월 전 안내입니다.\n"
            "-물건지: #{address}\n"
            "-계약유형: #{contract_type}\n"
            "-계약기간: #{start_date} ~ #{end_date}\n"
            "-보증금: #{deposit}원\n"
            "\n"
            "계약 갱신 또는 종료 여부를 결정해주세요.\n"
            "임대인과의 협의가 필요합니다."
        ),
        "templateType": "BA",
    },

    # ─── 3. 계약 만료 1개월 전 ───
    "CONTRACT_EXPIRY_1M": {
        "templateCode": "CONTRACT_EXPIRY_1M",
        "templateName": "계약 만료 1개월 전 안내",
        "templateContent": (
            "#{tenant_name}님 안녕하세요.\n"
            "\n"
            "임대차계약 만료 1개월 전입니다.\n"
            "-물건지: #{address}\n"
            "-만료일: #{end_date}\n"
            "-보증금: #{deposit}원\n"
            "\n"
            "보증금 반환 일정을 확인해주세요.\n"
            "이사 예정인 경우, 퇴거 일정을 임대인과 협의하시기 바랍니다."
        ),
        "templateType": "BA",
    },

    # ─── 4. 월세/관리비 납부 D-3 ───
    "PAYMENT_D3": {
        "templateCode": "PAYMENT_D3",
        "templateName": "납부일 3일전 안내",
        "templateContent": (
            "#{tenant_name}님 안녕하세요.\n"
            "\n"
            "#{payment_type} 납부일 3일 전 안내드립니다.\n"
            "-물건지: #{address}\n"
            "-납부일: #{due_date}\n"
            "#{payment_type}: #{amount}원\n"
            "-입금계좌: #{bank} #{account}\n"
            "-예금주: #{landlord_name}"
        ),
        "templateType": "BA",
    },

    # ─── 5. 월세/관리비 납부 당일 ───
    "PAYMENT_DDAY": {
        "templateCode": "PAYMENT_DDAY",
        "templateName": "납부일 당일 안내",
        "templateContent": (
            "#{tenant_name}님 안녕하세요.\n"
            "\n"
            "금일 #{payment_type} 납부일입니다.\n"
            "-물건지: #{address}\n"
            "#{payment_type}: #{amount}원\n"
            "-입금계좌: #{bank} #{account}\n"
            "-예금주: #{landlord_name}"
        ),
        "templateType": "BA",
    },

    # ─── 6. 납부 확인 완료 ───
    "PAYMENT_CONFIRMED": {
        "templateCode": "PAYMENT_CONFIRMED",
        "templateName": "납부 완료 확인",
        "templateContent": (
            "#{tenant_name}님 안녕하세요.\n"
            "\n"
            "#{payment_type} 납부가 확인되었습니다.\n"
            "-물건지: #{address}\n"
            "-납부일: #{paid_date}\n"
            "-#{payment_type}: #{amount}원\n"
            "\n"
            "감사합니다."
        ),
        "templateType": "BA",
    },
}


# ============================================================
# NHN Cloud 발송 서비스
# ============================================================

class NHNCloudNotificationService:

    def __init__(self):
        self.sms_appkey = getattr(settings, 'NHN_SMS_APPKEY', '')
        self.sms_secret = getattr(settings, 'NHN_SMS_SECRET', '')
        self.sms_sender = getattr(settings, 'NHN_SMS_SENDER', '')
        self.sms_url = f"https://api-sms.cloud.toast.com/sms/v3.0/appKeys/{self.sms_appkey}"

        self.at_appkey = getattr(settings, 'NHN_ALIMTALK_APPKEY', '')
        self.at_secret = getattr(settings, 'NHN_ALIMTALK_SECRET', '')
        self.at_senderkey = getattr(settings, 'NHN_ALIMTALK_SENDERKEY', '')
        self.at_url = f"https://api-alimtalk.cloud.toast.com/alimtalk/v2.3/appKeys/{self.at_appkey}"
        
        # 테스트/개발을 위한 Mock 모드 (기본값 True)
        self.mock_mode = getattr(settings, 'NHN_MOCK_MODE', True)
        # 알림톡 검수 중 여부 (True일 경우 알림톡 시도 없이 바로 SMS 발송)
        self.under_review = getattr(settings, 'NHN_ALIMTALK_UNDER_REVIEW', False)

    def _headers(self, secret):
        return { 'Content-Type': 'application/json;charset=UTF-8', 'X-Secret-Key': secret }

    def _render(self, template_id, variables):
        """템플릿을 SMS용 텍스트로 렌더링 (Python 변수 형식)"""
        tmpl = ALIMTALK_TEMPLATES.get(template_id, {})
        text = tmpl.get("templateContent", f"[계약관리] 알림 ({template_id})")
        
        # 브랜딩 접두어가 없는 경우 추가 (유저 요청 텍스트에 따라 조정)
        full_text = text
        if not full_text.startswith("[계약관리]"):
            full_text = f"[계약관리] {full_text}"
            
        # #{var} → Python {var} 변환 후 format
        py_text = full_text.replace("#{", "{")
        try:
            return py_text.format(**variables)
        except KeyError as e:
            logger.warning(f"Template var missing: {e} in {template_id}")
            return py_text

    # ─── SMS 발송 ───
    def send_sms(self, to, text):
        if self.mock_mode or not self.sms_appkey:
            logger.warning(f"[SMS MOCK] To:{to} | {text[:60]}...")
            return {"success": True, "mock": True, "channel": "sms", "msg": "Mock send success"}
        msg_type = "SMS" if len(text.encode('utf-8')) <= 90 else "LMS"
        endpoint = "/sender/sms" if msg_type == "SMS" else "/sender/mms"
        try:
            payload = {
                "body": text, 
                "sendNo": self.sms_sender.replace("-", ""),
                "recipientList": [{"recipientNo": to.replace("-", "")}],
            }
            if msg_type == "LMS":
                payload["title"] = "[계약관리] 안내"
            
            res = requests.post(f"{self.sms_url}{endpoint}", headers=self._headers(self.sms_secret), json=payload, timeout=10)
            result = res.json()
            ok = result.get("header", {}).get("isSuccessful", False)
            logger.info(f"[SMS] To:{to} Type:{msg_type} OK:{ok}")
            return {"success": ok, "data": result, "channel": "sms"}
        except Exception as e:
            logger.error(f"[SMS ERROR] {e}")
            return {"success": False, "error": str(e), "channel": "sms", "msg": "Internal connection error"}

    # ─── 알림톡 발송 ───
    def send_alimtalk(self, to, template_id, variables):
        if self.under_review:
            logger.info(f"[ALIMTALK REVIEW] Bypassing to SMS fallback for {template_id}")
            return self.send_sms(to, self._render(template_id, variables))

        if self.mock_mode or not self.at_appkey:
            logger.warning(f"[ALIMTALK MOCK] To:{to} Template:{template_id}")
            return {"success": True, "mock": True, "channel": "kakao", "msg": "Mock send success"}

        tmpl = ALIMTALK_TEMPLATES.get(template_id, {})
        template_code = tmpl.get("templateCode", template_id)
        body_text = self._render(template_id, variables)

        try:
            payload = {
                "senderKey": self.at_senderkey,
                "templateCode": template_code,
                "recipientList": [{
                    "recipientNo": to.replace("-", ""),
                    "templateParameter": {k: str(v) for k, v in variables.items()},
                }],
            }
            # SMS 대체 발송 설정
            if self.sms_appkey:
                payload["resendParameter"] = {
                    "isResend": True, "resendType": "SMS",
                    "resendNo": self.sms_sender.replace("-", ""),
                    "resendContent": body_text[:90],
                }
            # 버튼 설정
            if tmpl.get("buttons"):
                payload["recipientList"][0]["buttons"] = tmpl["buttons"]

            res = requests.post(f"{self.at_url}/messages", headers=self._headers(self.at_secret), json=payload, timeout=10)
            result = res.json()
            ok = result.get("header", {}).get("isSuccessful", False)
            msg = result.get("header", {}).get("resultMessage", "")
            logger.info(f"[ALIMTALK] To:{to} Template:{template_code} OK:{ok} MSG:{msg}")
            if not ok:
                logger.warning(f"[ALIMTALK FAIL] {result} → SMS fallback")
                sms_res = self.send_sms(to, body_text)
                sms_res["kakao_error"] = msg
                return sms_res
            return {"success": ok, "data": result, "channel": "kakao", "msg": msg}
        except Exception as e:
            logger.error(f"[ALIMTALK ERROR] {e} → SMS fallback")
            return self.send_sms(to, body_text)

    # ─── 알림톡 + SMS 동시 발송 ───
    def send_dual(self, to, template_id, variables):
        """알림톡과 SMS를 동시에 발송 (검수 중에는 SMS만 발송)"""
        if self.under_review:
            logger.info(f"[ALIMTALK REVIEW] Dual-send bypassed to single SMS for {template_id}")
            return {"success": True, "sms": self.send_alimtalk(to, template_id, variables)}

        text = self._render(template_id, variables)
        at_result = self.send_alimtalk(to, template_id, variables)
        sms_result = self.send_sms(to, text)
        return {
            "success": any(r.get("success") for r in [at_result, sms_result]),
            "alimtalk": at_result, "sms": sms_result, "text": text,
        }


# Singleton
notification_service = NHNCloudNotificationService()


def send_notification_to_user(user, template_id, variables, dual=True):
    """사용자에게 알림 발송 (알림톡 + SMS 동시)"""
    from schedules.models import Notification

    phone = user.phone
    if not phone:
        logger.warning(f"[NOTIFY] User {user.id} no phone")
        return None

    text = notification_service._render(template_id, variables)

    if dual:
        result = notification_service.send_dual(phone, template_id, variables)
    else:
        result = notification_service.send_alimtalk(phone, template_id, variables)

    # DB 기록 - 알림톡
    kakao_success = result.get('alimtalk', result).get('success') if isinstance(result.get('alimtalk', result), dict) else False
    noti = Notification.objects.create(
        user=user, channel='kakao',
        status='sent' if kakao_success else 'failed',
        title=template_id, content=text[:500],
        sent_at=timezone.now() if kakao_success else None,
    )
    # DB 기록 - SMS
    if dual:
        sms_success = result.get('sms', {}).get('success') if isinstance(result.get('sms'), dict) else False
        Notification.objects.create(
            user=user, channel='sms',
            status='sent' if sms_success else 'failed',
            title=template_id, content=text[:500],
            sent_at=timezone.now() if sms_success else None,
        )
    return noti, result
