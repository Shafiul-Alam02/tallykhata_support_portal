import ssl
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from requests.adapters import HTTPAdapter


#API - 1: The following API is used to check the status of order_id at Nagad End
def check_order_id_status_at_nagad_api(payment_refernce_id):
    url = f"https://api.mynagad.com/api/dfs/verify/payment/{payment_refernce_id}"

    payload = {}
    headers = {
        'Cookie': 'WMONID=-gjwmV6B-6Z'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response

#API - 2: The following API is used to send SMS with TallyKhata Masking using Mobireach
def send_sms_via_mobireach_api(phone_number, text):
    url = f'''https://api.mobireach.com.bd/SendTextMessage?Username=progoti_2&Password=Windows@123&From=TallyKhata&To=88{phone_number}&Message="{text}"'''

    payload = {}
    headers = {
        'Cookie': 'BIGipServerpool_api_mobireach_com_bd=!z0ohIzLznLyNWuP38fqIr7/bpSqP815qKb+lO3uvmkWidXnUvy1OxBbnHKWhDUy3UCO/jtbNaTLDg0c=; TS01ac1b51=01c9bf80bb7cd967a235dc1ec6d04bd2e790aa5b836916c63ad80afa029032bbe8d4999ad797fe3f9ced6b3fb383b4c6c74c6922a2e47d17de36c0276c968bccfed11277ac'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response


#API - 3: The following API is used to check status of transactions at CityBank for BEFTN bank cash out
#Use dates in DD-MM-YYYY format in a string only
def beftn_cbl_status_check_api(fromDate=None, toDate=None, amount=None, txnId=None, routingNo=None):
    url = "http://10.10.67.3:8280/services/wso2.np.bank.integration.City.OtherBankStatus"

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
    url = "https://dbblobftlive.dutchbanglabank.com:8003/rocketgw/api/v1/transactionInquiry"
    payload = f"""<?xml version='1.0' encoding='UTF-8'?>
    <TransactionInquiryRequest>
        <Header>
            <PartnerId>username</PartnerId>
            <Password>password</Password>
        </Header>
        <Body>
            <RefNo>{trace_data}</RefNo>
            <TxnChannel/>
            <SourceAccountNo/>
            <SourceAccountName/>
            <SourceRoutingNo/>
            <SourceBankCode/>
            <DestinationAccountNo/>
            <DestinationAccountName/>
            <DestinationRoutingNo/>
            <TransactionAmount/>
            <PartnerTransactionId/>
            <PartnerTransactionDate/>
            <PartnerCallBackUrl/>
        </Body>
    </TransactionInquiryRequest>
    """

    headers = {
        'Content-Type': 'application/xml'
    }


    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    return response

#API - 5: The following API is used to check the status of transactions at Rocket for Add Money from Rocket

def add_money_from_rocket_status_check_api(txn_id, client_ip):
    url = "https://ecom.dutchbanglabank.com/ecomws/dbblecomtxn"

    payload = f'''
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ecom="http://ecom.dbbl/">
                    <soapenv:Header/>
                    <soapenv:Body>
                      <ecom:getresultfield>
                         <userid>000599992430000</userid>
                         <pwd>2d551ba722d665d8678967af341c32e26f0b15a0</pwd>
                         <transid>{txn_id}</transid>
                         <clientip>{client_ip}</clientip>
                         <billinginfo>6</billinginfo>
                      </ecom:getresultfield>
                    </soapenv:Body>
                    </soapenv:Envelope>
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
    url = f'''http://10.10.67.10:8080/nobopay-nid-crawler/nid/internal/crawl/getNidInfo/PSL/{nid}/{dob}'''

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response




#PRAN_RFL Recharge Status check API Pran's external transaction reference number and pran's bearer token from topup_service.public.pran_auth_info
def pran_rfl_recharge(pran_txn_ref_num, bearer_token):
    bearer_token = 'Bearer ' + bearer_token
    url = "http://103.206.184.30:90/api/RechargeStatus"

    payload = 'retailer_code=PRG00009627&Trx_id='+pran_txn_ref_num
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': bearer_token
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response



#IDTP Status Check API:
# In the API response for 3:00 PM to 12:00 AM the <SettlementCycle>1</SettlementCycle> is 1
def idtp_status_check_api(current_date_time_utc_6, from_date, to_date):
    url = "https://tpaybddh.binimoy.org.bd:7001/GetTransactionsbyFI"

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
            <GetTransactionsbyFI xmlns:Binimoy="http://binimoy.gov.bd/xxx/schema/">
            <Head ver="{ver}" ts="{ts}" orgId="{orgId}" msgId="{msgId}"/>
            <Req id="{id_}" note="{note}" ts="{ts}" type="GETTRANSACTIONSBYFI"/>
            <ChannelInfo>
                <ChannelID>{channelID}</ChannelID>
            </ChannelInfo>
            <ReqInfo>
                <FIInfo>
                    <UserVID value="{userVID_value}"/>
                </FIInfo>
                <OtherInfo>
                    <FromDate>{from_date}</FromDate>
                    <ToDate>{to_date}</ToDate>
                    <PageNumber/>
                    <PageSize/>
                    <SettlementStatus>{settlementStatus}</SettlementStatus>
                    <SettlementID/>
                    <TransactionStatus>{transactionStatus}</TransactionStatus>
                    <TransactionType>{transactionType}</TransactionType>
                </OtherInfo>
            </ReqInfo>
        </GetTransactionsbyFI>
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
    url = "http://103.206.184.30:90/api/RechargeStatus"
    bearer_token = f'Bearer {bearer_token}'

    payload = f'''retailer_code=PRG00009627&Trx_id={remote_end_txn_num}'''
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': bearer_token
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)

    return response

def paystation_recharge_status_check(request_id):
    url = "http://api.shl.com.bd:8282/enquiry"

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

    #Test
    #url = "https://testapigw.nobopay.com/api/v1/external/get/token"

    #Live
    url = "https://npapigwnew.nobopay.com/api/v1/external/get/token"

    payload = json.dumps({
        "externalFi": "TALLY_FO",
        "userId": username,
        "password": password
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return response


def register_corporate_merchant_new_wallet(token, wallet, nid, dob, biz_name, displayName, merchantCategoryCode, nidFrontBase64, nidBackBase64, profileImageBase64):

    #Test
    #url = "https://testapigw.nobopay.com/api/v1/external/registration/biz-user"

    #Live
    url = "https://npapigwnew.nobopay.com/api/v1/external/registration/biz-user"

    payload = json.dumps({
        "userType": "MERCHANT_CORPORATE",
        "wallet": wallet,
        "nid": nid,
        "dateOfBirth": dob,
        "bizName": biz_name,
        "displayName": displayName,
        "merchantCategoryCode": merchantCategoryCode,
        "nidFront": nidFrontBase64,
        "nidBack": nidBackBase64,
        "profileImage": profileImageBase64
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
    url = "http://10.9.0.41:8080/nobopay-backend/api/biz/user/registration"

    payload = json.dumps({
        "userType": "MERCHANT_CORPORATE",
        "wallet": wallet,
        "nid": nid,
        "dateOfBirth": dob,
        "bizName": biz_name,
        "displayName": displayName,
        "merchantCategoryCode": merchantCategoryCode,
        "nidFront": nidFrontBase64,
        "nidBack": nidBackBase64,
        "profileImage": profileImageBase64,
        "coreUserId":user_id
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)

    return response


def corporate_merchant_attach_bank_account(token, user_id, account_name, account_number, routing_number, bank_name):
    #Test
    url = f"https://testapigw.nobopay.com/api/portal/bank/biz-user/{user_id}"

    #Live
    url = f"https://npapigwnew.nobopay.com/api/portal/bank/biz-user/{user_id}"

    payload = json.dumps({
        "routing_number": routing_number,
        "account_name": account_name,
        "account_number": account_number,
        "bank_name": bank_name
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)

    return response



def corporate_merchant_outlet_and_qr_generate(wallet, token, qr_name,officer_name,sms_mobile,send_sms,city, address):
    #Test
    #url = f"https://testapigw.nobopay.com/api/v1/external/biz/attach/outlet/{wallet}"

    #Live
    url = f"https://npapigwnew.nobopay.com/api/v1/external/biz/attach/outlet/{wallet}"

    payload = json.dumps([
        {
            "superQrName": qr_name,
            "officerName": officer_name,
            "transactionSmsMobileNo": sms_mobile,
            "sendSms": send_sms,
            "city": city,
            "address": address
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

    url = f"http://10.10.67.10:8080/nobopay-backend-new/api/qrCode/corporate/download/qr-template?wallet={wallet}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    #print(response.text)

    return response



def get_fo_token(username, password):
    url = "https://upms.tallykhata.com/api/users/login"

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

    url = f"http://10.10.67.10:7010/api/transaction/{block_unblock_type}"

    payload = json.dumps({
        "wallet_no": f"{wallet}",
        "block_type": f"{block_type}"
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

    url = f"http://10.10.67.10:7070/bank-consumer/api/v1/external/visa/inquiry/txn/{txn_num}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)
    return response


def nagad_rocket_enquiry(txn_num):
    print("I am checking status")

    url = f"http://10.10.67.10:4040/tallypay-to-fi-consumer/api/v1/external/cashout/inquiry/{txn_num}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    return response

def recharge_enquiry(txn_num):

    url = f"http://10.10.67.10:8080/topup-consumer/api/v1/external/recharge/inquiry/txn/{txn_num}"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    return response

def npsb_enquiry(txn_id):

    url = f"http://10.10.67.10:7070/bank-consumer/api/v1/external/inquiry/{txn_id}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    return response


