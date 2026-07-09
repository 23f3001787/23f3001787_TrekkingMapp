from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

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
    staff=db.relationship('User',backref='assigned_treks')
    start_date = db.Column(db.Date,nullable=False)

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

@app.before_request
def check_if_blacklisted():
    if current_user.is_authenticated and current_user.status=='blacklisted':
        if request.endpoint not in ['logout','static']:
            logout_user() 
            return render_template('blacklisted.html')
        


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

    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff',status='approved').count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    pending_staff = User.query.filter_by(role='staff', status='pending').all()
    all_treks=Trek.query.all()

    active_tab=request.args.get('open_tab','overview')
    
    approve_staff=User.query.filter_by(role='staff',status='approved').all()
    
    
    
    search_query=request.args.get('search_trek')
    if search_query:
        all_treks=Trek.query.filter(Trek.name.ilike(f"%{search_query}%")).order_by(Trek.id.desc()).all()
    else:
        all_treks=Trek.query.order_by(Trek.id.desc()).all()
        
    
    search_user=request.args.get('search_user')
    if search_user:
        if search_user.isdigit():
            manageable_users=User.query.filter(User.role!='admin',User.id==int(search_user)).all()
        else:
            manageable_users=User.query.filter(User.role!='admin',User.username.ilike(f"%{search_user}%")).all()
    else:
        manageable_users=User.query.filter(User.role!='admin').all()
        
    return render_template('admin_dashboard.html', 
                           users=total_users, 
                           staff=total_staff, 
                           treks=total_treks,
                           bookings=total_bookings,
                           pending_staff=pending_staff,
                           all_treks=all_treks,
                           active_tab=active_tab,
                           approve_staff=approve_staff,
                           manageable_users=manageable_users
                        )



@app.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        return redirect('/')
    active_tab = request.args.get('open_tab','profile')
    
    assigned_treks=current_user.assigned_treks
    
    return render_template('staff_dashboard.html',
                           active_tab=active_tab,
                           assigned_treks=assigned_treks)
    

@app.route('/update_staff_profile',methods=['POST'])
@login_required
def update_staff_profile():
    if current_user.role!='staff':
        return redirect('/')
    current_user.username=request.form.get('username')
    
    new_password=request.form.get('password')
    if new_password:
        current_user.password=generate_password_hash(new_password)
    db.session.commit()
    
    return redirect('/staff_dashboard?open_tab=profile')

@app.route('/update_staff_trek/<int:id>',methods=['POST'])
@login_required
def update_staff_trek(id):
    if current_user.role!='staff':
        return redirect('/')
    trek = Trek.query.get(id)
    if trek and trek.staff_id==current_user.id:
        new_status=request.form.get('status')
        if new_status:
            trek.status=new_status
            
        trek.available_slots=int(request.form.get('available_slots'))
        db.session.commit()
    return redirect('/staff_dashboard?open_tab=treks')


@app.route('/approve_staff_trek/<int:id>')
@login_required
def approve_staff_trek(id):
    if current_user.role!='staff':
        return redirect('/')
    trek = Trek.query.get(id)
    if trek and trek.staff_id==current_user.id and trek.status=='Pending':
        trek.status='Open'
        db.session.commit()
    return redirect('/staff_dashboard?open_tab=treks')




@app.route('/staff_remove_participant/<int:booking_id>')
@login_required
def staff_remove_participant(booking_id):
    if current_user.role!='staff':
        return redirect('/')
    booking = Booking.query.get(booking_id)
    if booking and booking.trek.staff_id==current_user.id:
        booking.trek.available_slots+=1
        db.session.delete(booking)
        db.session.commit()
    return redirect('/staff_dashboard?open_tab=treks')

@app.route('/trekker_dashboard')
@login_required
def trekker_dashboard():
    if current_user.role != 'trekker':
        return redirect('/')
    return render_template('trekker_dashboard.html')


@app.route('/approve_staff/<int:id>')
@login_required
def approve_staff(id):
    if current_user.role!='admin':
        return redirect('/')
    staff_to_approve = User.query.get(id)
    if staff_to_approve:
        staff_to_approve.status='approved'
        db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/reject_staff/<int:id>')
@login_required
def reject_staff(id):
    if current_user.role!='admin':
        return redirect('/')
    staff_to_reject = User.query.get(id)
    if staff_to_reject:
        db.session.delete(staff_to_reject)
        
        #send mail to email saying not approved unfortunately
        db.session.commit()
    return redirect('/admin_dashboard')




@app.route('/create_trek', methods=['POST'])
@login_required
def create_trek():
    if current_user.role != 'admin':
        return redirect('/')
    date_string=request.form.get('start_date')
    start_date=datetime.strptime(date_string, '%Y-%m-%d').date()
    
    new_trek = Trek(
        name=request.form.get('name'),
        location=request.form.get('location'),
        difficulty=request.form.get('difficulty'),
        duration_days=int(request.form.get('duration_days')),
        available_slots=int(request.form.get('available_slots'))
    )
    
    new_trek.start_date = start_date 
    
    staff_input=request.form.get('staff_id')
    if staff_input:
        new_trek.staff_id=int(staff_input)
    
    db.session.add(new_trek)
    db.session.commit()
    
    return redirect('/admin_dashboard?open_tab=treks')

@app.route('/delete_trek/<int:id>')
@login_required
def delete_trek(id):
    if current_user.role!='admin':
        return redirect('/')
    trek_to_delete=Trek.query.get(id)
    if trek_to_delete:
        db.session.delete(trek_to_delete)
        db.session.commit()
    return redirect('/admin_dashboard?open_tab=treks')

@app.route('/edit_trek/<int:id>',methods=['GET','POST'])
@login_required
def edit_trek(id):
    if current_user.role!='admin':
        return redirect('/')
    trek_to_edit=Trek.query.get(id)
    if request.method=='POST':
        trek_to_edit.name=request.form.get('name')
        trek_to_edit.location=request.form.get('location')
        trek_to_edit.difficulty=request.form.get('difficulty')
        trek_to_edit.duration_days=request.form.get('duration_days')
        trek_to_edit.available_slots=request.form.get('available_slots')
        
        date_string = request.form.get('start_date')
        start_date = datetime.strptime(date_string, '%Y-%m-%d').date()
        
        trek_to_edit.start_date=start_date
        
        staff_input=request.form.get('staff_id')
        if staff_input:
            trek_to_edit.staff_id=staff_input
        else:
            trek_to_edit.staff_id=None
        
        db.session.commit()
    return redirect('/admin_dashboard?open_tab=treks')


@app.route('/toggle_blacklist/<int:id>')
@login_required
def toggle_blacklist(id):
    if current_user.role!='admin':
        return redirect('/')
    user_to_toggle=User.query.get(id)
    if user_to_toggle:
        if user_to_toggle.status=='blacklisted':
            user_to_toggle.status='approved'
        else:
            user_to_toggle.status='blacklisted'
        db.session.commit()
    return redirect('/admin_dashboard?open_tab=users')


@app.route('/edit_user/<int:id>',methods=['POST'])
@login_required
def edit_user(id):
    if current_user.role!='admin':
        return redirect('/')
    user_to_edit=User.query.get(id)
    if user_to_edit:
        user_to_edit.username=request.form.get('username')
        new_password=request.form.get('password')
        if new_password:
            user_to_edit.password=generate_password_hash(new_password)
        db.session.commit()
    return redirect('/admin_dashboard?open_tab=users')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=9191,debug=True)
    