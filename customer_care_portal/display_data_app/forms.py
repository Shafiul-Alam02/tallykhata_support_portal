from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import DateInput

from .models import pne_support_monitoring, user_profile, corporate_merchant_registration

access_choices = (
    ('NO', 'NO'),
    ('YES', 'YES')
)

department_choices = [
    ('UNDEFINED', 'UNDEFINED'),
    ('SYSTEM', 'SYSTEM'),
    ('TECHOPS', 'TECHOPS'),
    ('CUSTOMER_SUPPORT', 'CUSTOMER_SUPPORT'),
    ('BUSINESS', 'BUSINESS')
]

service_choices = [
    ('MOBILE_RECHARGE', 'MOBILE_RECHARGE'),
    ('CASH_OUT_TO_BANK', 'CASH_OUT_TO_BANK'),
    ('MONEY_IN', 'MONEY_IN'),
    ('MONEY_OUT', 'MONEY_OUT')
]

external_fi_choices = [
    ('NAGAD', 'NAGAD'),
    ('ROCKET', 'ROCKET'),
    ('CBL', 'CBL'),
    ('BEFTN', 'BEFTN'),
    ('VISA', 'VISA'),
    ('NPSB', 'NPSB'),
    ('GP', 'GP'),
    ('ROBI', 'ROBI'),
    ('AIRTEL', 'AIRTEL'),
    ('TT', 'TT'),
    ('BL', 'BL')
]

ACTION_CHOICES = [
    ('PROACTIVE', 'PROACTIVE'),
    ('DAILY_SUPPORT', 'DAILY_SUPPORT'),
    ('PROJECT_MANAGEMENT', 'PROJECT_MANAGEMENT'),
    ('POST_DEPLOYMENT_SQA', 'POST_DEPLOYMENT_SQA'),
    ('DEVELOPMENT', 'DEVELOPMENT'),
    ('OPERATIONS', 'OPERATIONS'),
    ('CUSTOMER_CARE_SUPPORT', 'CUSTOMER_CARE_SUPPORT'),
    ('BUG', 'BUG')
]

PNE_STATUS = [
    ('NOT_ASSIGNED', 'NOT_ASSIGNED'),
    ('IN_PROGRESS', 'IN_PROGRESS'),
    ('COMPLETED', 'COMPLETED'),
    ('NOT_NEEDED', 'NOT_NEEDED'),
]

SERVICE_NAME = [
    ('NPSB_MONEY_OUT', 'NPSB_MONEY_OUT'),
    ('ROCKET_MONEY_OUT', 'ROCKET_MONEY_OUT'),
    ('NAGAD_MONEY_IN', 'NAGAD_MONEY_IN'),
    ('MOBILE_RECHARGE_PAYSTATION', 'MOBILE_RECHARGE_PAYSTATION')
]

business_type_tp_choice = [
    ('মুদি দোকান', 'মুদি দোকান'),
    ('ডিপার্টমেন্টাল স্টোর', 'ডিপার্টমেন্টাল স্টোর'),
    ('ফার্মেসি', 'ফার্মেসি'),
    ('ইলেক্ট্রনিক্স', 'ইলেক্ট্রনিক্স'),
    ('হার্ডওয়্যার', 'হার্ডওয়্যার'),
    ('মোবাইল রিচার্জ', 'মোবাইল রিচার্জ'),
    ('মোবাইল হ্যান্ডসেট এন্ড এক্সেসরিজ', 'মোবাইল হ্যান্ডসেট এন্ড এক্সেসরিজ'),
    ('কম্পিউটার এন্ড এক্সেসরিজ', 'কম্পিউটার এন্ড এক্সেসরিজ'),
    ('কাপড়ের দোকান বা ফ্যাশন হাউজ', 'কাপড়ের দোকান বা ফ্যাশন হাউজ'),
    ('ষ্টেশনারী', 'ষ্টেশনারী'),
    ('কৃষিজাত পণ্য', 'কৃষিজাত পণ্য'),
    ('অফিস সামগ্রী', 'অফিস সামগ্রী'),
    ('আর্ট গ্যালারি', 'আর্ট গ্যালারি'),
    ('এক্সপোর্ট-ইম্পোর্ট বা ট্রেডিং', 'এক্সপোর্ট-ইম্পোর্ট বা ট্রেডিং'),
    ('কনফেকশনারি বা স্ন্যাকস', 'কনফেকশনারি বা স্ন্যাকস'),
    ('কসমেটিকস', 'কসমেটিকস'),
    ('কুটির শিল্প', 'কুটির শিল্প'),
    ('খেলাধুলা সামগ্রী', 'খেলাধুলা সামগ্রী'),
    ('গিফট শপ', 'গিফট শপ'),
    ('গৃহসজ্জা', 'গৃহসজ্জা'),
    ('ঘড়ির দোকান', 'ঘড়ির দোকান'),
    ('চশমার দোকান', 'চশমার দোকান'),
    ('চা/কফি শপ বা জুস বার', 'চা/কফি শপ বা জুস বার'),
    ('জুতার দোকান', 'জুতার দোকান'),
    ('জুয়েলারি', 'জুয়েলারি'),
]


