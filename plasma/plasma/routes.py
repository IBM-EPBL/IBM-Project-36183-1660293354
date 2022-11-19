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

Admin_Login = False

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            print('decorated_view')
            if not current_user.is_authenticated:
               print('not is_authenticated')
               return app.login_manager.unauthorized()
            urole = current_user.role
            print('urole', urole)
            if ((urole != role) and (role != "ANY")):
                print('unauthorized')
                return app.login_manager.unauthorized()      
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

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

@app.route("/")
@app.route("/home")
def home():
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
       return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, 
            password=hashed_password,
            contact_no=form.contact_no.data, gender=form.gender.data, role=form.role.data,
            blood_group=form.blood_group.data)
        db.session.add(user)
        db.session.commit()
        ibm_sync('user', [user.id, form.name.data, form.username.data, form.email.data, hashed_password, 
            form.contact_no.data, form.gender.data,
            form.role.data, form.blood_group.data])
        print(user)
        flash('Your account has been created! You are now able to log in', 'success')
        time.sleep(5)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', formsss=forms)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_operation'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            print("Login Success", user)
            next_page = request.args.get('next')
            return redirect(url_for('user_operation'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/user_operation", methods=['GET', 'POST'])
@login_required()
def user_operation():
    form1 = SearchForm()
    form2 = MessageForm()
    donors = []

    if form1.validate_on_submit() and form1.submit.data:
        donors = []
        blood_group = form1.blood_group.data
        data = User.query.filter_by(blood_group=blood_group, role='Donar').all()
        print('data', data)
        if data:
            for datam in data:
                if datam.email != current_user.email:
                    donors.append([datam.name, datam.email, datam.contact_no])

    if form2.validate_on_submit() and form2.submit.data:
        to_id = form2.to_id.data
        message = form2.message.data
        print(to_id, message)
        add_message = Message(from_id=current_user.email, to_id=to_id, message=message)
        db.session.add(add_message)
        db.session.commit()
        #ibm_sync('message', [add_message.id, current_user.email, form2.to_id.data, form2.message.data])

    messages = []
    text = Message.query.filter_by(to_id=current_user.email).all()
    if text:
        for t in text:
            messages.append([t.from_id, t.message])

    if len(donors)>0:
        donor_flag = True
    else:
        donor_flag = False
    return render_template('user_operation.html', title="Dashboard", form1=form1, form2=form2, 
        donors=donors, messages=messages, donor_flag=donor_flag)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


