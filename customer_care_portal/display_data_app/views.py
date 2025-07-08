import datetime
import json
import logging
import random
import xml
import xml.dom.minidom
from datetime import datetime, timedelta
from io import TextIOWrapper

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.messages import success
from django.core.mail import send_mail
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from display_data_app.python_modules import api_calls as api
from display_data_app.python_modules import important_functions as func
from display_data_app.python_modules import isheet_controller as google_sheet_func
from display_data_app.python_modules import sql_connections as sql_conn
from display_data_app.python_modules import sql_queries as sql
from .forms import PNELogFilterForm
from .forms import registration_form, data_missing_form, OTPAuthenticationForm, corporate_merchant_registration_form, \
    pne_log_edit_form, pne_log_form, edit_corporate_merchant_data_form
from .forms import service_health_check_form, eventapp_event_form, sqr_timeout_form, CSVUploadForm, \
    wallet_nid_search_form
from .forms import status_check_form, UserSelectionForm
from .models import TaskUpdate, otp_table, corporate_merchant_registration
from .models import pne_support_monitoring, user_profile
from .serializers import CustomTokenObtainPairSerializer
from .models import TransactionPermission

# Create your views here.

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DB Names to deal with are below.
SQA_MODE = False

if SQA_MODE == False:
    tk_db = "tallykhata_v2_live"
    nobopay_db = "nobopay_payment_gw"
    nobopay_core = "nobopay_core"
    sms_prod = "sms_prod"
    topup = "topup_service"
    profino_rbl = "profino_rbl"
    switch = "switch"
    tp_sms_db = "wso2_db"
    keycloak = "keycloak"
    icp_db = "ICPDatabase"
    tp_core = "nobopay_core"
    backend_db = "backend_db"
    tp_bank_service="tp_bank_service"
    nobopay_nid_gw = "nobopay_nid_gw"
    tallypay_to_fi_integration = 'tallypay_to_fi_integration'
    nobopay_api = 'nobopay_api'
    nobopay_nid_gw = 'nobopay_nid_gw'
    tallypay_issuer = 'tallypay_issuer'
    nobopay_payment_gw = 'nobopay_payment_gw'
    tallykhata_log = 'tallykhata_log'
    nobopay_nid_crawler = 'nobopay_nid_crawler'
    pne_execution_log = 'pne_execution_log_live'
else:
    tk_db = "tallykhata_sqa"
    nobopay_db = "nobopay_payment_gw"
    sc_sms_db = "sc_sms_xyz"
    topup = "topup_service"
    profino_rbl = "profino_rbl"
    switch = "switch"
    tp_sms_db = "wso2_db"
    keycloak = "keycloak"
    icp_db = "ICPDatabase"
    tp_core = "nobopay_core"
    backend_db = "backend_db"
    tp_bank_service = "tp_bank_service"
    tallypay_to_fi_integration = 'tallypay_to_fi_integration'
    nobopay_api = 'nobopay_api'
    tallypay_issuer = 'tallypay_issuer'
    nobopay_payment_gw = 'nobopay_payment_gw'
    tallykhata_log = 'tallykhata_log'
    pne_execution_log = 'pne_execution_log_local'