class OTPAuthenticationForm(forms.Form):
    otp = forms.CharField(label="", max_length=6)

    class Meta:
        fields = (
            'OTP'
        )


class registration_form(UserCreationForm):
    department = forms.ChoiceField(choices=department_choices)
    admin_access = forms.ChoiceField(choices=access_choices)
    tk_otp_mnp_access = forms.ChoiceField(choices=access_choices)
    wallet_mdr_limit_access = forms.ChoiceField(choices=access_choices)
    tallypay_transaction_status_check = forms.ChoiceField(choices=access_choices)

    # corporate_merchant_registration = forms.ChoiceField(choices=access_choices)
    # corporate_merchant_bank_account_attach = forms.ChoiceField(choices=access_choices)
    # corporate_merchant_qr_outlet_generate = forms.ChoiceField(choices=access_choices)
    # corporate_merchant_qr_download = forms.ChoiceField(choices=access_choices)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'department',
            'admin_access',
            'tk_otp_mnp_access',
            'wallet_mdr_limit_access',
            'tallypay_transaction_status_check',
            # 'corporate_merchant_registration',
            # 'corporate_merchant_bank_account_attach',
            # 'corporate_merchant_qr_outlet_generate',
            # 'corporate_merchant_qr_download',
            'password1',
            'password2',
        )


# class corporate_merchant_registration_form(forms.Form):
#     wallet = forms.CharField(max_length=11)
#     existing_wallet = forms.ChoiceField(choices=access_choices)
#     nid = forms.CharField(max_length=18)
#     dateOfBirth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
#     bizName = forms.CharField(max_length=100)
#     displayName = forms.CharField(max_length=100)
#     merchantCategoryCode = forms.CharField(max_length=4)
#     nidFront = forms.FileField()
#     nidBack = forms.FileField()
#     profileImage = forms.FileField()
#     np_api_username = forms.CharField(max_length=100)
#     np_api_password = forms.CharField(max_length=100, widget=forms.PasswordInput(render_value=True))
#
#     def clean_nid(self):
#         nid = self.cleaned_data['nid']
#         if len(nid) not in [10, 13, 17]:
#             raise ValidationError("NID must be either 10, 13, or 17 digits.")
#         return nid
#
#     def clean_bizName(self):
#         bizName = self.cleaned_data['bizName']
#         if len(bizName) > 25:
#             raise ValidationError("BizName cannot exceed 25 characters.")
#         return bizName
#
#     def clean_displayName(self):
#         displayName = self.cleaned_data['displayName']
#         if len(displayName) > 55:
#             raise ValidationError("DisplayName cannot exceed 55 characters.")
#         return displayName
#
#     def clean_wallet(self):
#         wallet = self.cleaned_data['wallet']
#         # Mobile number pattern for Bangladesh: 01X-YYYYYYYY
#         if not wallet.startswith('01') or not wallet[2:].isdigit() or len(wallet) != 11:
#             raise ValidationError("Invalid mobile number format. Please enter a valid mobile number.")
#         return wallet

class corporate_bank_account_attach_form(forms.Form):
    wallet = forms.CharField(max_length=11)
    bank_name = forms.CharField(max_length=100)
    account_name = forms.CharField(max_length=100)
    account_number = forms.CharField(max_length=20)
    routing_number = forms.CharField(max_length=20)
    nportal_token = forms.CharField()

    def clean_account_number(self):
        account_number = self.cleaned_data['account_number']
        if not account_number.isdigit():
            raise forms.ValidationError("Account number must be a numeric value with a length of 20 characters.")
        return account_number

    def clean_routing_number(self):
        routing_number = self.cleaned_data['routing_number']
        if not routing_number.isdigit():
            raise forms.ValidationError("Routing number must be a numeric value with a length of 20 characters.")
        return routing_number


