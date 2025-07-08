import ssl
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from requests.adapters import HTTPAdapter


#API - 1: The following API is used to check the status of order_id at Nagad End
def check_order_id_status_at_nagad_api(payment_refernce_id):
    url = f""

    payload = {}
    headers = {
        'Cookie': ''
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response

#API - 2: The following API is used to send SMS with TallyKhata Masking using Mobireach
def send_sms_via_mobireach_api(phone_number, text):
    url = f''''''

    payload = {}
    headers = {
        'Cookie': ''
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response


#API - 3: The following API is used to check status of transactions at CityBank for BEFTN bank cash out
#Use dates in DD-MM-YYYY format in a string only
def beftn_cbl_status_check_api(fromDate=None, toDate=None, amount=None, txnId=None, routingNo=None):
    url = ""

    payload = {}
    if fromDate is not None:
        payload['fromDate'] = fromDate
    if toDate is not None:
        payload['toDate'] = toDate
    if amount is not None:
        payload['amount'] = amount
    if txnId is not None:
        payload['txnId'] = txnId
    if routingNo is not None:
        payload['routingNo'] = routingNo

    headers = {
        'Content-Type': 'application/json'
    }

    payload = json.dumps(payload)

    response = requests.request("POST", url, headers=headers, data=payload)

    return response


#API - 4 The following API is used to check the status of transactions at Rocket for Money Out to Rocket
def money_out_to_rocket_status_check_api(trace_data):
    url = ""
    payload = f"""
    """

    headers = {
        'Content-Type': 'application/xml'
    }


    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    return response

#API - 5: The following API is used to check the status of transactions at Rocket for Add Money from Rocket

def add_money_from_rocket_status_check_api(txn_id, client_ip):
    url = ""

    payload = f'''
                    '''

    # headers
    headers = {
        'Content-Type': 'text/xml; charset=utf-8'
    }

    response = requests.post(url, headers=headers, data=payload)

    return response

# API - 6 NID Crawler API. Th following API is used to crawl NID from Election Commision and store in
# nobopay_nid_crawler.ec_basic_info table 10 digit NID are stored in national_id column and 17 digit ones are
# stored in PIN column. The format for DOB is yyyy-mm-dd

def nid_crawler_api(nid, dob):
    url = f''''''

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response




#PRAN_RFL Recharge Status check API Pran's external transaction reference number and pran's bearer token from topup_service.public.pran_auth_info
def pran_rfl_recharge(pran_txn_ref_num, bearer_token):
    bearer_token = 'Bearer ' + bearer_token
    url = ""

    payload = ''+pran_txn_ref_num
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': bearer_token
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response



#IDTP Status Check API:
# In the API response for 3:00 PM to 12:00 AM the <SettlementCycle>1</SettlementCycle> is 1
def idtp_status_check_api(current_date_time_utc_6, from_date, to_date):
    url = ""

    # Define the variables
    #from_date = '2023-07-23'
    #to_date = '2023-07-23'
    ver = "1.0"
    ts = current_date_time_utc_6
    orgId = "TPAYBDDH"
    msgId = "1"
    id_ = "8ENSVVR4QOS7X1UGPY7JGUV444PL9T2C3QM"
    note = "Get Transactions by FI"
    channelID = "Online"
    userVID_value = "tpaybddh@fin.binimoy"
    settlementStatus = "2"
    transactionStatus = "2"
    transactionType = "0"

    # Use triple-quotes for the f-string to create a multiline string
    payload = f"""
        """

    print(payload)

    headers = {
        'REQUEST_SOURCE':'FIAPP',
        'Content-Type': 'application/xml'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    #print(response.text)

    return response


def pran_rfl_remote_end_check(remote_end_txn_num, bearer_token):
    url = ""
    bearer_token = f'Bearer {bearer_token}'

    payload = f''''''
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': bearer_token
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)

    return response

def paystation_recharge_status_check(request_id):
    url = ""

    payload = json.dumps({
        "refer_no": request_id
    })
    headers = {
        'username': '1014',
        'password': 'n%V#zp1Y',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)

    return(response)


def get_np_api_token(username, password):



    #Live
    url = ""

    payload = json.dumps({

    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return response


def register_corporate_merchant_new_wallet(token, wallet, nid, dob, biz_name, displayName, merchantCategoryCode, nidFrontBase64, nidBackBase64, profileImageBase64):


    url = ""

    payload = json.dumps({

    })

    print(payload)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)

    return response


def register_corporate_merchant_existing_wallet(token, wallet, nid, dob, biz_name, displayName, merchantCategoryCode, nidFrontBase64, nidBackBase64, profileImageBase64, user_id):
    url = ""

    payload = json.dumps({

    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)

    return response


def corporate_merchant_attach_bank_account(token, user_id, account_name, account_number, routing_number, bank_name):

    #Live
    url = f""

    payload = json.dumps({

    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)

    return response



def corporate_merchant_outlet_and_qr_generate(wallet, token, qr_name,officer_name,sms_mobile,send_sms,city, address):

    #Live
    url = f""

    payload = json.dumps([
        {

        }
    ])
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return response



def corporate_merchant_qr_download(wallet):

    url = f""

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    #print(response.text)

    return response



def get_fo_token(username, password):
    url = ""

    payload = json.dumps({
        "username": username,
        "password": password
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)

    return response


def tp_to_upms_sync(wallet, token):
    url = f"https://upms.tallykhata.com/api/loan/tp-client-data/details?business_account_number_tp={wallet}"

    payload = ""
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    #print(response.text)

    return response


def npsb_money_out_status_check(transaction_number):
    import requests

    url = f"http://10.10.67.10:7070/bank-consumer/api/v1/external/inquiry/{transaction_number}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    #print(response.text)

    return response


def limit_change_api(payload):
    # import requests
    # import json
    #
    # url = "10.10.67.10:7010/api/transaction/limit-config/wallet"
    #
    # payload = json.dumps(payload)
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    #
    # response = requests.request("POST", url, headers=headers, data=payload)
    #
    # print(response.text)
    print(payload)

    # return response

def block_debit(wallet,block_type,block_unblock_type):
    print("reached here")
    print(wallet)
    print(block_unblock_type)
    print(block_type)

    url = f""

    payload = json.dumps({

    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print("++++++++++++++++++++")
    print(response.text)
    print("++++++++++++++++++++")
    return response


def visa_enquiry(txn_num):

    url = f""

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)
    return response


def nagad_rocket_enquiry(txn_num):
    print("I am checking status")

    url = f""

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    return response

def recharge_enquiry(txn_num):

    url = f""

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    return response

def npsb_enquiry(txn_id):

    url = f""

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    return response