class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        try:
            # Verify the token using Simple JWT
            payload = AccessToken(token)  # Decode and verify the token
            user = request.user  # Get the user from the request context

            return Response({
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        try:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            return Response({
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
            })
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=400)

# @login_required
def get_access_information(user_id):
    filtered_objects = user_profile.objects.filter(user_id=user_id)
    print(filtered_objects)

    all_profiles_info = {}  # Dictionary to store combined information from all profiles
    for obj in filtered_objects:
        for field in obj._meta.fields:
            field_name = field.name
            field_value = getattr(obj, field_name)
            all_profiles_info[field_name] = field_value  # Assign value directly to dictionary key
    print(all_profiles_info)  # Print or return the combined dictionary

    return all_profiles_info


@login_required
def user_registration(request):
    access = user_profile.objects.filter(user=request.user).values_list('admin_access')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied.')
        return redirect('/home')

    if department[0][0] not in ('TECHOPS', 'SYSTEM'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if request.method == 'POST':
        form = registration_form(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.user_profile.email = form.cleaned_data.get('email')
            user.user_profile.first_name = form.cleaned_data.get('first_name')
            user.user_profile.last_name = form.cleaned_data.get('last_name')
            user.user_profile.department = form.cleaned_data.get('department')
            user.user_profile.admin_access = form.cleaned_data.get('admin_access')
            user.user_profile.tk_otp_mnp_access = form.cleaned_data.get('tk_otp_mnp_access')
            user.user_profile.tallypay_transaction_status_check = form.cleaned_data.get(
                'tallypay_transaction_status_check')
            user.user_profile.wallet_mdr_limit_access = form.cleaned_data.get('wallet_mdr_limit_access')
            # user.user_profile.corporate_merchant_registration = form.cleaned_data.get('corporate_merchant_registration')
            # user.user_profile.corporate_merchant_bank_account_attach = form.cleaned_data.get('corporate_merchant_bank_account_attach')
            # user.user_profile.corporate_merchant_qr_outlet_generate = form.cleaned_data.get('corporate_merchant_qr_outlet_generate')
            # user.user_profile.corporate_merchant_qr_download = form.cleaned_data.get('corporate_merchant_qr_download')
            user.save()
            messages.success(request, 'User registered successfully')
            return redirect('user_management')
    else:
        form = registration_form()
    return render(request, 'registration.html', {'form': form, 'access_info': access_info})


# Home Page View
@login_required
def home_page(request):
    template = "home_page.html"
    title = "Welcome to Customer Care Portal"
    access_info = get_access_information(request.user.id)

    context = {
        'title': title,
        'access_info': access_info
    }

    return render(request, template, context)


@login_required
def change_password(request):
    template = 'change_password.html'
    access_info = get_access_information(request.user.id)

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
        'access_info': access_info
    }

    return render(request, template, context)


@login_required
def otp_authentication(request):
    template = 'otp_login.html'

    if request.method == 'POST':
        form = OTPAuthenticationForm(request.POST)
        # print(otp)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            username = request.user.username
            print(f'Entered otp is: {entered_otp}')
            three_minutes_ago = timezone.now() - timedelta(minutes=3)
            queryset = otp_table.objects.filter(
                username=username,
                is_active=True,
                create_date__gte=three_minutes_ago
            ).order_by('-create_date')

            logger.info(f'OTP queryset is: {queryset.values()}')

            # Get the latest instance
            latest_instance = queryset.first()  # Alternatively, you can use queryset[0]

            if latest_instance:
                db_otp = latest_instance.otp
                print(f'DB OTP is: {db_otp}')
                if db_otp == str(entered_otp):
                    print('OTP Matched')
                    updated_rows_count = otp_table.objects.filter(
                        username=username,
                        otp=entered_otp
                    ).update(
                        is_active=False
                    )
                    return redirect('home')
                else:
                    print('OTP not matched')
                    messages.error(request, 'OTP not matched')
                    return redirect('otp_authentication')
            else:
                print('Queryset not found')
                return redirect('otp_authentication')
    else:
        otp = random.randint(100000, 999999)
        print(otp)
        username = request.user.username
        print(f'Username is: {username}')
        target_email = request.user.email
        print(target_email)
        # insert data to table here
        instance = otp_table(
            username=username,
            otp=otp
        )
        instance.save()

        subject = 'Customer Care Portal - Login OTP'
        message = f'''
            Hello,
            
            Your OTP for logging into Customer Care portal is: {otp}
            
            For any issues please contact Product Engineering
            
            Sincerely
        '''
        from_email = settings.EMAIL_HOST_USER  # Sender's email address
        to_email = [target_email]  # List of recipient email addresses

        send_mail(subject, message, from_email, to_email)

        form = OTPAuthenticationForm()

    return render(request, template, {'form': form})


@login_required
def tk_mnp_issue(request):
    access = user_profile.objects.filter(user=request.user).values_list('tk_otp_mnp_access')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied.')
        return redirect('/home')

    if department[0][0] not in ('TECHOPS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    template = 'tk_mnp_issue.html'
    title = 'TallyKhata OTP MNP Solution'
    queryset_otp = queryset_txn = None

    if request.POST.get('verify_btn'):
        print('Starting OTP MNP operation')
        wallet = request.POST['wallet_mnp']
        # amount = request.POST['wallet_amount']

        # Wallet number verification
        # result = re.search("(^(\+8801|8801|01))[1|3-9]{1}(\d){8}$", wallet)
        #
        # if result:
        #     pass
        # else:
        #     messages.error(request, 'Please enter a valid mobile number')
        #     return redirect('/tk_mnp_issue')
        #
        # if (len(wallet)==0):
        #     messages.error(request, 'Please enter wallet number')
        #     return redirect('/tk_mnp_issue')

        # Wallet number verification end

        print("wallet number is: ", wallet)
        query = sql.tk_mnp_issue(wallet)
        # queryset_tk_txn = sql_conn.run_pgsql_server(query[1], tk_db)
        # print("TK Queryset: ", queryset_tk_txn)
        # queryset_tp_txn = sql_conn.run_mysql_server(query[2],tp_core)
        # print("TP Queryset: ", queryset_tp_txn)
        # verification_result = func.otp_mnp_verification(amount, queryset_tk_txn, queryset_tp_txn)
        # print(verification_result)

        verification_result = 'MATCHED'
        if verification_result == 'MATCHED':
            queryset_otp = sql_conn.run_pgsql_server(query, sms_prod)
            print(queryset_otp)
            if len(queryset_otp) == 0:
                messages.error(request, 'User did not generate OTP yet')
                return redirect('/tk_mnp_issue')
            elif type(queryset_otp) == str:
                messages.error(request, 'Error is: ' + queryset_otp)
                return redirect('/tk_mnp_issue')
            else:
                message = queryset_otp[0][3]  # Prod case
                print(f'Raw message is: {message}')
                # message = message.decode('utf-8')
                print(f'Decoded message is: {message}')

                message = message.replace("<#>", "<>")
                # from datetime import datetime
                # Get current date and time
                now = datetime.now()
                # Format the date and time with milliseconds
                ref_no = now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"
                print(ref_no)
                sms_resp_status = func.sms_sending_api_banglalink(wallet, message, ref_no)  # prod case
                if sms_resp_status == 200:
                    print('SMS Successfully sent to user')
                    print(message)
                    messages.success(request, 'OTP SMS sent successfully to the user')
                    return redirect('/tk_mnp_issue')
                    # print(tp_wallet_numbers[x])
                else:
                    messages.error(request,
                                   'User wallet number has matched but there was an error in sending SMS. Contact TechOps')
                    return redirect('/tk_mnp_issue')
        else:
            messages.error(request,
                           'User amount did not match with last 5 transactions in TallyKhata. OTP SMS not sent')
            return redirect('/tk_mnp_issue')

    context = {
        'title': title,
        'queryset_otp': queryset_otp,
        'queryset_txn': queryset_txn,
        'access_info': access_info
    }

    return render(request, template, context)


@login_required
def admin_panel(request):
    access = user_profile.objects.filter(user=request.user).values_list('admin_access')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied.')
        return redirect('/home')

    if department[0][0] not in ('TECHOPS', 'SYSTEM'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    template = "admin_user_management.html"
    title = "User Management"

    queryset = user_profile.objects.all()

    context = {
        'title': title,
        'queryset': queryset,
        'access_info': access_info
    }

    return render(request, template, context)


def shafiul_generate_html_table(heading, queryset):
    # Start the table with improved styling
    table_html = '''
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            font-family: Helvetica, Arial, sans-serif;
            color: #333;
            margin: 20px auto;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            table-layout: auto;
        }
        #table th, #table td {
                    padding: 12px 15px;
                    text-align: left;
                    word-wrap: break-word; /* Prevents text overflow */
                }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            # background-color: #DC4C64;
            #color: #333;
            width: 25%;
            font-family: Arial, sans-serif;
        }
        td {
            background-color: #f9f9f9;
        }
        tr:hover td {
            background-color: #f1f1f1;
        }
    </style>
    <table id="table" class="table table-bordered"  style="table-layout: auto;">
    <tbody>
    '''

    # Assuming queryset contains a single record (tuple/list) since headings correspond to the columns
    for i, column_name in enumerate(heading):
        table_html += '<tr>\n'
        table_html += f'<th>{column_name}</th>\n'
        table_html += f'<td>{queryset[0][i]}</td>\n'
        table_html += '</tr>\n'

    table_html += '</tbody>\n'

    # End the table
    table_html += '</table>'

    return table_html


def generate_html_table(headers, data):
    # Start building the HTML table
    html_table = '''
        <style>
            /* Table Styling */
            #table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 12px;
                background-color: #02b0b0;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            #table th {
                background-color: #02b0b0;
                color: #fff;
                font-weight: bold;
                text-transform: uppercase;
                padding: 10px;
            }
            
            #table td {
                padding: 10px;
            }
            
            #table tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            
            #table tr:nth-child(odd) {
                background-color: #ffffff;
            }
            
            #table tr:hover {
                background-color: #e9ecef;
            }




        </style>
         <table id="table" class="table table-bordered" style="table-layout: auto;">
        '''

    # Add table headers
    html_table += "<thead>\n<tr>\n"
    for header in headers:
        html_table += "<th>{}</th>\n".format(header)
    html_table += "</tr>\n</thead>\n"

    # Add table data
    html_table += "<tbody>\n"
    for row in data:
        # html_table += "<tbody>\n<tr>\n"
        html_table += "<tr>\n"
        for value in row:
            html_table += "<td>{}</td>\n".format(value)
        # html_table += "</tr>\n</tbody>\n"
        html_table += "</tr>\n"
    html_table += "</tbody>\n"

    # Add an empty tbody for DataTables pagination to work correctly
    html_table += "<tbody></tbody>\n"

    # Add table footer
    # html_table += "<tfoot>\n<tr>\n"
    # for header in headers:
    #     html_table += "<th>{}</th>\n".format(header)
    # html_table += "</tr>\n</tfoot>\n"

    # End the table
    html_table += "</table>\n"

    return html_table


# TP Transaction Status Search
@login_required
def tp_txn_status_search(request):
    template = "tp_transaction_status_search.html"
    title = "TallyPay Transaction Status Search"
    access_info = get_access_information(request.user.id)

    txn_date = txn_amount = txn_description = reverse_status = None
    txn_number = txn_tag = escrow_status = release_txn_num = transaction_name = None
    from_account = to_account = remote_end_response = invoice_no = trace_data = html_table_code = None
    show_table_and_pre = False
    decision_status = txn_type = from_account_type = to_account_type = charge_flag = None

    access = user_profile.objects.filter(user=request.user).values_list('tallypay_transaction_status_check')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        txn_num = request.POST.get(
            'txn_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered transaction number is: {txn_num}')

        query = sql.tallypay_master_txn_search(txn_num)
        logger.info(f'Query is: {query}')
        queryset = sql_conn.run_pgsql_server(query, tp_core)
        logger.info(f'Result of queryset is: {queryset}')

        if len(queryset) == 0:
            messages.error(request, 'Transaction not found in transfers table.')
            return redirect('/tp_txn_status_search')

        txn_date = queryset[0][0]
        txn_amount = queryset[0][1]
        txn_description = queryset[0][2]
        reverse_status = queryset[0][3]
        txn_number = queryset[0][4]
        txn_tag = queryset[0][5]
        escrow_status = queryset[0][6]
        release_txn_num = queryset[0][7]
        transaction_name = queryset[0][8]
        from_account = queryset[0][9]
        to_account = queryset[0][10]
        transfers_type_id = queryset[0][11]
        invoice_no = queryset[0][12]
        trace_data = queryset[0][13]
        txn_type = queryset[0][14]
        from_account_type = queryset[0][15]
        to_account_type = queryset[0][16]
        charge_flag = queryset[0][17]
        customer_id = queryset[0][18]

        if reverse_status is not None:
            reverse_status = 'REVERSED'
        else:
            reverse_status = 'NOT REVERSED'

        if escrow_status == 'I':
            escrow_status = 'Escrow Initiated'
        elif escrow_status == 'R':
            escrow_status = 'Escrow Released'
        else:
            pass

        logger.info(f'Transfers type is: {transfers_type_id}')

        # For bank cash out
        if txn_type == 'CASH_OUT_TO_BANK':
            logger.info(
                'CASH_OUT_TO_BANK component table query, Get PK and date from bank_txn_request table and call API')
            query = sql.get_data_for_remote_end_checking(trace_data, txn_type, charge_flag)
            logger.info(query)
            queryset = sql_conn.run_pgsql_server(query, backend_db)
            logger.info(f'BTR queryset is: {queryset}')

            if type(queryset) == list and len(queryset) != 0:
                heading = [
                    'BTR_ID',
                    'TXN_REQUEST_TYPE',
                    'BTR_STATUS',
                    'NP_LOG_STATUS',
                    'AMOUNT',
                    'ISSUE_TIME',
                    'ACCOUNT_NUMBER',
                    'ROUTING_NUMBER',
                    'BTR_CORE_TXN_ID',
                    'NP_TXN_NUM',
                    'TYPE_NAME',
                    'BANK_NAME',
                    'BRANCH_NAME',
                    'RESPONSE_CODE',
                    'REQUEST_TEXT',
                    'RESPONSE_TEXT'
                ]

                html_table_code = generate_html_table(heading, queryset)

                print(f'HTML Code is: {html_table_code}')
            else:
                html_table_code = f'''
                    <p>No component or request table data found</p>
                '''
        # For SQR
        elif txn_type == 'NPSB_TRANSFER_CREDIT':
            logger.info('NPSB_TRANSFER_CREDIT component table query')
            query = sql.get_data_for_remote_end_checking(customer_id, txn_type, charge_flag)
            logger.info(query)
            queryset = sql_conn.run_pgsql_server(query, tallypay_issuer)
            logger.info(f'Tallypay issuer queryset is: {queryset}')

            if type(queryset) == list and len(queryset) != 0:
                heading = [
                    'CREATE_DATE',
                    'UPDATE_DATE',
                    'REQUEST_ID',
                    'REQUEST',
                    'RESPONSE',
                    'PROCESS_TIME'
                ]

                html_table_code = generate_html_table(heading, queryset)
                print(f'HTML Code is: {html_table_code}')
            else:
                html_table_code = f'''
                    <p>No component or request table data found</p>
                '''
        # For money out to external
        elif txn_type == 'CASH_OUT_TO_EXTERNAL':
            logger.info('CASH_OUT_TO_EXTERNAL component table query')
            query = sql.get_data_for_remote_end_checking(trace_data, txn_type, charge_flag)
            logger.info(f'Component table query is {query}')
            queryset = sql_conn.run_pgsql_server(query, tallypay_to_fi_integration)
            logger.info(f'Tallypay queryset is: {queryset}')

            if type(queryset) == list and len(queryset) != 0:
                heading = [
                    'ID',
                    'CREATE_DATE',
                    'UPDATE_DATE',
                    'STATUS',
                    'FROM_WALLET',
                    'EXTERNAL_WALLET',
                    'AMOUNT',
                    'REQUEST_ID',
                    'FINANCIAL_INSTITUTE',
                    'TALLY_PAY_TXN_ID',
                    'EXTERNAL_TXN_ID',
                    'EXTRA_INFO',
                    'CHANNEL',
                    'NUMBER_OF_TRY_INTERNAL',
                    'NUMBER_OF_TRY_EXTERNAL',
                    'DESCRIPTION',
                    'REF_NO',
                    'NOTE',
                    'REQUEST_ID',
                    'REQUEST',
                    'RESPONSE',
                    'PROCESS_TIME'
                ]

                html_table_code = shafiul_generate_html_table(heading, queryset)
                print(f'HTML Code is: {html_table_code}')
            else:
                html_table_code = f'''
                    <p>No component or request table data found</p>
                '''
        # Mobile recharge
        elif txn_type == 'MOBILE_RECHARGE':
            logger.info(
                f'''Transaction type is {txn_description}, search topup_service.public.top_up_info using transaction number in txn_id column''')
            query = sql.get_data_for_remote_end_checking(trace_data, txn_type, charge_flag)
            logger.info(f'''Query for searching topup_service.public.top_up_info is: {query}''')
            queryset = sql_conn.run_pgsql_server(query, topup)
            logger.info(f'''Result of topup_service query is: {queryset}''')

            if type(queryset) == list and len(queryset) != 0:
                heading = [
                    "CREATE_DATE",
                    "MOBILE_OPERATOR",
                    "RECHARGE_VENDOR",
                    "WALLET",
                    "RECEIVER_MOBILE",
                    "RECHARGE_AMOUNT",
                    "INITIATED_TXN_NUM",
                    "RELEASE_TXN_NUM",
                    "STATUS",
                    "EXTERNAL_REF",
                    "DESCRIPTION",
                    "REQUEST_ID",
                    "REQUEST",
                    "RESPONSE",
                    "REQUEST_CREATE_DATE",
                    "REQUEST_PROCESS_TIME"
                ]

                html_table_code = generate_html_table(heading, queryset)

                print(f'HTML Code is: {html_table_code}')
            else:
                html_table_code = f'''
                    <p>No component or request table data found</p>
                '''
        # For money in from external
        elif txn_type == 'CASH_IN_FROM_EXTERNAL':
            if charge_flag == 'NAGAD':
                logger.info('MONEY IN FROM NAGAD component table query')
                query = sql.get_data_for_remote_end_checking(trace_data, txn_type, charge_flag)
                logger.info(query)
                queryset = sql_conn.run_pgsql_server(query, nobopay_payment_gw)
                logger.info(f'NAGAD CASH IN queryset is: {queryset}')

                if type(queryset) == list and len(queryset) != 0:
                    heading = [
                        "WALLET",
                        "CLIENT_MOBILE_NO",
                        "AMOUNT",
                        "NAGAD_STATUS",
                        "STATUS",
                        "ORDER_ID",
                        "ORDER_DATE_TIME",
                        "PAYMENT_REFERENCE_ID",
                        "ISSUER_PAYMENT_REF_NO",
                        "ISSUER_PAYMENT_DATE_TIME",
                        "CANCEL_ISSUER_REF_NO",
                        "CANCEL_ISSUER_DATE_TIME",
                        "NAGAD_STATUS_CODE",
                        "CREDIT_COLLECTION_ID",
                        "CREATE_DATE",
                        "UPDATE_DATE"
                    ]

                    html_table_code = generate_html_table(heading, queryset)
                    print(f'HTML Code is: {html_table_code}')
            elif charge_flag == 'ROCKET':
                logger.info('MONEY IN FROM ROCKET component table query')
                query = sql.get_data_for_remote_end_checking(trace_data, txn_type, charge_flag)
                logger.info(query)
                queryset = sql_conn.run_pgsql_server(query, nobopay_payment_gw)
                logger.info(f'ROCKET CASH IN queryset is: {queryset}')

                if type(queryset) == list and len(queryset) != 0:
                    heading = [
                        "WALLET",
                        "CARD_NUMBER",
                        "TP_TRANSACTION_NUMBER",
                        "AMOUNT",
                        "STATUS",
                        "RRN",
                        "TXN_DATE",
                        "DBBL_TXN_ID",
                        "DESCRIPTION",
                        "IP",
                        "RESULT",
                        "RESULT_CODE",
                        "CREDIT_COLLECTION_ID"
                    ]

                    html_table_code = generate_html_table(heading, queryset)
                    print(f'HTML Code is: {html_table_code}')
        # For money in from card
        elif txn_type == 'CASH_IN_FROM_CARD':
            logger.info(
                f'''Transaction type is {txn_description}, search topup_service.public.top_up_info using transaction number in txn_id column''')
            query = sql.get_data_for_remote_end_checking(trace_data, txn_type, charge_flag)
            logger.info(f'''Query for searching payment_info is: {query}''')
            queryset = sql_conn.run_pgsql_server(query, nobopay_payment_gw)
            logger.info(f'''Result of payment_info query is: {queryset}''')

            if type(queryset) == list and len(queryset) != 0:
                heading = [
                    "WALLET",
                    "ORDER_ID",
                    "AMOUNT",
                    "CREATE_DATE",
                    "UPDATE_DATE",
                    "STATUS",
                    "TXN_ID",
                    "CARD_NO",
                    "CARD_TYPE",
                    "EXPIRY",
                    "NAME",
                    "CREDIT_COLLECTION_ID",
                    "REQUEST",
                    "RESPONSE",
                    "EXTERNAL_REQUEST",
                    "EXTERNAL_RESPONSE",
                    "EXTERNAL_PROCESS_TIME"
                ]

                html_table_code = generate_html_table(heading, queryset)

                print(f'HTML Code is: {html_table_code}')
            else:
                html_table_code = f'''
                    <p>No component or request table data found</p>
                '''
        else:
            messages.error(request, 'Transaction type not mapped yet in the portal.')
    else:
        show_table_and_pre = False

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'txn_date': txn_date,
        'txn_amount': txn_amount,
        'txn_description': txn_description,
        'reverse_status': reverse_status,
        'txn_number': txn_number,
        'txn_tag': txn_tag,
        'escrow_status': escrow_status,
        'release_txn_num': release_txn_num,
        'transaction_name': transaction_name,
        'from_account': from_account,
        'to_account': to_account,
        'remote_end_response': remote_end_response,
        'invoice_no': invoice_no,
        'decision_status': decision_status,
        'txn_type': txn_type,
        'from_account_type': from_account_type,
        'to_account_type': to_account_type,
        'charge_flag': charge_flag,
        'html_table_code': html_table_code,
        'access_info': access_info
    }

    return render(request, template, context)


@login_required
def custom_wallet_mdr_limit(request):
    title = 'Custom Wallet Limit and MDR'
    template = "custom_wallet_mdr.html"
    access_info = get_access_information(request.user.id)

    show_table_and_pre = False
    transfers_queryset = mdr_queryset = limit_queryset = transfers_daily_queryset = wallet_num = global_limit_dataframe = table = None

    access = user_profile.objects.filter(user=request.user).values_list('wallet_mdr_limit_access')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        wallet_num = request.POST.get(
            'wallet_num')  # Replace 'input_name' with the actual name of your input field in the HTML form

        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {wallet_num}')

        queries = sql.wallet_mdr_limit_and_rate_queries(wallet_num)

        mdr_query = queries['mdr_query']
        limit_query = queries['limit_query']
        transfers_query = queries['transfers_query']
        transfers_daily_query = queries['transfers_daily_query']
        global_mdr_query = queries['global_mdr_query']
        user_type_query = queries['user_type_query']

        logger.info(global_mdr_query)
        logger.info(mdr_query)
        logger.info(limit_query)
        logger.info(transfers_query)
        logger.info(transfers_daily_query)
        logger.info(user_type_query)
        logger.info('MDR query starting')

        mdr_queryset = sql_conn.run_pgsql_server(
            mdr_query,
            nobopay_core
        )

        if len(mdr_queryset) == 0:
            global_mdr_queryset = sql_conn.run_pgsql_server(
                global_mdr_query,
                nobopay_core
            )

            mdr_rate = global_mdr_queryset[0][0]
            create_date = global_mdr_queryset[0][1]
            wallet = wallet_num

            mdr_queryset = [
                (
                    wallet,
                    mdr_rate,
                    'GLOBAL_RATE_ACTIVE',
                    create_date
                )
            ]

            mdr_dataframe = pd.DataFrame(
                mdr_queryset,
                columns=[
                    'wallet',
                    'rate',
                    'is_active',
                    'create_date'
                ]
            )

        logger.info('Limit query starting')

        limit_queryset = sql_conn.run_pgsql_server(
            limit_query,
            nobopay_api
        )

        user_type_queryset = sql_conn.run_pgsql_server(
            user_type_query,
            nobopay_core
        )
        logger.info(f'User Type Queryset is: {user_type_queryset}')

        if len(user_type_queryset) != 0:
            user_type = user_type_queryset[0][1]
            global_limit_query = sql.get_global_limit(user_type)
            global_limit_queryset = sql_conn.run_pgsql_server(
                global_limit_query,
                nobopay_api
            )
            logger.info(f'Global Limit queryset is: \n{global_limit_queryset}')
            global_limit_dataframe = pd.DataFrame(
                global_limit_queryset,
                columns=[
                    "type",
                    "user_type",
                    "min_amount_per_txn",
                    "max_amount_per_txn",
                    "max_count_per_day",
                    "max_amount_per_day",
                    "max_count_per_month",
                    "max_amount_per_month",
                    "status"
                ]
            )

        limit_dataframe = pd.DataFrame(
            limit_queryset,
            columns=[
                'wallet',
                'type',
                'user_type',
                'min_amount_per_txn',
                'max_amount_per_txn',
                'max_count_per_day',
                'max_amount_per_day',
                'max_count_per_month',
                'max_amount_per_month',
                'status',
                'created_at'
            ]
        )

        logger.info(f'''
        Global limit dataframe is:
        {global_limit_dataframe}
        Limit dataframe is:
        {limit_dataframe}
        ''')

        # Fills null values in one DataFrame with non-null values from another DataFrame.
        global_limit_dataframe.set_index(['type', 'user_type'], inplace=True)
        limit_dataframe.set_index(['type', 'user_type'], inplace=True)

        # Use combine_first() to merge the dataframes
        limit_dataframe = limit_dataframe.combine_first(global_limit_dataframe)
        # Reset index if needed
        limit_dataframe.reset_index(inplace=True)

        logger.info('Transfers monthly query starting')
        transfers_queryset = sql_conn.run_pgsql_server(
            transfers_query,
            nobopay_core
        )

        transfers_dataframe = pd.DataFrame(
            transfers_queryset,
            columns=[
                'txn_type',
                'amount'
            ]
        )

        logger.info('Transfers daily query starting')
        transfers_daily_queryset = sql_conn.run_pgsql_server(
            transfers_daily_query,
            nobopay_core
        )

        transfers_daily_dataframe = pd.DataFrame(
            transfers_daily_queryset,
            columns=[
                'txn_type',
                'amount'
            ]
        )

        logger.info(mdr_queryset)
        logger.info(limit_queryset)
        logger.info(transfers_queryset)
        logger.info(transfers_daily_queryset)

        # Monthly Data
        # Assuming 'type' column in limit_dataframe and 'txn_type' column in transfers_dataframe are the columns to be merged on
        merged_monthly_df = pd.merge(transfers_dataframe, limit_dataframe, left_on='txn_type', right_on='type',
                                     how='left')
        logger.info(merged_monthly_df)
        columns_list = merged_monthly_df.columns.tolist()
        columns_to_keep = ['txn_type', 'amount', 'user_type', 'max_amount_per_month']
        merged_monthly_df = merged_monthly_df.loc[:, columns_to_keep]
        merged_monthly_df['remaining_amount'] = merged_monthly_df['max_amount_per_month'] - abs(
            merged_monthly_df['amount'])
        merged_monthly_df.fillna('Not Set', inplace=True)
        logger.info(f'Merged Monthly dataframe is: {merged_monthly_df}')
        records = merged_monthly_df[
            ['txn_type', 'user_type', 'amount', 'max_amount_per_month', 'remaining_amount']].to_records(index=False)
        transfers_queryset = list(records)

        # Daily Data
        # Assuming 'type' column in limit_dataframe and 'txn_type' column in transfers_dataframe are the columns to be merged on
        merged_daily_df = pd.merge(transfers_daily_dataframe, limit_dataframe, left_on='txn_type', right_on='type',
                                   how='left')
        logger.info(merged_daily_df)
        columns_list = merged_daily_df.columns.tolist()
        columns_to_keep = ['txn_type', 'amount', 'user_type', 'max_amount_per_day', 'max_amount_per_txn']
        merged_daily_df = merged_daily_df.loc[:, columns_to_keep]
        merged_daily_df['remaining_amount'] = merged_daily_df['max_amount_per_day'] - abs(merged_daily_df['amount'])
        merged_daily_df.fillna('Not Set', inplace=True)
        logger.info(f'Merged daily dataframe is: \n{merged_daily_df}')
        records = merged_daily_df[['txn_type', 'user_type', 'amount', 'max_amount_per_day', 'remaining_amount',
                                   'max_amount_per_txn']].to_records(index=False)
        transfers_daily_queryset = list(records)

    context = {
        'title': title,
        'wallet_num': wallet_num,
        'show_table_and_pre': show_table_and_pre,
        'mdr_queryset': mdr_queryset,
        'limit_queryset': limit_queryset,
        'transfers_queryset': transfers_queryset,
        'transfers_daily_queryset': transfers_daily_queryset,
        'access_info': access_info,
    }

    logger.info('Sending data to front end')
    return render(request, template, context)


@login_required
def wallet_statement(request):
    template = "wallet_statement.html"
    title = "Wallet Statement"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = balance = None
    date_of_birth = full_name = profile_photo = business_name = identity_status = bank_account_status = qr_code = doc_type = doc_status = doc_is_active = None
    nid_front_image = nid_front_doc_type = nid_front_status = nid_front_id_no = nid_back_image = nid_back_doc_type = nid_back_status = None
    nid_back_id_no = trade_license_image = trade_license_doc_type = trade_license_status = trade_license_id_no = SHOP_IMAGE_1_image = None
    SHOP_IMAGE_1_doc_type = SHOP_IMAGE_1_status = SHOP_IMAGE_1_id_no = None

    access = user_profile.objects.filter(user=request.user).values_list('wallet_statement_details')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        wallet_num = request.POST.get(
            'wallet_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(wallet_num) > 11:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('/wallet_statement')
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {wallet_num}')

        account_id_query = sql.get_account_id(wallet_num)
        account_id_queryset = sql_conn.run_pgsql_server(
            account_id_query,
            nobopay_core
        )

        logger.info(f'''
            Account statement Query is: {account_id_query}
            \nQueryset is {account_id_queryset}
        ''')

        if type(account_id_queryset) != str and len(account_id_queryset) != 0:
            account_id = account_id_queryset[0][0]
            wallet = account_id_queryset[0][1]
            user_type = account_id_queryset[0][2]

            profile_query = sql.get_profile_data(wallet_num)
            print(profile_query)
            profile_queryset = sql_conn.run_pgsql_server(
                profile_query['query1'],
                backend_db
            )

            profile_detail_queryset = sql_conn.run_pgsql_server(
                profile_query['query2'],
                backend_db
            )

            logger.info(f'''
                Profile table queryset is:
                {profile_queryset}
                Wallet: {profile_queryset[0][0]}
                DOB: {profile_queryset[0][1]}
                Full Name: {profile_queryset[0][2]}
                Profile Photo: {profile_queryset[0][3]}
                Business Name: {profile_queryset[0][4]}
                Identity Status: {profile_queryset[0][5]}
                Bank Account Status: {profile_queryset[0][6]}
                QR Code: {profile_queryset[0][7]}
                Doc Type: {profile_queryset[0][8]}
                Doc Status: {profile_queryset[0][9]}
                Doc Is Active: {profile_queryset[0][10]}
            ''')

            profile_details_df = pd.DataFrame(data=profile_detail_queryset, columns=[
                'TYPE',
                'IMAGE',
                'ACTIVE',
                'DOC_TYPE',
                'STATUS',
                'ID_NO'
            ])

            logger.info(f'''
                        Profile detail queryset is:
                        {profile_detail_queryset}
                        Dataframe is:
                        {profile_details_df}
                        ''')

            # wallet = profile_queryset[0][0]
            date_of_birth = profile_queryset[0][1]
            full_name = profile_queryset[0][2]
            profile_photo = profile_queryset[0][3]
            business_name = profile_queryset[0][4]
            identity_status = profile_queryset[0][5]
            bank_account_status = profile_queryset[0][6]
            qr_code = profile_queryset[0][7]
            doc_type = profile_queryset[0][8]
            doc_status = profile_queryset[0][9]
            doc_is_active = profile_queryset[0][10]

            try:
                # Query for NID_FRONT
                nid_front = profile_details_df.query("TYPE == 'NID_FRONT'")
                nid_front_image = nid_front.iloc[0, 1]
                nid_front_doc_type = nid_front.iloc[0, 3]
                nid_front_status = nid_front.iloc[0, 4]
                nid_front_id_no = nid_front.iloc[0, 5]
            except IndexError:
                # Handle the case when no rows are found for NID_FRONT
                nid_front_image = None
                nid_front_doc_type = None
                nid_front_status = None
                nid_front_id_no = None
                print("No rows found for TYPE == 'NID_FRONT'")

            try:
                # Query for NID_BACK
                nid_back = profile_details_df.query("TYPE == 'NID_BACK'")
                nid_back_image = nid_back.iloc[0, 1]
                nid_back_doc_type = nid_back.iloc[0, 3]
                nid_back_status = nid_back.iloc[0, 4]
                nid_back_id_no = nid_back.iloc[0, 5]
            except IndexError:
                # Handle the case when no rows are found for NID_BACK
                nid_back_image = None
                nid_back_doc_type = None
                nid_back_status = None
                nid_back_id_no = None
                print("No rows found for TYPE == 'NID_BACK'")

            try:
                # Query for NID_BACK
                trade_license = profile_details_df.query("TYPE == 'TRADE_LICENSE_PROFILE'")
                trade_license_image = trade_license.iloc[0, 1]
                trade_license_doc_type = trade_license.iloc[0, 3]
                trade_license_status = trade_license.iloc[0, 4]
                trade_license_id_no = trade_license.iloc[0, 5]
            except IndexError:
                # Handle the case when no rows are found for NID_BACK
                trade_license_image = None
                trade_license_doc_type = None
                trade_license_status = None
                trade_license_id_no = None
                print("No rows found for TYPE == 'TRADE_LICENSE_PROFILE'")

            try:
                # Query for NID_BACK
                SHOP_IMAGE_1 = profile_details_df.query("TYPE == 'SHOP_IMAGE_1'")
                SHOP_IMAGE_1_image = SHOP_IMAGE_1.iloc[0, 1]
                SHOP_IMAGE_1_doc_type = SHOP_IMAGE_1.iloc[0, 3]
                SHOP_IMAGE_1_status = SHOP_IMAGE_1.iloc[0, 4]
                SHOP_IMAGE_1_id_no = SHOP_IMAGE_1.iloc[0, 5]
            except IndexError:
                # Handle the case when no rows are found for NID_BACK
                SHOP_IMAGE_1_image = None
                SHOP_IMAGE_1_doc_type = None
                SHOP_IMAGE_1_status = None
                SHOP_IMAGE_1_id_no = None
                print("No rows found for TYPE == 'SHOP_IMAGE_1'")

            query = sql.get_wallet_statement(wallet_num)
            statement_queryset = sql_conn.run_pgsql_server(
                query['statement_query'],
                backend_db
            )

            balance_queryset = sql_conn.run_pgsql_server(
                query['balance_query'],
                nobopay_core
            )

            balance = balance_queryset[0][0]

            logger.info(f'''
                Wallet: {wallet}
                Statement Query is: {query['statement_query']}\n
                Queryset is: {statement_queryset}\n
                
                Balance Query is: {query['balance_query']}\n
                Balance Queryset is: {balance_queryset}\n
            ''')

            show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'wallet': wallet,
        'user_type': user_type,
        'balance': balance,
        'date_of_birth': date_of_birth,
        'full_name': full_name,
        'profile_photo': profile_photo,
        'business_name': business_name,
        'identity_status': identity_status,
        'bank_account_status': bank_account_status,
        'qr_code': qr_code,
        'doc_type': doc_type,
        'doc_status': doc_status,
        'doc_is_active': doc_is_active,
        'nid_front_image': nid_front_image,
        'nid_front_doc_type': nid_front_doc_type,
        'nid_front_status': nid_front_status,
        'nid_front_id_no': nid_front_id_no,
        'nid_back_image': nid_back_image,
        'nid_back_doc_type': nid_back_doc_type,
        'nid_back_status': nid_back_status,
        'nid_back_id_no': nid_back_id_no,
        'trade_license_image': trade_license_image,
        'trade_license_doc_type': trade_license_doc_type,
        'trade_license_status': trade_license_status,
        'trade_license_id_no': trade_license_id_no,
        'SHOP_IMAGE_1_image': SHOP_IMAGE_1_image,
        'SHOP_IMAGE_1_doc_type': SHOP_IMAGE_1_doc_type,
        'SHOP_IMAGE_1_status': SHOP_IMAGE_1_status,
        'SHOP_IMAGE_1_id_no': SHOP_IMAGE_1_id_no
    }

    return render(request, template, context)


@login_required
def data_missing(request):
    template = 'data_missing.html'
    title = 'Data Missing TK'

    show_table_and_pre = queryset = html_table = None

    access = user_profile.objects.filter(user=request.user).values_list('tk_data_missing')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')
    tk_mobile_number=None
    customer_need=None
    form = data_missing_form(request.POST)
    if form.is_valid():
        tk_mobile_number = form.cleaned_data['tk_mobile_number']
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        category = form.cleaned_data['OPTION_']
        customer_need = form.cleaned_data['customer_need']

        logger.info(
            f'''
                Entered Data is:
                tk_mobile_number = {tk_mobile_number}
                from_date = {from_date}
                to_date = {to_date}
                category = {category}
                customer_need = {customer_need}
            '''
        )

        get_user_id_query = sql.get_tallykhatayuser_id(tk_mobile_number)
        get_user_id_queryset = sql_conn.run_pgsql_server(get_user_id_query, tk_db)

        if type(get_user_id_queryset) == list:
            if len(get_user_id_queryset) != 0:
                user_id = get_user_id_queryset[0][3]
                print(f'User id is: {user_id}')
            else:
                messages.error(request, 'TK mobile not found in Database')
                return redirect('data_missing')
        else:
            messages.error(request, 'Error connecting to DB')
            return redirect('data_missing')

        query = sql.data_missing(user_id, from_date, to_date, category, customer_need)
        logger.info(f'Query is: {query}')
        print(query)
        if query == False:
            messages.error(request, 'Query not specified for this scenario')
            return redirect('data_missing')

        queryset = sql_conn.run_pgsql_server(query, tk_db)
        logger.info(queryset)

        if type(queryset) != list:
            messages.error(request, 'Error connecting to Database')
            return redirect('data_missing')
        if len(queryset) == 0:
            messages.error(request, 'Data not found')
            return redirect('data_missing')

        if category == 'FROM_JOURNAL' and customer_need == 'TRANSACTION_LIST':
            header = [
                "AMOUNT",
                "AMOUNT_RECEIVED",
                "TXN_DATE",
                "DESCRIPTION",
                "MOBILE_NO",
                "ADDED_CUSTOMER_MOBILE",
                "CUSTOMER_NAME",
                "TXN_TYPE"
            ]
        elif category == 'FROM_JOURNAL' and customer_need == 'CUSTOMER_LIST':
            header = [
                "DATE",
                "NAME",
                "CONTACT",
                "TYPE",
                "PABO",
                "DEBO"
            ]
        elif category == 'FROM_HISTORY' and customer_need == 'CUSTOMER_LIST':
            header = [
                "DATE",
                "NAME",
                "CONTACT",
                "TYPE",
                "PABO",
                "DEBO"
            ]
        elif category == 'FROM_HISTORY' and customer_need == 'TRANSACTION_LIST':
            header = [
                "AMOUNT",
                "AMOUNT_RECEIVED",
                "TXN_DATE",
                "DESCRIPTION",
                "MOBILE_NO",
                "ADDED_CUSTOMER_MOBILE",
                "CUSTOMER_NAME",
                "TXN_TYPE"
            ]
        else:
            messages.error(request, f'Table heading not specified')
            return redirect('data_missing')

        html_table = generate_html_table(header, queryset)
        show_table_and_pre = True
    else:
        form = data_missing_form()

    context = {
        'title': title,
        'template': template,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'form': form,
        'html_table': html_table,
        'profile': tk_mobile_number,
        'customer_need': customer_need
    }

    return render(request, template, context)


@login_required
def service_health_check(request):
    template = 'service_health_check.html'
    title = 'Service Health Check'
    show_table_and_pre = queryset = html_table = day_chart_image = month_chart_image = daily_bar_chart_image = daily_status_pie_image = daily_description_pie_image = None
    monthly_bar_chart_image = monthly_status_pie_image = monthly_description_pie_image = None
    form = service_health_check_form(request.POST)
    access = user_profile.objects.filter(user=request.user).values_list('service_health_check')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if form.is_valid():
        service_name = form.cleaned_data['service']
        partner_name = form.cleaned_data['partner_name']

        logger.info(f'User selected service name is: {service_name} and partner name is: {partner_name}')

        if service_name == 'MOBILE_RECHARGE' and partner_name in ('GP', 'ROBI', 'AIRTEL', 'TT', 'BL'):
            query = sql.service_health_query(service_name, partner_name)
            # print (f'Query is: {query}')
            queryset = sql_conn.run_pgsql_server(query, topup)
            # print(queryset)

            analysis_query = sql.service_health_check_report(service_name, partner_name)
            # print(f'Query is: {analysis_query}')
            day_query = analysis_query['day_query']
            month_query = analysis_query['month_query']
            day_queryset = sql_conn.run_pgsql_server(day_query, topup)
            month_queryset = sql_conn.run_pgsql_server(month_query, topup)
            print(f'Day query is: {day_query} \n\n and Month Queryset is: {month_query}')
            print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')

            if type(queryset) == list and len(queryset) != 0:
                html_table = generate_html_table(
                    headers=[
                        'CREATE_DATE',
                        'TXN_ID',
                        'AMOUNT',
                        'STATUS',
                        'MOBILE_OPERATOR',
                        'VENDOR_NAME',
                        'DESCRIPTION'
                    ], data=queryset
                )
                show_table_and_pre = True
                # print(html_table)

            if (type(day_queryset) == list and type(month_queryset) == list) and (
                    len(day_queryset) != 0 and len(month_queryset) != 0):
                print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')
                day_df = pd.DataFrame(day_queryset, columns=[
                    "HOUR",
                    "MOBILE_OPERATOR",
                    "STATUS",
                    "DESCRIPTION",
                    "COUNT",
                    "TOTAL_AMOUNT"
                ])

                print(day_df.columns)
                month_df = pd.DataFrame(month_queryset, columns=[
                    "DAY",
                    "MOBILE_OPERATOR",
                    "STATUS",
                    "DESCRIPTION",
                    "COUNT",
                    "TOTAL_AMOUNT"
                ])
                print(month_df.columns)
                print(f'''
                Day DF: \n {day_df}\n\n
                Month DF: \n {month_df}
                ''')

                print('Starting day image')
                daily_bar_chart_image, daily_status_pie_image, daily_description_pie_image = func.create_service_report(
                    service_name,
                    day_df,
                    'DAILY',
                    partner_name
                )
                print('Starting month image')
                monthly_bar_chart_image, monthly_status_pie_image, monthly_description_pie_image = func.create_service_report(
                    service_name,
                    month_df,
                    'MONTHLY',
                    partner_name
                )

                print(f'''
                    Day status pie image is: \n\n
                    Month chart pie image is: \n\n
                ''')
        elif service_name == 'MONEY_IN' and partner_name in ('NAGAD'):
            query = sql.service_health_query(service_name, partner_name)
            print(f'Query is: {query}')
            queryset = sql_conn.run_pgsql_server(query, nobopay_payment_gw)
            print(queryset)
            analysis_query = sql.service_health_check_report(service_name, partner_name)
            print(f'Analysis query is: {analysis_query}')
            if analysis_query != False:
                # print(f'Query is: {analysis_query}')
                day_query = analysis_query['day_query']
                month_query = analysis_query['month_query']
                day_queryset = sql_conn.run_pgsql_server(day_query, nobopay_payment_gw)
                month_queryset = sql_conn.run_pgsql_server(month_query, nobopay_payment_gw)
                print(f'Day query is: {day_query} \n\n and Month Queryset is: {month_query}')
                print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')

                if (type(day_queryset) == list and type(month_queryset) == list) and (
                        len(day_queryset) != 0 and len(month_queryset) != 0):
                    print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')
                    day_df = pd.DataFrame(day_queryset, columns=[
                        "HOUR",
                        "STATUS",
                        "COUNT",
                        "UNIQUE_USERS",
                        "TOTAL_AMOUNT"
                    ])

                    print(day_df.columns)
                    month_df = pd.DataFrame(month_queryset, columns=[
                        "DAY",
                        "STATUS",
                        "COUNT",
                        "UNIQUE_USERS",
                        "TOTAL_AMOUNT"
                    ])
                    print(month_df.columns)
                    print(f'''
                    Day DF: \n {day_df}\n\n
                    Month DF: \n {month_df}
                    ''')

                    print('Starting day image')
                    daily_bar_chart_image, daily_status_pie_image, daily_description_pie_image = func.create_service_report(
                        service_name,
                        day_df,
                        'DAILY',
                        partner_name
                    )
                    print('Starting month image')
                    monthly_bar_chart_image, monthly_status_pie_image, monthly_description_pie_image = func.create_service_report(
                        service_name,
                        month_df,
                        'MONTHLY',
                        partner_name
                    )

                    print(f'''
                        day chart image is: {day_chart_image}\n\n
                        Month chart image is: {month_chart_image}\n\n
                    ''')

            if type(queryset) == list and len(queryset) != 0:
                html_table = generate_html_table(
                    headers=[
                        "CREATE_DATE",
                        "WALLET",
                        "CLIENT_MOBILE_NO",
                        "AMOUNT",
                        "TP_TXN_NUMBER",
                        "TXN_TIME",
                        "STATUS",
                        "NAGAD_STATUS",
                        "NAGAD_STATUS_CODE",
                        "ISSUER_PAYMENT_REF_NO",
                        "ISSUER_PAYMENT_DATE",
                        "CANCEL_ISSUER_REF_NO",
                        "CANCEL_ISSUER_DATE",
                        "CREDIT_COLLECTION_ID",
                        "ORDER_ID",
                        "ORDER_DATE",
                        "PAYMENT_REFERENCE_ID"
                    ], data=queryset
                )
                show_table_and_pre = True
                # print(html_table)
        elif service_name == 'MONEY_IN' and partner_name in ('ROCKET'):
            query = sql.service_health_query(service_name, partner_name)
            print(f'Query is: {query}')
            queryset = sql_conn.run_pgsql_server(query, nobopay_payment_gw)
            print(queryset)

            analysis_query = sql.service_health_check_report(service_name, partner_name)
            print(f'Analysis query is: {analysis_query}')
            if analysis_query != False:
                print('Reached Money in rocket stage')
                day_query = analysis_query['day_query']
                month_query = analysis_query['month_query']
                day_queryset = sql_conn.run_pgsql_server(day_query, nobopay_payment_gw)
                month_queryset = sql_conn.run_pgsql_server(month_query, nobopay_payment_gw)
                print(f'Day query is: {day_query} \n\n and Month Queryset is: {month_query}')
                print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')

                if (type(day_queryset) == list and type(month_queryset) == list) and (
                        len(day_queryset) != 0 and len(month_queryset) != 0):
                    print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')
                    day_df = pd.DataFrame(day_queryset, columns=[
                        "HOUR",
                        "STATUS",
                        "COUNT",
                        "UNIQUE_USER_COUNT",
                        "TOTAL_AMOUNT"
                    ])

                    print(day_df.columns)
                    month_df = pd.DataFrame(month_queryset, columns=[
                        "DAY",
                        "STATUS",
                        "COUNT",
                        "UNIQUE_USER_COUNT",
                        "TOTAL_AMOUNT"
                    ])
                    print(month_df.columns)
                    print(f'''
                    Day DF: \n {day_df}\n\n
                    Month DF: \n {month_df}
                    ''')

                    print('Starting day image')
                    daily_bar_chart_image, daily_status_pie_image, daily_description_pie_image = func.create_service_report(
                        service_name,
                        day_df,
                        'DAILY',
                        partner_name
                    )
                    print('Starting month image')
                    monthly_bar_chart_image, monthly_status_pie_image, monthly_description_pie_image = func.create_service_report(
                        service_name,
                        month_df,
                        'MONTHLY',
                        partner_name
                    )

                    print(f'''
                        day chart image is: {day_chart_image}\n\n
                        Month chart image is: {month_chart_image}\n\n
                    ''')

            if type(queryset) == list and len(queryset) != 0:
                html_table = generate_html_table(
                    headers=[
                        "CREATE_DATE",
                        "WALLET",
                        "CARD_NAME",
                        "AMOUNT",
                        "TP_TRANSACTION_NUMBER",
                        "ROCKET_TXN_NUM",
                        "STATUS",
                        "ROCKET_STATUS",
                        "RESULT_CODE",
                        "DBBL_TXN_ID",
                        "TXN_REF_NO",
                        "DESCRIPTION",
                        "TXN_DATE"
                    ], data=queryset
                )
                show_table_and_pre = True
                # print(html_table)
        elif service_name == 'MONEY_OUT' and partner_name in ('NAGAD', 'ROCKET'):
            query = sql.service_health_query(service_name, partner_name)
            # print (f'Query is: {query}')
            queryset = sql_conn.run_pgsql_server(query, tallypay_to_fi_integration)
            # print(queryset)

            analysis_query = sql.service_health_check_report(service_name, partner_name)
            print(f'Query is: {analysis_query}')
            day_query = analysis_query['day_query']
            month_query = analysis_query['month_query']
            day_queryset = sql_conn.run_pgsql_server(day_query, tallypay_to_fi_integration)
            month_queryset = sql_conn.run_pgsql_server(month_query, tallypay_to_fi_integration)
            print(f'Day query is: {day_query} \n\n and Month query is: {month_query}')
            print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')

            if type(queryset) == list and len(queryset) != 0:
                html_table = generate_html_table(
                    headers=[
                        "CREATE_DATE",
                        "FROM_WALLET",
                        "EXTERNAL_WALLET",
                        "TALLY_PAY_TXN_ID",
                        "EXTERNAL_TXN_ID",
                        "AMOUNT",
                        "STATUS",
                        "FINANCIAL_INSTITUTE",
                        "REQUEST_ID",
                        "EXTRA_INFO"

                    ], data=queryset
                )
                show_table_and_pre = True
                # print(html_table)

            if (type(day_queryset) == list and type(month_queryset) == list) and (
                    len(day_queryset) != 0 and len(month_queryset) != 0):
                print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')
                day_df = pd.DataFrame(day_queryset, columns=[
                    "HOUR",
                    "STATUS",
                    "COUNT",
                    "SUM"
                ])

                print(day_df.columns)
                month_df = pd.DataFrame(month_queryset, columns=[
                    "DAY",
                    "STATUS",
                    "COUNT",
                    "SUM"
                ])
                # print(month_df.columns)
                # print(f'''
                # Day DF: \n {day_df}\n\n
                # Month DF: \n {month_df}
                # ''')

                print('Starting day image')
                daily_bar_chart_image, daily_status_pie_image, daily_description_pie_image = func.create_service_report(
                    service_name,
                    day_df,
                    'DAILY',
                    partner_name
                )
                print('Starting month image')
                monthly_bar_chart_image, monthly_status_pie_image, monthly_description_pie_image = func.create_service_report(
                    service_name,
                    month_df,
                    'MONTHLY',
                    partner_name
                )

                print(f'''
                    day chart image is: {day_chart_image}\n\n
                    Month chart image is: {month_chart_image}\n\n
                ''')

        elif service_name == 'CASH_OUT_TO_BANK' and partner_name in ('CBL'):
            query = sql.service_health_query(service_name, partner_name)
            print(f'Query is: {query}')
            queryset = sql_conn.run_pgsql_server(query, backend_db)
            print(queryset)

            analysis_query = sql.service_health_check_report(service_name, partner_name)
            print(f'Query is: {analysis_query}')
            day_query = analysis_query['day_query']
            month_query = analysis_query['month_query']
            day_queryset = sql_conn.run_pgsql_server(day_query, backend_db)
            month_queryset = sql_conn.run_pgsql_server(month_query, backend_db)
            print(f'Day query is: {day_query} \n\n and Month query is: {month_query}')
            print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')

            if type(queryset) == list and len(queryset) != 0:
                html_table = generate_html_table(
                    headers=[
                        "ID",
                        "WALLET_NO",
                        "ISSUE_TIME",
                        "AMOUNT",
                        "STATUS",
                        "CORE_TXN_ID",
                        "BANK_SWIFT_CODE",
                        "BANK_NAME",
                        "BRANCH_NAME"
                    ], data=queryset
                )
                show_table_and_pre = True
                print(html_table)

            if (type(day_queryset) == list and type(month_queryset) == list) and (
                    len(day_queryset) != 0 and len(month_queryset) != 0):
                print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')
                day_df = pd.DataFrame(day_queryset, columns=[
                    "HOUR",
                    "STATUS",
                    "COUNT",
                    "UNIQUE_USER",
                    "SUM"
                ])

                print(day_df.columns)
                month_df = pd.DataFrame(month_queryset, columns=[
                    "DAY",
                    "STATUS",
                    "COUNT",
                    "UNIQUE_USER",
                    "SUM"
                ])

                print('Starting day image')
                daily_bar_chart_image, daily_status_pie_image, daily_description_pie_image = func.create_service_report(
                    service_name,
                    day_df,
                    'DAILY',
                    partner_name
                )
                print('Starting month image')
                monthly_bar_chart_image, monthly_status_pie_image, monthly_description_pie_image = func.create_service_report(
                    service_name,
                    month_df,
                    'MONTHLY',
                    partner_name
                )

                print(f'''
                    day chart image is: {day_chart_image}\n\n
                    Month chart image is: {month_chart_image}\n\n
                ''')

        elif service_name == 'CASH_OUT_TO_BANK' and partner_name in ('BEFTN'):
            query = sql.service_health_query(service_name, partner_name)
            print(f'Query is: {query}')
            queryset = sql_conn.run_pgsql_server(query, backend_db)
            print(queryset)

            analysis_query = sql.service_health_check_report(service_name, partner_name)
            print(f'Query is: {analysis_query}')
            day_query = analysis_query['day_query']
            month_query = analysis_query['month_query']
            day_queryset = sql_conn.run_pgsql_server(day_query, backend_db)
            month_queryset = sql_conn.run_pgsql_server(month_query, backend_db)
            print(f'Day query is: {day_query} \n\n and Month query is: {month_query}')
            print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')

            if type(queryset) == list and len(queryset) != 0:
                html_table = generate_html_table(
                    headers=[
                        "BTR_ID",
                        "WALLET_NO",
                        "ISSUE_TIME",
                        "AMOUNT",
                        "STATUS",
                        "CORE_TXN_ID",
                        "BANK_SWIFT_CODE",
                        "BANK_NAME",
                        "BRANCH_NAME"
                    ], data=queryset
                )
                show_table_and_pre = True
                print(html_table)

            if (type(day_queryset) == list and type(month_queryset) == list) and (
                    len(day_queryset) != 0 and len(month_queryset) != 0):
                print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')
                day_df = pd.DataFrame(day_queryset, columns=[
                    "HOUR",
                    "STATUS",
                    "COUNT",
                    "UNIQUE_USER",
                    "SUM"
                ])

                print(day_df.columns)
                month_df = pd.DataFrame(month_queryset, columns=[
                    "DAY",
                    "STATUS",
                    "COUNT",
                    "UNIQUE_USER",
                    "SUM"
                ])

                print('Starting day image')
                daily_bar_chart_image, daily_status_pie_image, daily_description_pie_image = func.create_service_report(
                    service_name,
                    day_df,
                    'DAILY',
                    partner_name
                )
                print('Starting month image')
                monthly_bar_chart_image, monthly_status_pie_image, monthly_description_pie_image = func.create_service_report(
                    service_name,
                    month_df,
                    'MONTHLY',
                    partner_name
                )

                print(f'''
                    day chart image is: {day_chart_image}\n\n
                    Month chart image is: {month_chart_image}\n\n
                ''')
        elif service_name == 'CASH_OUT_TO_BANK' and partner_name in ('NPSB'):
            query = sql.service_health_query(service_name, partner_name)
            print(f'Query is: {query}')
            queryset = sql_conn.run_pgsql_server(query, tp_bank_service)

            analysis_query = sql.service_health_check_report(service_name, partner_name)
            print(f'Query is: {analysis_query}')
            # day_query = analysis_query['day_query']
            # month_query = analysis_query['month_query']
            # day_queryset = sql_conn.run_pgsql_server(day_query, tp_bank_service)
            # month_queryset = sql_conn.run_pgsql_server(month_query, tp_bank_service)
            # print(f'Day query is: {day_query} \n\n and Month query is: {month_query}')
            # print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')

            if type(queryset) == list and len(queryset) != 0:
                html_table = generate_html_table(
                    headers=[
                        "ID",
                        "WALLET_NO",
                        "CREATE_TIME",
                        "AMOUNT",
                        "STATUS",
                        "CORE_TXN_ID",
                        "REQUEST_ID",
                        "BANK_SWIFT_CODE",
                        "DESCRIPTION"
                    ], data=queryset
                )
                show_table_and_pre = True

            # if (type(day_queryset) == list and type(month_queryset) == list) and (
            #         len(day_queryset) != 0 and len(month_queryset) != 0):
            #     print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')
            #     day_df = pd.DataFrame(day_queryset, columns=[
            #         "HOUR",
            #         "STATUS",
            #         "COUNT",
            #         "UNIQUE_USER",
            #         "SUM"
            #     ])
            #
            #     print(day_df.columns)
            #     month_df = pd.DataFrame(month_queryset, columns=[
            #         "DAY",
            #         "STATUS",
            #         "COUNT",
            #         "UNIQUE_USER",
            #         "SUM"
            #     ])
            #
            #     print('Starting day image')
            #     daily_bar_chart_image, daily_status_pie_image, daily_description_pie_image = func.create_service_report(
            #         service_name,
            #         day_df,
            #         'DAILY',
            #         partner_name
            #     )
            #     print('Starting month image')
            #     monthly_bar_chart_image, monthly_status_pie_image, monthly_description_pie_image = func.create_service_report(
            #         service_name,
            #         month_df,
            #         'MONTHLY',
            #         partner_name
            #     )

                print(f'''
                           day chart image is: {day_chart_image}\n\n
                           Month chart image is: {month_chart_image}\n\n
                       ''')
        elif service_name == 'CASH_OUT_TO_BANK' and partner_name in ('VISA'):
            query = sql.service_health_query(service_name, partner_name)
            print(f'Query is: {query}')
            queryset = sql_conn.run_pgsql_server(query, tp_bank_service)
            print(queryset)

            analysis_query = sql.service_health_check_report(service_name, partner_name)
            print(f'Query is: {analysis_query}')
            # day_query = analysis_query['day_query']
            # month_query = analysis_query['month_query']
            # day_queryset = sql_conn.run_pgsql_server(day_query, tp_bank_service)
            # month_queryset = sql_conn.run_pgsql_server(month_query, tp_bank_service)
            # print(f'Day query is: {day_query} \n\n and Month query is: {month_query}')
            # print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')

            if type(queryset) == list and len(queryset) != 0:
                html_table = generate_html_table(
                    headers=[
                        "ID",
                        "WALLET_NO",
                        "CREATE_TIME",
                        "AMOUNT",
                        "STATUS",
                        "CORE_TXN_ID",
                        "REQUEST_ID",
                        "BANK_NAME",
                        "DESCRIPTION"
                    ], data=queryset
                )
                show_table_and_pre = True
                print(html_table)

            # if (type(day_queryset) == list and type(month_queryset) == list) and (
            #         len(day_queryset) != 0 and len(month_queryset) != 0):
            #     print(f'Day queryset is: {day_queryset} \n\n and Month Queryset is: {month_queryset}')
            #     day_df = pd.DataFrame(day_queryset, columns=[
            #         "HOUR",
            #         "STATUS",
            #         "COUNT",
            #         "UNIQUE_USER",
            #         "SUM"
            #     ])
            #
            #     print(day_df.columns)
            #     month_df = pd.DataFrame(month_queryset, columns=[
            #         "DAY",
            #         "STATUS",
            #         "COUNT",
            #         "UNIQUE_USER",
            #         "SUM"
            #     ])
            #
            #     print('Starting day image')
            #     daily_bar_chart_image, daily_status_pie_image, daily_description_pie_image = func.create_service_report(
            #         service_name,
            #         day_df,
            #         'DAILY',
            #         partner_name
            #     )
            #     print('Starting month image')
            #     monthly_bar_chart_image, monthly_status_pie_image, monthly_description_pie_image = func.create_service_report(
            #         service_name,
            #         month_df,
            #         'MONTHLY',
            #         partner_name
            #     )

                print(f'''
                           day chart image is: {day_chart_image}\n\n
                           Month chart image is: {month_chart_image}\n\n
                       ''')

        else:
            messages.error(request, "Invalid Service and Partner combination.")
            return redirect('service_health_check')

    context = {
        'title': title,
        'template': template,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'form': form,
        'html_table': html_table,
        # 'day_chart_image':day_chart_image,
        # 'month_chart_image':month_chart_image,
        'daily_bar_chart_image': daily_bar_chart_image,
        'daily_status_pie_image': daily_status_pie_image,
        'daily_description_pie_image': daily_description_pie_image,
        'monthly_bar_chart_image': monthly_bar_chart_image,
        'monthly_status_pie_image': monthly_status_pie_image,
        'monthly_description_pie_image': monthly_description_pie_image
        # 'queryset': queryset
    }

    return render(request, template, context)


@login_required
def check_eventapp_event(request):
    template = 'eventapp_event.html'
    title = 'Event App Event'
    show_table_and_pre = queryset = html_table = None
    form = eventapp_event_form(request.POST)
    access = user_profile.objects.filter(user=request.user).values_list('eventapp_event')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if form.is_valid():
        wallet = form.cleaned_data['wallet']
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']

        logger.info(f'Entered details are: wallet is {wallet}, from_date is {from_date}, to date is {to_date}')

        query = sql.get_tallykhatayuser_id(wallet)
        queryset = sql_conn.run_pgsql_server(query, tk_db)
        print(f'Query is: {query} and \n Queryset is: {queryset}')

        if type(queryset) == list:
            if len(queryset) != 0:
                tk_user_id = queryset[0][3]
                print(f'TK user id is: {tk_user_id}')
                query = sql.get_event_app_event(wallet, tk_user_id, from_date, to_date)
                queryset = sql_conn.run_pgsql_server(query, tallykhata_log)
                print(f'Query is {query} \n and queryset is: {queryset}')
                if type(queryset) == list:
                    if len(queryset) != 0:
                        html_table = generate_html_table(
                            headers=[
                                "CREATED_AT",
                                "LEVEL",
                                "EVENT_NAME",
                                "MESSAGE",
                                "DETAILS",
                                "USER_ID",
                                "APP_VERSION"
                            ], data=queryset
                        )
                        show_table_and_pre = True
            else:
                print('User not found')
        else:
            print('Database connection error')

    context = {
        'title': title,
        'template': template,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'form': form,
        'html_table': html_table
    }

    return render(request, template, context)


@login_required
def check_tallypay_issuer(request):
    template = 'check_tallypay_issuer.html'
    title = 'TallyPay Issuer'
    show_table_and_pre = queryset = html_table = None
    form = eventapp_event_form(request.POST)
    access = user_profile.objects.filter(user=request.user).values_list('tallypay_issuer')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if form.is_valid():
        wallet = form.cleaned_data['wallet']
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']

        logger.info(f'Entered details are: wallet is {wallet}, from_date is {from_date}, to date is {to_date}')

        merchant_id_query = sql.get_merchant_id(wallet)
        merchant_id_queryset = sql_conn.run_pgsql_server(
            merchant_id_query,
            backend_db
        )

        if type(merchant_id_queryset) == list:
            if len(merchant_id_queryset) != 0:
                print(f'''
                Merchant ID query is: {merchant_id_query}
                
                Merchant ID queryset is: {merchant_id_queryset}
                ''')

                merchant_id = merchant_id_queryset[0][1]
                if merchant_id == None:
                    print('Wallet does not have a merchant ID (no QR)')
                    messages.error(request, 'Wallet does not have a merchant ID (no QR)')
                else:
                    issuer_query = sql.tallypay_issuer_query(from_date, to_date, merchant_id)
                    issuer_queryset = sql_conn.run_pgsql_server(
                        issuer_query,
                        tallypay_issuer
                    )
                    print(f'''
                    Issuer Queryset for wallet: {wallet} for date range {from_date} to {to_date}
                    {issuer_queryset}
                    ''')

                    html_table = generate_html_table(
                        headers=[
                            "REQUEST_ID",
                            "REQUEST",
                            "RESPONSE",
                            "CREATE_DATE",
                            "UPDATE_DATE",
                            "PROCESS_TIME"
                        ], data=issuer_queryset
                    )
                    show_table_and_pre = True
            else:
                print('Wallet not found')
                messages.error(request, 'Wallet not registered in TallyPay')
        else:
            print('Database connection error. Please contact Product Engineering')
            messages.error(request, 'Database connection error. Please contact Product Engineering')

    context = {
        'title': title,
        'template': template,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'form': form,
        'html_table': html_table
    }

    return render(request, template, context)


@login_required
def check_tallypay_activity_log(request):
    template = 'tallypay_activity_log.html'
    title = 'TallyPay Activity Log'
    show_table_and_pre = queryset = html_table = None
    form = eventapp_event_form(request.POST)
    access = user_profile.objects.filter(user=request.user).values_list('tallypay_activity_log')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if form.is_valid():
        wallet = form.cleaned_data['wallet']
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']

        logger.info(f'Entered details are: wallet is {wallet}, from_date is {from_date}, to date is {to_date}')
        user_id_query = sql.get_core_user_id(wallet)
        user_id_queryset = sql_conn.run_pgsql_server(
            user_id_query,
            backend_db
        )

        print(f'User id queryset is: {user_id_queryset}')

        if type(user_id_queryset) == list:
            if len(user_id_queryset) != 0:
                user_id = user_id_queryset[0][0]
                print(f'User id for wallet {wallet} is {user_id}')
                activity_log_query = sql.tallypay_activity_log(from_date, to_date, user_id)
                activity_log_queryset = sql_conn.run_pgsql_server(
                    activity_log_query,
                    nobopay_api_gw
                )
                print(f'Activity log queryset is: {activity_log_queryset}')

                if type(activity_log_queryset) == list:
                    if len(activity_log_queryset) != 0:
                        html_table = generate_html_table(
                            headers=[
                                "USER_ID",
                                "USER_NAME",
                                "REQUEST_METHOD",
                                "URL",
                                "LONG_TEXT",
                                "RESPONSE",
                                "RESPONSE_CODE",
                                "CREATED_AT"
                            ], data=activity_log_queryset
                        )
                        show_table_and_pre = True
                    else:
                        print('No data found in activity log')
                        messages.error(request, 'No data found in activity log')
                        return redirect('/check_tallypay_activity_log')
                else:
                    print('Database connection error')
                    messages.error(request, 'Database connection error please contact Product Engineering')
                    return redirect('/check_tallypay_activity_log')
            else:
                print('Wallet not registered')
                messages.error(request, 'Wallet not registered in tallypay')
                return redirect('/check_tallypay_activity_log')
        else:
            print('Database connection error')
            messages.error(request, 'Database connection error please contact Product Engineering')
            return redirect('/check_tallypay_activity_log')

    context = {
        'title': title,
        'template': template,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'form': form,
        'html_table': html_table
    }

    return render(request, template, context)


@login_required
def check_sqr_time_out_cases(request):
    template = 'sqr_timeout.html'
    title = 'SQR Timeout'
    show_table_and_pre = queryset = html_table = None
    form = sqr_timeout_form(request.POST)
    access = user_profile.objects.filter(user=request.user).values_list('tallypay_activity_log')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if form.is_valid():
        # wallet = form.cleaned_data['wallet']
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        print(f'From date is: {from_date} and to date is: {to_date}')

        query = sql.sqr_timeout_cases(
            from_date,
            to_date
        )

        print(f'Query is: \n{query}')

        queryset = sql_conn.run_pgsql_server(
            query,
            tallypay_issuer
        )
        print(f'Queryset is: {queryset}')

        if type(queryset) == list:
            if len(queryset) != 0:
                html_table = generate_html_table(
                    headers=[
                        "REQUEST_ID",
                        "REQUEST",
                        "RESPONSE",
                        "CREATE_DATE",
                        "UPDATE_DATE"
                    ], data=queryset
                )
                print(f'HTML table is: \n{html_table}')
                show_table_and_pre = True
            else:
                messages.info('No data found')
                return redirect('/check_sqr_timeout_cases')
        else:
            messages.error('Possible Database connection error. Please contact Product Engineering')
            return redirect('/check_sqr_timeout_cases')

    context = {
        'title': title,
        'template': template,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'form': form,
        'html_table': html_table
    }

    return render(request, template, context)


@login_required
def edit_pne_log(request, id):
    row = get_object_or_404(pne_support_monitoring, id=id)

    # Retrieve user profile once
    profile = get_object_or_404(user_profile, user=request.user)
    is_product_engineering_manager = profile.is_product_engineering_manager

    print(f'Value of product engineering manager: {is_product_engineering_manager}')

    if request.method == 'POST':
        print('Reached edit post method')
        print(f'Post data is: {request.POST}')

        # Determine the appropriate form based on the user role
        if is_product_engineering_manager == 'YES':
            form = pne_log_form(request.POST, instance=row)
        else:
            form = pne_log_edit_form(request.POST, instance=row)

        if form.is_valid():
            print("Form cleaned data:", form.cleaned_data)
            updated_task = form.save()

            # Save the new update if provided
            new_update_text = form.cleaned_data.get('new_update')
            if new_update_text:
                TaskUpdate.objects.create(
                    task=updated_task,
                    update_text=new_update_text,
                    updated_by_name=f'{profile.first_name} {profile.last_name}',
                    updated_by_username=request.user.username
                )

            messages.success(request, "Task Updated successfully")
            return redirect('pne_support_log')
        else:
            print("Form errors:", form.errors)
            # Return the form with errors
            return render(request, 'edit_modal.html', {'form': form, 'row': row})

    # If GET request or form is not valid, instantiate the form
    if is_product_engineering_manager == 'YES':
        form = pne_log_form(instance=row)
    else:
        form = pne_log_edit_form(instance=row)

    context = {
        'form': form,
        'row': row  # Include row in context to use in template
    }

    return render(request, 'edit_modal.html', context)


@login_required
def delete_pne_log(request, id):
    queryset = user_profile.objects.filter(user=request.user).values_list('is_product_engineering_manager', flat=True)
    # Extract the value
    value_list = list(queryset)  # Convert queryset to a list if needed
    print(value_list)
    if value_list:
        value = value_list[0]  # Get the first value
        # print(value)  # This should print 'NO' or the relevant value
        is_product_engineering_manager = value
    else:
        is_product_engineering_manager = 'UNDEFINED'

    print(f'Product Engineering manager value: {is_product_engineering_manager}')

    if is_product_engineering_manager == 'YES':
        row = get_object_or_404(pne_support_monitoring, id=id)
        if request.method == 'POST':
            row.delete()
            messages.success(request, 'Task deleted successfully')
            return redirect('pne_support_log')
    else:
        messages.error(request, "You do not have access for task deletion")
        return redirect('pne_support_log')


@login_required
def pne_support_log(request):
    access = user_profile.objects.filter(user=request.user).values_list('pne_log', flat=True).first()
    department = user_profile.objects.filter(user=request.user).values_list('department', flat=True).first()
    access_info = get_access_information(request.user.id)

    if access != 'YES':
        messages.error(request, 'Access denied.')
        return redirect('/home')

    if department not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department}.')
        return redirect('/home')

    print('Reached pne log home page')

    profile = user_profile.objects.get(user=request.user)

    # Start with an empty queryset
    task_data_queryset = pne_support_monitoring.objects.filter(status="IN_PROGRESS")
    in_progress_count = pne_support_monitoring.objects.filter(status='IN_PROGRESS').count()
    not_assigned_count = pne_support_monitoring.objects.filter(status='NOT_ASSIGNED').count()

    if request.method == 'POST':
        # Count of IN_PROGRESS and NOT_ASSIGNED per assignee
        in_progress_count = pne_support_monitoring.objects.filter(status='IN_PROGRESS').count()
        not_assigned_count = pne_support_monitoring.objects.filter(status='NOT_ASSIGNED').count()

        if 'new_update' in request.POST:
            # Check if user has access to create a new task
            is_product_engineering_manager = user_profile.objects.filter(user=request.user).values_list(
                'is_product_engineering_manager', flat=True).first()
            if is_product_engineering_manager != 'YES':
                messages.error(request, "You do not have access for task creation")
                return redirect('pne_support_log')

            print('Reached Create method')
            form = pne_log_form(request.POST, current_user=request.user)
            if form.is_valid():
                log = form.save(commit=False)
                username = request.user.username
                log.created_by_name = f"{profile.first_name} {profile.last_name}"
                log.created_by_username = username
                log.department = f'{profile.department}'
                log.action_type = form.cleaned_data.get('action_type')
                log.subject = form.cleaned_data.get('subject')
                log.details = form.cleaned_data.get('details')
                log.save()
                messages.success(request, 'Log saved successfully')
                return redirect('pne_support_log')
        else:
            filter_form = PNELogFilterForm(request.POST)
            if filter_form.is_valid():
                # Build the filtering logic based on the filter form
                filters = Q()
                action_type = filter_form.cleaned_data.get('action_type')
                assignee = filter_form.cleaned_data.get('assignee')
                status = filter_form.cleaned_data.get('status')

                if action_type:
                    filters &= Q(action_type=action_type)
                if assignee:
                    filters &= Q(assignee__icontains=assignee)
                if status:
                    filters &= Q(status=status)

                # Apply the filters to the queryset
                task_data_queryset = pne_support_monitoring.objects.filter(filters)
    else:
        form = pne_log_form(current_user=request.user)
        filter_form = PNELogFilterForm()

    # Step 2: Extract headers and data from the queryset
    # Step 2: Populate the form for each item in task_data_queryset
    for item in task_data_queryset:
        item.form = pne_log_edit_form(instance=item)
    headers = [
        '#',
        'Created By',
        'Created By Username',
        'Action Type',
        'Subject',
        'Details'
    ]

    data = task_data_queryset.values_list(
        'id',
        'created_by_name',
        'created_by_username',
        'action_type',
        'subject',
        'details'
    )

    # Step 3: Generate the HTML table
    html_table = generate_html_table(headers, data)
    graph_form = UserSelectionForm()

    return render(request, 'pne_log_save.html', {
        'form': pne_log_form(current_user=request.user),
        'graph_form': graph_form,
        'filter_form': filter_form,
        'access_info': access_info,
        'html_table': html_table,
        'in_progress_count': in_progress_count,
        'not_assigned_count': not_assigned_count,
        'task_data_queryset': task_data_queryset
    })


@login_required
def sqr_data_download(request):
    access = user_profile.objects.filter(user=request.user).values_list('sqr_data_download')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)
    title = 'Download Wallet SQR data'

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied.')
        return redirect('/home')

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # csv_file = request.FILES['upload_csv']
            username = form.cleaned_data['upms_username']
            password = form.cleaned_data['upms_password']

            fo_token = api.get_fo_token(
                username,
                password
            )

            if fo_token.status_code == 200:
                token = json.loads(fo_token.text)
                token = token['access_token']
                print(f'Token is: {token}')
            else:
                messages.error(request,
                               'UPMS username or Password is incorrect. Otherwise please contact Product Engineering')
                return redirect('/sqr_data_download')

            sheet_id = ''
            data = google_sheet_func.get_sheet_data(sheet_id)
            print(data)
            df = pd.DataFrame(data[1:], columns=data[0])
            # Print the DataFrame
            df = df.astype(str)
            print(df)

            # Check for header
            if 'wallet' not in df.columns.str.lower():
                messages.error(request, 'The CSV file must have a header named wallet.')
                return redirect('/sqr_data_download')

            # Validate the row count
            if len(df) > 50:
                messages.error(request, 'The CSV file cannot contain more than 50 rows.')
                return redirect('/sqr_data_download')

            # Validate the rows
            if df.shape[1] != 1:
                messages.error(request, 'Each row must have exactly one column.')
                return redirect('/sqr_data_download')

            if not df['wallet'].apply(lambda x: str(x).isdigit()).all():
                messages.error(request, 'All cells in the wallet column must contain numbers.')
                return redirect('/sqr_data_download')

            if not df['wallet'].apply(lambda x: len(str(x)) == 11).all():
                messages.error(request, 'Each cell in the wallet column must contain exactly 11 digits.')
                return redirect('/sqr_data_download')

            # Convert the 'wallet' column to a list of values
            wallet_list = df['wallet'].tolist()

            # Join the list into a comma-separated string
            wallet_string = "','".join(wallet_list)
            wallet_string = f"'{wallet_string}'"

            query = sql.sqr_data_download_query(wallet_string)
            print(f'Query is: \n{query}')
            queryset = sql_conn.run_pgsql_server(
                query,
                backend_db
            )

            print(f'Queryset is: {queryset}')

            if type(queryset) != list:
                messages.error(request, 'Database Connection error. Please contact Product Engineering')
                return redirect('/sqr_data_download')

            if len(queryset) == 0:
                messages.error(request, 'No data found')
                return redirect('/sqr_data_download')

            output_df = pd.DataFrame(queryset, columns=[
                'WALLET',
                'MERCHANT_ID',
                'FULL_NAME',
                'BIZ_NAME',
                'QR_CODE'
            ])

            # Add new columns to the DataFrame with default values
            output_df['DISPLAY_NAME_BN'] = 'NOT FOUND'
            output_df['DISTRICT'] = 'NOT FOUND'
            output_df['UPAZILA'] = 'NOT FOUND'
            output_df['ADDRESS'] = 'NOT FOUND'

            print(f'Output dataframe is: \n{output_df}')

            # Process the DataFrame as needed
            print(f'Dataframe is: \n{output_df}')
            for index, rows in output_df.iterrows():
                wallet = rows['WALLET']

                print(f'---Running operation for index {index} and wallet {wallet}---')
                upms_data = api.tp_to_upms_sync(
                    wallet,
                    token
                )

                upms_data_resp = json.loads(upms_data.text)

                if upms_data.status_code == 200:
                    if 'business_display_name_bn' in upms_data_resp:
                        # business_display_name_bn = upms_data_resp['business_display_name_bn']['value']
                        output_df.at[index, 'DISPLAY_NAME_BN'] = upms_data_resp['business_display_name_bn']['value']

                    if 'business_district_tp' in upms_data_resp:
                        # business_district_tp = upms_data_resp['business_district_tp']['value']
                        output_df.at[index, 'DISTRICT'] = upms_data_resp['business_district_tp']['value']

                    if 'business_upazila_tp' in upms_data_resp:
                        # business_upazila_tp = upms_data_resp['business_upazila_tp']['value']
                        output_df.at[index, 'UPAZILA'] = upms_data_resp['business_upazila_tp']['value']

                    if 'business_address_tp' in upms_data_resp:
                        # business_address_tp = upms_data_resp['business_address_tp']['value']
                        output_df.at[index, 'ADDRESS'] = upms_data_resp['business_address_tp']['value']

            print(output_df)
            list_of_lists = output_df.values.tolist()
            print(f'list of list is: \n{list_of_lists}')

            col_names = [
                'Wallet Number',
                'Merchant ID',
                'Customer Name',
                'Business Name',
                'Business Name (Bangla)',
                'BIZ_QR(QR Code) Url from nportal',
                'Districts',
                'Thana',
                'Address'
            ]

            list_of_lists = [col_names] + list_of_lists
            sheet_name = f'Auto Add {datetime.now().strftime("%Y-%m-%d")}'

            add_sheet_result, paste_data_result = google_sheet_func.sheet_update(
                list_of_lists,
                sheet_name=sheet_name,
                sheet_id=''
            )

            messages.info(request, f'Add sheet result: {add_sheet_result}\n Paste data result: {paste_data_result}')
            return redirect('/sqr_data_download')
    else:
        form = CSVUploadForm()

    context = {
        'access_info': access_info,
        'form': form,
        'title': title
    }

    return render(request, 'wallet_sqr_data.html', context)


@login_required
def corporate_merchant_registration_view(request):
    access = user_profile.objects.filter(user=request.user).values_list('pne_log')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)
    title = 'Corporate Merchant Registration'

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied.')
        return redirect('/home')

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    print('Reached Corporate Merchant Registration page')

    profile = user_profile.objects.get(user=request.user)
    task_data_queryset = corporate_merchant_registration.objects.all().order_by('-id')

    if request.method == 'POST':
        print('Reached Create method')
        form = corporate_merchant_registration_form(request.POST, request.FILES)
        if form.is_valid():
            username = request.user.username
            print(f'User name is: {username}')
            profile = user_profile.objects.get(user=request.user)
            created_by_name = f"{profile.first_name} {profile.last_name}"
            csv_file = form.cleaned_data['upload_csv']

            # Ensure the file is a CSV
            if not csv_file.name.endswith('.csv'):
                messages.success(request, 'Uploaded file is not a CSV file')
                return redirect('corporate_merchant_registration')

            try:
                # Decode the file and read it into a DataFrame
                decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
                df = pd.read_csv(decoded_file, dtype=str)

                # Print the DataFrame or process it as needed
                print(df)
                for _, row in df.iterrows():
                    corporate_merchant_registration.objects.create(
                        wallet=row['Wallet Number'],
                        qr_sticker_name=row['QR Sticker Name (for stand/sticker/banner)'],
                        qr_display_name=row['QR Display Name (Upon Scan)'],
                        business_type=row['Business Type'],
                        account_manager_nid_number=row["Account Manager's NID Number"],
                        account_manager_dob=row["Account Manager's DOB (as per NID)"],
                        account_manager_face_photo=row["Account Manager's Photo"],
                        account_manager_nid_photo_front=row["Account Manager's NID Copy"],
                        account_manager_nid_photo_back=row["Account Manager's NID Copy"],
                        created_by_name=created_by_name  # or any other value you want to set
                    )
                messages.success(request, 'CSV file successfully processed')
                return redirect('corporate_merchant_registration')

            except Exception as e:
                messages.error(request, f'Error processing CSV file: {e}')
                return redirect('corporate_merchant_registration')
        else:
            print(form.errors)
    else:
        print('Reached else')
        form = corporate_merchant_registration_form()

    # Add the form to each item in the queryset
    for task in task_data_queryset:
        # task.form = corporate_merchant_registration_form()
        task.form = edit_corporate_merchant_data_form(instance=task)

    return render(request, 'corporate_merchant_registration.html', {
        'title': title,
        'form': form,
        'access_info': access_info,
        'task_data_queryset': task_data_queryset
    })


