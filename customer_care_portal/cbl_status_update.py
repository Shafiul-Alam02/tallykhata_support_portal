import datetime
import sqlite3
import psycopg2
import requests
from requests.structures import CaseInsensitiveDict

#Keep this Flase in production deployment
DEBUG = False

def beftn_status_check_api():
    date_today = datetime.datetime.today()
    date_t_3_days = date_today - datetime.timedelta(7)
    date_today=date_today.strftime("%d-%m-%Y")
    date_t_3_days = date_t_3_days.strftime("%d-%m-%Y")

    start_date = date_t_3_days
    end_date = date_today

    #print(start_date)
    start_date = '"'+start_date+'"'
    end_date = '"' + end_date + '"'
    url = ""

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = '{\n"fromDate":' + start_date + ',\n"toDate":' + end_date +'\n}'

    print("Payload is: \n",data)

    resp = requests.post(url, headers=headers, data=data)
    resp_status = resp.status_code
    resp_dict = resp.json()

    print(resp_status)
    #print(resp_dict)

    if resp_status != 200:
        txn_status = 'UNABLE TO CONNECT TO CBL'
        return txn_status

    len_list = len(resp_dict['OtherBankTransactionStatusResponse']['return']['responseData'])

    print("Length of X is: ")
    print(len_list)

    api_result_set = []
    for x in range(len_list):
        api_result_set.append(resp_dict['OtherBankTransactionStatusResponse']['return']['responseData'][x])

    return api_result_set


def beftn_recon_fix_date(date):
    date = date.split(' ',1)[0]

    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        new_date = date[6]+date[7]+date[8]+date[9]+date[5]+date[3]+date[4]+date[5]+date[0]+date[1]
        date = datetime.datetime.strptime(new_date, '%Y-%m-%d')

    return date


def generate_query(value_dict):
    type = "'"+ str(value_dict['@type']) + "'"
    amount = str(value_dict['amount'])
    bank_name = "'"+str(value_dict['bankName']) + "'"
    account_name = "'"+str(value_dict['beneficiaryAccountName']) + "'"
    account_number = "'"+str(value_dict['beneficiaryAccountNumber']) + "'"
    branch_name = "'"+str(value_dict['branchName']) + "'"
    departmentId = "'"+str(value_dict['departmentId']) + "'"
    payeeAccountNumber = "'"+str(value_dict['payeeAccountNumber']) + "'"
    returnDate = "'"+str(value_dict['returnDate']) + "'"
    returnReason = "'"+str(value_dict['returnReason']) + "'"
    routingNo = "'"+str(value_dict['routingNo']) + "'"
    sessionID = "'"+str(value_dict['sessionID']) + "'"
    settlementDate = value_dict['settlementDate']
    status = "'"+str(value_dict['status']) + "'"
    transactionDate = value_dict['transactionDate']
    transactionFlagCBS = "'"+str(value_dict['transactionFlagCBS']) + "'"
    transactionId = "'"+str(value_dict['transactionId']) + "'"
    transactionRefNumber = "'"+str(value_dict['transactionRefNumber']) + "'"
    transactionReturnFlagCBS = "'"+str(value_dict['transactionReturnFlagCBS']) + "'"
    transactionType = "'"+str(value_dict['transactionType']) + "'"
    created_at = "'"+str(datetime.datetime.now()) + "'"
    updated_at = "'"+str(datetime.datetime.now()) + "'"
    #status_meaning = "'"+"NEED TO UPDATE THIS LOGIC"+"'"

    #checking
    print("Created at: ", created_at)
    print("Updated at: ", updated_at)

    if transactionDate != None:
        print(transactionDate)
        transactionDate = beftn_recon_fix_date(transactionDate)
        transactionDate = "'" + str(value_dict['transactionDate']) + "'"
        print("Transaction Date: ",transactionDate)

    if settlementDate != None:
        print(settlementDate)
        settlementDate = beftn_recon_fix_date(settlementDate)
        settlementDate = "'" + str(value_dict['settlementDate']) + "'"
        print("Settlement Date: ",settlementDate)

    if transactionDate == None:
        transactionDate = "NONE"
        print(transactionDate)

    if settlementDate == None:
        settlementDate = "NONE"
        print(settlementDate)


    query_select = 'select * from public.display_data_app_tp_beftn_history_model d ' \
            +'where 1=1 ' \
            +' and d."transactionId" = ' + transactionId \
            +' and d."transactionRefNumber" = ' + transactionRefNumber \
            +' order by d."id" desc;'

    if status=="'1'" and transactionFlagCBS=="'1'" and transactionReturnFlagCBS=="'0'":
        txn_status = '110 - INSTRUCTION SENT TO BEFTN NETWORK BY CBL.'
    elif status=="'0'" and transactionFlagCBS=="'0'" and transactionReturnFlagCBS=="'0'":
        txn_status = '000 - BEFTN INSTRUCTION RECEIVED BY CBL, GL TRANSACTION NOT PROCESSED, NOT FORWARDED TO BEFTN NETWORK.'
    elif status=="'0'" and transactionFlagCBS=="'1'" and transactionReturnFlagCBS=="'0'":
        txn_status = '010 - BEFTN REQUEST RECEIVED BY CBL, GL TRANSACTION PROCESSED, NOT FORWARDED TO BEFTN NETWORK.'
    elif status=="'2'" and transactionFlagCBS=="'1'" and transactionReturnFlagCBS=="'1'":
        txn_status = '211 - FAILED.'
    else:
        txn_status = 'CBL RESPONSE UNKNOWN.'

    status_meaning = "'"+txn_status+"'"
    print(status_meaning)


    query_insert = 'insert into public.display_data_app_tp_beftn_history_model (' \
                   +'"txn_type","amount","bankName","beneficiaryAccountName","beneficiaryAccountNumber",' \
                   +'"branchName","departmentId","payeeAccountNumber","returnDate","returnReason","routingNo",' \
                   +'"sessionID","settlementDate","status","transactionDate","transactionFlagCBS","transactionId",' \
                   +'"transactionRefNumber","transactionReturnFlagCBS","transactionType","status_meaning","created_at","updated_at"' \
                   +')' \
                   +'values(' \
                   +type+','+amount+','+bank_name+','+account_name+','+account_number+','+branch_name+','+departmentId+','+payeeAccountNumber+',' \
                   +returnDate+','+returnReason+','+routingNo+','+sessionID+','+settlementDate+','+status+','+transactionDate+','+transactionFlagCBS+',' \
                   +transactionId+','+transactionRefNumber+','+transactionReturnFlagCBS+','+transactionType+','+status_meaning+","+created_at+","+updated_at+');'


    query_update = 'update public.display_data_app_tp_beftn_history_model ' \
                   + 'set ' \
                   + '"status" = ' + status + ',' \
                   + '"transactionFlagCBS" = ' + transactionFlagCBS + ',' \
                   + '"transactionReturnFlagCBS" = ' +transactionReturnFlagCBS + ',' \
                   + '"settlementDate" = ' +settlementDate+', ' \
                   + '"status_meaning" = '+status_meaning+', ' \
                   + '"updated_at" = '+updated_at+' ' \
                   + 'where 1=1 ' \
                   + 'and "transactionId" = '+transactionId+' ' \
                   + 'and "transactionRefNumber" = ' + transactionRefNumber+';'


    query = [query_select, query_insert, query_update]

    return query


