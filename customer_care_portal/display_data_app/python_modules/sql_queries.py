# SQL query selection functions are here

def credit_collection_via_nagad_query(start_date, end_date):  # 1
    if start_date == end_date:
        d_string = " and pc.created_at::date= " + str(start_date)
        # print(d_string)
    else:
        d_string = " and pc.created_at between " + str(start_date) + " and " + str(end_date)
        # print(d_string)

    query = "select pc.collection_media, rt.mobile_no as tp_wallet, pc.amount as amount_owed, pc.amount_given as amount_received, " \
            + "pn.status as tp_collection_status, pn.nagad_status as nagad_status, pc.status, pc.created_at as create_date, pn.order_id " \
            + "from payment_creditcollection pc " \
            + "left join payment_nagadtransaction pn on pc.nagad_transaction_id =pn.id " \
            + "left join register_tallykhatauser rt on rt.id = pc.tallykhata_user_id " \
            + "where 1=1 " \
            + "and pc.collection_media = 'NAGAD' " \
            + d_string \
            + " order by pc.id desc; "

    return query


def card_transaction_query(start_date, end_date):  # 2
    if start_date == end_date:
        d_string = " and pi2.create_date::date= " + str(start_date)
        # print(d_string)
    else:
        d_string = " and pi2.create_date between " + str(start_date) + " and " + str(end_date)
        # print(d_string)

    query = "select pi2.id, pi2.wallet, pi2.amount, pi2.order_id, pi2.status, pi2.create_date, rlv.create_date as response_create_date," \
            + " rlv.external_request, rlv.external_response, rlv.response  from payment_info pi2" \
            + " inner join request_log_v2 rlv on pi2.order_id = rlv.order_id" \
            + " where 1=1" \
            + " and pi2.status != 'SUCCESS'" \
            + d_string \
            + " order by pi2.id desc;"
    # print(query)
    return query


def sms_failure_report_query(start_date, end_date):  # 3
    if start_date == end_date:
        d_string = " request_time >= date(" + start_date + ") and request_time < date(" + start_date + ") + INTERVAL 1 DAY "
    else:
        d_string = " request_time >= " + start_date + " and " + "request_time < " + end_date

    query = "select channel, description, telecom_operator, message_status, count(*) from message_v2 mv " \
            + "where" \
            + d_string \
            + "and message_status not in('SUCCESS', '0') " \
            + "and channel in('TALLYKHATA_OTP','TALLYKHATA_TXN') " \
            + "group by 1,2,3,4 " \
            + ";"

    return query


def telco_recharge_report_query(start_date, end_date):
    if start_date == end_date:
        d_string = "create_date::date = " + start_date
    else:
        d_string = " create_date >= " + start_date + " and " + "create_date < " + end_date
        # print(d_string)

    query = "select request_id, wallet, amount, create_date, description, mobile_operator, vendor_name, status from top_up_info tu " \
            + "where 1=1 " \
            + "and status != 'SUCCESS' and " \
            + d_string \
            + " order by tu.id desc " \
            + ";"

    return query


def daily_sms_failure_query():  # 4
    query = " select channel, sum(total_failure) as total_failure from" \
            + " (select channel, count(1) as total_failure from message_v2 mv" \
            + " where" \
            + " 1 = 1" \
            + " and request_time >= CURRENT_DATE()" \
            + " and message_status not in('SUCCESS', '0')" \
            + " and channel in('TALLYKHATA_OTP', 'TALLYKHATA_TXN')" \
            + " group by channel UNION" \
            + " select * from (select 'TALLYKHATA_OTP' as channel, 0 as total_failure UNION select 'TALLYKHATA_TXN' as channel, 0 as total_failure)t1" \
            + " )t2" \
            + " group by 1" \
            + " order by channel" \
            + " ;"

    return query


def daily_card_transaction_query():  # 5
    query = "select count(*), 'SUCCESS' as res from payment_info pi2" \
            " where" \
            " 1 = 1" \
            " and status = 'SUCCESS'" \
            " and create_date::date = current_date" \
            " union" \
            " select count(*), 'FAILURE' as res from payment_info pi2" \
            " where" \
            " 1 = 1" \
            " and status != 'SUCCESS'" \
            " and create_date::date = current_date" \
            " ;"

    return query


def daily_telco_recharge_summary():
    query = "select * from (select count(*), 'SUCCESS' as res from top_up_info tui " \
            "where " \
            "1 = 1 " \
            "and status = 'SUCCESS' " \
            "and create_date >= current_date  and create_date < (current_date+1) " \
            "union " \
            "select count(*), 'FAILED' as res from top_up_info tui " \
            "where " \
            "1 = 1 " \
            "and status != 'SUCCESS' " \
            "and create_date >= current_date  and create_date < (current_date+1) " \
            ") as fin order by res " \
            ";"

    return query


def daily_credit_collection_via_nagad_summary():
    query = "select 'SUCCESS' as res, count(*) " \
            "from payment_nagadtransaction p " \
            "left join registered_users ru on p.tallykhata_user_id = ru.tallykhata_user_id " \
            "left join payment_creditcollection pc on p.id=pc.nagad_transaction_id " \
            "where 1=1 " \
            "and ru.device_status = 'active' " \
            "and p.status ='SUCCESS' " \
            "and p.created_at >= current_date and p.created_at < (current_date+1) " \
            "union " \
            "select 'FAILED' as res, count(*) " \
            "from payment_nagadtransaction p " \
            "left join registered_users ru on p.tallykhata_user_id = ru.tallykhata_user_id " \
            "left join payment_creditcollection pc on p.id=pc.nagad_transaction_id " \
            "where 1=1 " \
            "and ru.device_status = 'active' " \
            "and p.status !='SUCCESS' " \
            "and p.created_at >= current_date and p.created_at < (current_date+1) " \
            ";"

    return query


def bank_wallet_reactivate_request_query(wallets):
    query = "SELECT a.owner_name, a.member_id, sutp.profinoUserStatus FROM accounts a " \
            + "left join sc_user_temp_profile sutp on sutp.userName = a.owner_name " \
            + "WHERE 1=1 " \
            + "and a.owner_name IN " \
            + wallets + ";"

    return query


def telco_sms_bill_verification_query(start_date, end_date):
    d_string = " and m.request_time >= " + str(start_date) + " and m.request_time < " + str(end_date)

    # query = "select tucv.telco_code, message_status, count(*) from message_v2 mv " \
    #         +"left join telco_url_config_v2 tucv " \
    #         +"on mv.telco_identifier_id = tucv.id " \
    #         +"where 1=1 " \
    #         +d_string \
    #         +"and message_status in ('SUCCESS','0','200') " \
    #         +"group by 1,2;"

    query = "select c.telco_code, count(*) " \
            + "from message_v2 m, telco_url_config_v2 c " \
            + "where m.telco_identifier_id =c.id " \
            + d_string \
            + "and m.channel in('TALLYKHATA_OTP', 'TALLYKHATA_TXN') " \
            + "and m.message_status in('SUCCESS', '200', '0') " \
            + "group by 1;"

    return query


def tp_daily_sms_summary():
    query = "select 'SUCCESS' as res, count(*) from sms_response_log srl " \
            "where 1=1 " \
            "and create_date::date = current_date " \
            "and status = 'SUCCESS' " \
            "union " \
            "select 'FAILURE' as res, count(*) from sms_response_log srl " \
            "where 1=1 " \
            "and create_date::date = current_date " \
            "and status != 'SUCCESS';"

    return query


def tp_sms_failure_report_query(start_date, end_date):
    if start_date == end_date:
        d_string = " and create_date::date= " + str(start_date)
        # print(d_string)
    else:
        d_string = " and create_date >= " + str(start_date) + " and create_date <=" + str(end_date)

    query = "select * from sms_response_log srl " \
            + "where 1=1 " \
            + "and status != 'SUCCESS' " \
            + d_string \
            + " order by id desc;"

    return query


def tp_wallet_unblock(wallet_list):
    d_string = "and username in " + wallet_list

    query = "select username, enabled from user_entity ue " \
            + "where 1=1 " \
            + "and ((username not like '0198000%') and (username not like '0140444%') and  (username not like '0190444%') and (username not like 'israt_cs')) " \
            + "and enabled is false " \
            + d_string + " order by created_timestamp desc;"

    return query


def tp_wallet_unblock_verify(wallet_list):
    d_string = "and username in " + wallet_list

    query = "select username, enabled from user_entity ue " \
            + "where 1=1 " \
            + "and ((username not like '0198000%') and (username not like '0140444%') and  (username not like '0190444%') and (username not like 'israt_cs')) " \
            + d_string + " order by created_timestamp desc;"

    return query


def tp_check_blocked_wallets():
    query = "select username, enabled from user_entity ue " \
            "where 1=1 " \
            "and ((username not like '0198000%') and (username not like '0140444%') and  (username not like '0190444%') and (username not like 'israt_cs')) " \
            "and enabled is false;"

    return query