@login_required
def corporate_merchant_delete_entry(request, pk):
    row = get_object_or_404(corporate_merchant_registration, pk=pk)
    if request.method == 'POST':
        row.delete()
        messages.success(request, 'Task deleted successfully')
        return redirect('corporate_merchant_registration')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('corporate_merchant_registration')


@login_required
def corporate_merchant_edit_entry(request, pk):
    row = get_object_or_404(corporate_merchant_registration, pk=pk)

    print('Reached Corporate Merchant edit method')
    if request.method == 'POST':
        print('reached edit post method')
        form = edit_corporate_merchant_data_form(request.POST, instance=row)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entry updated successfully')
            return redirect('corporate_merchant_registration')
        else:
            # form = edit_corporate_merchant_data_form(instance=row)
            return render(request, 'edit_corporate_merchant_modal.html', {'form': form, 'row': row})
    else:
        form = edit_corporate_merchant_data_form(instance=row)
        # Optional: Handle other methods if necessary

    context = {
        'form': form,
        'row': row
    }

    return render(request, 'edit_corporate_merchant_modal.html', context)


@login_required
def register_corporate_merchant(request, pk):
    row = get_object_or_404(corporate_merchant_registration, pk=pk)

    if request.method == 'POST':
        print(f'''
            Wallet: {row.wallet}
            QR Sticker Name: {row.qr_sticker_name}
            QR Display Name: {row.qr_display_name}
            Business Type: {row.business_type}
            Account Manager NID Number: {row.account_manager_nid_number}
            Account Manager DOB: {row.account_manager_dob}
            Account Manager Face Photo: {row.account_manager_face_photo}
            Account Manager NID Photo Front: {row.account_manager_nid_photo_front}
            Account Manager NID Photo Back: {row.account_manager_nid_photo_back}
            Is Active: {row.is_active}
            Created Date: {row.created_date}
            Updated Date: {row.updated_date}
            Created By Name: {row.created_by_name}
            '''
              )

        if row.is_active == True:
            messages.warning(request, 'Merchant is already registered')
            return redirect('corporate_merchant_registration')

        messages.success(request, 'Registered successfully')
        return redirect('corporate_merchant_registration')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('corporate_merchant_registration')


