
from flask import Flask, render_template, request, redirect, url_for, flash,send_file,session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
from datetime import date
from sqlalchemy import exc 
from sqlalchemy import create_engine




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


@app.route('/', methods=['GET', 'POST']) 
@app.route('/',methods=['GET',  'POST'])              
def home():
   if (request.method == 'POST') and len(request.form["ipaddress1"]):
        IPAddr = request.form["ipaddress1"]
        session['loggedin'] = True
        session['name'] = IPAddr
        return redirect(url_for("index"))
   return render_template("ipaddress.html")

@app.route('/index')
@app.route('/index', methods=['GET', 'POST'], defaults={"page": 1}) 
@app.route('/index/<int:page>', methods=['GET', 'POST'])

def index(page=1):
 if 'loggedin' in session:
   IPAddr =  session['name']
   postgreSQL_select_Query = "select * from users where ipaddress = :search"
   userresult = db.session.execute(postgreSQL_select_Query, {"search": IPAddr}).fetchone()
   if userresult == None:
       return render_template("error.html")
   else:
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
 else:
   # User is not loggedin redirect to login page
   return redirect(url_for('home'))

@app.route('/search_link', methods=['GET', 'POST'])


def search_link():
  # for interface in interfaces():
   #     if AF_INET in ifaddresses(interface):
    #         for link in ifaddresses(interface)[AF_INET]:
     #          if(link['addr']) != "127.0.0.1":
      #            IPAddr = link['addr']
                                 
   #postgreSQL_select_Query = "select * from users where ipaddress = :search"
   #userresult = db.session.execute(postgreSQL_select_Query, {"search": IPAddr}).fetchone()
   #if userresult == None:
     #return render_template("error.html")
      # Check if user is loggedin
   if 'loggedin' in session:
      IPAddr =  session['name']
      postgreSQL_select_Query = "select * from users where ipaddress = :search"
      userresult = db.session.execute(postgreSQL_select_Query, {"search": IPAddr}).fetchone()
      if userresult == None:
         return render_template("error.html")
      else:
       if request.method == 'GET':
         return render_template("bulksearch.html")
       if request.method == 'POST':
         x = 0
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
            x = x + 1
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
         #os.remove(fname)ß
         return result
      return render_template("bulksearch.html")
   else:
      # User is not loggedin redirect to login page
      return redirect(url_for('home'))
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
      
      page = page
      pages = 200
      users_ip = Users.query.order_by(Users.id.desc()).paginate(page, per_page=pages)
      return render_template("admin.html",users_ip=users_ip)
      
   @app.route('/admin_post', methods=['POST'])
   def admin_post(page=1):
      print("ddd")
      text = request.form['text']
      create_user = Users(ipaddress=text, datetime=date.today())
      print("tester")
      print(create_user)
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
    #app.run(debug=True,host="0.0.0.0",port=8080)
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