def connect_to_pgsql(database, query):
    if DEBUG == False:
        print('Establishing Connection to Live Customer Support PostGres portal: ')
        host = "localhost"
        db_name = database
        user = ""
        password = ""
        port = '5432'
    else:
        print('Establishing Connection to Test Customer Support PostGres Database: ')
        host = "localhost"
        db_name = database
        user = "support_portal"
        password = "123456789"
        port = '5433'

    pg_conn = None

    try:
        print(db_name)
        print('connecting to pgSQL db name:', db_name)
        pg_conn = psycopg2.connect(
            host=host,
            database=db_name,
            user=user,
            password=password,
            port=port
        )
        print('Connection to PostGres successful: ', host, " ", db_name)

        # create pg cursor
        cur = pg_conn.cursor()
        print('Cursor created')
        cur.execute(query)
        print('Cursor executed')
        pg_conn.commit()
        print('Connection committed')
        # fetch the query results here
        queryset = cur.fetchall()

        #pg_conn.commit()
        #print('Connection committed')

        cur.close()
        # print(queryset)
        return queryset

    except(Exception, psycopg2.DataError) as error:
        queryset = "Exception Raised While connecting to PgSQL: Error is: " + str(error)
        # print(queryset)
        return queryset
    finally:
        if pg_conn is not None:
            pg_conn.close()


def manage_db(api_result_set):
    for i in range(len(api_result_set)):
        print(i)
        # print(api_result_set[i])
        # print(type(api_result_set[i]))


        query = generate_query(api_result_set[i])
        queryset = connect_to_pgsql('support_portal', query[0])
        print(query[0])
        print(queryset)

        if type(queryset) == str:
            print("Error connecting to DB")
        elif len(queryset) == 0:
            print("No result found running Insert Query")
            print(query[1])
            queryset = connect_to_pgsql('support_portal', query[1])
            print(query[1])

            print(queryset)
        else:
            print("Result found running update query")
            print(query[2])
            queryset = connect_to_pgsql('support_portal', query[2])

            print(queryset)


def main():
    print('Starting Main Function:')
    api_result_set = beftn_status_check_api()

    if type(api_result_set) != str:
        manage_db(api_result_set)


if __name__=="__main__":
    main()

