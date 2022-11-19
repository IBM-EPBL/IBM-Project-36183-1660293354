from flask import render_template, url_for, flash, redirect, request
from plasma import app, db, bcrypt
from plasma.forms import RegistrationForm, SearchForm, LoginForm, MessageForm
from plasma.models import User, Message
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os, time
from functools import wraps
from sqlalchemy import and_, or_, not_
import ibm_db

def ibm_sync(table, values):
    host_name = 'ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud'
    port = '31321'
    uid = 'bpb00468'
    passcode = 'tgzHCHBroVLejGnG'
    DRIVER ='{IBM DB2 ODBC DRIVER}'
    database = 'bludb'
    protocol = 'TCPIP'
    SECURITY = 'SSL'
    SSL_C = 'Certificate.crt'

    conn_str='DRIVER='+DRIVER+';'+\
            'DATABASE='+database+';'+\
            'HOSTNAME='+host_name+';'+\
            'PORT='+port+';'+\
            'PROTOCOL='+protocol+';'+\
            'UID='+uid+';'+\
            'PWD='+passcode+';'+\
            'SECURITY='+SECURITY+';'+\
            'dsn=dashdb'
            #'AUTHENTICATION=SERVER'

    print(conn_str)
    #database=Db2-jw;hostname=55fbc997-9266-4331-afd3-888b05e734c0.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;port=31929;protocol=tcpip;uid=tnn10322;pwd=U6HFRVCJ509YWcF2

    #try connecting with an invalid user name
    start = time.time()
    try:
        ibm_db_conn = ibm_db.connect(conn_str,'','')
    except:
        print("Error in connection, sqlstate = ")
        errorState = ibm_db.conn_error()
        print(errorState)
        error_msg = ibm_db.conn_errormsg()
        print(error_msg)
    print('Time:', time.time()-start)

    try:
        server = ibm_db.server_info(ibm_db_conn)
        print(server)
        print('a1', server.DBMS_NAME, server.DBMS_VER, server.DB_NAME)
    except Exception as e:
        print("? server", e)
    #create table user(id int, name varchar(50), username varchar(50), email varchar(120), password varchar(60), contact_no varchar(20), gender varchar(20), role varchar(20), blood_group varchar(20))
    #create table message(id int, from_id varchar(120), to_id varchar(120), message varchar(120))
    try:
        if table == 'user':
            print('user')
            query_string = "insert into "+ table + " values (?,?,?,?,?,?,?,?,?)"
            params = ((values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8]), ) 
            print(params)
            stmt_select = ibm_db.prepare(ibm_db_conn, query_string)
            ibm_db.execute_many(stmt_select,params)
        if table == 'message':
            print('Message')
            query_string = 'insert into '+ table + ' values (?,?,?,?)'
            params = ((values[0], values[1], values[2], values[3]),) 
            stmt_select = ibm_db.prepare(ibm_db_conn, query_string)
            ibm_db.execute_many(stmt_select,params)            
    except Exception as e:
        print("? ops", e)

    ibm_db.close(ibm_db_conn)
    print('Closed')
