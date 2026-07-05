from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

app.secret_key = '23f3001787'
login_manager = LoginManager()
login_manager.init_app(app)


#user can have many bookings
#one booking by one user

#one trek can have many booking
#one booking is for one trek

#one staff can have many treks
#one trek can have one staff


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='trekker')#admin,staff,trekker
    status = db.Column(db.String(20), nullable=False, default='approved')
    bookings = db.relationship('Booking', backref='user', lazy=True)#staff need approval to login 'pending' then


class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(300),nullable=False)
    difficulty = db.Column(db.String(100),nullable=False)#easy,moderate,hard
    duration_days = db.Column(db.Integer,nullable=False)
    available_slots = db.Column(db.Integer,nullable=False)
    status = db.Column(db.String(100),nullable=False, default='Pending') #pending,approved,open,closed,completed
    staff_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    bookings = db.relationship('Booking', backref='trek', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'))
    status = db.Column(db.String(20),nullable=False, default="Booked")
    booking_date = db.Column(db.DateTime,default=datetime.now)
    
    
    
    
with app.app_context():
    db.create_all()

    admin = User.query.filter_by(role='admin').all()

    if len(admin)==0:
        new_admin = User(
            username='admin',
            email='admin@admin.com',
            password=generate_password_hash('admin123'),
            role='admin',
            status='approved'
        )
        db.session.add(new_admin)
        db.session.commit()
        print('admin account initiated')
        print('startup complete')
    else:
        print('startup complete')


#db x---x

#login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':
        
        form_username = request.form.get('username')
        form_email = request.form.get('email')
        form_password = request.form.get('password')
        form_role = request.form.get('role')
        
        hashed_pw = generate_password_hash(form_password)
        
        if form_role == 'staff':
            user_status = 'pending'
        else:
            user_status = 'approved'
        
        existing_user = User.query.filter((User.email == form_email)|(User.username == form_username)).first()
        
        if existing_user:
            return render_template("register.html", error="Username or Email already exists!")
    
        new_user = User(
            username = form_username,
            email = form_email,
            password=hashed_pw,
            role = form_role,
            status = user_status
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect('/login')
    return render_template('register.html', error = None )
    
    
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        form_email = request.form.get('email')
        form_password = request.form.get('password')
        
        user = User.query.filter_by(email=form_email).first()
        
        if user and check_password_hash(user.password,form_password):
            if user.status == "pending":
                return render_template("login.html",error = "Kindly , wait for Admin approval.")
            login_user(user)
            
            if user.role=='admin':
                return redirect("/admin_dashboard")
            elif user.role=='staff':
                return redirect("/staff_dashboard")
            else:
                return redirect("/trekker_dashboard")
        else:
            return render_template("login.html",error = "Invalid Email or Password")
    return render_template("login.html",error=None)


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect('/admin_dashboard')
    elif current_user.role == 'staff':
        return redirect('/staff_dashboard')
    else :
        return redirect('/trekker_dashboard')


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect('/')
    return render_template('admin_dashboard.html')

@app.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        return redirect('/')
    return render_template('staff_dashboard.html')

@app.route('/trekker_dashboard')
@login_required
def trekker_dashboard():
    if current_user.role != 'trekker':
        return redirect('/')
    return render_template('trekker_dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
    