def tp_check_unblocked_wallets(wallets):
    d_string = "and username in " + wallets + " "
    query = "select username, enabled from user_entity ue " \
            + "where 1=1 " \
            + "and ((username not like '0198000%') and (username not like '0140444%') and  (username not like '0190444%') and (username not like 'israt_cs')) " \
            + d_string + "and enabled is true;"

    return query


def tk_mnp_issue(wallet):
    query = f'''
            SELECT
                mobile_no,
                bank_name,
                channel,
                message_body,
                request_time
            FROM
                sms_prod.public.message_v2 AS mv
            WHERE
                mv.request_time >= NOW() - INTERVAL '359 seconds'
                AND mv.mobile_no = '{wallet}'
                AND message_status IN ('SUCCESS', '0')
            ORDER BY
                mv.request_time DESC
            LIMIT 1;
    '''

    # query_verification_tk = "select j.mobile_no, j.amount as amount_given, j.amount_received, j.txn_date, rt.shop_name, rt.merchant_name from journal j " \
    #          "left join register_tallykhatauser rt on j.tallykhata_user_id = rt.id " \
    #          "where 1=1 " \
    #          "and rt.mobile_no = '"+wallet+"' " \
    #          "order by j.id desc limit 5;"
    #
    # query_verification_tp ="select a.owner_name, t.amount as Amount, t.process_date from transfers t , accounts a " \
    #                        "where 1=1 " \
    #                        "and (a.id = t.from_account_id or a.id = t.to_account_id) " \
    #                        "and a.owner_name = '"+wallet+"' " \
    #                        "order by t.id desc " \
    #                        "limit 5;"

    return query


# Data missing or calculation mismatch issue queries start
def calculation_mismatch_query1(wallet):
    query = "select mobile_number, account_count, cash_txn_count, credit_txn_count, total_txn_count, created_at from user_summary " \
            "where 1=1 " \
            "and mobile_number = '" + wallet + "' " \
                                               "order by id desc;"

    return query


def calculation_mismatch_query2(wallet):
    query = 'select mobile, "name", device_brand, device_name, device_model, device_manufacturer, device_status,os_version, os_api_level, app_version_name, app_version_number, created_at from registered_users ru ' \
            'where 1=1 ' \
            "and mobile = '" + wallet + "'" \
                                        "order by id desc;"

    return query


def calculation_mismatch_query3(wallet):
    query = "select h.mobile_no, account_id, owner_id, amount, amount_received, txn_date, txn_type, txn_mode, create_date, is_updated, last_update_date, is_active, synced_date, backup_at from history_journal h " \
            "where 1=1 " \
            "and mobile_no = '" + wallet + "' " \
                                           "order by h.id desc;"

    return query


# Data missing or calculation mismatch issue queries end

def credit_collection_via_rocket_query(start_date, end_date):  # 1
    if start_date == end_date:
        d_string = " and pc.created_at::date= " + str(start_date)
        # print(d_string)
    else:
        d_string = " and pc.created_at between " + str(start_date) + " and " + str(end_date)
        # print(d_string)

    query = "select pc.collection_media, rt.mobile_no as tp_wallet, pc.amount as amount_owed, pc.amount_given as amount_received, " \
            + "pr.status as rocket_collection_status, pc.status, pc.created_at as create_date, pr.txn_id " \
            + "from payment_creditcollection pc " \
            + "left join payment_rockettransactions pr on pc.rocket_transaction_id = pr.id " \
            + "left join register_tallykhatauser rt on rt.id = pc.tallykhata_user_id " \
            + "where 1=1 " \
            + "and pc.collection_media = 'ROCKET' " \
            + d_string \
            + "order by pc.id desc;"

    return query


def idtp_log_transaction_report(start_date, end_date):
    if start_date == end_date:
        d_string = " and CAST(CreatedOn as date)= " + str(start_date)
        # print(d_string)
    else:
        d_string = " and CreatedOn BETWEEN " + str(start_date) + " and " + str(end_date)
        # print(d_string)

    query = "select * from LogTransactions lt " \
            + "where 1=1 " \
            + d_string \
            + " order by LogId desc; "

    return query


def check_nagad_status_query(nagad_txn_id):
    nagad_txn_id = "'" + nagad_txn_id + "'"
    query = "select rt.mobile_no as tp_wallet,pn.client_mobile_no as nagad_wallet,pn.amount  as amount_sent_by_nagad, " \
            "pc.status as tp_status,pc.collection_media,pn.order_id,pn.issuer_payment_reference, " \
            "pn.payment_reference_id,pn.order_datetime,pn.issuer_payment_datetime, wt.txn_type, wt.transaction_number, wt.txn_time " \
            "from payment_creditcollection pc " \
            "left join payment_nagadtransaction pn on pc.nagad_transaction_id = pn.id " \
            "left join register_tallykhatauser rt on pc.tallykhata_user_id = rt.id " \
            "left join wallet_tallypaytransaction wt on pc.tallypay_transaction_id = wt.id " \
            "where 1=1 " \
            "and collection_media = 'NAGAD' " \
            "and pn.issuer_payment_reference = " + nagad_txn_id + ";"

    return query


def check_rocket_status_query(txn_date):
    # tp_wallet = "'"+tp_wallet+"'"

    query = "select rt.mobile_no as tp_wallet, pr.amount as amount_recieved_from_rocket, " \
            "pc.status,pc.collection_media, pc.created_at, pr.status, pr.txn_id, pr.client_ip, pr.rrn " \
            "from payment_creditcollection pc " \
            "left join payment_rockettransactions pr on pc.rocket_transaction_id = pr.id " \
            "left join register_tallykhatauser rt on pc.tallykhata_user_id = rt.id " \
            "where 1=1 " \
            "and pc.collection_media = 'ROCKET' " \
            "and pc.status not in (1,4,7,9) " \
            "and pc.created_at :: date = " + txn_date + " " \
                                                        "order by pc.id desc;"
    # "and rt.mobile_no = "+ tp_wallet +" " \

    return query


def beftn_status_check(wallet, txn_date):
    wallet = "'" + wallet + "'"
    txn_date = "'" + txn_date + "'"

    query = "select p.wallet_no, btr.amount, txn_request_type, status, b2.bank_name, ba.account_number, ba.routing_number, " \
            "ba.account_name, btr.core_txn_id, btr.id as bank_search_id, btr.request_time::date " \
            "from backend_db.public.bank_txn_request btr " \
            "left join bank_account ba on btr.account_id = ba.id " \
            "left join profile p on ba.user_id = p.user_id " \
            "left join branch b on ba.routing_number = b.routing_number " \
            "left join bank b2 on b.bank_id = b2.id " \
            "where 1=1 " \
            "and txn_request_type not in ('CARD_TXN','LOAN_REPAYMENT') " \
            "and p.wallet_no = " + wallet + " " \
                                            "and btr.request_time::date = " + txn_date + " " \
                                                                                         "order by btr.id desc;"

    return query


def nagad_cash_out_status_check_query(tp_txn_id):
    tp_txn_id = "'" + tp_txn_id + "'"

    query1 = "select from_wallet, external_wallet, tally_pay_txn_id, status, extra_info, amount from transaction_info ti " \
             "where 1=1 " \
             "and financial_institute = 'NAGAD' " \
             "and tally_pay_txn_id = " + tp_txn_id + " " \
                                                     "order by id desc;"

    query2 = "select request from request_log rl " \
             "where 1=1 " \
             "and request_id = ( " \
             "select request_id from transaction_info ti " \
             "where 1=1 " \
             "and financial_institute = 'NAGAD' " \
             "and tally_pay_txn_id = " + tp_txn_id + ") " \
                                                     "and request like '%https://api.mynagad.com/api/secure-handshake/dfs/disbursement%' order by id desc;"

    query = [query1, query2]

    return query


def idtp_txn_search_query(tp_txn_id):
    query1 = f'''
        select ResponsePayload from LogCommunication lc 
        where 1=1
        and MasterRefId = (
        select DISTINCT MasterRefId from LogTransactions lt 
        where 1=1
        and RefNoSendingBank = '{tp_txn_id}'
        or RefNoReceivingBank = '{tp_txn_id}'
        )
        and ResponsePayload is not null
        and ResponsePayload != ''
        order by LogId desc;
    '''

    query2 = f'''
            select DISTINCT SenderVID, ReceiverVID from LogTransactions lt 
            where 1=1
            and RefNoSendingBank = '{tp_txn_id}'
            or RefNoReceivingBank = '{tp_txn_id}'
            ;
    '''

    query = [query1, query2]

    return query


