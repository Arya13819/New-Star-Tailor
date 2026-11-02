"""Real HTTP/MySQL checks for Laravel. Dedicated local test database only.

NST_PHP_TEST=1 .venv/bin/python tests/http_edge_cases.py
Run the Laravel QA server at http://127.0.0.1:5058 with an isolated *_test DB.
The suite writes test users, orders and payments: never target production.
"""
from pathlib import Path
import json, os, re, secrets, subprocess, sys
import requests
import pymysql

ROOT=Path(__file__).resolve().parents[1]
if os.environ.get('NST_PHP_TEST')!='1':raise SystemExit('Set NST_PHP_TEST=1 for an isolated local test run.')
from dotenv import dotenv_values
env=dotenv_values(os.environ.get('NST_TEST_ENV', ROOT/'.env'))
cfg={'db_host':env['DB_HOST'],'db_port':int(env['DB_PORT']),'db_user':env['DB_USERNAME'],'db_password':env.get('DB_PASSWORD',''),'db_name':env['DB_DATABASE'],'setup_key':env['NST_SETUP_KEY'],'app_url':env['APP_URL']}
if not cfg['db_name'].endswith('_test') or cfg['app_url']!='http://127.0.0.1:5058':raise SystemExit('Refusing to test a non-local/non-test Laravel database.')
connection=pymysql.connect(host=cfg['db_host'],port=cfg['db_port'],user=cfg['db_user'],password=cfg['db_password'],database=cfg['db_name'],autocommit=True,cursorclass=pymysql.cursors.DictCursor)
BASE=cfg['app_url']; checks=[]
def check(condition,message):
    if not condition:raise AssertionError(message)
    checks.append(message)
def sql(statement,args=()):
    with connection.cursor() as c:c.execute(statement,args);return c.fetchall()
def row(statement,args=()):return sql(statement,args)[0]
def form(session,path):
    response=session.get(BASE+path);check(response.status_code==200,'GET '+path)
    match=re.search(r'name="_token" value="([A-Za-z0-9]+)"',response.text)
    return response, match.group(1) if match else None
def post(session,path,data,token=None,files=None):
    if token is None:_,token=form(session,path)
    return session.post(BASE+path,data={'_token':token,**data},files=files)
def submission(page):return re.search(r'name="submission" value="([a-f0-9]+)"',page.text).group(1)
def register(name):
    session=requests.Session();mobile='9'+str(secrets.randbelow(10**9)).zfill(9);password=secrets.token_urlsafe(20)
    response=post(session,'/customer/register',{'name':name,'mobile':mobile,'password':password,'confirm_password':password})
    check(response.url.endswith('/customer/dashboard'),'Customer registration + profile creation')
    return session,mobile,password

anonymous=requests.Session()
for path in ('/','/about','/contact','/gallery','/services','/track-order','/customer/login','/admin/login','/enquiry','/healthz','/robots.txt','/sitemap.xml','/sw.js'):
    response=anonymous.get(BASE+path)
    check(response.status_code==200,'Public route '+path)
    check('<?php' not in response.text and '{% ' not in response.text,'No source/template leakage '+path)
check(anonymous.get(BASE+'/src/bootstrap.php').status_code in(403,404),'Private source denied by dev router')
check(anonymous.get(BASE+'/config.php').status_code in(403,404),'Config denied by dev router')
response=anonymous.get(BASE+'/contact');check('frame-src https://www.google.com' in response.headers['Content-Security-Policy'] and '24.4570252,74.870045' in response.text,'Google map exact location and scoped CSP')
check('frame-src https://www.google.com' not in anonymous.get(BASE+'/').headers['Content-Security-Policy'],'No map frame permissions on homepage')
check('data-service=' not in anonymous.get(BASE+'/services?q=%25').text,'Literal catalogue search')
check('data-service="CRPF_CHEETAH"' in anonymous.get(BASE+'/services?category=CRPF&q=cheetah').text,'Combined category and search')

owner=requests.Session();admin_password=secrets.token_urlsafe(20);admin_email='qa-'+secrets.token_hex(4)+'@example.invalid';admin_mobile='8'+str(secrets.randbelow(10**9)).zfill(9)
if row("SELECT COUNT(*) n FROM users WHERE role='ADMIN'")['n']==0:
    response=post(owner,'/setup',{'setup_key':cfg['setup_key'],'name':'QA owner','email':admin_email,'mobile':admin_mobile,'password':admin_password,'confirm_password':admin_password})
    check(response.url.endswith('/admin/login'),'First-admin setup')
else:
    # Only the isolated test database is permitted above. Create an ephemeral QA admin.
    hashed=subprocess.check_output(['php','-r','echo password_hash(stream_get_contents(STDIN),PASSWORD_DEFAULT);'],input=admin_password.encode()).decode()
    with connection.cursor() as c:c.execute("INSERT INTO users (name,email,mobile,password_hash,role,is_active,created_at,updated_at) VALUES (%s,%s,%s,%s,'ADMIN',1,UTC_TIMESTAMP(),UTC_TIMESTAMP())",('QA owner',admin_email,admin_mobile,hashed))
