from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

access_choices = [
    ('YES', 'YES'),
    ('NO', 'NO')
]

department_choices = [
    ('SYSTEM', 'SYSTEM'),
    ('TECHOPS', 'TECHOPS'),
    ('CUSTOMER_SUPPORT', 'CUSTOMER_SUPPORT'),
    ('BUSINESS', 'BUSINESS'),
    ('UNDEFINED', 'UNDEFINED')
]

ACTION_CHOICES = [
    ('PROACTIVE', 'PROACTIVE'),
    ('DAILY_SUPPORT', 'DAILY_SUPPORT'),
    ('PROJECT_MANAGEMENT', 'PROJECT_MANAGEMENT'),
    ('POST_DEPLOYMENT_SQA', 'POST_DEPLOYMENT_SQA'),
    ('DEVELOPMENT', 'DEVELOPMENT'),
    ('OPERATIONS', 'OPERATIONS'),
    ('CUSTOMER_CARE_SUPPORT', 'CUSTOMER_CARE_SUPPORT'),
    ('BUG', 'BUG'),
    ('EMAIL', 'EMAIL')
]

PNE_STATUS = [
    ('NOT_ASSIGNED', 'NOT_ASSIGNED'),
    ('IN_PROGRESS', 'IN_PROGRESS'),
    ('COMPLETED', 'COMPLETED'),
    ('NOT_NEEDED', 'NOT_NEEDED'),
]


class otp_table(models.Model):
    username = models.CharField(max_length=1000)
    otp = models.CharField(max_length=6)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


# Create your models here.
class user_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=500)
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    department = models.CharField(max_length=30, choices=department_choices, default='UNDEFINED')
    admin_access = models.CharField(max_length=10, choices=access_choices, default='NO')
    tk_otp_mnp_access = models.CharField(max_length=10, choices=access_choices, default='NO')
    wallet_mdr_limit_access = models.CharField(max_length=10, choices=access_choices, default='NO')
    tallypay_transaction_status_check = models.CharField(max_length=10, choices=access_choices, default='NO')
    wallet_statement_details = models.CharField(max_length=10, choices=access_choices, default='NO')
    tk_data_missing = models.CharField(max_length=10, choices=access_choices, default='NO')
    service_health_check = models.CharField(max_length=10, choices=access_choices, default='NO')
    eventapp_event = models.CharField(max_length=10, choices=access_choices, default='NO')
    tallypay_issuer = models.CharField(max_length=10, choices=access_choices, default='NO')
    tallypay_activity_log = models.CharField(max_length=10, choices=access_choices, default='NO')
    sqr_timeout_cases = models.CharField(max_length=10, choices=access_choices, default='NO')
    pne_log = models.CharField(max_length=10, choices=access_choices, default='NO')
    sqr_data_download = models.CharField(max_length=10, choices=access_choices, default='NO')
    corporate_merchant_registration = models.CharField(max_length=10, choices=access_choices, default='NO')
    check_wallet_or_nid = models.CharField(max_length=10, choices=access_choices, default='NO')
    is_product_engineering_manager = models.CharField(max_length=10, choices=access_choices, default='NO')
    can_check_remote_end_status = models.CharField(max_length=10, choices=access_choices, default='NO')
    customer_care_portal = models.CharField(max_length=10, choices=access_choices, default='NO')
    debit_credit_block_unblock = models.CharField(max_length=10, choices=access_choices, default='NO')
    complience = models.CharField(max_length=10, choices=access_choices, default='NO')
    complience_execution = models.CharField(max_length=10, choices=access_choices, default='NO')
    complience_maker = models.CharField(max_length=10, choices=access_choices, default='NO')
    complience_call = models.CharField(max_length=10, choices=access_choices, default='NO')

    def __str__(self):
        return f"{self.user} ({self.first_name}) ({self.last_name}) ({self.department}) "


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        user_profile.objects.create(user=instance)
    instance.user_profile.save()


class pne_support_monitoring(models.Model):
    action_type = models.CharField(max_length=100, choices=ACTION_CHOICES)
    subject = models.TextField()
    details = models.TextField()
    assignee = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=100, choices=PNE_STATUS)
    created_by_name = models.CharField(max_length=255)
    created_by_username = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.action_type} - {self.subject}'


class TaskUpdate(models.Model):
    task = models.ForeignKey(pne_support_monitoring, on_delete=models.CASCADE, related_name='updates')
    update_text = models.TextField()
    updated_by_name = models.CharField(max_length=255)
    updated_by_username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Update by {self.updated_by_name} on {self.updated_at}'


class corporate_merchant_registration(models.Model):
    wallet = models.CharField(max_length=11, blank=False, null=False)
    qr_sticker_name = models.CharField(max_length=500, blank=False, null=False)
    qr_display_name = models.CharField(max_length=500, blank=False, null=False)
    business_type = models.CharField(max_length=500, blank=False, null=False)
    account_manager_nid_number = models.CharField(max_length=17, blank=False, null=False)
    account_manager_dob = models.CharField(max_length=500, blank=False, null=False)
    account_manager_face_photo = models.CharField(max_length=1000, blank=False, null=False)
    account_manager_nid_photo_front = models.CharField(max_length=1000, blank=False, null=False)
    account_manager_nid_photo_back = models.CharField(max_length=1000, blank=False, null=False)
    is_active = models.BooleanField(default=False)
    remarks = models.CharField(max_length=1000, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by_name = models.CharField(max_length=255)




from django.db import models

class WalletTransactionType(models.Model):
    wallet = models.CharField(max_length=100)  # Store wallet name or ID
    transaction_type = models.CharField(max_length=100)  # Store type (e.g., CASH_OUT_TO_BANK)
    min_amount_per_txn = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_amount_per_txn = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_count_per_day = models.IntegerField(null=True, blank=True)
    max_amount_per_day = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_count_per_month = models.IntegerField(null=True, blank=True)
    max_amount_per_month = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.wallet} - {self.transaction_type}"

from django.db import models
from django.utils import timezone

from django.utils import timezone
from django.db import models

class TransactionPermission(models.Model):
    wallet = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=100)
    permission = models.CharField(max_length=100)
    chatagory = models.CharField(max_length=100)
    reason = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    initiator_username = models.CharField(max_length=150, null=True, blank=True)
    executor_username = models.CharField(max_length=150, null=True, blank=True)
    initiator_fullname= models.CharField(max_length=150, null=True, blank=True)
    executor_fullname = models.CharField(max_length=150, null=True, blank=True)
    update_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    ticket_number = models.CharField(max_length=100, default='TICKET-0001')

    class Meta:
        db_table = 'transaction_permission'

    def __str__(self):
        return f"{self.wallet} - {self.transaction_type}"