def tallypay_txn_search(wallet, start_date, end_date):
    query_balance = f'''
    select 
    (select SUM(amount) as credit  from transfers t 
    inner join accounts a on t.to_account_id = a.id 
    where 1=1
    and 
    a.owner_name = '{wallet}') 
    -
    (select SUM(amount) as debit  from transfers t 
    inner join accounts a on t.from_account_id = a.id 
    where 1=1
    and 
    a.owner_name = '{wallet}') as balance;
'''

    query_transfers = f'''
    SET @runtot := (
	select -(select COALESCE(SUM(amount),0) as debit  from transfers t 
	inner join accounts a on t.from_account_id = a.id 
	where 1=1
	and a.owner_name = '{wallet}'
	and `date` <{start_date})
	+
	(select COALESCE(SUM(amount),0) as credit  from transfers t 
	inner join accounts a on t.to_account_id = a.id 
	where 1=1
	and a.owner_name = '{wallet}'
	and `date` <{start_date}) as balance
	);
	
	SET @user_id := (select id from accounts where owner_name = '{wallet}');
    
	select
		t.process_date,
		tt.name,
		CASE
			when t.description COLLATE UTF8_GENERAL_CI like '%idtp%' then 'IDTP'
			when t.description COLLATE UTF8_GENERAL_CI like '%robi%' then 'ROBI'
			when t.description COLLATE UTF8_GENERAL_CI like '%gp%' then 'GP'
			when t.description COLLATE UTF8_GENERAL_CI like '%bl%' then 'BANGLALINK'
			when t.description COLLATE UTF8_GENERAL_CI like '%tt%' then 'TELETALK'
			when t.description COLLATE UTF8_GENERAL_CI like '%airtel%' then 'AIRTEL'
			when t.description COLLATE UTF8_GENERAL_CI like '%card%' then 'CARD'
			when t.description COLLATE UTF8_GENERAL_CI like '%rocket%' then 'ROCKET'
			when t.description COLLATE UTF8_GENERAL_CI like '%nagad%' then 'NAGAD'
			when t.description COLLATE UTF8_GENERAL_CI like '%cashback%' then 'CASHBACK'
			when t.description COLLATE UTF8_GENERAL_CI like '%send money from merchant to customer%' then 'TALLYPAY'
			when t.description COLLATE UTF8_GENERAL_CI like '%send money to customer from customer%' then 'TALLYPAY'
			when t.description COLLATE UTF8_GENERAL_CI like '%charge to escrow wallet%' then 'TALLYPAY'
			when t.description COLLATE UTF8_GENERAL_CI like '%cash-out to other bank%' then 'BANK'
			else 'UNNAMED'
		END as vendor,
		a.owner_name,
		t.transaction_number,
		parent_id,
		case
			when t.chargedback_by_id is not NULL then 'REVERSED'
			else NULL
		end as reverse_status,
		case
			when t.from_account_id = @user_id then abs(t.amount)
			else NULL
		end as debit,
		case
			when t.to_account_id = @user_id then abs(t.amount)
			else NULL
		end as credit,
		case
			when t.from_account_id = @user_id then (@runtot := @runtot - t.amount)
			when t.to_account_id = @user_id then (@runtot := @runtot + t.amount)
			else NULL
		end as balance
		from
		transfers t
	inner join accounts a on
		t.from_account_id = a.id
		or t.to_account_id = a.id
	inner join transfer_types tt on
		t.type_id = tt.id
	where
		1 = 1
		and a.owner_name = '{wallet}'
		and t.process_date between {start_date} and {end_date}
	ORDER by
		t.id desc;
'''

    query = {
        'query_balance': query_balance,
        'query_transfers': query_transfers,
    }

    return query


def channel_wise_transaction_status(tp_txn_id):
    recharge_query = f'''
        select txn_id, status, tui.external_ref_no 
        from top_up_info tui
        where 1 = 1
        and txn_id in ({tp_txn_id})
        order by id desc;
'''

    cash_out_to_nagad = f'''
        select tally_pay_txn_id,status,external_txn_id from transaction_info ti
        where 1=1
        and financial_institute = 'NAGAD'
        and tally_pay_txn_id in({tp_txn_id})
        order by id desc;
'''

    cash_out_to_rocket = f'''
        select tally_pay_txn_id,status,external_txn_id from transaction_info ti
        where 1=1
        and financial_institute = 'ROCKET'
        and tally_pay_txn_id in({tp_txn_id})
        order by id desc;
'''

    credit_collection_via_nagad = f'''
        select
        wt.transaction_number,pn.nagad_status,pn.issuer_payment_reference
        from payment_creditcollection pc
        inner join payment_nagadtransaction pn on pc.nagad_transaction_id = pn.id
        inner join wallet_tallypaytransaction wt on pc.tallypay_transaction_id = wt.id
        where 1=1
        and collection_media = 'NAGAD'
        and wt.transaction_number in ({tp_txn_id})
        order by pc.id desc;
'''

    credit_collection_via_rocket = f'''
        select
        wt.transaction_number,pr.status, pr.rrn
        from payment_creditcollection pc
        inner join payment_rockettransactions pr on pc.rocket_transaction_id  = pr.id
        inner join wallet_tallypaytransaction wt on pc.tallypay_transaction_id = wt.id
        where 1=1
        and collection_media = 'ROCKET'
        and wt.transaction_number in ({tp_txn_id})
        order by pc.id desc;
'''

    query = {
        'recharge_query': recharge_query,
        'cash_out_to_nagad': cash_out_to_nagad,
        'cash_out_to_rocket': cash_out_to_rocket,
        'credit_collection_via_nagad': credit_collection_via_nagad,
        'credit_collection_via_rocket': credit_collection_via_rocket
    }

    return query


def recharge_vendor_switch():
    query_display = '''
            select
            mobile_operator,
            vc.vendor_name,
            vs.vendor_config_id,
            vs.create_date,
            vs.update_date
        from
            vendor_selection vs
        inner join vendor_config vc on
            vs.vendor_config_id = vc.id
        order by
            vs.id desc;
    '''

    query = [query_display]

    return query


def tallypay_master_txn_search(transaction_number):
    query = f'''
            select
                t.process_date,
                amount,
                t.description,
                chargedback_by_id,
                transaction_number,
                tag,
                escrow_type,
                related_txn_number,
                tt.name,
                a.owner_name as from_account,
                a2.owner_name as to_account,
                t.type_id,
                t.invoice_no,
                t.trace_data,
                ntt.txn_type,
                ntt.from_ac_type,
                ntt.to_ac_type,
                ntt.charge_flag,
                t.customer_id 
            from
                transfers t
            inner join transfer_types tt on
                t.type_id = tt.id
            inner join accounts a on
                t.from_account_id = a.id
            inner join accounts a2 on
                t.to_account_id = a2.id
            inner join np_transaction_type ntt on
                t.type_id = ntt.transfer_type
            where
                1 = 1
                and transaction_number = '{transaction_number}';   
            '''

    return query


def get_pran_rfl_auth_token_from_db():
    query = f'''
            select
                "token"
            from
                pran_auth_info pai
            order by
                id desc
            limit 1;
        '''

    return query


def get_data_for_remote_end_checking(transaction_number, txn_type, charge_flag):
    query_component = None

    if txn_type == 'CASH_OUT_TO_BANK':
        query_component = f'''
            select
                btr.id as btr_id,
                txn_request_type,
                btr.status as btr_status,
                ntl.status as np_log_status,
                btr.amount,
                btr.issue_time,
                ba.account_number,
                ba.routing_number,
                btr.core_txn_id as btr_core_txn_id,
                ntl.transaction_number as np_txn_num,
                ntl.type_name,
                ban.bank_name ,
                b.branch_name,
                btl.response_code ,
                btl.request_text ,
                btl.response_text 
            from
                bank_txn_request btr
            inner join bank_account ba on
                btr.account_id = ba.id
            inner join np_txn_log ntl on
                btr.np_txn_log_id = ntl.id
            inner join branch b on
                ba.routing_number = b.routing_number
            inner join bank ban on
                b.bank_id = ban.id
            left join bank_txn_log btl on btl.np_txn_request_id = btr.id
            where
                1 = 1
                and btr.request_id = '{transaction_number}'
            order by
                btr.id desc;
        '''
    elif txn_type == 'NPSB_TRANSFER_CREDIT':
        query_component = f'''
            select
                create_date,
                update_date,
                request_id,
                request,
                response,
                process_time
            from
                request_log rl
            where
                1 = 1
                and request_id = '{transaction_number}'
            order by
                id desc;
        '''
    elif txn_type == 'CASH_OUT_TO_EXTERNAL':
        query_component = f'''
            select
                ti.*,
                rl.request_id ,
                rl.request ,
                rl.response ,
                rl.process_time
            from
                transaction_info ti
            right join request_log rl on
                ti.request_id = rl.request_id
            where
                1 = 1
                and ti.request_id = '{transaction_number}'
            order by
                rl.id desc;
        '''
    elif txn_type == 'MOBILE_RECHARGE':
        query_component = f'''
            SELECT
                tui.create_date AS "CREATE_DATE",
                tui.mobile_operator AS "MOBILE_OPERATOR",
                tui.vendor_name AS "RECHARGE_VENDOR",
                tui.wallet AS "WALLET",
                tui.receiver_mobile AS "RECEIVER_MOBILE",
                tui.amount AS "RECHARGE_AMOUNT",
                tui.txn_id AS "INITIATED_TXN_NUM",
                tui.complete_txn_id AS "RELEASE_TXN_NUM",
                tui.status AS "STATUS",
                tui.external_ref_no AS "EXTERNAL_REF",
                tui.description AS "DESCRIPTION",
                tui.request_id AS "REQUEST_ID", 
                rl.request AS "REQUEST",
                rl.response AS "RESPONSE",
                rl.create_date AS "REQUEST_CREATE_DATE",
                rl.process_time AS "REQUEST_PROCESS_TIME"
            FROM
                topup_service.public.top_up_info tui
                RIGHT JOIN request_log rl ON tui.request_id = rl.request_id
            WHERE
                1 = 1
                AND tui.request_id = '{transaction_number}'
            ORDER BY
                rl.id DESC;
        '''
    elif txn_type == 'CASH_IN_FROM_EXTERNAL':
        if charge_flag == 'NAGAD':
            query_component = f'''
                select
                    wallet,
                    client_mobile_no,
                    amount ,
                    nagad_status ,
                    status, 
                    order_id ,
                    order_date_time ,
                    payment_reference_id,
                    issuer_payment_ref_no ,
                    issuer_payment_date_time ,
                    cancel_issuer_ref_no ,
                    cancel_issuer_date_time,
                    nagad_status_code ,
                    credit_collection_id ,
                    create_date,
                    update_date
                from
                    nagad_txn nt
                where
                    1 = 1
                    and nt.order_id = '{transaction_number}'
                order by
                    nt.id desc;
            '''
        elif charge_flag == 'ROCKET':
            query_component = f'''
                select
                    wallet,
                    card_number,
                    tp_transaction_number ,
                    amount,
                    status,
                    rrn ,
                    txn_date,
                    dbbl_txn_id ,
                    description,
                    ip,
                    "result",
                    result_code ,
                    credit_collection_id
                from
                    dbbl_transaction dt
                where
                    1 = 1
                    and txn_ref_no = '{transaction_number}'
                order by
                    id desc;
            '''
    elif txn_type == 'CASH_IN_FROM_CARD':
        query_component = f'''
                select
                    pi2.wallet ,
                    pi2.order_id ,
                    amount ,
                    pi2.create_date ,
                    pi2.update_date ,
                    status,
                    txn_id ,
                    card_no ,
                    card_type ,
                    expiry ,
                    "name" ,
                    credit_collection_id,
                    rlv.request,
                    rlv.response,
                    rlv.external_request ,
                    rlv.external_response ,
                    rlv.external_process_time
                from
                    payment_info pi2
                inner join request_log_v2 rlv on
                    pi2.order_id = rlv.order_id
                where
                    1 = 1
                    and pi2.order_id = '{transaction_number}'
                order by
                    rlv.id desc;
            '''

    return query_component


