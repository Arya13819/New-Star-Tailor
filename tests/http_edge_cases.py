"""Additional Laravel workflow checks, using the same guarded local test configuration."""
import importlib.util
from pathlib import Path
import re
# Reuse the complete integration harness, which creates isolated random QA accounts.
spec=importlib.util.spec_from_file_location('suite',Path(__file__).with_name('http_integration.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
owner=s.owner;anonymous=s.anonymous
# Walk-in customer, unpriced service with an explicit urgent stitching quote, shop cloth.
response=s.post(owner,'/admin/customers/new',{'name':'QA Walk-in','mobile':'9777777711','address':'QA address'})
match=re.search(r'/admin/customers/(\d+)$',response.url);s.check(bool(match),'Staff creates a walk-in customer')
customer_id=int(match.group(1));shirt=s.row("SELECT id FROM services WHERE code='SHIRT'")['id']
page,token=s.form(owner,'/admin/orders/new?customer='+str(customer_id))
s.post(owner,'/admin/orders/new',{'submission':s.submission(page),'customer_id':str(customer_id),'service_id[]':str(shirt),'quantity[]':'3','stitching_price[]':'17.25','material_price[]':'20.00','fabric_source':'SHOP','priority':'URGENT'},token)
walkin=s.row('SELECT * FROM orders WHERE customer_id=%s ORDER BY id DESC LIMIT 1',(customer_id,))
s.check(str(walkin['grand_total'])=='111.75' and str(walkin['required_advance'])=='111.75' and walkin['priority']=='URGENT','Manual urgent pricing and full shop-cloth advance')
s.check(str(walkin['subtotal_stitching'])=='51.75' and str(walkin['subtotal_material'])=='60.00','Material and stitching remain separate')
# Enquiry conversion: no order until the order form is actually submitted.
response=s.post(anonymous,'/enquiry',{'name':'QA enquiry','mobile':'9777777722','message':'Need a shirt'})
enquiry=s.row("SELECT * FROM enquiries WHERE mobile='9777777722' ORDER BY id DESC LIMIT 1")
s.check(enquiry['converted_order_id'] is None,'An enquiry is not an order')
page,token=s.form(owner,'/admin/enquiries')
response=s.post(owner,f'/admin/enquiries/{enquiry["id"]}/convert',{},token)
s.check('/admin/orders/new?' in response.url,'Enquiry opens a draft order form')
page=response;token=re.search(r'name="_token" value="([A-Za-z0-9]+)"',page.text).group(1)
customer=int(re.search(r'<option value="(\d+)" selected>',page.text).group(1))
s.post(owner,'/admin/orders/new',{'submission':s.submission(page),'customer_id':str(customer),'enquiry_id':str(enquiry['id']),'service_id[]':str(s.combo['id']),'quantity[]':'1','stitching_price[]':'550','material_price[]':'0','fabric_source':'CUSTOMER'},token)
converted=s.row('SELECT * FROM enquiries WHERE id=%s',(enquiry['id'],))
s.check(converted['status']=='CONVERTED' and converted['converted_order_id'] is not None,'Successful order atomically links its enquiry')
# Inactive catalogue item cannot be ordered by forging an id.
with s.connection.cursor() as cursor:cursor.execute("UPDATE services SET is_active=0 WHERE code='POLICE_KHAAKI'")
police=s.row("SELECT id FROM services WHERE code='POLICE_KHAAKI'")['id']
s.check('data-service="POLICE_KHAAKI"' not in anonymous.get(s.BASE+'/services').text,'Inactive catalogue entry is hidden')
page,token=s.form(s.bob,'/order');before=s.row('SELECT COUNT(*) n FROM orders')['n']
s.post(s.bob,'/order',{'submission':s.submission(page),'service_id[]':str(police),'quantity[]':'1','fabric_source':'CUSTOMER'},token)
s.check(s.row('SELECT COUNT(*) n FROM orders')['n']==before,'Inactive service cannot be forged into an online order')
s.check(anonymous.post(s.BASE+'/api/payments/webhook',json={'verified':True}).status_code==501,'Unconfigured webhook cannot verify a payment')
# Repeated bad logins eventually return a real 429 response.
login=s.requests.Session();page,token=s.form(login,'/customer/login');last=None
for _ in range(12):last=login.post(s.BASE+'/customer/login',data={'_token':token,'mobile':'9777777799','password':'badpassword'})
s.check(last.status_code==429,'Persistent rate limiter blocks repeated login attempts')
print(s.json.dumps({'passed':len(s.checks),'failures':[],'checks':s.checks},ensure_ascii=False,indent=2))