@login_required
def search_wallet_nid(request):
    access = user_profile.objects.filter(user=request.user).values_list('check_wallet_or_nid')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied.')
        return redirect('/home')

    if department[0][0] not in ('TECHOPS', 'CUSTOMER_SUPPORT', 'BUSINESS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    title = 'Search Wallet Or NID'
    wallet = nid = pin = merchant_id = None
    show = False

    if request.method == 'POST':
        print('Reached Post method')
        form = wallet_nid_search_form(request.POST)
        if form.is_valid():
            print('Reached form validation')
            number = form.cleaned_data['wallet_or_nid']
            info_type = form.cleaned_data['data_type']
            print(f'Number is {number} and info_type is: {info_type}')

            if info_type == 'WALLET':
                query = sql.get_wallet_query(number)
                queryset = sql_conn.run_pgsql_server(
                    query,
                    backend_db
                )
                print(f'Queryset is: {queryset}')

                if type(queryset) == list:
                    if len((queryset)) != 0:
                        wallet = queryset[0][0]
                        id_no = queryset[0][1]
                        merchant_id = queryset[0][2]
                        query = sql.get_ec_data(id_no)
                        queryset = sql_conn.run_pgsql_server(
                            query,
                            nobopay_nid_crawler
                        )
                        if type(queryset) == list:
                            if len((queryset)) != 0:
                                pin = queryset[0][0]
                                nid = queryset[0][1]
                                show = True
                                context = {
                                    'access_info': access_info,
                                    'form': form,
                                    'title': title,
                                    'wallet': wallet,
                                    'nid': nid,
                                    'pin': pin,
                                    'show': show,
                                    'merchant_id': merchant_id
                                }
                                return render(request, 'wallet_or_nid_search.html', context)
                            else:
                                messages.error(request, 'NID or PIN not found')
                                return redirect('check_wallet_or_nid')
                        else:
                            messages.error(request, 'Database Connectivity Error. Please contact Product Engineering')
                            return redirect('check_wallet_or_nid')
                    else:
                        messages.error(request, 'Wallet not registered in TallyPay')
                        return redirect('check_wallet_or_nid')
                else:
                    messages.error(request, 'Database Connectivity Error. Please contact Product Engineering')
                    return redirect('check_wallet_or_nid')
            elif info_type == 'NID':
                query = sql.get_ec_data(number)
                queryset = sql_conn.run_pgsql_server(
                    query,
                    nobopay_nid_crawler
                )
                print(f'NID Queryset is: {queryset}')

                if type(queryset) == list:
                    if len((queryset)) != 0:
                        pin = queryset[0][0]
                        nid = queryset[0][1]
                        query = sql.get_wallet_from_nid(
                            nid,
                            pin
                        )
                        queryset = sql_conn.run_pgsql_server(
                            query,
                            backend_db
                        )
                        print(f'Wallet queryset is {queryset}')
                        if type(queryset) == list:
                            if len((queryset)) != 0:
                                wallet = queryset[0][0]
                                merchant_id = queryset[0][2]

                                show = True
                                context = {
                                    'access_info': access_info,
                                    'form': form,
                                    'title': title,
                                    'wallet': wallet,
                                    'nid': nid,
                                    'pin': pin,
                                    'show': show,
                                    'merchant_id': merchant_id
                                }
                                return render(request, 'wallet_or_nid_search.html', context)
                            else:
                                messages.error(request, 'NID or PIN not found')
                                return redirect('check_wallet_or_nid')
                        else:
                            messages.error(request, 'Database Connectivity Error. Please contact Product Engineering')
                            return redirect('check_wallet_or_nid')
                    else:
                        messages.error(request, 'NID/PIN not found in TallyPay database')
                        return redirect('check_wallet_or_nid')
                else:
                    messages.error(request, 'Database Connectivity Error. Please contact Product Engineering')
                    return redirect('check_wallet_or_nid')

            messages.success(request, 'Success')
            return redirect('check_wallet_or_nid')
        else:
            print(form.errors)
            # return redirect('check_wallet_or_nid')
    else:
        form = wallet_nid_search_form()

    context = {
        'access_info': access_info,
        'form': form,
        'title': title,
        'wallet': wallet,
        'nid': nid,
        'pin': pin,
        'show': show,
        'merchant_id': merchant_id
    }

    return render(request, 'wallet_or_nid_search.html', context)


@login_required
def check_remote_end_status(request):
    access = user_profile.objects.filter(user=request.user).values_list('can_check_remote_end_status')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    access_info = get_access_information(request.user.id)

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied.')
        return redirect('/home')

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    title = 'Check Remote End Transaction Status'
    response = data_format = None
    show = False

    if request.method == 'POST':
        print('Reached Post method')
        form = status_check_form(request.POST)
        if form.is_valid():
            print('Reached form validation')
            txn_num = form.cleaned_data['remote_end_transaction_number']
            service_name = form.cleaned_data['service_name']
            print(f'Transaction Number is {txn_num} and info_type is: {service_name}')

            if service_name == 'NPSB_MONEY_OUT':
                print('NPSB')
                data_format = 'language-json'
                response = api.npsb_money_out_status_check(transaction_number=txn_num)
                response = json.dumps(response.json(), indent=4)
                show = True
            elif service_name == 'ROCKET_MONEY_OUT':
                print('ROCKET')
                data_format = 'language-xml'
                response = api.money_out_to_rocket_status_check_api(trace_data=txn_num)
                response = response.text
                # Parse and prettify the XML
                dom = xml.dom.minidom.parseString(response)
                response = dom.toprettyxml()
                show = True
            elif service_name == 'NAGAD_MONEY_IN':
                print('NAGAD')
                data_format = 'language-json'
                response = api.check_order_id_status_at_nagad_api(payment_refernce_id=txn_num)
                response = json.dumps(response.json(), indent=4)
                show = True
            elif service_name == 'MOBILE_RECHARGE_PAYSTATION':
                print('MOBILE_RECHARGE_PAYSTATION')
                data_format = 'language-json'
                response = api.paystation_recharge_status_check(request_id=txn_num)
                response = json.dumps(response.json(), indent=4)
                show = True
            else:
                print('Service not integrated yet')
                messages.error(request, 'Service not integrated yet. Please contact Product Engineering')
                return redirect('remote_end_transaction_status_search')
    else:
        form = status_check_form()

    context = {
        'access_info': access_info,
        'form': form,
        'title': title,
        'show': show,
        'response': response,
        'data_format': data_format
    }

    return render(request, 'remote_end_transaction_status_search.html', context)


@login_required
def user_graph_view(request):
    print('Reached graph function')

    if request.method == 'POST':
        form = UserSelectionForm(request.POST)  # Initialize form with POST data
        if form.is_valid():  # Validate the form
            username = form.cleaned_data.get('username')
            print(f'Username is: {username}')
            try:
                print('Reached try section')
                # data = pne_support_monitoring.objects.filter(created_by_username=username).values('created_at__date','action_type').annotate(count=Count('id')).order_by('created_at__date')

                # Filter the user_profile by user and get the first_name
                user_instance = User.objects.get(username=username)

                # Get the user ID
                user_id = user_instance.id
                profile = user_profile.objects.filter(user=user_id).first()
                print(f'profile is{profile}')
                first_name = profile.first_name
                last_name = profile.last_name

                full_name = f'{first_name} {last_name}'

                print(f'first name is: {first_name}')

                data = pne_support_monitoring.objects.filter(
                    Q(created_by_username=username) | Q(assignee=first_name)
                ).values('created_at__date', 'action_type').annotate(count=Count('id')).order_by('created_at__date')

                print(f'Data is: {data}')
                # Prepare data for Plotly
                graph_data = {
                    'x': [],
                    'traces': []
                }
                action_types = pne_support_monitoring.objects.values_list('action_type', flat=True).distinct()
                dates = sorted(set(item['created_at__date'] for item in data))
                graph_data['x'] = dates

                for action_type in action_types:
                    trace = {
                        'name': action_type,
                        'type': 'bar',
                        'x': [],
                        'y': []
                    }
                    for date in dates:
                        count = next((item['count'] for item in data if
                                      item['created_at__date'] == date and item['action_type'] == action_type), 0)
                        trace['x'].append(date)
                        trace['y'].append(count)
                    graph_data['traces'].append(trace)

                print(f'Graph data is: {graph_data}')

                graph_data = {
                    'x': [date.isoformat() for date in graph_data['x']],  # Convert dates to ISO format strings
                    'traces': [
                        {
                            'name': trace['name'],
                            'type': 'bar',
                            'x': [date.isoformat() for date in trace['x']],  # Convert dates to ISO format strings
                            'y': trace['y']
                        }
                        for trace in graph_data['traces']
                    ]
                }

                print(f'Graph data is: {graph_data}')

                # Second Graph:
                # Second Graph:
                data = pne_support_monitoring.objects.filter(
                    Q(created_by_username=username) | Q(assignee=first_name)
                ).values('action_type', 'status').annotate(count=Count('id')).order_by('id')

                print(f'Data is: {data}')

                # Prepare data for Plotly
                graph_data_2 = {
                    'x': [],
                    'traces': []
                }

                # Get unique action types and statuses from data
                action_types = sorted(set(item['action_type'] for item in data))
                statuses = sorted(set(item['status'] for item in data))

                graph_data_2['x'] = statuses

                for action_type in action_types:
                    trace = {
                        'name': action_type,
                        'type': 'bar',
                        'x': [],
                        'y': []
                    }
                    for status in statuses:
                        count = next((item['count'] for item in data if
                                      item['status'] == status and item['action_type'] == action_type), 0)
                        trace['x'].append(status)
                        trace['y'].append(count)
                    graph_data_2['traces'].append(trace)

                print(f'Graph data2 is: {graph_data_2}')

                return JsonResponse(
                    {
                        'graph': graph_data,
                        'graph2': graph_data_2,
                        'full_name': full_name
                    })

            except Exception as e:
                print(f"Error while processing data: {e}")
                return JsonResponse({'error': 'There was an error processing the data.'}, status=500)
        else:
            print(f'Form errors: {form.errors}')  # Print form errors
            print('Form is not valid')
            return JsonResponse({'error': 'Invalid form data.'}, status=400)
    else:
        form = UserSelectionForm()  # Initialize form for GET request

    return render(request, 'pne_log_save.html', {'form': form})


@login_required
def customer_care_view(request):
    template = "customer_care_view.html"
    title = "Customer Support"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = None

    SHOP_IMAGE_1_doc_type = SHOP_IMAGE_1_status = SHOP_IMAGE_1_id_no = None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        wallet_num = request.POST.get('wallet_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(wallet_num) > 11:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('/customer_care_view')

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'wallet': wallet,
        'user_type': user_type,
    }

    return render(request, template, context)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@login_required
def wallet_details(request):
    template = "wallet_details.html"
    title = "Wallet Details"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet = user_type = balance = None
    bank_account_queryset = mfs_queryset = None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        wallet_num = request.POST.get(
            'wallet_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(wallet_num) > 11:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('/wallet_statement')
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {wallet_num}')

        profile_query = sql.get_wallet_details(wallet_num)
        print(profile_query)
        bank_account_queryset = sql_conn.run_pgsql_server(
            profile_query['query2'],
            backend_db
        )
        print(f'Bank account Queryset is: {bank_account_queryset}')

        mfs_queryset = sql_conn.run_pgsql_server(
            profile_query['query1'],
            backend_db
        )
        print(f'MFS account Queryset is: {mfs_queryset}')

        # show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'bank_account_queryset': bank_account_queryset,
        'mfs_queryset': mfs_queryset,
        'wallet': wallet,
    }

    return render(request, template, context)


@login_required
def selfie_matching_score(request):
    template = "selfie_matching_score.html"
    title = "Selfie & NID photo matching score"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = balance = None
    SHOP_IMAGE_1_doc_type = SHOP_IMAGE_1_status = SHOP_IMAGE_1_id_no = None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        wallet_num = request.POST.get(
            'selfie_matching_score')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(wallet_num) > 11:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('/customer_care_view')
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {wallet_num}')

        query = sql.selfie_matching_score(wallet_num)
        queryset = sql_conn.run_pgsql_server(
            query,
            nobopay_nid_gw
        )

        logger.info(f'''
            Wallet: {wallet}
            Statement Query is: {query}\n
            Queryset is: {selfie_matching_score}\n
        ''')
        if type(queryset) == list and len(queryset) != 0:
            heading = [
                "CREATE_DATE",
                "PROFILE PHOTO MATCHING SCORE"
            ]

            html_table_code = generate_html_table(heading, queryset)

            print(f'HTML Code is: {html_table_code}')
        else:
            html_table_code = f'''
                <p>No component or request table data found</p>
            '''

        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': selfie_matching_score,
        'wallet': wallet,
        'html_table_code': html_table_code,
    }

    return render(request, template, context)


