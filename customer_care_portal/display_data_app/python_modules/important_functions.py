#Important functions to perform certain backend tasks goes here

#function to switch date to format correctly as per pgsql or mysql format
import plotly.graph_objs as go
import os, io, datetime,re, json, requests,base64
from xml.etree import ElementTree
import pandas as pd
from requests.structures import CaseInsensitiveDict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def switch_dates(date):
    date=date.replace("/","-")
    final_date="'"+date[6]+date[7]+date[8]+date[9]+date[5]+date[0]+date[1]+date[2]+date[3]+date[4]+"'"
    #print(final_date)
    return(final_date)

def beftn_recon_switch_dates(date):
    date=date.replace("/","-")
    final_date='"'+date[3]+date[4]+date[2]+date[0]+date[1]+date[5]+date[6]+date[7]+date[8]+date[9]+'"'
    #print(final_date)
    return(final_date)


def beftn_recon_fix_date(date):
    date = date.split(' ',1)[0]

    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        new_date = date[6]+date[7]+date[8]+date[9]+date[5]+date[3]+date[4]+date[5]+date[0]+date[1]
        date = datetime.datetime.strptime(new_date, '%Y-%m-%d')

    return date


def bank_wallet_or_mobile_number_set(var):
    var = "".join(var.split())
    var = var.replace(",","','")
    var = "('"+var+"')"

    return var

def bank_wallet_list(var):
    file_dir = os.getcwd()+"\media\\"+var
    file_exists = os.path.exists(file_dir)
    final_list = []
    final_string=""

    if file_exists:
        wallet_df = pd.read_excel(file_dir)
        wallet_list = wallet_df.values.tolist()

        for i, val in enumerate(wallet_list):
            #print(type(val[0]))
            x=str(val[0])

            if x[0] == "0":
                final_list.append(str(val[0]))
            else:
                final_list.append("'0"+str(val[0])+"'")
    else:
        final_list = None

    for i, val in enumerate(final_list):
        final_string = final_string + final_list[i]+","

    if final_string[len(final_string)-1] == ",":
        final_string=final_string.rstrip(final_string[-1])

    final_string = "("+final_string+")"

    if file_exists:
        os.remove(file_dir)

    #print("Final string after mod is: " + final_string)

    return final_string

def bank_wallet_json_config(CWD):
    JSON_CONFIG_FILE_PATH = '%s/%s' % (CWD, 'config.json')

    # Dictionary holding config.json values
    CONFIG_PROPERTIES = {}

    # Open config.json, parse values and store them in Dictionary
    try:
        with open(JSON_CONFIG_FILE_PATH) as data_file:
            CONFIG_PROPERTIES = json.load(data_file)
    except IOError as e:
        print(e)
        print("IOError: Unable to open config.json. Terminating execution")
        exit(1)

    purpose_of_txn = CONFIG_PROPERTIES["purposeoftxn"]

    return purpose_of_txn


def tp_wallet_unblock_set(var):
    print("TP Wallet Unblock Set function wallet list:")
    var = "".join(var.split())
    var = var.replace(",", "','")
    var = "('" + var + "')"
    print(var)

    return var


def tp_wallet_unblock_status(tp_wallet_numbers):
    s = "("
    for x in range(len(tp_wallet_numbers)):
        if x == len(tp_wallet_numbers) - 1:
            s = s + "'" + tp_wallet_numbers[x] + "')"
        else:
            s = s + "'" + tp_wallet_numbers[x] + "',"

    return s


def tp_wallet_unblock_api(wallet, token):
    url = ""
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = "Bearer " + token

    print("Bearer Token:")
    print(headers["Authorization"])

    data = '{\n' \
            '   "wallet":"'+wallet+'",\n' \
            '   "enabled":true' \
            '\n}'

    print('API Body: \n' + str(data))

    response = requests.put(url, headers=headers, data=data)     #This is the request which will be called.
    response_status = response.status_code

    #print('Request Header:') #print(response.request.headers) #print("Request Body") #print(response.request.body)
    print('Response status code:')
    print(response.status_code)
    print('Response text:')
    print(response.text)

    return response_status

def sms_sending_api_mobireach(wallet, message):
    numbers_sms = "88"+wallet
    #message = 'Hello'
    username = ''
    password = ''
    url = ""
    print(url)
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    resp = requests.get(url, headers=headers)
    print(resp.status_code)
    print(resp.text)

    return resp.status_code


