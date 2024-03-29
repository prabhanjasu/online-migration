from flask import Flask, render_template, request, redirect, url_for, flash,send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import os
from datetime import date
from sqlalchemy import exc 
from sqlalchemy import create_engine
import socket
import requests


from netifaces import interfaces, ifaddresses, AF_INET

app = Flask(__name__)
app.secret_key = "l1a2n3e4"
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xls','xlsx'}
#local uri
#DATABSE_URI = 'postgresql://postgres:postgres1@localhost:5432/Lanecqgh'
DATABSE_URI = 'postgresql://Lanepostgres:Lanepostgres!2022@35.200.170.53:5432/Lanecqgh'



app.config['SQLALCHEMY_DATABASE_URI'] = DATABSE_URI 

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#Creating model table for our CRUD database
class OnlineCustomer(db.Model):
    __tablename__ = 'OnlineCustomer'
    Id = db.Column(db.Integer, primary_key = True)
    Name = db.Column(db.String(100))
    Email = db.Column(db.String(100))
    Phone = db.Column(db.String(100))
    Address = db.Column(db.String(100))
    DateCreated = db.Column(db.String(100))



#This is the index route where we are going to
#query on all our  data

@app.route('/')
@app.route('/', methods=['GET', 'POST'], defaults={"page": 1}) 
@app.route('/<int:page>', methods=['GET', 'POST'])

def index(page=1):
    
    public_ip = requests.get("http://wtfismyip.com/text").text
    print(public_ip)
    for interface in interfaces():
        if AF_INET in ifaddresses(interface):
             for link in ifaddresses(interface)[AF_INET]:
               if(link['addr']) != "127.0.0.1":
                  IPAddr = link['addr']
    print('ipaddress')
    print(IPAddr)
    postgreSQL_select_Query = "select * from users where ipaddress = :search"
    userresult = db.session.execute(postgreSQL_select_Query, {"search": IPAddr}).fetchone()
    if userresult == None:
      return render_template("error.html")
    page = page
    pages = 500
    customerList = OnlineCustomer.query.order_by(OnlineCustomer.Id.asc()).paginate(page, per_page=pages)
    
    if request.method == 'POST' and len(request.form["name"]):
       name = request.form["name"]
       search = "%{}%".format(name)
       customerList = OnlineCustomer.query.filter(OnlineCustomer.Name.like(search)).paginate(per_page=pages, error_out=True) # OR: from sqlalchemy import or_  filter(or_(User.name == 'ednalan', User.name == 'caite'))
       return render_template('index.html', customerList = customerList, name=name)
    elif request.method == 'POST' and len(request.form["email"]):
       email = request.form["email"]
       search = "%{}%".format(email)
       customerList = OnlineCustomer.query.filter(OnlineCustomer.Email.like(search)).paginate(per_page=pages, error_out=True) # OR: from sqlalchemy import or_  filter(or_(User.name == 'ednalan', User.name == 'caite'))
       return render_template('index.html', customerList = customerList, email=email)
    elif request.method == 'POST' and len(request.form["phone"]):
       phone = request.form["phone"]
       search = "%{}%".format(phone)
       customerList = OnlineCustomer.query.filter(OnlineCustomer.Phone.like(search)).paginate(per_page=pages, error_out=True) # OR: from sqlalchemy import or_  filter(or_(User.name == 'ednalan', User.name == 'caite'))
       return render_template('index.html', customerList = customerList, phone=phone)
    elif request.method == 'POST' and len(request.form["address"]):
       address = request.form["address"]
       search = "%{}%".format(address)
       customerList = OnlineCustomer.query.filter(OnlineCustomer.Address.like(search)).paginate(per_page=pages, error_out=True) # OR: from sqlalchemy import or_  filter(or_(User.name == 'ednalan', User.name == 'caite'))
       return render_template('index.html', customerList = customerList, address=address)
    return render_template("index.html", customerList = customerList)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/search_link', methods=['GET', 'POST'])


def search_link():
   for interface in interfaces():
        if AF_INET in ifaddresses(interface):
             for link in ifaddresses(interface)[AF_INET]:
               if(link['addr']) != "127.0.0.1":
                  IPAddr = link['addr']
                                 
   postgreSQL_select_Query = "select * from users where ipaddress = :search"
   userresult = db.session.execute(postgreSQL_select_Query, {"search": IPAddr}).fetchone()
   if userresult == None:
     return render_template("error.html")
   x = 0
   if request.method == 'GET':
      return render_template("bulksearch.html")
   if request.method == 'POST':
      csv_file = request.files['file']
      data = pd.read_csv (csv_file)   
      df = pd.DataFrame(data) 
      data1 = []
      tf =[]
      for row in df.itertuples():
         if(hasattr(row,'EMAIL')):
            tf.append(row.EMAIL)
            header ='email'
         else:
            phone =str(row.Phone)
            tf.append(phone)
            header ='phone'
         #print("file creating...")
      if(header =='email'):
       cus_data = OnlineCustomer.query.filter(OnlineCustomer.Email.in_(tf)).all()
      else:
       cus_data = OnlineCustomer.query.filter(OnlineCustomer.Phone.in_(tf)).all()   
      size = len(cus_data)
      if size==0:
          flash("There is no data")
          return render_template("bulksearch.html")
      else :
         for j in cus_data  :
            data = {'Name':[j.Name],'Email':[j.Email],'Phone':[j.Phone],'Address':[j.Address]}
            df = pd.DataFrame(data)
            fname="search_"+str(x)+".csv"
             #print("file csv creating...")
            df.to_csv(fname,mode="a",index=False,header=None)
         result = send_file(fname,attachment_filename='search_result.csv', mimetype='text/csv',as_attachment=True)
       #print("file sent, deleting...")
         os.remove(fname)

      #result = send_file(fname,attachment_filename='search_result.csv', mimetype='text/csv',as_attachment=True)
      #print("file sent, deleting...")
      #os.remove(fname)
      return result
   return render_template("bulksearch.html")
class Users(db.Model):
   __tablename__ = 'users'
   id = db.Column(db.Integer, primary_key = True,unique=True)
   ipaddress = db.Column(db.String(100))
   datetime = db.Column(db.DateTime)
   #CHECK_INV_RE = re.compile('[^a-zA-Z0-9_-]')
   @app.route('/admin')
   @app.route('/admin', methods=['GET', 'POST'], defaults={"page": 1}) 
   @app.route('/admin/<int:page>', methods=['GET', 'POST'])
   def admin(page=1):
      for interface in interfaces():
        if AF_INET in ifaddresses(interface):
             for link in ifaddresses(interface)[AF_INET]:
               if(link['addr']) != "127.0.0.1":
                  IPAddr = link['addr']
      page = page
      pages = 200
      users_ip = Users.query.order_by(Users.id.desc()).paginate(page, per_page=pages)
      return render_template("admin.html",users_ip=users_ip,IPAddr=IPAddr)
   @app.route('/admin', methods=['POST'])
   def admin_post(page=1):
      text = request.form['text']
      create_user = Users(ipaddress=text, datetime=date.today())
      try:
         userresult = db.session.add(create_user)
         userresult1 = db.session.commit()
         flash("Data Inserted successfully.")
      except exc.SQLAlchemyError as e:
         print(e)
         print("ERROR : ", str(e))
         flash("Invalid Ip Address.")
      return redirect(url_for("admin"))
   @app.route("/delete/<id>/", methods=["GET", "POST"])
   def delete(id):
      my_data = Users.query.get(id)
      db.session.delete(my_data)
      db.session.commit()
      flash("Data deleted successfully.")
      return redirect(url_for("admin"))

  
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5004)
