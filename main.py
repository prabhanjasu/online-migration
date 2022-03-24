import json
from flask import Flask, render_template, request, redirect, url_for, flash,send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import csv

app = Flask(__name__)
app.secret_key = "dadasdasd"
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xls','xlsx'}
POSTGRES = {
    'user': 'Lanepostgres',
    'pw': 'Lanepostgres!2022',
    'db': 'Lanecqgh',
    'host': '35.200.170.53',
    'port': '5432',
}
#DDATABSE_URI = 'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
#DATABSE_URI='mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='root', server='localhost:3306', database='testdatabase')
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
   x = 0
   if request.method == 'GET':
      return render_template("bulksearch.html")
   if request.method == 'POST':
      csv_file = request.files['file']
      data = pd.read_csv (csv_file)   
      df = pd.DataFrame(data) 
      data1 = []
      for row in df.itertuples():
         email = row.EMAIL
         
         customerList = OnlineCustomer.query.filter(OnlineCustomer.Email==email).all() #() OR: from sqlalchemy import or_  filter(or_(User.name == 'ednalan', User.name == 'caite'))
         data1.append(customerList)
         
      x = x+1
      for rbc in data1  :
          for j in rbc: # inner loop
             data = {'Name':[j.Name],'Email':[j.Email],'Phone':[j.Phone],'Address':[j.Address]} 
             df = pd.DataFrame(data)
             fname="search_"+str(x)+".csv"
             df.to_csv(fname,mode="a",index=False,header=None)
      result = send_file(fname,attachment_filename='search_result.csv', mimetype='text/csv',as_attachment=True)
      print("file sent, deleting...")
      os.remove(fname)
      return result
      
  
   return render_template("bulksearch.html")
 
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)