def wallet_mdr_limit_and_rate_queries(wallet_number):
    mdr_query = f'''
        select
            wallet ,
            rate,
            is_active,
            create_date
        from
            wallet_mdr_config wmc
        where
            1 = 1
            and wallet = '{wallet_number}'
            and is_active = true
        order by
            id desc
        limit 1;
    '''

    global_mdr_query = f'''
        select
            rate ,
	        create_date
        from
            mdr_config mc
        where
            1 = 1
            and mc.user_type = (
            select
                at2."name"
            from
                accounts a
            inner join account_types at2 on
                a.type_id = at2.id
            where
                1 = 1
                and a.owner_name = '{wallet_number}'
            order by
                a.id desc)
        order by
            id desc;
    '''

    limit_query = f'''  
        select
            wallet,
            "type",
            user_type,
            min_amount_per_txn,
            max_amount_per_txn,
            max_count_per_day,
            max_amount_per_day,
            max_count_per_month,
            max_amount_per_month,
            status,
            created_at
        from
            npapi_npwallettxnlimit nn
        where
            1 = 1
            and nn.wallet = '{wallet_number}'
        order by
            id desc;
    '''

    transfers_query = f'''
                select
            ntt.txn_type,
            ROUND(coalesce(SUM(t.amount),0),2) as total_amount
        from
            np_transaction_type ntt
        left join
            transfers t on
            t.type_id = ntt.transfer_type
            and (t.to_account_id = (
            select
                id
            from
                accounts a
            where
                a.owner_name = '{wallet_number}')
            or t.from_account_id = (
            select
                id
            from
                accounts a
            where
                a.owner_name = '{wallet_number}'))
            and t.process_date >= DATE_TRUNC('month', CURRENT_DATE)
            and t.process_date < DATE_TRUNC('month',  CURRENT_DATE) + interval '1 month'
        group by
            ntt.txn_type;
    '''

    transfers_daily_query = f'''
         select
            ntt.txn_type,
            ROUND(coalesce(SUM(t.amount),0),2) as total_amount
        from
            np_transaction_type ntt
        left join
            transfers t on
            t.type_id = ntt.transfer_type
            and (t.to_account_id = (
            select
                id
            from
                accounts a
            where
                a.owner_name = '{wallet_number}')
            or t.from_account_id = (
            select
                id
            from
                accounts a
            where
                a.owner_name = '{wallet_number}'))
            and t.process_date >= current_date 
        group by
            ntt.txn_type;
    '''

    user_type_query = f'''
        select
        a.owner_name ,
        at2."name"
    from
        accounts a
    inner join account_types at2 on
        a.type_id = at2.id
    where
        1 = 1
        and a.owner_name = '{wallet_number}';
    '''

    queries = {
        'global_mdr_query': global_mdr_query,
        'mdr_query': mdr_query,
        'limit_query': limit_query,
        'transfers_query': transfers_query,
        'transfers_daily_query': transfers_daily_query,
        'user_type_query': user_type_query
    }

    return queries


def get_global_limit(user_type):
    query = f'''
        select
        	type,
            user_type,
            min_amount_per_txn,
            max_amount_per_txn,
            max_count_per_day,
            max_amount_per_day,
            max_count_per_month,
            max_amount_per_month,
            status
        from
            npapi_nptxnlimit nn
        where
            1 = 1
            and user_type = '{user_type}'
            and status = 'ACTIVE'
        order by
            id desc;
    '''

    return query


def get_core_user_id(wallet):
    query = f'''
        select
            user_id
        from
            profile p
        where
            1 = 1
            and wallet_no = '{wallet}'
        order by
            user_id desc;
    '''

    return query


def get_account_id(wallet):
    query = f'''
    select
        a.id,
        a.owner_name ,
        at2."name"
    from
        accounts a
    inner join account_types at2 on
        a.type_id = at2.id
    where
        1 = 1
        and a.owner_name = '{wallet}';
    '''

    return query


def get_wallet_statement(account_id):
    balance_query = f'''        
        select
            coalesce((sum(total_credit) - sum(total_debit)),0)
        from 
            (
            select 
                sum(t.amount) as total_debit,
                0 as total_credit
            from nobopay_core.public.transfers as t 
            where t.from_account_id ={account_id}
            union all 
            select 
                0 as total_debit,
                sum(t.amount) as total_credit
            from nobopay_core.public.transfers as t 
            where t.to_account_id ={account_id}
        ) as t ;
    '''

    statement_query = f'''
        SELECT
            ntl.txn_time,
            ntl.amount,
            ntl.transaction_number,
            ntl.txn_type,
            ntl.status
        FROM
            np_txn_log ntl
        INNER JOIN profile p ON
            (ntl.from_id = p.user_id
                OR ntl.to_id = p.user_id )
        WHERE
            1 = 1
            AND p.wallet_no = '{account_id}'
            ORDER BY txn_time desc
        ;
    '''

    queries = {
        'balance_query': balance_query,
        'statement_query': statement_query
    }

    return queries


def transaction_info(account_id):
    statement_query = f'''
            SELECT
                ntl.txn_time + INTERVAL '6 hours' AS txn_time_plus_6h,
                ntl.amount,
                ntl.transaction_number,
                ntl.txn_type,
                ntl.status,
                CONCAT(
                    'SQR balance: ', COALESCE((ntl.transaction_fees::json -> 0 ->> 'sqrAmount'), 'N/A'),
                    ' MDR: ', COALESCE((ntl.transaction_fees::json -> 0 ->> 'mdrFeeRate'), 'N/A'),
                    ' SQR charge: ', COALESCE((ntl.transaction_fees::json -> 0 ->> 'sqrFee'), 'N/A'),
                    ' Regular balance: ', COALESCE((ntl.transaction_fees::json -> 0 ->> 'regularAmount'), 'N/A'),
                    ' Regular Fee Rate: ', COALESCE((ntl.transaction_fees::json -> 0 ->> 'regularFeeRate'), 'N/A'),
                    ' Regular Charge: ', COALESCE((ntl.transaction_fees::json -> 0 ->> 'regularFee'), 'N/A'),
                    ' Total charge: ', COALESCE((ntl.transaction_fees::json -> 0 ->> 'amount'), 'N/A')
                ) AS formatted_transaction_fees
            FROM
                np_txn_log ntl
            INNER JOIN profile p ON
                (ntl.from_id = p.user_id OR ntl.to_id = p.user_id)
            WHERE
                p.wallet_no = '{account_id}'
            ORDER BY
                txn_time_plus_6h DESC
                LIMIT 500;

        '''
    return statement_query


