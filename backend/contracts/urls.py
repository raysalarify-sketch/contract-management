from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InquiryViewSet, ContractAgreementViewSet, ContractViewSet
from .contract_api import (
    register_contract, my_contracts, contract_schedules,
    mark_rent_paid, contract_notifications, send_test_notification,
    update_profile
)

router = DefaultRouter()
router.register("inquiries", InquiryViewSet, basename="inquiry")
router.register("agreements", ContractAgreementViewSet, basename="agreement")

urlpatterns = [
    path("register-contract/", register_contract, name="register-contract"),
    path("my-contracts/", my_contracts, name="my-contracts"),
    path("<int:contract_id>/schedules/", contract_schedules, name="contract-schedules"),
    path("schedules/<int:schedule_id>/mark-paid/", mark_rent_paid, name="mark-paid"),
    path("<int:contract_id>/notifications/", contract_notifications, name="contract-notifications"),
    path("test-notification/", send_test_notification, name="test-notification"),
    path("accounts/profile/update/", update_profile, name="update-profile"),
    path("", include(router.urls)),
]
