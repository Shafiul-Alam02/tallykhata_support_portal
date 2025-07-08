"""display_data URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
# from display_data_app.views import TaskEditView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

# import display_data_app.views as views
from display_data_app import views
from display_data_app.views import CustomTokenObtainPairView, VerifyTokenView  # Ensure your custom view is imported

urlpatterns = [
    path('api/token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify', VerifyTokenView.as_view(), name='token-verify'),
    path('', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('admin/', admin.site.urls),
    path('otp_authentication/', views.otp_authentication, name='otp_authentication'),
    path('home/', views.home_page, name='home'),
    path('user_management/', views.admin_panel, name='user_management'),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('change_password/', views.change_password, name='change_password'),
    path('tk_mnp_issue/', views.tk_mnp_issue, name='tk_mnp_issue'),
    path('tk_mnp_issue/', views.tk_mnp_issue, name='get_tk_mnp_issue'),
    path('tp_txn_status_search/', views.tp_txn_status_search, name='tp_txn_status_search'),
    path('tp_txn_status_search/', views.tp_txn_status_search, name='get_tp_txn_status_search'),
    path('wallet_mdr_limit_search/', views.custom_wallet_mdr_limit, name='wallet_mdr_limit_search'),
    path('wallet_mdr_limit_search/', views.custom_wallet_mdr_limit, name='get_wallet_mdr_limit_search'),
    path('wallet_statement/', views.wallet_statement, name='wallet_statement'),
    path('get_wallet_statement/', views.transaction_info, name='get_wallet_statement'),
    path('transaction_info/', views.transaction_info, name='transaction_info'),
    path('wallet_details/', views.wallet_details, name='wallet_details'),
    path('wallet_details/', views.wallet_details, name='get_wallet_details'),
    path('data_missing/', views.data_missing, name='data_missing'),
    path('data_missing/', views.data_missing, name='get_data_missing'),
    path('service_health_check/', views.service_health_check, name='service_health_check'),
    path('service_health_check/', views.service_health_check, name='get_service_health_check'),
    path('eventapp_event/', views.check_eventapp_event, name='eventapp_event'),
    path('eventapp_event/', views.check_eventapp_event, name='get_eventapp_event'),
    path('check_tallypay_issuer/', views.check_tallypay_issuer, name='check_tallypay_issuer'),
    path('check_tallypay_issuer/', views.check_tallypay_issuer, name='get_check_tallypay_issuer'),
    path('check_tallypay_activity_log/', views.check_tallypay_activity_log, name='check_tallypay_activity_log'),
    path('check_tallypay_activity_log/', views.check_tallypay_activity_log, name='get_check_tallypay_activity_log'),
    path('check_sqr_timeout_cases/', views.check_sqr_time_out_cases, name='check_sqr_timeout_cases'),
    path('check_sqr_timeout_cases/', views.check_sqr_time_out_cases, name='get_sqr_timeout_cases'),
    path('pne_support_log/', views.pne_support_log, name='pne_support_log'),
    path('pne_support_log/', views.pne_support_log, name='get_pne_support_log'),
    path('edit/<int:id>/', views.edit_pne_log, name='edit_task'),
    path('delete/<int:id>/', views.delete_pne_log, name='delete_task'),
    path('customer_care_view', views.customer_care_view, name='customer_care_view'),
    path('selfie_matching_score', views.selfie_matching_score, name='selfie_matching_score'),
    path('sqr_data_download/', views.sqr_data_download, name='sqr_data_download'),
    path('corporate_merchant_registration/', views.corporate_merchant_registration_view,
         name='corporate_merchant_registration'),
    path('corporate_merchant_registration/', views.corporate_merchant_registration_view,
         name='get_corporate_merchant_registration'),
    path('corporate_merchant_registration_edit/<int:pk>/', views.corporate_merchant_edit_entry,
         name='corporate_merchant_registration_edit_task'),
    path('corporate_merchant_registration_delete_task/<int:pk>/', views.corporate_merchant_delete_entry,
         name='corporate_merchant_registration_delete_task'),
    path('corporate_merchant_registration_register_merchant/<int:pk>/', views.register_corporate_merchant,
         name='corporate_merchant_registration_register_merchant'),
    path('check_wallet_or_nid/', views.search_wallet_nid, name='check_wallet_or_nid'),
    path('check_wallet_or_nid/', views.search_wallet_nid, name='get_check_wallet_or_nid'),
    path('remote_end_transaction_status_search/', views.check_remote_end_status,
         name='remote_end_transaction_status_search'),
    path('user-graph/', views.user_graph_view, name='user_graph_view'),
    path('recharge_package_update/', views.recharge_package_update, name='recharge_package_update'),
    path('merchant_id/', views.merchant_id, name='merchant_id'),
    path('limit_email_generator/', views.limit_email_generator, name='limit_email_generator'),
    path('block_debit/', views.block_debit, name='block_debit'),
    path('limit_info/', views.wallet_limit, name='limit_info'),
    path('service_enquiry/', views.service_enquiry, name='service_enquiry'),
    path('nid_usage_log/', views.nid_usage_log, name='nid_usage_log'),
    path('wallets_against_nid/', views.wallets_against_nid, name='wallets_against_nid'),
    path('npsb_inquery/', views.npsb_inquery, name='npsb_inquery'),
    path('permissions/', views.permission_table, name='permission_table'),
    path('txn_details/', views.txn_details, name='txn_details'),
    path('ticket_details/', views.ticket_details, name='ticket_details'),
]