def sms_sending_api_banglalink(wallet, message, ref_no):
    wallet = "88" + wallet

    url = ""

    payload = json.dumps({
        "username": "",
        "password": "",
        "apicode": "5",
        "msisdn": [
            wallet
        ],
        "countrycode": "880",
        "cli": "TallyKhata",
        "messagetype": "1",
        "message": message,
        "clienttransid": ref_no,
        "bill_msisdn": "8801404447808",
        "tran_type": "T",
        "request_type": "S",
        "rn_code": "91"
    })
    headers = {
        'Content-Type': 'application/json',
        'Cookie': ''
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return response.status_code


def get_np_portal_token(username, password):
    username = '"' + username + '",'
    password = '"' + password + '"'

    url = ""

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = '{\n"username":' + username + '\n"password":' + password + '\n}'

    #print(data)

    resp = requests.post(url, headers=headers, data=data)
    resp_dict = resp.json()
    token = resp_dict['token']

    print(resp.status_code)
    # print(resp.text)
    print('Response token is: ')
    print(token)

    return token

def beftn_reconciliation_report_api(start_date, end_date):
    url = ""

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = '{\n"fromDate":' + start_date + ',\n"toDate":' + end_date + '\n}'

    print(data)

    resp = requests.post(url, headers=headers, data=data)
    resp_status = resp.status_code
    resp_dict = resp.json()

    print(resp_status)
    #print(resp_dict)
    len_list = len(resp_dict['OtherBankTransactionStatusResponse']['return']['responseData'])

    print("Length of X is: ")
    print(len_list)

    api_result_set = []
    for x in range(len_list):
        api_result_set.append(resp_dict['OtherBankTransactionStatusResponse']['return']['responseData'][x])

    return api_result_set


def beftn_recon_status_meaning(status, txn_Flag_CBS, txn_return_flag_CBS):

    if status == 2 and txn_Flag_CBS == 1 and txn_return_flag_CBS == 1:
        final_status = '211 - FAILED'
    elif status == 1 and txn_Flag_CBS == 1 and txn_return_flag_CBS == 0:
        final_status = '110- INSTRUCTION SENT TO BEFTN NETWORK BY CBL'
    elif status == 0 and txn_Flag_CBS == 0 and txn_return_flag_CBS == 0:
        final_status = '000 - BEFTN REQUEST RECEIVED BY CBL, GL TRANSACTION NOT PROCESSED, NOT FORWARDED TO BEFTN NETWORK'
    elif status == 0 and txn_Flag_CBS == 1 and txn_return_flag_CBS == 0:
        final_status = '010 - BEFTN REQUEST RECEIVED BY CBL, GL TRANSACTION PROCESSED, NOT FORWARDED TO BEFTN NETWORK'
    else:
        final_status = 'UNKNOWN'

    return final_status

def nagad_credit_collection_status_check_api(payment_reference_id):

    url = ""+payment_reference_id
    print(url)
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"


    resp = requests.get(url, headers=headers)
    resp_dict = resp.json()

    print(resp.status_code)
    print(resp_dict)

    return resp_dict

def nagad_credit_collection_tp_decision(tp_status):
    if tp_status == 1:
        decision = 'Neither Nagad user has been debited nor TallyPay user has been credited, no action needed from us.'
    elif tp_status == 2:
        decision = 'Please check Nagad status response above. If status is success then we need to refund. If status is failed or refunded then no action needed from us.'
    elif tp_status == 3:
        decision = 'Please check Nagad status response above. If status is success then we need to refund. If status is failed or refunded then no action needed from us.'
    elif tp_status == 4:
        decision = 'Nagad user has not been debited, no action needed from us.'
    elif tp_status == 5:
        decision = 'TP Status is 5, please contact with TechOps team.'
    elif tp_status == 6:
        decision = 'Please check Nagad status response above. If status is success then we need to refund. If status is failed or refunded then no action needed from us.'
    elif tp_status == 7:
        decision = 'Nagad user has been debited and TallyPay user has been credited, hence no action needed from us.'
    elif tp_status == 8:
        decision = 'Please check Nagad status response above. If status is success then we need to refund. If status is failed or refunded then no action needed from us.'
    elif tp_status == 9:
        decision = 'Nagad user has been refunded, no action needed from us.'
    else:
        decision = 'This is a unknown reason for us please contact with TechOps team.'

    return decision

def rocket_status_check_api(transaction_id, client_ip):
    print("Rocket check status API function reached. Calling rocket API. Transaction ID: ", transaction_id, " Client IP: ", client_ip)

    url = ""

    payload = f""


    # headers
    headers = {
        'Content-Type': 'text/xml; charset=utf-8'
    }

    # POST request
    response = requests.request("POST", url, headers=headers, data=payload)
    xml_response = ElementTree.fromstring(response.content)
    #event_id = xml_response.find('.//return')
    #print(event_id)

    #print(payload)
    #print(response)
    #print(type(response))
    print(response.text)
    print(response.status_code)
    #print(xml_response)

    return response.text

def rocket_credit_collection_decision(tp_status):
    decision = " Please check Rocket response below. If status is 000 transaction is successful at Rocket End. If status is 999 Transaction failed at Rocket End."

    if tp_status == 1:
        decision = 'No action Needed'
    elif tp_status == 2:
        decision = 'Need to determine from Rocket response and TP Status. Then take action.' + decision
    elif tp_status == 3:
        decision = 'Need to determine from Rocket response and TP Status. Then take action.' + decision
    elif tp_status == 4:
        decision = 'Transaction Failed at Rocket end. No action needed from us.'
    elif tp_status == 5:
        decision = 'Need to determine from Rocket response and TP Status. Then take action.' + decision
    elif tp_status == 6:
        decision = 'Need to determine from Rocket response and TP Status. Then take action.' + decision
    elif tp_status == 7:
        decision = 'Successful transaction. No action needed from us.'
    elif tp_status == 8:
        decision = 'Need to determine from Rocket response and TP Status. Then take action.' + decision
    elif tp_status == 9:
        decision = 'Rocket user has been refunded, no action needed from us.'
    else:
        decision = 'This is a unknown reason for us please contact with TechOps team.'

    return decision

def otp_mnp_verification(amount, queryset_tk, queryset_tp):
    result = "NOT MATCHED"
    amount = int(amount)
    print(queryset_tk)
    print(queryset_tp)
    for x in range(len(queryset_tk)):
        retreived_amount_1 = int(queryset_tk[x][1])
        retreived_amount_2 = int(queryset_tk[x][2])
        print(retreived_amount_1)
        if retreived_amount_1 == amount:
            result = "MATCHED"
            print(result, " with TK")
            return result
        elif retreived_amount_2 == amount:
            result = "MATCHED"
            print(result, " with TK")
            return result

    for i in range(len(queryset_tp)):
        retreived_amount = int(queryset_tp[i][1])
        print(retreived_amount)
        if retreived_amount == amount:
            result = "MATCHED"
            print(result, " with TP")
            return result

    return result


def beftn_status_check_api(start_date, bank_txn_id):
    print(start_date)
    start_date = '"'+start_date+'"'
    bank_txn_id = '"' + bank_txn_id + '"'
    url = ""

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = '{\n"fromDate":' + start_date + ',\n"toDate":' + start_date + ',\n"txnId":' + bank_txn_id + '\n}'

    print(data)

    resp = requests.post(url, headers=headers, data=data)
    resp_status = resp.status_code
    resp_dict = resp.json()

    print(resp_status)
    print(resp_dict)
    api_result_set = resp_dict

    if resp_status != 200:
        txn_status = 'UNABLE TO CONNECT TO CBL'
        return txn_status

    status = resp_dict['OtherBankTransactionStatusResponse']['return']['responseData']['status']
    transactionFlagCBS = resp_dict['OtherBankTransactionStatusResponse']['return']['responseData']['transactionFlagCBS']
    transactionReturnFlagCBS = resp_dict['OtherBankTransactionStatusResponse']['return']['responseData']['transactionReturnFlagCBS']
    amount = resp_dict['OtherBankTransactionStatusResponse']['return']['responseData']['amount']
    bank_name = resp_dict['OtherBankTransactionStatusResponse']['return']['responseData']['bankName']
    settlement_date = resp_dict['OtherBankTransactionStatusResponse']['return']['responseData']['settlementDate']
    return_reason = resp_dict['OtherBankTransactionStatusResponse']['return']['responseData']['returnReason']
    return_date = resp_dict['OtherBankTransactionStatusResponse']['return']['responseData']['returnDate']


    print(status," ", transactionFlagCBS, " ", transactionReturnFlagCBS)

    if status==1 and transactionFlagCBS==1 and transactionReturnFlagCBS==0:
        txn_status = '110 - INSTRUCTION SENT TO BEFTN NETWORK BY CBL.'
    elif status==0 and transactionFlagCBS==0 and transactionReturnFlagCBS==0:
        txn_status = '000 - BEFTN INSTRUCTION RECEIVED BY CBL, GL TRANSACTION NOT PROCESSED, NOT FORWARDED TO BEFTN NETWORK.'
    elif status==0 and transactionFlagCBS==1 and transactionReturnFlagCBS==0:
        txn_status = '010 - BEFTN REQUEST RECEIVED BY CBL, GL TRANSACTION PROCESSED, NOT FORWARDED TO BEFTN NETWORK.'
    elif status==2 and transactionFlagCBS==1 and transactionReturnFlagCBS==1:
        txn_status = '211 - FAILED.'
    else:
        txn_status = 'CBL RESPONSE UNKNOWN.'

    print(txn_status)

    return txn_status

def nagad_cash_out_status_check(extra_info, db_request):
    queryset = db_request
    x = [(
         '91134","random":""} | Header: ,X-KM-Client-Type: PC_WEB,X-KM-Api-Version: v-0.2.0,X-KM-MC-Id: 689044455305399,X-KM-MA-Id: 660217024214684',)]
    x = x[0][0]
    print(x, "\n")

    delimiter1 = ""
    delimiter2 = ""

    idx1 = x.index(delimiter1)
    idx2 = x.index(delimiter2)

    res = ''

    for idx in range(idx1 + len(delimiter1), idx2):
        res = res + x[idx]

    # API Get Key
    payload = "{" + res + "}"

    url = ""

    headers = {

    }

    response = requests.request("POST", url, headers=headers, data=payload)
    km_api_key = response.headers['X-KM-Api-Key']

    # Status check API

    # get this from DB query
    print("\nExtra info is: ",extra_info,"\n")

    extra_info = json.loads(extra_info)


    requestDateTime = extra_info['requestDateTime']
    print(requestDateTime)
    referenceNo = extra_info['referenceNo']
    print(referenceNo)
    rechargeId = extra_info['rechargeId']
    print(rechargeId)

    url = ""+requestDateTime+"&referenceNo="+referenceNo+"&rechargeId="+rechargeId
    print("Url is: ",url)
    payload = {}
    headers = {

    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response


def cashback_disbursement_api(wallet,amount, disbursement_note):
    print('Reached cashback disbursement API for : ', wallet, " ", amount)
    url = ""

    payload = json.dumps({
        "amount": f"{amount}",
        "wallet_no": f"{wallet}",
        "offer_id": f"{disbursement_note}"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.status_code)
    print(response.text)

    status_code = response.status_code
    status = response.text
    print(type(status_code))

    status_result_set = [status_code,status]

    return status_result_set


#FUNCTION TO CHECK WALLET PATTERN AND AMOUNT FOR DISBURSEMENT
def disbursement_data_check(main_list):
    parent_list=main_list
    mobile_pattern=re.compile("(01)([0-9]{9})")
    amount_pattern=re.compile("(([0-9]+)\.?[0-9]+)|[1-9]")
    zero_pattern=re.compile("(0)+\.(0+)")
    for child_list in parent_list:
        mobile_no, amount=child_list[0],str(child_list[1])

        if not mobile_pattern.fullmatch(mobile_no):
            print("This Mobile Number "+mobile_no+" is invalid")
            return False

        if amount[0]=="0" and amount[1]!=".":
            print("This amount "+amount+" of this Mobile Number "+mobile_no+" is invalid")
            return False

        if (not amount_pattern.fullmatch(amount)) or (zero_pattern.fullmatch(amount)):
            print("This amount "+amount+" of this Mobile Number "+mobile_no+" is invalid")
            return False

    return True


def tallypay_transaction_search_external_fi_status(f1, f2, f3, f4, f5, f6):
    f1.rename(columns={'tp_transaction_number': 'transaction_number'}, inplace=True)
    f2.rename(columns={'tp_transaction_number': 'transaction_number'}, inplace=True)
    f3.rename(columns={'tp_transaction_number': 'transaction_number'}, inplace=True)
    f4.rename(columns={'tp_transaction_number': 'transaction_number'}, inplace=True)
    f5.rename(columns={'tp_transaction_number': 'transaction_number'}, inplace=True)
    f6.rename(columns={'tp_transaction_number': 'transaction_number'}, inplace=True)

    output = pd.merge(f1, f2, on="transaction_number", how="outer")
    output2 = pd.merge(f1, f3, on="transaction_number", how="outer")
    output3 = output.fillna(output2)

    output4 = pd.merge(f1, f4, on="transaction_number", how="outer")
    output4 = output3.fillna(output4)

    output5 = pd.merge(f1, f5, on="transaction_number", how="outer")
    output5 = output4.fillna(output5)

    output6 = pd.merge(f1, f6, on="transaction_number", how="outer")
    output6 = output5.fillna(output6)

    list1 = list(zip(*map(output6.get, output6)))
    return list1


def convert_to_base64(file):
    # Read the file data and encode it as base64
    return base64.b64encode(file.read()).decode('utf-8')



def create_service_report(service_name, df, report_type, partner_name):
    print('Service health check analysis section')
    pd.set_option('display.max_columns', None)  # Set to None to display all columns

    #print(df['STATUS'].dtype)

    print(f'''
    Service Name is: {service_name}
    Report type is: {report_type}
    Partner Name is: {partner_name}
    ''')

    print(f'Service Health Check Dataframe is: {df}')
    if service_name == 'MOBILE_RECHARGE' and report_type in ['DAILY', 'MONTHLY'] and partner_name in ['GP','ROBI','AIRTEL','TT','BL']:
        if 'STATUS' in df.columns:
            print('Status column present')
        else:
            # Handle the case where 'STATUS' column is missing
            print("Error: 'STATUS' column not found in DataFrame")

        # Determine the index column based on the report type
        index_column = 'HOUR' if report_type == 'DAILY' else 'DAY'

        # Aggregate data by index column and status, and sum the counts
        pivot_df = df.groupby([index_column, 'STATUS'])['COUNT'].sum().reset_index()

        # Create a list to store traces for each status
        traces = []

        # Iterate over unique statuses
        for status in pivot_df['STATUS'].unique():
            # Filter data for the current status
            status_data = pivot_df[pivot_df['STATUS'] == status]

            # Create trace for the current status
            trace = go.Bar(x=status_data[index_column], y=status_data['COUNT'], name=status)

            # Append the trace to the list
            traces.append(trace)

        # Create layout for the graph
        layout = go.Layout(
            title=f'Total Count by {"Hour" if report_type == "DAILY" else "Day"} and Status',
            xaxis=dict(title='Hour' if report_type == 'DAILY' else 'Day'),
            yaxis=dict(title='Total Count'),
            barmode='stack',  # Stacking bars on top of each other
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            height=500,
            width=700
        )

        # Create Plotly figure with multiple traces
        fig = go.Figure(data=traces, layout=layout)

        # Convert Plotly figure to HTML
        chart_image = fig.to_html(
            full_html=False,
            default_height=500,
            default_width=700
        )

        # Generate pie chart for overall distribution of STATUS
        #status_counts = df['STATUS'].value_counts()
        status_counts = df.groupby('STATUS')['COUNT'].sum()
        status_labels = status_counts.index.tolist()
        status_values = status_counts.values.tolist()

        status_pie_trace = go.Pie(labels=status_labels,
                                  values=status_values)
        status_pie_layout = go.Layout(
            title='Overall Distribution of STATUS',
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            height=500,
            width=700
        )
        status_pie_fig = go.Figure(data=[status_pie_trace], layout=status_pie_layout)
        status_pie_image = status_pie_fig.to_html(
            full_html=False,
            default_height=500,
            default_width=700
        )

        # Generate pie chart for overall distribution of DESCRIPTION
        #description_counts = df['DESCRIPTION'].value_counts()
        description_counts = df.groupby('DESCRIPTION')['COUNT'].sum()
        description_labels = description_counts.index.tolist()
        description_values = description_counts.values.tolist()

        description_pie_trace = go.Pie(
            labels=description_labels,
            values=description_values
        )
        description_pie_layout = go.Layout(
            title='Overall Distribution of DESCRIPTION',
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5),
            height=500,
            width=700
        )

        description_pie_fig = go.Figure(
            data=[description_pie_trace],
            layout=description_pie_layout
        )

        description_pie_image = description_pie_fig.to_html(
            full_html=False,
            default_height=500,
            default_width=700
        )
    elif service_name == 'MONEY_OUT' and report_type in ['DAILY', 'MONTHLY'] and partner_name in ['ROCKET','NAGAD']:
        print(f'Reached generating charts for {service_name}')
        if 'STATUS' in df.columns:
            print('Status column present')
        else:
            # Handle the case where 'STATUS' column is missing
            print("Error: 'STATUS' column not found in DataFrame")

        # Determine the index column based on the report type
        index_column = 'HOUR' if report_type == 'DAILY' else 'DAY'

        # Aggregate data by index column and status, and sum the counts
        pivot_df = df.groupby([index_column, 'STATUS'])['COUNT'].sum().reset_index()

        # Create a list to store traces for each status
        traces = []

        # Iterate over unique statuses
        for status in pivot_df['STATUS'].unique():
            # Filter data for the current status
            status_data = pivot_df[pivot_df['STATUS'] == status]

            # Create trace for the current status
            trace = go.Bar(x=status_data[index_column], y=status_data['COUNT'], name=status)

            # Append the trace to the list
            traces.append(trace)

        # Create layout for the graph
        layout = go.Layout(
            title=f'Total Count by {"Hour" if report_type == "DAILY" else "Day"} and Status',
            xaxis=dict(title='Hour' if report_type == 'DAILY' else 'Day'),
            yaxis=dict(title='Total Count'),
            barmode='stack',  # Stacking bars on top of each other
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5),
            height=500,
            width=700
        )

        # Create Plotly figure with multiple traces
        fig = go.Figure(data=traces, layout=layout)

        # Convert Plotly figure to HTML
        chart_image = fig.to_html(
            full_html=False,
            default_height=500,
            default_width=700
        )

        # Generate pie chart for overall distribution of STATUS
        # status_counts = df['STATUS'].value_counts()
        status_counts = df.groupby('STATUS')['COUNT'].sum()
        status_labels = status_counts.index.tolist()
        status_values = status_counts.values.tolist()

        status_pie_trace = go.Pie(labels=status_labels,
                                  values=status_values)
        status_pie_layout = go.Layout(
            title='Overall Distribution of STATUS',
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            height=500,
            width=700
        )
        status_pie_fig = go.Figure(data=[status_pie_trace], layout=status_pie_layout)
        status_pie_image = status_pie_fig.to_html(
            full_html=False,
            default_height=500,
            default_width=700
        )

        # Generate pie chart for overall distribution of DESCRIPTION
        # description_counts = df['DESCRIPTION'].value_counts()

        description_pie_image = None
    elif service_name == 'MONEY_IN' and report_type in ['DAILY', 'MONTHLY'] and partner_name in ['ROCKET','NAGAD']:
        print(f'Reached generating charts for {service_name}')
        if 'STATUS' in df.columns:
            print('Status column present')
        else:
            # Handle the case where 'STATUS' column is missing
            print("Error: 'STATUS' column not found in DataFrame")

        # Determine the index column based on the report type
        index_column = 'HOUR' if report_type == 'DAILY' else 'DAY'

        # Aggregate data by index column and status, and sum the counts
        pivot_df = df.groupby([index_column, 'STATUS'])['COUNT'].sum().reset_index()

        # Create a list to store traces for each status
        traces = []

        # Iterate over unique statuses
        for status in pivot_df['STATUS'].unique():
            # Filter data for the current status
            status_data = pivot_df[pivot_df['STATUS'] == status]

            # Create trace for the current status
            trace = go.Bar(x=status_data[index_column], y=status_data['COUNT'], name=status)

            # Append the trace to the list
            traces.append(trace)

        # Create layout for the graph
        layout = go.Layout(
            title=f'Total Count by {"Hour" if report_type == "DAILY" else "Day"} and Status',
            xaxis=dict(title='Hour' if report_type == 'DAILY' else 'Day'),
            yaxis=dict(title='Total Count'),
            barmode='stack',  # Stacking bars on top of each other
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            height=500,
            width=700
        )

        # Create Plotly figure with multiple traces
        fig = go.Figure(data=traces, layout=layout)

        # Convert Plotly figure to HTML
        chart_image = fig.to_html(
            full_html=False,
            default_height=500,
            default_width=700
        )

        # Generate pie chart for overall distribution of STATUS
        # status_counts = df['STATUS'].value_counts()
        status_counts = df.groupby('STATUS')['COUNT'].sum()
        status_labels = status_counts.index.tolist()
        status_values = status_counts.values.tolist()

        status_pie_trace = go.Pie(labels=status_labels,
                                  values=status_values)
        status_pie_layout = go.Layout(
            title='Overall Distribution of STATUS',
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            height=500,
            width=700
        )
        status_pie_fig = go.Figure(data=[status_pie_trace], layout=status_pie_layout)
        status_pie_image = status_pie_fig.to_html(
            full_html=False,
            default_height=500,
            default_width=700
        )

        # Generate pie chart for overall distribution of DESCRIPTION
        # description_counts = df['DESCRIPTION'].value_counts()

        description_pie_image = None
    elif service_name == 'CASH_OUT_TO_BANK' and report_type in ['DAILY', 'MONTHLY'] and partner_name in ['CBL','BEFTN']:
        print(f'Reached generating charts for {service_name}')
        if 'STATUS' in df.columns:
            print('Status column present')
        else:
            # Handle the case where 'STATUS' column is missing
            print("Error: 'STATUS' column not found in DataFrame")

        # Determine the index column based on the report type
        index_column = 'HOUR' if report_type == 'DAILY' else 'DAY'

        # Aggregate data by index column and status, and sum the counts
        pivot_df = df.groupby([index_column, 'STATUS'])['COUNT'].sum().reset_index()

        # Create a list to store traces for each status
        traces = []

        # Iterate over unique statuses
        for status in pivot_df['STATUS'].unique():
            # Filter data for the current status
            status_data = pivot_df[pivot_df['STATUS'] == status]

            # Create trace for the current status
            trace = go.Bar(x=status_data[index_column], y=status_data['COUNT'], name=status)

            # Append the trace to the list
            traces.append(trace)

        # Create layout for the graph
        layout = go.Layout(
            title=f'Total Count by {"Hour" if report_type == "DAILY" else "Day"} and Status',
            xaxis=dict(title='Hour' if report_type == 'DAILY' else 'Day'),
            yaxis=dict(title='Total Count'),
            barmode='stack',  # Stacking bars on top of each other
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5),
            height=500,
            width=700
        )

        # Create Plotly figure with multiple traces
        fig = go.Figure(data=traces, layout=layout)

        # Convert Plotly figure to HTML
        chart_image = fig.to_html(
            full_html=False,
            default_height=500,
            default_width=700
        )

        # Generate pie chart for overall distribution of STATUS
        # status_counts = df['STATUS'].value_counts()
        status_counts = df.groupby('STATUS')['COUNT'].sum()
        status_labels = status_counts.index.tolist()
        status_values = status_counts.values.tolist()

        status_pie_trace = go.Pie(labels=status_labels,
                                  values=status_values)
        status_pie_layout = go.Layout(
            title='Overall Distribution of STATUS',
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            height=500,
            width=700
        )
        status_pie_fig = go.Figure(data=[status_pie_trace], layout=status_pie_layout)
        status_pie_image = status_pie_fig.to_html(
            full_html=False,
            default_height=500,
            default_width=700
        )

        # Generate pie chart for overall distribution of DESCRIPTION
        # description_counts = df['DESCRIPTION'].value_counts()

        description_pie_image = None
    else:
        chart_image = status_pie_image = description_pie_image = None

    return chart_image, status_pie_image, description_pie_image


def convert_to_download_link(view_url):
    # Extract the file ID from the view URL
    file_id = view_url.split('/d/')[1].split('/')[0]

    # Construct the download URL
    download_url = f""

    return download_url


def download_and_convert_to_base64(service_account_file, file_id):
    """
    Downloads a file from Google Drive and converts it to a Base64-encoded string.

    Args:
        service_account_file (str): Path to the service account JSON key file.
        file_id (str): The ID of the file to download from Google Drive.

    Returns:
        str: The Base64-encoded content of the downloaded file.
    """
    # Scopes needed to access Google Drive
    SCOPES = ['']

    # Authenticate and create the service
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    # Create a request to download the file
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()

    # Download the file
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}% complete.")

    # Convert the downloaded file to Base64
    fh.seek(0)
    file_content = fh.read()
    base64_encoded_content = base64.b64encode(file_content).decode('utf-8')

    return base64_encoded_content





