@login_required
def transaction_info(request):
    template = "transaction_info.html"
    title = "Transaction INFO"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        wallet_num = request.POST.get(
            'wallet_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(wallet_num) > 11:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('transaction_info')
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {wallet_num}')

        query = sql.transaction_info(wallet_num)
        statement_queryset = sql_conn.run_pgsql_server(
            query,
            backend_db
        )

        logger.info(f'''
            Wallet: {wallet}
            Statement Query is: {query}\n
            Queryset is: {statement_queryset}\n
        ''')

        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'wallet': wallet,
        'user_type': user_type,
    }
    return render(request, template, context)


@login_required
def recharge_package_update(request):
    template = "recharge_package_update.html"
    title = "RECHARGE PACKAGE UPDATE"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False

    access = user_profile.objects.filter(user=request.user).values_list('wallet_statement_details')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        pass

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
    }
    return render(request, template, context)
    pass




@login_required
def merchant_id(request):
    template = "merchant_id.html"
    title = "Merchant Details"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        wallet_num = request.POST.get(
            'merchant_id')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(wallet_num) > 16:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('merchant_id')
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {wallet_num}')

        query = sql.merchant_id(wallet_num)
        statement_queryset = sql_conn.run_pgsql_server(
            query,
            backend_db
        )

        logger.info(f'''
            Wallet: {wallet}
            Statement Query is: {query}\n
            Queryset is: {statement_queryset}\n
        ''')

        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'wallet': wallet,
        'user_type': user_type,
    }
    return render(request, template, context)