class corporate_merchant_outlet_and_qr_generation_form(forms.Form):
    wallet = forms.CharField(max_length=11)
    superQrName = forms.CharField(max_length=100)
    officerName = forms.CharField(max_length=100)
    transactionSmsMobileNo = forms.CharField(max_length=11)
    sendSms = forms.ChoiceField(choices=access_choices)
    city = forms.CharField(max_length=100)
    address = forms.CharField(max_length=200)
    np_api_username = forms.CharField(max_length=100)
    np_api_password = forms.CharField(max_length=100, widget=forms.PasswordInput(render_value=True))


class corporate_merchant_qr_download_form(forms.Form):
    wallet = forms.CharField(max_length=11)


class DatePicker(DateInput):
    input_type = "date"

    def format_value(self, value):
        return value.isoformat() if value is not None and hasattr(value, "isoformat") else ""


class data_missing_form(forms.Form):
    tk_mobile_number = forms.CharField(label='Wallet Numbers', max_length=11)
    from_date = forms.DateField(widget=DatePicker(), label='Start Date')
    to_date = forms.DateField(widget=DatePicker(), label='End Date')
    customer_need = forms.ChoiceField(
        choices=[
            ('TRANSACTION_LIST', 'TRANSACTION_LIST'),
            ('CUSTOMER_LIST', 'CUSTOMER_LIST')],
        label='Customer Need')
    OPTION_ = forms.ChoiceField(
        choices=[
            ('FROM_JOURNAL', 'FROM_JOURNAL'),
            ('FROM_HISTORY', 'FROM_HISTORY')],
        label='Category')

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")

        if from_date and to_date:
            if from_date > to_date:
                raise forms.ValidationError("From date cannot be greater than To date.")

        return cleaned_data


class service_health_check_form(forms.Form):
    service = forms.ChoiceField(choices=service_choices)
    partner_name = forms.ChoiceField(choices=external_fi_choices)


class eventapp_event_form(forms.Form):
    wallet = forms.CharField(max_length=11)
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    def clean_wallet(self):
        wallet = self.cleaned_data['wallet']
        # Mobile number pattern for Bangladesh: 01X-YYYYYYYY
        if not wallet.startswith('01') or not wallet[2:].isdigit() or len(wallet) != 11:
            raise ValidationError("Invalid mobile number format. Please enter a valid mobile number.")
        return wallet


class sqr_timeout_form(forms.Form):
    from_date = forms.DateField(widget=DatePicker(), label='Start Date')
    to_date = forms.DateField(widget=DatePicker(), label='End Date')

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")

        if from_date and to_date:
            if from_date > to_date:
                raise forms.ValidationError("From date cannot be greater than To date.")

        return cleaned_data


class pne_log_form(forms.ModelForm):
    action_type = forms.ChoiceField(choices=ACTION_CHOICES)
    assignee = forms.ChoiceField(choices=[], required=True)
    status = forms.ChoiceField(choices=PNE_STATUS)
    new_update = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False)

    # Add more custom fields here if needed

    class Meta:
        model = pne_support_monitoring
        fields = (
            'action_type',
            'assignee',
            'status',
            'subject',
            'details',
        )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(pne_log_form, self).__init__(*args, **kwargs)

        # Populate assignee choices
        self.fields['assignee'].choices = [(p.first_name, p.first_name) for p in
                                           user_profile.objects.filter(department='TECHOPS')]

        # Set default value for assignee if current_user is provided
        # if current_user:
        #     try:
        #         profile = user_profile.objects.get(user=current_user)
        #         self.fields['assignee'].initial = profile.first_name
        #     except user_profile.DoesNotExist:
        #         self.fields['assignee'].initial = None

        self.fields['action_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['subject'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['details'].widget.attrs.update({'class': 'form-control', 'rows': 5})
        self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_update'].widget.attrs.update({'class': 'form-control', 'rows': 3})


class pne_log_edit_form(forms.ModelForm):
    action_type = forms.ChoiceField(choices=ACTION_CHOICES)
    # assignee = forms.ChoiceField(choices=[], required=False)
    status = forms.ChoiceField(choices=PNE_STATUS)
    new_update = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False)

    # Add more custom fields here if needed

    class Meta:
        model = pne_support_monitoring
        fields = (
            'action_type',
            # 'assignee',
            'status',
            'subject',
            'details',
        )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(pne_log_edit_form, self).__init__(*args, **kwargs)

        self.fields['action_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['subject'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['details'].widget.attrs.update({'class': 'form-control', 'rows': 5})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_update'].widget.attrs.update({'class': 'form-control', 'rows': 3})