def get_profile_data(wallet):
    query1 = f'''
        select
            p.wallet_no,
            date_of_birth,
            full_name,
            concat('',profile_image),
            biz_name,
            identity_status,
            bank_account_status,
            concat('',biz_qr_code) ,
            d.doc_type, 
            d.status ,
            d.is_active 
        from
            profile p
        inner join "document" d on
            p.user_id = d.user_id
        where
            1 = 1
            and p.wallet_no = '{wallet}'
            and d.is_active = true;
    '''

    query2 = f'''
        select
            df."type",
            concat('',df.img_path) as image,
            df.active,
            d.doc_type ,
            d.status,
            d.id_no
        from
            document_file df
        inner join "document" d on
            df.document_id = d.id
        inner join profile p on
            p.user_id = d.user_id
        where
            1 = 1
            and p.wallet_no = '{wallet}'
            and df.active = true
            and d.doc_type in ('NID', 'SHOP_IMAGE', 'TRADE_LICENSE');
    '''

    query = {
        'query1': query1,
        'query2': query2
    }

    return query


def get_tallykhatayuser_id(wallet):
    query = f'''
        select
            *
        from
            register_usermobile ru
        where
            ru.mobile_number = '{wallet}';
    '''

    return query


def data_missing(user_id, from_date, to_date, category, customer_need):
    if category == 'FROM_JOURNAL' and customer_need == 'TRANSACTION_LIST':
        query = f'''
                    select 
                    j.amount,
                    j.amount_received,
                    j.txn_date::text as txn_date,
                    j.description::text as description,
                    j.tallykhata_user_id::text as mobile_no,
                    a.contact::text as added_customer_mobile,
                    a."name"::text as customer_name,
                    case when j.txn_type =1 and j.txn_mode = 1 then 'নগদ বিক্রি'
                        when j.txn_type =2 and j.txn_mode = 1 then 'নগদ কেনা'
                        when j.txn_type =5 and j.txn_mode = 1 then 'খরচ'
                        when j.txn_type =3 and j.txn_mode = 1 and coalesce(amount_received,0)>0 then 'বাকি বিক্রি আদায়'
                        when j.txn_type =4 and j.txn_mode = 1 and coalesce(amount_received,0)>0 then 'বাকি কেনা'
                        when j.txn_type =9 and j.txn_mode = 3 and coalesce(amount_received,0)>0 then 'বাকি আদায়'
                        when j.txn_type =3 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'বাকি বিক্রি'
                        when j.txn_type =4 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'বাকি কেনা পরিশোধ'
                        when j.txn_type =10 and j.txn_mode = 3 and coalesce(amount,0)>0 then 'সাপ্লায়ার পেমেন্ট'
                        when j.txn_type =11 and j.txn_mode = 3 and coalesce(amount,0)>0 then 'ডিজিটাল নগদ বিক্রি'
                        when j.txn_type =6 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'মালিক নিলো'
                        when j.txn_type =7 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'মাালিক দিলো '
                        when j.txn_type =8 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'ক্যাশ এডজাস্টমেন্ট '
                    end::text as txn_type
            from tallykhata_v2_live.public.journal as j 
            inner join tallykhata_v2_live.public.account as a on j.account_id  = a.id
            where j.is_active =true
            and j.create_date ::date >='{from_date}'
            and j.create_date ::date < '{to_date}'
            and j.tallykhata_user_id ='{user_id}'
            ;    
            '''
    elif category == 'FROM_JOURNAL' and customer_need == 'CUSTOMER_LIST':
        query = f'''
                        SELECT
                            COALESCE(tbl_1.create_date::text, 'Not Updated') AS Date,
                            tbl_1.name ,
                            tbl_1.contact,
                                CASE 
                                WHEN tbl_1.type = 2 THEN 'CUSTOMER'
                                WHEN tbl_1.type = 3 THEN 'SUPPLIER'
                                ELSE tbl_1.type::text
                            END AS type,
                            -- Calculate DEBO and PABO columns
                            CASE 
                                WHEN COALESCE(tbl_2.total_sales, 0) + tbl_1.total_jer - COALESCE(tbl_2.total_credit_return, 0) > 0 
                                THEN COALESCE(tbl_2.total_sales, 0) + tbl_1.total_jer - COALESCE(tbl_2.total_credit_return, 0)
                                ELSE 0
                            END AS PABO,
                            CASE 
                                WHEN COALESCE(tbl_2.total_sales, 0) + tbl_1.total_jer - COALESCE(tbl_2.total_credit_return, 0) < 0 
                                THEN COALESCE(tbl_2.total_sales, 0) + tbl_1.total_jer - COALESCE(tbl_2.total_credit_return, 0)
                                ELSE 0
                            END AS DEBO
                        FROM
                            (
                            SELECT
                                a.create_date,
                                a.name,
                                a.tallykhata_user_id ,
                                a.contact,
                                a.id,
                                a.start_balance AS total_jer,
                                a.type
                            FROM
                                account a
                            WHERE
                                1 = 1
                                AND a.tallykhata_user_id = '{user_id}'
                                AND a.is_active IS TRUE
                                AND a.type != 1
                                    ) AS tbl_1
                        LEFT JOIN
                                    (
                            SELECT
                                j.tallykhata_user_id ,
                                j.account_id ,
                                sum(j.amount) AS total_sales,
                                sum(j.amount_received) AS total_credit_return
                            FROM
                                journal j
                            WHERE
                                1 = 1
                                AND j.tallykhata_user_id = '{user_id}'
                                AND j.create_date::date >= '{from_date}'
                                AND j.create_date::date < '{to_date}'
                                AND j.is_active IS TRUE
                            GROUP BY
                                1,
                                2
                                    ) AS tbl_2 ON
                            tbl_1.tallykhata_user_id = tbl_2.tallykhata_user_id
                            AND tbl_1.id = tbl_2.account_id
                        ORDER BY
                            tbl_1.create_date desc;
        '''
    elif category == 'FROM_HISTORY' and customer_need == 'CUSTOMER_LIST':
        query = f'''    
            SELECT
                ha."name",
                ha.contact,
                CASE
                    WHEN ha."type" = 2 THEN 'CUSTOMER'
                    WHEN ha."type" = 3 THEN 'SUPPLIER'
                    ELSE 'UNKNOWN'
                END AS external_user_type,
                ha.create_date,
                max(hj.txn_date) AS last_txn,
                ha.start_balance AS START_BALANCE,
                CASE
                    WHEN (SUM(hj.amount) + (ha.start_balance) - SUM(hj.amount_received)) < 0 THEN 
                        ABS(SUM(hj.amount) + (ha.start_balance) - SUM(hj.amount_received))
                    ELSE 0
                END AS debo_amount,
                CASE
                    WHEN (SUM(hj.amount) + (ha.start_balance) - SUM(hj.amount_received)) >= 0 THEN 
                        (SUM(hj.amount) + (ha.start_balance) - SUM(hj.amount_received))
                    ELSE 0
                END AS pabo_amount
            FROM
                history_journal hj
            INNER JOIN history_account ha ON
                hj.account_id = ha.src_id
            WHERE
                1 = 1
                AND hj.batch_id IN (
                SELECT
                    DISTINCT(batch_id)
                FROM
                    history_journal
                WHERE
                    tallykhata_user_id = '{user_id}'
                    AND txn_date::date <= CURRENT_DATE
                    AND txn_date ::date>='{from_date}'
                )
                AND hj.tallykhata_user_id = '{user_id}'
                AND hj.is_active = TRUE
                AND ha.TYPE IN (2, 3)
            GROUP BY
                1,
                2,
                3,
                4,
                6
            ORDER BY
                last_txn DESC ;
        '''
    elif category == 'FROM_HISTORY' and customer_need == 'TRANSACTION_LIST':
        query = f'''
            select 
			j.amount,
			j.amount_received,
			j.txn_date::text as txn_date,
			j.description::text as description,
			j.tallykhata_user_id::text as mobile_no,
			a.contact::text as added_customer_mobile,
			a."name"::text as customer_name,
			case when j.txn_type =1 and j.txn_mode = 1 then 'নগদ বিক্রি'
				when j.txn_type =2 and j.txn_mode = 1 then 'নগদ কেনা'
				when j.txn_type =5 and j.txn_mode = 1 then 'খরচ'
				when j.txn_type =3 and j.txn_mode = 1 and coalesce(amount_received,0)>0 then 'বাকি বিক্রি আদায়'
				when j.txn_type =4 and j.txn_mode = 1 and coalesce(amount_received,0)>0 then 'বাকি কেনা'
				when j.txn_type =9 and j.txn_mode = 3 and coalesce(amount_received,0)>0 then 'বাকি আদায়'
				when j.txn_type =3 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'বাকি বিক্রি'
				when j.txn_type =4 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'বাকি কেনা পরিশোধ'
				when j.txn_type =10 and j.txn_mode = 3 and coalesce(amount,0)>0 then 'সাপ্লায়ার পেমেন্ট'
				when j.txn_type =11 and j.txn_mode = 3 and coalesce(amount,0)>0 then 'ডিজিটাল নগদ বিক্রি'
				when j.txn_type =6 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'মালিক নিলো'
				when j.txn_type =7 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'মাালিক দিলো '
				when j.txn_type =8 and j.txn_mode = 1 and coalesce(amount,0)>0 then 'ক্যাশ এডজাস্টমেন্ট '
		    end::text as txn_type
	from tallykhata_v2_live.public.history_journal as j 
	inner join tallykhata_v2_live.public.history_account as a on j.account_id  = a.id
	where j.is_active =true
	and j.create_date ::date >='{from_date}'
	and j.create_date ::date < '{to_date}'
	and j.tallykhata_user_id ='{user_id}';
        '''
    else:
        query = False

    return query