from django.shortcuts import render, redirect
from .models import WalletTransactionType
from .forms import WalletTransactionForm


@login_required
def limit_email_generator(request):
    template = "limit_email_generator.html"
    title = "Merchant Details"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = None

    access = user_profile.objects.filter(user=request.user).values_list('wallet_statement_details')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == "POST":
        wallet = request.POST.get("wallet")  # Get wallet

        transaction_types = request.POST.getlist("types[]")  # Get selected types
        selected_transactions = []

        for txn_type in transaction_types:
            selected_transactions.append({
                "type": txn_type,
                "min_amount_per_txn": request.POST.get(f"{txn_type}_min_amount_per_txn"),
                "max_amount_per_txn": request.POST.get(f"{txn_type}_max_amount_per_txn"),
                "max_count_per_day": request.POST.get(f"{txn_type}_max_count_per_day"),
                "max_amount_per_day": request.POST.get(f"{txn_type}_max_amount_per_day"),
                "max_count_per_month": request.POST.get(f"{txn_type}_max_count_per_month"),
                "max_amount_per_month": request.POST.get(f"{txn_type}_max_amount_per_month")
            })

        print("Wallet:", wallet)
        print("Selected Transactions:", selected_transactions)
        if len(selected_transactions)!=0:
            for item in selected_transactions:
                payload={}
                transation_type=item["type"]
                if transation_type!="":
                    payload["type"]=transation_type
                    payload["wallet"]=f"{wallet}"
                print(transation_type)
                min_amount_per_txn=item["min_amount_per_txn"]
                if min_amount_per_txn!="":
                    payload["min_amount_per_txn"]=int(min_amount_per_txn)
                    print(min_amount_per_txn)
                max_amount_per_txn=item["max_amount_per_txn"]
                if max_amount_per_txn!="":
                    payload["max_amount_per_txn"]=int(max_amount_per_txn)
                    print(max_amount_per_txn)
                max_count_per_day=item["max_count_per_day"]
                if max_count_per_day!="":
                    payload["max_count_per_day"]=int(max_count_per_day)
                    print(max_count_per_day)
                max_amount_per_day = item["max_amount_per_day"]
                if max_amount_per_day != "":
                    payload["max_amount_per_day"] = int(max_amount_per_day)
                    print(max_count_per_day)
                max_count_per_month=item["max_count_per_month"]
                if max_count_per_month!="":
                    payload["max_count_per_month"]=int(max_count_per_month)
                    print(max_count_per_month)
                max_amount_per_month=item["max_amount_per_month"]
                if max_amount_per_month!="":
                    payload["max_amount_per_month"]=int(max_amount_per_month)
                    print(max_amount_per_month)
                print(payload)
                if len(payload)!=0:
                    api.limit_change_api(payload)

        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'wallet': wallet,
        'user_type': user_type,
    }
    return render(request, template, context)