class CSVUploadForm(forms.Form):
    upms_username = forms.CharField(max_length=150, label='UPMS Username')
    upms_password = forms.CharField(widget=forms.PasswordInput(), label='UPMS Password')
    # upload_csv = forms.FileField()


class corporate_merchant_registration_form(forms.Form):
    upload_csv = forms.FileField()
    # upms_username = forms.CharField(max_length=150, label='TALLY_FO Username')
    # upms_password = forms.CharField(widget=forms.PasswordInput(), label='TALLY_FO Password')


class edit_corporate_merchant_data_form(forms.ModelForm):
    class Meta:
        model = corporate_merchant_registration
        fields = (
            'wallet',
            'qr_sticker_name',
            'qr_display_name',
            'business_type',
            'account_manager_nid_number',
            'account_manager_dob',
            'account_manager_face_photo',
            'account_manager_nid_photo_front',
            'account_manager_nid_photo_back',
            'remarks',
        )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(edit_corporate_merchant_data_form, self).__init__(*args, **kwargs)

        self.fields['wallet'].widget.attrs.update({'class': 'form-control'})
        self.fields['qr_sticker_name'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['qr_display_name'].widget.attrs.update({'class': 'form-control', 'rows': 5})
        self.fields['business_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['account_manager_nid_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['account_manager_dob'].widget.attrs.update({'class': 'form-control'})
        self.fields['account_manager_face_photo'].widget.attrs.update({'class': 'form-control'})
        self.fields['account_manager_nid_photo_front'].widget.attrs.update({'class': 'form-control'})
        self.fields['account_manager_nid_photo_back'].widget.attrs.update({'class': 'form-control'})
        self.fields['remarks'].widget.attrs.update({'class': 'form-control'})


class wallet_nid_search_form(forms.Form):
    wallet_or_nid = forms.CharField(
        max_length=17,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='Enter digits only.',
                code='invalid_number'
            )
        ]
    )
    data_type = forms.ChoiceField(choices=[
        ('WALLET', 'WALLET'),
        ('NID', 'NID')
    ])


class status_check_form(forms.Form):
    remote_end_transaction_number = forms.CharField(max_length=1000, label='Remote End Transaction Identifier')
    service_name = forms.ChoiceField(choices=SERVICE_NAME)


class UserSelectionForm(forms.Form):
    username = forms.ChoiceField(
        choices=[(user.username, user.username) for user in User.objects.distinct()],
        label="Select User",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class PNELogFilterForm(forms.Form):
    action_type = forms.ChoiceField(
        choices=[('', 'None')] + list(pne_support_monitoring._meta.get_field('action_type').choices),
        required=False,
        initial='',
        label=''
    )

    # Fetch unique assignee values from the database, ordered by id in descending order
    assignee_choices = [('', 'None')] + [
        (assignee['assignee'], assignee['assignee'])
        for assignee in pne_support_monitoring.objects.values('assignee').distinct()
    ]
    assignee = forms.ChoiceField(
        choices=assignee_choices,
        required=False,
        initial='',
        label=''
    )

    status = forms.ChoiceField(
        choices=[('', 'None')] + list(
            pne_support_monitoring._meta.get_field('status').choices),
        required=False,
        initial=['IN_PROGRESS', 'NOT_ASSIGNED'],
        label=''
    )




from django import forms
from .models import WalletTransactionType

class WalletTransactionForm(forms.ModelForm):
    class Meta:
        model = WalletTransactionType
        fields = ['wallet', 'transaction_type', 'min_amount_per_txn', 'max_amount_per_txn',
                  'max_count_per_day', 'max_amount_per_day', 'max_count_per_month', 'max_amount_per_month']
