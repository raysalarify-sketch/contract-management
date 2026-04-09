from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """상호 리뷰"""

    class ReviewType(models.TextChoices):
        LANDLORD_REVIEW = 'landlord_review', '임대인 리뷰 (임차인이 작성)'
        TENANT_REVIEW = 'tenant_review', '임차인 리뷰 (임대인이 작성)'

    contract = models.ForeignKey('contracts.Contract', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews_written')
    reviewee = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews_received')
    review_type = models.CharField(max_length=20, choices=ReviewType.choices)

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='평점'
    )
    content = models.TextField(verbose_name='리뷰 내용')

    # 세부 평가
    cleanliness = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)],
                                       verbose_name='청결도')
    communication = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)],
                                         verbose_name='소통')
    punctuality = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)],
                                       verbose_name='시간 약속')
    deposit_return = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)],
                                          verbose_name='보증금 반환')

    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '리뷰'
        unique_together = ['contract', 'reviewer']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer} → {self.reviewee} ({self.rating}점)"
