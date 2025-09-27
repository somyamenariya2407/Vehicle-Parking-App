from flask import Blueprint,render_template,redirect,request,url_for,session,flash
from models.models import User,db
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':

        email= request.form['email'].strip()
        password= request.form['password'].strip()

        if not email or not password:
            flash("Email and Password required.","danger")
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            session['user_id']=user.id
            session['user']=user.name
            session['role']=user.role

            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard')) 
        else:
            flash('Invalid Credentials!! Try again ', 'danger')
            return redirect(url_for('auth.login'))
        
    return render_template('login.html')

    

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':

        
        email= request.form['email'].strip()
        password=request.form['password'].strip()
        name=request.form['name'].strip()
        address=request.form['address'].strip()
        pincode=request.form['pincode'].strip()
        hashed_pass= generate_password_hash(password)


        if not name or not email or not password or not address or not pincode:
            flash("All fields are required.",'danger')
            return redirect(url_for('auth.register'))
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+",email):
            flash("Invalid email format")
            return redirect(url_for('auth.register'))
        
        if len(password) < 5:
            flash("Password must be greater than 5 characters.","warning")
            return redirect(url_for('auth.register'))
        
        if not pincode.isdigit() or len(pincode) != 6:
            flash("Pincode must be a 6 digit number.","danger")
            return redirect(url_for('auth.register'))




        existing_user=User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!","warning")
            return redirect(url_for('auth.register'))

        

        new_user=User(email=email,password=hashed_pass,name=name,address=address,pincode=pincode)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please login.",'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

    


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.",'success')
    return redirect(url_for('home'))