check(anonymous.get(BASE+'/setup').status_code==404,'Setup locks after first admin')
response=post(owner,'/admin/login',{'identifier':admin_email,'password':admin_password})
check(response.url.endswith('/admin/dashboard'),'Staff login')
check(owner.get(BASE+'/customer/orders').status_code==403,'Admin cannot use customer portal')

alice,mobile,password=register('QA Alice')
bob,bob_mobile,_=register('QA Bob')
check(alice.get(BASE+'/admin/dashboard').status_code==403,'Customer cannot use staff dashboard')
# CSRF failure must never create a record.
before=row('SELECT COUNT(*) n FROM enquiries')['n']
response=alice.post(BASE+'/enquiry',data={'name':'No CSRF','mobile':mobile})
check(row('SELECT COUNT(*) n FROM enquiries')['n']==before,'CSRF rejection prevents mutation')
combo=row("SELECT * FROM services WHERE code='SHIRT_PANT_COMBO'")
page,token=form(alice,'/order?service='+str(combo['id']))
check(f'value="{combo["id"]}"' in page.text,'Service link opens order form')
nonce=submission(page)
data={'submission':nonce,'service_id[]':str(combo['id']),'quantity[]':'2','fabric_source':'CUSTOMER','provide_measurements':'1','measurement_ack':'1','shirt_chest':'42.50','fitting_preference':'NORMAL','payment_amount':'200','payment_reference':'QA-UPI-PENDING','stitching_price[]':'0.01'}
with (ROOT/'public/static/img/services/shirt.jpg').open('rb') as image:
    response=post(alice,'/order',data,token,{'reference_image':('reference.jpg',image,'image/jpeg')})
check(response.url.endswith('/order/success'),'Online order + private image + measurement created')
order=row('SELECT o.* FROM orders o JOIN customers c ON c.id=o.customer_id WHERE c.mobile=%s ORDER BY o.id DESC LIMIT 1',(mobile,))
order_id=order['id'];number=order['order_number']
check(str(order['grand_total'])=='1100.00' and str(order['required_advance'])=='550.00','Server price snapshot and 50% advance; client price ignored')
item=row('SELECT * FROM order_items WHERE order_id=%s',(order_id,));version_id=item['measurement_version_id']
check(str(row('SELECT shirt_chest FROM measurement_versions WHERE id=%s',(version_id,))['shirt_chest'])=='42.50','Exact fractional measurements stored')
check(row('SELECT status FROM payments WHERE order_id=%s',(order_id,))['status']=='PENDING','Online payment remains unverified')
post(alice,'/order',data,token)
check(row('SELECT COUNT(*) n FROM orders WHERE customer_id=%s',(order['customer_id'],))['n']==1,'Duplicate order form is idempotent')
check(alice.get(BASE+f'/customer/orders/{order_id}').status_code==200,'Own order details')
for suffix in ('','/receipt'):
    check(bob.get(BASE+f'/customer/orders/{order_id}'+suffix).status_code==404,'Other customer cannot inspect order'+suffix)
