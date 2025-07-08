# Connection to PGSQL and MySQL takes place here
import mysql.connector
import psycopg2
import pymssql
from mysql.connector import Error


# Function to connect to mysql server and retrieve results
def run_mysql_server(query, db_name):
    queryset = None
    mysql_conn = None
    cursor = None

    if db_name == "sms_prod":
        host = ""
        db = db_name
        user = ""
        password = ""
        ssl_disabled = True
    elif db_name == "sc_sms":
        host = ""
        db = db_name
        user = ""
        password = ""
        ssl_disabled = False
    elif db_name == "":
        host = ""
        db = db_name
        user = ""
        password = ""
        ssl_disabled = True
    elif db_name == "nobopay_core":
        host = ""
        db = db_name
        user = ""
        password = ""
        ssl_disabled = False
    else:
        host = None
        db = db_name
        user = None
        password = None
        ssl_disabled = None
    try:

        mysql_conn = mysql.connector.connect(
            host=host,
            database=db,
            user=user,
            password=password,
            use_pure=True
        )

        cursor = mysql_conn.cursor()
        cursor.execute(query)

        if cursor.with_rows:
            queryset = cursor.fetchall()
            print("Rows produced by statement '{}':".format(query))
            print(queryset)

            print(f'''
                            Details are: 
                            Host: {host}
                            Database: {db}
                            User: {user}
                            Password: {password}

                            Query is: \n{query}

                            Queryset is: \n{queryset}
                            ''')


        else:
            queryset = "No result set to fetch from."
            print("Number of rows affected by statement '{}': {}".format(query, cursor.rowcount))

        return queryset

        return queryset
        # cursor.close()

    except Error as e:
        queryset = "Failed to connect to MySQL. Error is: " + str(e) + " " + db_name + " " + host
        return queryset
    finally:
        print('Reached MySQL finally: ')
        # print(mysql_conn)
        # print(mysql_conn.is_connected())
        if mysql_conn is None:
            print("Failed to establish connection to Database (Check if you are connected to internet and vpn)")
        elif mysql_conn.is_connected():
            print("Connection to MySQL is successful: ", db_name, " ", host)
            cursor.close()
            mysql_conn.close()
        else:
            print("Connection to MySQL is successful: ", db_name, " ", host)
            cursor.close()
            mysql_conn.close()


# Function to make connection PostgreSQL server and retrieve results
def run_pgsql_server(query, db_name):
    # VPN CONNECTION MANDATORY
    queryset = None
    pg_conn = None
    # Host and db selector
    if db_name == "tallykhata_v2_live":
        host = ""
        database = db_name
        user = "django_portal"
        password = ""
    elif db_name == "tallykhata_log":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "tallykhata_sqa":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "nobopay_payment_gw":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "sms_prod":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "topup_service":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == 'nobopay_nid_crawler':
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "wso2_db":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "keycloak":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "backend_db":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "nobopay_nid_gw":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "nobopay_nid_gw":
        host = ""
        database = db_name
        user = "django_portal"
        password = ""
    elif db_name == "tallypay_issuer":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "tallypay_to_fi_integration":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "nobopay_core":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "tp_bank_service":
        host = ""
        database = db_name
        user = ""
        password = ""
    elif db_name == "nobopay_api":
        host = ""  # "10.10.66.2" "10.82.82.10"
        database = db_name
        user = ""
        password = ""
    elif db_name == "pne_execution_log_local":
        host = ""
        database = "pne_execution_log"
        user = ""
        password = ""
    elif db_name == "pne_execution_log_live":
        host = ""
        database = ""
        user = ""
        password = ""
    else:
        host = ""
        database = db_name
        user = ""
        password = ""

    try:
        print(db_name)
        print('connecting to pgSQL db name:', db_name)
        pg_conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
        )
        print('Connection to PostGres successful: ', host, " ", db_name)

        # create pg cursor
        cur = pg_conn.cursor()
        cur.execute(query)

        # fetch the query results here
        queryset = cur.fetchall()
        cur.close()
        # print(queryset)
        return queryset

    except(Exception, psycopg2.DataError) as error:
        queryset = "Failed to connect to PostGres. Error is: " + str(error)
        # print(queryset)
        return queryset
    finally:
        if pg_conn is not None:
            pg_conn.close()


# MS SQL Connections
def run_mssql_server(query, db_name):
    if db_name == "ICPDatabase":
        host = ""
        database = db_name
        user = ""
        password = ""

    conn = pymssql.connect(
        server=host,
        user=user,
        password=password,
        database=database
    )

    cursor = conn.cursor()
    cursor.execute(query)
    queryset = cursor.fetchall()

    return queryset