def service_health_check_report(service_name, partner_name):
    if service_name == 'MOBILE_RECHARGE' and partner_name in ('GP', 'ROBI', 'AIRTEL', 'TT', 'BL'):
        day_query = f'''
            select
                DATE_TRUNC('hour', tui.create_date) as cohort_hour,
                mobile_operator,
                status,
                CASE 
                    WHEN description ilike '%cannot use the any recharge service within 3.00 minutes of last successful transaction as last transfer amount is same as current requested amount.%' THEN '3006202: cannot use the any recharge service within 3.00 minutes of last successful transaction as last transfer amount is same as current requested amount.'
                    WHEN description ilike '%cannot use the same recharge service within 3.00 minutes of last successful transaction as last transfer amount is same as current requested amount.%' THEN '3006202: cannot use the any recharge service within 3.00 minutes of last successful transaction as last transfer amount is same as current requested amount.'
                    WHEN description ilike '%cannot use the same recharge service within 2.00 minutes of last successful transaction as last transfer amount is same as current requested amount.%' THEN 'cannot use the same recharge service within 2.00 minutes of last successful transaction as last transfer amount is same as current requested amount.'
                    WHEN description ilike '%Your account has been credited back for failed transaction number%' THEN 'Your account has been credited back for failed transaction number'
                    WHEN description ilike '%Invalid transfer value%' THEN 'Invalid transfer value'
                    WHEN description ilike '%next payment can be done after 5.00 minutes of last successful payment with same amount.%' THEN 'next payment can be done after 5.00 minutes of last successful payment with same amount.'
                    WHEN description ilike '%Invalid transfer value%' THEN 'Invalid transfer value'
                    WHEN description ilike '%210:Recharge request of Tk%' THEN '210:Recharge request is successful'
                    WHEN description ilike '%210:Recharge request of Tk%' THEN '210:Recharge request is successful'
                    WHEN description ilike '%cannot be processed as the daily number of transfer for%' THEN 'Your current request to transfer cannot be processed as the daily number of transfer and the maximum allowed number of transfer exceeded'
                    WHEN description ilike '%cannot be processed as you do not have enough credit.%' THEN 'Recharge Request cannot be processed as you do not have enough credit.'
                    WHEN description ilike '%Service:RC Error: Refill not accepted%' THEN 'Service:RC Error: Refill not accepted'
                    WHEN description ilike '%is under process, please try again later.%' THEN 'The previous request of the recipient is under process, please try again later.'
                    WHEN description ilike '%Service:RC Error: Max Balance Reached at IN%' THEN 'Request Failed Service:RC Error: Max Balance Reached at IN'
                    WHEN description ilike '%Service:TRRC Error: Refill not accepted%' THEN 'Request Failed Service:TRRC Error: Refill not accepted'
                    WHEN description ilike '%Service:RC Error: Other Error No Retry%' THEN 'Service:RC Error: Other Error No Retry'
                    WHEN description ilike '%Service:RC Error: Refill not accepted%' THEN 'Service:RC Error: Refill not accepted'
                    ELSE description
                END AS description,
                count(1),
                sum(amount)
            from
                top_up_info tui
            where
                1 = 1
                and tui.create_date >= current_date
                and mobile_operator = '{partner_name}'
                group by 1,2,3,4
            order by 1 desc;
        '''
        month_query = f'''
                select
                    DATE_TRUNC('day', tui.create_date)::date as cohort_hour,
                    mobile_operator,
                    status,
                    CASE 
                        WHEN description ilike '%cannot use the any recharge service within 3.00 minutes of last successful transaction as last transfer amount is same as current requested amount.%' THEN '3006202: cannot use the any recharge service within 3.00 minutes of last successful transaction as last transfer amount is same as current requested amount.'
                        WHEN description ilike '%cannot use the same recharge service within 3.00 minutes of last successful transaction as last transfer amount is same as current requested amount.%' THEN '3006202: cannot use the any recharge service within 3.00 minutes of last successful transaction as last transfer amount is same as current requested amount.'
                        WHEN description ilike '%cannot use the same recharge service within 2.00 minutes of last successful transaction as last transfer amount is same as current requested amount.%' THEN 'cannot use the same recharge service within 2.00 minutes of last successful transaction as last transfer amount is same as current requested amount.'
                        WHEN description ilike '%Your account has been credited back for failed transaction number%' THEN 'Your account has been credited back for failed transaction number'
                        WHEN description ilike '%Invalid transfer value%' THEN 'Invalid transfer value'
                        WHEN description ilike '%next payment can be done after 5.00 minutes of last successful payment with same amount.%' THEN 'next payment can be done after 5.00 minutes of last successful payment with same amount.'
                        WHEN description ilike '%Invalid transfer value%' THEN 'Invalid transfer value'
                        WHEN description ilike '%210:Recharge request of Tk%' THEN '210:Recharge request is successful'
                        WHEN description ilike '%210:Recharge request of Tk%' THEN '210:Recharge request is successful'
                        WHEN description ilike '%cannot be processed as the daily number of transfer for%' THEN 'Your current request to transfer cannot be processed as the daily number of transfer and the maximum allowed number of transfer exceeded'
                        WHEN description ilike '%cannot be processed as you do not have enough credit.%' THEN 'Recharge Request cannot be processed as you do not have enough credit.'
                        WHEN description ilike '%Service:RC Error: Refill not accepted%' THEN 'Service:RC Error: Refill not accepted'
                        WHEN description ilike '%is under process, please try again later.%' THEN 'The previous request of the recipient is under process, please try again later.'
                        WHEN description ilike '%Service:RC Error: Max Balance Reached at IN%' THEN 'Request Failed Service:RC Error: Max Balance Reached at IN'
                        WHEN description ilike '%Service:TRRC Error: Refill not accepted%' THEN 'Request Failed Service:TRRC Error: Refill not accepted'
                        WHEN description ilike '%Service:RC Error: Other Error No Retry%' THEN 'Service:RC Error: Other Error No Retry'
                        WHEN description ilike '%Service:RC Error: Refill not accepted%' THEN 'Service:RC Error: Refill not accepted'
                        ELSE description
                    END AS description,
                    count(1),
                    sum(amount)
                from
                    top_up_info tui
                where
                    1 = 1
                    and tui.create_date >= DATE_TRUNC('month', CURRENT_DATE)
                    and mobile_operator = '{partner_name}'
                    group by 1,2,3,4
                order by 1 desc;
        '''

        query = {
            'day_query': day_query,
            'month_query': month_query
        }
    elif service_name == 'MONEY_OUT' and partner_name in ('NAGAD', 'ROCKET'):
        day_query = f'''
            select
                DATE_TRUNC('hour',create_date) as cohort_hour,
                status,
                count(1),
                sum(amount)
            from
                transaction_info ti
            where
                1 = 1
                and ti.create_date >= current_date
                and financial_institute = '{partner_name}'
            group by
                1,2
                order by 1 desc;
        '''
        month_query = f'''
            select
                DATE_TRUNC('day', create_date)::date as cohort_hour,
                status,
                count(1),
                sum(amount)
            from
                transaction_info ti
            where
                1 = 1
                and ti.create_date >= DATE_TRUNC('month', CURRENT_DATE)
                and financial_institute = '{partner_name}'
            group by
                1,2
            order by 1 desc;
        '''

        query = {
            'day_query': day_query,
            'month_query': month_query
        }
    elif service_name == 'MONEY_IN' and partner_name in ('ROCKET'):
        day_query = f'''
            select
                date_trunc('hour',create_date),
                status,
                count(*) as txn_count,
                count(distinct wallet) as unique_users, 
                sum(amount)
            from
                dbbl_transaction dt
            where
                1 = 1
                and create_date >= current_date
            group by
                1,2;
        '''
        month_query = f'''
            select
                date_trunc('day',create_date),
                status,
                count(*) as txn_count,
                count(distinct wallet) as unique_users, 
                sum(amount)
            from
                dbbl_transaction dt
            where
                1 = 1
                and create_date >= DATE_TRUNC('month',CURRENT_DATE)
            group by
                1,2;
        '''

        query = {
            'day_query': day_query,
            'month_query': month_query
        }
    elif service_name == 'MONEY_IN' and partner_name in ('NAGAD'):
        day_query = f'''
            select
                date_trunc('hour',create_date),
                status,
                count(1) as txn_count,
                count(distinct wallet) as unique_user,
                sum(amount)
            from
                nagad_txn nt
            where
                1 = 1
                and create_date >= current_date
            group by
                1,2;
        '''
        month_query = f'''
            select
                date_trunc('day',create_date),
                status,
                count(1) as txn_count,
                count(distinct wallet) as unique_user,
                sum(amount)
            from
                nagad_txn nt
            where
                1 = 1
                and create_date >= DATE_TRUNC('month',CURRENT_DATE)
            group by
                1,
                2;
        '''

        query = {
            'day_query': day_query,
            'month_query': month_query
        }
    elif service_name == 'CASH_OUT_TO_BANK' and partner_name in ('CBL', 'BEFTN'):
        if partner_name == 'CBL':
            print('Reached CBL query selection')
            day_query = f'''
                select
                    date_trunc('hour',issue_time) + interval '6 hours', 
                    status,
                    count(1) as txn_count,
                    count(distinct profile_id) as unique_user_count,
                    sum(amount) as total_amount
                from
                    bank_txn_request btr
                where
                    1 = 1
                    and issue_time >= current_date - interval '6 hours'
                    and txn_request_type = 'CASH_OUT'
                    and bank_swift_code = 'CIBLBDDH'
                group by
                    1,
                    2;
            '''
            month_query = f'''
                select
                    DATE_TRUNC('day',issue_time) , 
                    status,
                    count(1) as txn_count,
                    count(distinct profile_id) as unique_user_count,
                    sum(amount) as total_amount
                from
                    bank_txn_request btr
                where
                    1 = 1
                    and issue_time >= DATE_TRUNC('month', CURRENT_DATE)
                    and txn_request_type = 'CASH_OUT'
                    and bank_swift_code = 'CIBLBDDH'
                group by
                    1,
                    2
                order by 1 desc;
            '''
        else:
            day_query = f'''
                select
                    date_trunc('hour',issue_time) + interval '6 hours', 
                    status,
                    count(1) as txn_count,
                    count(distinct profile_id) as unique_user_count,
                    sum(amount) as total_amount
                from
                    bank_txn_request btr
                where
                    1 = 1
                    and issue_time >= current_date - interval '6 hours'
                    and txn_request_type = 'CASH_OUT'
                    and bank_swift_code != 'CIBLBDDH'
                group by
                    1,
                    2;
            '''
            month_query = f'''
                select
                    DATE_TRUNC('day',issue_time) , 
                    status,
                    count(1) as txn_count,
                    count(distinct profile_id) as unique_user_count,
                    sum(amount) as total_amount
                from
                    bank_txn_request btr
                where
                    1 = 1
                    and issue_time >= DATE_TRUNC('month', CURRENT_DATE)
                    and txn_request_type = 'CASH_OUT'
                    and bank_swift_code != 'CIBLBDDH'
                group by
                    1,
                    2
                order by 1 desc;
            '''
        query = {
            'day_query': day_query,
            'month_query': month_query
        }
    else:
        query = False

    return query