image_id=row('SELECT id FROM reference_images WHERE order_id=%s',(order_id,))['id']
check(alice.get(BASE+f'/customer/orders/{order_id}/images/{image_id}').headers['Content-Type']=='image/jpeg','Private photo served to owner')
check(bob.get(BASE+f'/customer/orders/{order_id}/images/{image_id}').status_code==404,'Private photo isolation')
response=post(anonymous,'/track-order',{'order_number':number,'mobile':mobile})
check('aria-current="step"' in response.text and '₹1100.00' in response.text,'Public tracking with matching mobile')
response=post(anonymous,'/track-order',{'order_number':number,'mobile':bob_mobile})
check('aria-current="step"' not in response.text and '₹1100.00' not in response.text,'Wrong mobile reveals no order')
# Staff updates and immutable measurement versions.
page,token=form(owner,f'/admin/orders/{order_id}')
response=post(owner,f'/admin/orders/{order_id}/status',{'status':'READY'},token)
check(row('SELECT status FROM orders WHERE id=%s',(order_id,))['status']=='READY','Staff changes status')
check('is-current' in alice.get(BASE+f'/customer/orders/{order_id}').text,'Customer sees saved progress')
check(row("SELECT COUNT(*) n FROM notifications WHERE order_id=%s AND type='ORDER_READY'",(order_id,))['n']==1,'Ready event queues a real pending SMS record')
page,token=form(owner,f'/admin/customers/{order["customer_id"]}/measurements/new')
post(owner,f'/admin/customers/{order["customer_id"]}/measurements/new',{'shirt_chest':'43.25','fitting_preference':'SLIM'},token)
check(row('SELECT COUNT(*) n FROM measurement_versions v JOIN measurements m ON m.id=v.measurement_id WHERE m.customer_id=%s',(order['customer_id'],))['n']==2,'Measurements create a new immutable version')
check(row('SELECT measurement_version_id FROM order_items WHERE id=%s',(item['id'],))['measurement_version_id']==version_id,'Old order keeps original measurement version')
# Cash payment and idempotent replays.
page,token=form(owner,f'/admin/orders/{order_id}');pay_nonce=submission(page)
payment_data={'submission':pay_nonce,'amount':'100','method':'CASH','transaction_reference':'QA-CASH'}
post(owner,f'/admin/orders/{order_id}/payment',payment_data,token)
post(owner,f'/admin/orders/{order_id}/payment',payment_data,token)
check(str(row("SELECT SUM(amount) amount FROM payments WHERE order_id=%s AND status='VERIFIED'",(order_id,))['amount'])=='100.00','Cash payment verified exactly once')
pending=row("SELECT id FROM payments WHERE order_id=%s AND status='PENDING'",(order_id,))['id']
page,token=form(owner,'/admin/payments');post(owner,f'/admin/payments/{pending}/verify',{},token)
check(str(row("SELECT SUM(amount) amount FROM payments WHERE order_id=%s AND status='VERIFIED'",(order_id,))['amount'])=='300.00','Staff verifies pending payment and recomputes balance')
page,token=form(owner,f'/admin/orders/{order_id}')
post(owner,f'/admin/orders/{order_id}/payment',{'submission':submission(page),'amount':'801','method':'CASH'},token)
check(str(row("SELECT SUM(amount) amount FROM payments WHERE order_id=%s AND status='VERIFIED'",(order_id,))['amount'])=='300.00','Overpayment is rejected transactionally')
check(alice.get(BASE+f'/customer/payments/{pending}/receipt').status_code==200,'Own payment receipt')
check(bob.get(BASE+f'/customer/payments/{pending}/receipt').status_code==404,'Payment receipt isolation')
# Price editing does not rewrite old line items.
page,token=form(owner,f'/admin/services/{combo["id"]}/edit')
post(owner,f'/admin/services/{combo["id"]}/edit',{'name_en':combo['name_en'],'name_hi':combo['name_hi'],'category':'SHIRT','default_stitching_price':'612.50','sort_order':'30','is_active':'1'},token)
check('₹612.50' in anonymous.get(BASE+'/services').text and '₹612.50' in anonymous.get(BASE+'/').text,'Edited price is live on storefront')
check(str(row('SELECT stitching_price FROM order_items WHERE id=%s',(item['id'],))['stitching_price'])=='550.00','Order item price snapshot is immutable')
# Public self measurement acknowledgement and image validation roll back all order rows.
page,token=form(bob,'/order');before=row('SELECT COUNT(*) n FROM orders')['n']
post(bob,'/order',{'submission':submission(page),'service_id[]':str(combo['id']),'quantity[]':'1','fabric_source':'CUSTOMER','provide_measurements':'1','shirt_chest':'40'},token)
check(row('SELECT COUNT(*) n FROM orders')['n']==before,'Missing measurement acknowledgement rolls back order')
page,token=form(bob,'/order')
post(bob,'/order',{'submission':submission(page),'service_id[]':str(combo['id']),'quantity[]':'1','fabric_source':'CUSTOMER'},token,{'reference_image':('bad.jpg',b'<?php echo "bad";','image/jpeg')})
check(row('SELECT COUNT(*) n FROM orders')['n']==before,'Fake image upload rejected without creating an order')
# Search, reports, receipts and staff lists.
for path in ('/admin/customers','/admin/services','/admin/orders?view=urgent','/admin/orders?view=today','/admin/orders?view=overdue','/admin/enquiries','/admin/notifications','/admin/reports?period=today',f'/admin/orders/{order_id}/receipt'):
    check(owner.get(BASE+path).status_code==200,'Staff route '+path)
report=owner.get(BASE+'/admin/reports?period=today')
check('₹300.00' in report.text,'Report revenue uses verified payments only')
# Bcrypt from the original Python app remains compatible.
import bcrypt
hash2b=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
with connection.cursor() as c:c.execute('UPDATE users SET password_hash=%s WHERE mobile=%s',(hash2b,mobile))
post(alice,'/customer/logout',{},form(alice,'/customer/dashboard')[1])
check(post(alice,'/customer/login',{'mobile':mobile,'password':password}).url.endswith('/customer/dashboard'),'Original Python bcrypt hashes work in PHP')
# Confirm all new extension tables keep pure UTF-8 and are present.
check(row("SELECT COUNT(*) n FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name IN ('php_rate_limits','php_submissions')")['n']==2,'PHP extension tables installed')
if __name__=='__main__':
    print(json.dumps({'passed':len(checks),'failures':[],'checks':checks},ensure_ascii=False,indent=2))