@login_required
def block_debit(request):
    template = "block_debit.html"
    title = "Block or Unblock Debit/Credit"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = None

    access = user_profile.objects.filter(user=request.user).values_list('complience_maker')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    user = user_profile.objects.filter(user=request.user).values_list('user')[0][0]
    first_name = user_profile.objects.filter(user=request.user).values_list('first_name')[0][0]
    last_name = user_profile.objects.filter(user=request.user).values_list('last_name')[0][0]
    full_name=first_name+" "+last_name
    username = request.user
    print(username)
    email=user_profile.objects.filter(user=request.user).values_list('email')[0][0]

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == "POST":
        wallet = request.POST.get("wallet")  # Get wallet
        block_type=request.POST.get("transaction_type")
        block_unblock_type=request.POST.get("block_unblock_type")
        chatagory = request.POST.get("chatagory")
        reason=request.POST.get("reason")
        ticket_number = request.POST.get("ticket_number")
        print(chatagory)
        print(reason)

        print(block_type)
        print(wallet)
        print(user)
        print(email)
 # Replace 'your_app' with your actual app name

        TransactionPermission.objects.create(
            wallet=wallet,
            transaction_type=block_type,
            permission=block_unblock_type,  # or True if needed
            chatagory=chatagory,
            reason=reason,
            initiator_username=username,
            executor_username=None,
            initiator_fullname=full_name,
            executor_fullname=None,
            is_active=True,
            ticket_number=ticket_number
        )
        print("table updated successfully")
        messages.success(request, "Added successfully")

        # response=api.block_debit(wallet,block_type,block_unblock_type)
        # resp = json.loads(response.text)
        # if 'message' in resp:
        #     msg = resp['message']
        #     if msg in ['wallet debit txn is blocked', 'wallet debit txn is now unblocked', 'wallet credit txn is now unblocked', 'wallet credit txn is blocked']:
        #         messages.success(request, f'{response.text}')
        #     elif msg in ['wallet debit txn is already blocked', 'wallet debit txn is already unblocked', 'Debit transaction is Not Blocked', 'Credit transaction is Not Blocked']:
        #         messages.error(request, f'{msg}')




        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'wallet': wallet,
        'user_type': user_type,
    }
    return render(request, template, context)