def service_health_query(service_name, partner_name):
    if service_name == 'MOBILE_RECHARGE' and partner_name in ('GP', 'ROBI', 'AIRTEL', 'TT', 'BL'):
        query = f'''
            select
                create_date,
                txn_id,
                amount,
                status,
                mobile_operator,
                vendor_name,
                description
            from
                top_up_info tui
            where
                1 = 1
                and mobile_operator = '{partner_name}'
                and create_date <= now() - interval '5 minutes'
            order by
                id desc
            limit 100;
        '''
    elif service_name == 'MONEY_OUT' and partner_name in ('NAGAD', 'ROCKET'):
        query = f'''
            select
                create_date,
                from_wallet,
                external_wallet ,
                tally_pay_txn_id ,
                external_txn_id ,
                amount,
                status,
                financial_institute,
                request_id ,
                extra_info 
            from
                transaction_info ti
            where
                1 = 1
                and financial_institute = '{partner_name}'
            order by
                id desc
                limit 100;
        '''
    elif service_name == 'CASH_OUT_TO_BANK' and partner_name in ('CBL'):
        query = f'''
            select
                btr.id,
                p.wallet_no,
                btr.issue_time,
                btr.amount,
                btr.status,
                btr.core_txn_id,
                btr.bank_swift_code ,
                b2.bank_name,
                b.branch_name
            from
                bank_txn_request btr
            inner join profile p on
                btr.profile_id = p.user_id
            inner join bank_account ba on
                btr.account_id = ba.id
            inner join branch b on
                ba.routing_number = b.routing_number
            inner join bank b2 on
                b2.id = b.bank_id
            where
                1 = 1
                and btr.bank_swift_code = 'CIBLBDDH'
                and btr.txn_request_type = 'CASH_OUT'
                and issue_time <= now() - interval '5 minutes'
            order by
                id desc
            limit 100;
        '''
    elif service_name == 'CASH_OUT_TO_BANK' and partner_name in ('BEFTN'):
        query = f'''
            select
                btr.id,
                p.wallet_no,
                btr.issue_time,
                btr.amount,
                btr.status,
                btr.core_txn_id,
                btr.bank_swift_code ,
                b2.bank_name,
                b.branch_name
            from
                bank_txn_request btr
            inner join profile p on
                btr.profile_id = p.user_id
            inner join bank_account ba on
                btr.account_id = ba.id
            inner join branch b on
                ba.routing_number = b.routing_number
            inner join bank b2 on
                b2.id = b.bank_id
            where
                1 = 1
                and btr.bank_swift_code != 'CIBLBDDH'
                and btr.txn_request_type = 'CASH_OUT'
                and issue_time <= now() - interval '5 minutes'
            order by
                id desc
            limit 100;
        '''
    elif service_name == 'CASH_OUT_TO_BANK' and partner_name in ('VISA'):
        query = f'''
            SELECT
                id,
                wallet_no,
                create_date ,
                amount ,
                status,
                escrow_init_txn_id ,
                request_id,
                bank_name ,
                description
            FROM
                card_txn_log
            WHERE
                1 = 1
                AND channel = 'VISA'
                AND transaction_type = 'VISA_TRANSFER'
                AND create_date <= now() - INTERVAL '5 minutes'
            ORDER BY
                id DESC
            LIMIT 100;
        '''
    elif service_name == 'CASH_OUT_TO_BANK' and partner_name in ('NPSB'):
        query = f'''
                    SELECT
                        id,
                        from_wallet,
                        create_date ,
                        amount ,
                        status,
                        escrow_initiate_txn_id ,
                        request_id,
                        bank_swift_code,
                        description
                    FROM
                        bank_transaction_info
                    WHERE
                        1 = 1
                        AND channel IN ('NPSB', 'MTB')
                        AND create_date <= now() - INTERVAL '5 minutes'
                    ORDER BY
                        id DESC
                    LIMIT 100;
        '''
    elif service_name == 'MONEY_IN' and partner_name in ('NAGAD'):
        query = f'''
            select
                create_date,
                wallet ,
                client_mobile_no ,
                amount ,
                tp_transaction_number,
                txn_time,
                status ,
                nagad_status ,
                nagad_status_code ,
                issuer_payment_ref_no ,
                issuer_payment_date_time ,
                cancel_issuer_ref_no,
                cancel_issuer_date_time,
                credit_collection_id,
                order_id ,
                order_date_time,
                payment_reference_id
            from
                nagad_txn nt
                where 1=1
                and create_date <= now() - interval '5 minutes'
            order by
                id desc
                limit 100;
        '''
    elif service_name == 'MONEY_IN' and partner_name in ('ROCKET'):
        query = f'''
            select
                create_date,
                wallet,
                card_name,
                amount ,
                tp_transaction_number,
                rrn as rocket_txn_num,
                status ,
                "result" as rocket_status,
                result_code ,
                dbbl_txn_id ,
                txn_ref_no ,
                description ,
                txn_date
            from
                dbbl_transaction dt
            where
                1 = 1
                and create_date <= now() - interval '5 minutes'
            order by
                id desc
            limit 100;
        '''
    else:
        query = False

    return query


def corporate_merchant_pre_registration_check(wallet):
    query_1 = f'''
        select
            wallet_no
        from
            profile p
        where
            1 = 1
            and wallet_no = '{wallet}';
    '''

    query_2 = f'''
        select
            owner_name
        from
            accounts a
        where
            1 = 1
            and a.owner_name = '{wallet}';
    '''

    query = {
        'profile': query_1,
        'accounts': query_2
    }

    return query


def get_event_app_event(wallet, user_id, from_date, to_date):
    query = f'''
        select
            created_at,
            "level",
            event_name ,
            message ,
            details ,
            user_id ,
            app_version 
        from
            eventapp_event ee
        where
            1 = 1
            and user_id in ('{wallet}', '{user_id}')
            and created_at  >= '{from_date}'
	        and created_at <= '{to_date}'
        order by
            id desc;
    '''

    return query


def get_merchant_id(wallet):
    query = f'''
        select
            wallet_no,
            merchant_id
        from
            profile p
        where
            1 = 1
            and wallet_no = '{wallet}';
    '''

    return query


def tallypay_issuer_query(from_date, to_date, merchant_id):
    query = f'''
        select
            request_id ,
            request ,
            response ,
            create_date,
            update_date,
            process_time
        from
            request_log rl
        where
            1 = 1
            and create_date >= '{from_date}'
            and create_date <= '{to_date}'
            and request ilike '%"receiver_wallet_no":"{merchant_id}"%'
        order by
            id desc;
    '''

    return query


def tallypay_activity_log(from_date, to_date, user_id):
    query = f'''
        select
            user_id ,
            user_name ,
            request_method ,
            url ,
            long_text ,
            response ,
            response_code ,
            created_at
        from
            activity_log al
            where 1=1
            and user_id = {user_id}
            and created_at >= '{from_date}'
            and created_at <= '{to_date}'
        order by
            id desc;
    '''

    return query


def sqr_timeout_cases(start_date, end_date):
    query = f'''
        select
            request_id,
            request ,
            response ,
            create_date ,
            update_date
        from
            request_log rl
        where
            1 = 1
            and response = 'timeout'
            and create_date <='{end_date}'
	        and create_date >='{start_date}'
        order by
            id desc;
    '''

    return query


def sqr_data_download_query(wallet):
    backend_query = f'''
        select 
            wallet_no
           ,merchant_id
           ,full_name 
           ,biz_name
           ,concat('',user_id,'/',wallet_no,'/details') as BIZ_QR
        from profile p 
            where 1=1
            and wallet_no in ({wallet});
    '''

    return backend_query


def get_ec_data(number):
    query = f'''
        select
            pin,
            national_id
        from
            ec_basic_info ebi
        where
            1 = 1
            and (
        national_id in ('{number}')
                or pin in ('{number}')
        )
        order by
            id desc
        limit 1;
    '''

    return query


def get_wallet_query(number):
    query = f'''
        select
            p.wallet_no,
            d.id_no,
            p.merchant_id
        from
            profile p
        inner join "document" d on
            p.user_id = d.user_id
        where
            1 = 1
            and d.doc_type = 'NID'
            and p.wallet_no = '{number}'
        ;
    '''

    return query


def get_wallet_from_nid(nid, pin):
    query = f'''
            select
                p.wallet_no,
                d.id_no,
                p.merchant_id
            from
                profile p
            inner join "document" d on
                p.user_id = d.user_id
            where
                1 = 1
                and d.doc_type = 'NID'
                and d.id_no in ('{nid}','{pin}')
            ;
    '''

    return query


def sqr_merchant_id_query(wallet):
    query_1 = f'''
        select
            wallet_no,
            merchant_id
        from
            profile p
        where
            1 = 1
            and wallet_no = '{wallet}';
    '''

    return query_1


def sqr_request_log_query(merchant_id):
    query_2 = f'''
            select
                response
            from
                request_log rl
            where
                1 = 1
                and request ilike '%"receiver_wallet_no":"{merchant_id}"%'
            order by
                id desc
            limit 5;
        '''
    return query_2


def get_wallet_details(wallet):
    query1 = f'''
        select
            p.wallet_no,
            p.identity_status,
            p.bank_account_status,
            p.merchant_id ,
            p.is_sim_nid_verified ,
            m.mfs_name ,
            ma."number" ,
            ma.status ,
            ma.added_on ,
            ma.account_name
        from
            profile p
        inner join mfs_account ma on
            ma.user_id = p.user_id
        inner join mfs m on
            ma.provider_id = m.id
        where
            1 = 1
            and p.wallet_no = '{wallet}'
        order by
            ma.id desc
                ;
    '''

    query2 = f'''
        select
        p.wallet_no ,
        p.identity_status ,
        p.bank_account_status ,
        ba.is_active ,
        b2.bank_name ,
        ba.account_name as bank_account_name,
        ba.account_number,
        b.routing_number ,
        b.branch_name ,
        b.branch_name_bn ,
        ba.is_active ,
        ba.is_verified
    from
        profile p
    inner join bank_account ba on
        p.user_id = ba.user_id
    inner join branch b on
        b.routing_number = ba.routing_number
    inner join bank b2 on
        b.bank_id = b2.id
    where
        1 = 1
        and p.wallet_no = '{wallet}'
        order by ba.id desc;
    '''

    query = {
        'query1': query1,
        'query2': query2
    }

    return query


def selfie_matching_score(wallet):
    selfie_matching_score = f'''        
        SELECT
            created_at,
            profile_picture_matching_score
        FROM
            nobopay_nid_gw.public.profile_photo_matching_score
        WHERE
            1 = 1
            AND request_id ILIKE '%{wallet}%'
            ORDER BY id DESC;
    '''
    print(selfie_matching_score)
    return selfie_matching_score



def merchant_id(wallet):
    statement_query = f'''
            SELECT
                p.wallet_no,
                p.merchant_id,
                p.identity_status ,
                p.bank_account_status ,
                p.created_at ,
                p.is_sim_nid_verified 
            FROM
                profile p
            WHERE
                1 = 1
                AND p.merchant_id = '{wallet}';
        '''
    return statement_query

def limit_update_check(wallet):
    statement_query = f'''
            SELECT
                type
            FROM
                nobopay_api.public.npapi_npwallettxnlimit
            WHERE
                wallet = '{wallet}';
        '''
    return statement_query


def limit_info(wallet_num):
    statement_query = f'''
                        SELECT
                            CASE 
                                WHEN "type" = 'CASH_IN_FROM_BANK' THEN 'Add money (Bank)'
                                WHEN "type" = 'CASH_IN_FROM_CARD' THEN 'Add money (Card)'
                                WHEN "type" = 'CASH_IN_FROM_EXTERNAL' THEN 'Add Money (Nagad/Rocket)'
                                WHEN "type" = 'CASH_OUT_TO_BANK' THEN 'Bank Transfer'
                                WHEN "type" = 'CASH_OUT_TO_BANK_NPSB' THEN 'NPSB Bank Transfer'
                                WHEN "type" = 'CASH_OUT_TO_EXTERNAL' THEN 'Nagad/Rocket Transfer'
                                WHEN "type" = 'CREDIT_COLLECTION' THEN 'Super QR Payment Received (Other FIs)'
                                WHEN "type" = 'MOBILE_RECHARGE' THEN 'Mobile Recharge'
                                WHEN "type" = 'NPSB_TRANSFER' THEN 'NPSB Bank Transfer'
                                WHEN "type" = 'NPSB_TRANSFER_CREDIT' THEN 'SQR Payment'
                                WHEN "type" = 'NPSB_TRANSFER_CREDIT_BKASH' THEN 'SQR Payment(bKash)'
                                WHEN "type" = 'PAYMENT' THEN 'SQR Payment Received (Other FIs)'
                                WHEN "type" = 'PAYMENT_EXTERNAL' THEN 'SQR Payment Received (Other FIs)'
                                WHEN "type" = 'SEND_MONEY' THEN 'Nagad/Rocket Transfer'
                                WHEN "type" = 'VISA_TRANSFER' THEN 'VISA Transfer'
                                ELSE "type" 
                            END AS transaction_type,
                            user_type,
                            min_amount_per_txn,
                            max_amount_per_txn,
                            max_count_per_day,
                            max_amount_per_day,
                            max_count_per_month,
                            max_amount_per_month,
                            status
                        FROM
                            nobopay_api.public.npapi_npwallettxnlimit
                        WHERE
                            wallet = '{wallet_num}';

        '''
    return statement_query



def nid_data(nid_num):
    statement_query = f'''
                        SELECT
                            id,
                            created_at,
                            nid_no,
                            sim_nid_verification_failed_count,
                            updated_at
                        FROM
                            nid_usage_log nul
                        WHERE
                            nid_no = '{nid_num}'
                        ;

        '''
    return statement_query



def wallets_against_nid(nid_num):
    statement_query = f'''
                        SELECT
                            	p.wallet_no,
                                d.id_no,
                                d.is_active,
                                d.status,
                                p.full_name,
                                p.is_biz_user,
                                p.biz_type,
                                p.biz_name,
                                p.identity_status,
                                p.bank_account_status,
                                p.created_at,
                                p.is_pin_set,
                                p.modified_date,
                                p.biz_qr_code,
                                p.merchant_id
                                                    FROM
                            "document" d
                        INNER JOIN profile p ON
                            p.user_id = d.user_id
                        WHERE
                            1 = 1
                            AND d.id_no = '{nid_num}'
                        ORDER BY
                            id DESC 
                        ;
        '''
    return statement_query

def txn_details(txn_num):
    statement_query = f'''
                        SELECT 
                            date,
                            amount,
                            tt.txn_type ,
                            tt.charge_flag ,
                            tag,
                            transaction_number,
                            trace_number,
                            note
                        FROM transfers t
                        INNER JOIN np_transaction_type tt 
                            ON tt.transfer_type = t.type_id
                        WHERE 1=1
                          AND t.transaction_number ='{txn_num}'
                            AND tt.id NOT IN (243)
                        ORDER BY t.id DESC;
        '''
    return statement_query



def ticket_details(wallet):
    statement_query = f'''
            SELECT
                    *
                FROM
                    compliance_project.duplicate_removed_compliance_data drcd
                WHERE
                    drcd.wallet_number = '{wallet}'
                ;

        '''
    return statement_query