# views.py
from django.shortcuts import render, redirect
from .models import TransactionPermission

from django.shortcuts import render, redirect
from .models import TransactionPermission
from django.contrib import messages


def permission_table(request):
    template = "permission_table.html"
    title = "COMPLIENCE EXECUTION"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = None

    access = user_profile.objects.filter(user=request.user).values_list('complience_execution')
    department = user_profile.objects.filter(user=request.user).values_list('department')
    user = user_profile.objects.filter(user=request.user).values_list('user')[0][0]
    first_name = user_profile.objects.filter(user=request.user).values_list('first_name')[0][0]
    last_name = user_profile.objects.filter(user=request.user).values_list('last_name')[0][0]
    full_name=first_name+" "+last_name
    print("full name: ", full_name)
    username = request.user
    email=user_profile.objects.filter(user=request.user).values_list('email')[0][0]

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')
    if request.method == 'POST':
        row_id = request.POST.get('row_id')
        permission = TransactionPermission.objects.filter(id=row_id, is_active=True).first()
        user = user_profile.objects.filter(user=request.user).values_list('user')
        print(f'User tuple is: {user}')
        first_name = user_profile.objects.filter(user=request.user).values_list('first_name')[0][0]
        last_name = user_profile.objects.filter(user=request.user).values_list('last_name')[0][0]
        full_name = first_name + " " + last_name
        username = str(request.user)
        print(f"executor user name:  {username} and type is: {type(username)}")
        # email = user_profile.objects.filter(user=request.user).values_list('email')[0][0]
        if permission:
            # Here you can print or process the row details
            print("Row Details:")
            wallet=permission.wallet
            print("Wallet:",wallet)
            transaction_type=permission.transaction_type
            print("Transaction Type:", transaction_type)
            block_unblock_type=permission.permission
            print("Permission:", permission)

            response=api.block_debit(wallet,transaction_type,block_unblock_type)
            resp = json.loads(response.text)
            if response.status_code == 200:
                permission.is_active = False
                permission.executor_username = username
                permission.executor_fullname = full_name
                permission.update_date = timezone.now()
                permission.save()
            if 'message' in resp:
                msg = resp['message']
                if msg in ['wallet debit txn is blocked', 'wallet debit txn is now unblocked', 'wallet credit txn is now unblocked', 'wallet credit txn is blocked']:
                    messages.success(request, f'{response.text}')
                elif msg in ['wallet debit txn is already blocked', 'wallet debit txn is already unblocked', 'Debit transaction is Not Blocked', 'Credit transaction is Not Blocked']:
                    messages.error(request, f'{msg}')

        return redirect('permission_table')

    data = TransactionPermission.objects.filter(is_active=True)
    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'wallet': wallet,
        'user_type': user_type,
        'data': data
    }
    return render(request, 'permission_table.html', context)


@login_required
def wallet_limit(request):
    template = "limit_info.html"
    title = "LIMIT INFO"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        wallet_num = request.POST.get(
            'wallet_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(wallet_num) > 11:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('limit_info')
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {wallet_num}')

        query = sql.limit_info(wallet_num)
        statement_queryset = sql_conn.run_pgsql_server(
            query,
            nobopay_api
        )

        logger.info(f'''
            Wallet: {wallet}
            Statement Query is: {query}\n
            Queryset is: {statement_queryset}\n
        ''')

        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'wallet': wallet,
        'user_type': user_type,
    }
    return render(request, template, context)

import xml.etree.ElementTree as ET
import json

@login_required
def service_enquiry(request):
    template = "service_enquiry.html"
    title = "Transaction Enquiry"
    access_info = get_access_information(request.user.id)
    api_response = None
    table_data = None
    status = None
    action=None
    txn_table_data=None

    access = user_profile.objects.filter(user=request.user).values_list('wallet_statement_details')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == "POST":
        txn_num = request.POST.get("txn_num")  # Get wallet
        transaction_type=request.POST.get("transaction_type")
        print(txn_num)
        print(transaction_type)

        if transaction_type == "visa":
            response = api.visa_enquiry(txn_num)
            print(response.text)
            api_response = response.json()  # directly parse JSON
            print(response)
        if transaction_type == "npsb":
            response = api.npsb_enquiry(txn_num)
            response = response.json()
            api_response=response["Data"][0]
            print(api_response)
            print(type)
            txnrespdata=response["Data"][0]["TxnRespData"]
            print(txnrespdata)
            print("====================================")
            txn_table_data = txnrespdata.items()
            print(txn_table_data)

        elif transaction_type == "nagad" or transaction_type == "rocket":
            response = api.nagad_rocket_enquiry(txn_num)
            print(response.text)
            api_response = response.json()  # directly parse JSON
            print(response)
            print("I am here")

        elif transaction_type == "recharge":
            response = api.recharge_enquiry(txn_num)
            try:
                root = ET.fromstring(response.text)
                api_response = {child.tag: child.text for child in root}
            except Exception:
                response = response.json()
                txnrespdata = response["data"]
                api_response = response
                txn_table_data = txnrespdata.items()
                print(txn_table_data)



        # Prepare data
        if isinstance(response, dict):
            try:
                table_data = api_response.items()
            except Exception:
                table_data = api_response
        elif isinstance(api_response, list):
            table_data = api_response[0]
            table_data = table_data.items()
            print(table_data)
            # print(table_data["actionCode"])

        else:
            try:
                table_data = api_response.items()
            except Exception:
                table_data=api_response


    context = {
        'title': title,
        'access_info': access_info,
        "api_response": api_response,
        "table_data": table_data,
        "status": status,
        "action": action,
        "txn_table_data":txn_table_data
    }

    return render(request, template, context)



@login_required
def nid_usage_log(request):
    template = "nid_usage_log.html"
    title = "NID Details"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    nid_num=wallet_num = html_table = statement_queryset = wallet = user_type = None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        nid_num = request.POST.get(
            'nid_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(nid_num) > 17:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('nid_usage_log')
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {nid_num}')

        query = sql.nid_data(nid_num)
        statement_queryset = sql_conn.run_pgsql_server(
            query,
            backend_db
        )

        logger.info(f'''
            NID: {nid_num}
            Statement Query is: {query}\n
            Queryset is: {statement_queryset}\n
        ''')

        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'nid': nid_num,
        'user_type': user_type,
    }
    return render(request, template, context)


@login_required
def wallets_against_nid(request):
    template = "wallets_against_nid.html"
    title = "Wallet against the NID Details"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    nid_num=wallet_num = html_table = statement_queryset = wallet = user_type = None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        nid_num = request.POST.get(
            'nid_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(nid_num) > 17:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('wallets_against_nid.html')
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {nid_num}')

        query = sql.wallets_against_nid(nid_num)
        statement_queryset = sql_conn.run_pgsql_server(
            query,
            backend_db
        )

        logger.info(f'''
            NID: {nid_num}
            Statement Query is: {query}\n
            Queryset is: {statement_queryset}\n
        ''')

        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'nid': nid_num,
        'user_type': user_type,
    }
    return render(request, template, context)

@login_required
def npsb_inquery(request):
    template = "npsb_inquery.html"
    title = "NPSB Transaction Enquiry"
    access_info = get_access_information(request.user.id)
    api_response = None
    table_data = None
    status = None
    action=None
    txn_table_data=None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == "POST":
        txn_num = request.POST.get("txn_num")  # Get wallet
        print(txn_num)

        response = api.npsb_enquiry(txn_num)
        if response.status_code==200:
            response = response.json()
            if response["ResponseCode"]=="000":
                api_response=response["Data"][0]
                print(api_response)
                print(type)
                txnrespdata=response["Data"][0]["TxnRespData"]
                print(txnrespdata)
                rescode=txnrespdata["resCode"]
                if rescode=="000":
                    print(txnrespdata["resCode"])
                    txnrespdata={"Transaction number":txn_num,'resCode': '000', 'resMsg': 'Successful.', "Message":'PLEASE TELL THE USER TO COLLECT BANK STATEMENT'}
                else:
                    txnrespdata = {"Transaction number":txn_num,"Message": 'PLEASE COMMUNICATE WITH PRODUCT ENGINEERING TEAM'}
            else:
                txnrespdata = {"Transaction number":txn_num,"Message": 'PLEASE COMMUNICATE WITH PRODUCT ENGINEERING TEAM'}
            print("====================================")
            txn_table_data = txnrespdata.items()
            print(txn_table_data)

        else:
            messages.error(request, 'wrong transaction number')
            return redirect('/customer_care_view')


        # Prepare data
        if isinstance(response, dict):
            try:
                table_data = api_response.items()
            except Exception:
                table_data = api_response
        elif isinstance(api_response, list):
            table_data = api_response[0]
            table_data = table_data.items()
            print(table_data)
            # print(table_data["actionCode"])

        else:
            try:
                table_data = api_response.items()
            except Exception:
                table_data=api_response


    context = {
        'title': title,
        'access_info': access_info,
        "api_response": api_response,
        # "table_data": table_data,
        "status": status,
        "action": action,
        "txn_table_data":txn_table_data
    }

    return render(request, template, context)


@login_required
def txn_details(request):
    template = "txn_details.html"
    title = "Transaction details"
    access_info = get_access_information(request.user.id)
    api_response = None
    table_data = None
    status = None
    action=None
    txn_table_data=None

    access = user_profile.objects.filter(user=request.user).values_list('customer_care_portal')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        txn_num = request.POST.get(
            'txn_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {txn_num}')

        query = sql.txn_details(txn_num)
        statement_queryset = sql_conn.run_pgsql_server(
            query,
            nobopay_core
        )

        logger.info(f'''
              txn num: {txn_num}
              Statement Query is: {query}\n
              Queryset is: {statement_queryset}\n
          ''')

        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'Txn_num': txn_num
    }
    return render(request, template, context)


@login_required
def ticket_details(request):
    template = "ticket_details.html"
    title = "Ticket Details"
    access_info = get_access_information(request.user.id)
    show_table_and_pre = False
    wallet_num = html_table = statement_queryset = wallet = user_type = None

    access = user_profile.objects.filter(user=request.user).values_list('complience_call')
    department = user_profile.objects.filter(user=request.user).values_list('department')

    if department[0][0] not in ('TECHOPS', 'BUSINESS', 'CUSTOMER_SUPPORT'):
        messages.error(request, f'Access denied for your department {department[0][0]}.')
        return redirect('/home')

    if access[0][0] != 'YES':
        messages.error(request, 'Access denied for user.')
        logger.info(f'Access denied for user. User access is {access[0][0]}')
        return redirect('/home')

    if request.method == 'POST':
        # Get the user input from the submitted form
        wallet_num = request.POST.get(
            'wallet_num')  # Replace 'input_name' with the actual name of your input field in the HTML form
        if len(wallet_num) > 11:
            messages.error(request, 'Entered number does not match pattern')
            return redirect('ticket_details')
        # print(txn_num)
        show_table_and_pre = True
        logger.info(f'Entered wallet number is: {wallet_num}')

        query = sql.ticket_details(wallet_num)
        statement_queryset = sql_conn.run_pgsql_server(
            query,
            pne_execution_log
        )

        logger.info(f'''
                Wallet: {wallet}
                Statement Query is: {query}\n
                Queryset is: {statement_queryset}\n
            ''')

        show_table_and_pre = True

    context = {
        'title': title,
        'show_table_and_pre': show_table_and_pre,
        'access_info': access_info,
        'statement_queryset': statement_queryset,
        'wallet': wallet,
        'user_type': user_type,
    }
    return render(request, template, context)
