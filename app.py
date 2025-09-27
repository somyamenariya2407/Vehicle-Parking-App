from flask import Flask,render_template,session,request,redirect,Blueprint
from werkzeug.security import generate_password_hash
from routes.admin import createadmin
from db import db
from dotenv import load_dotenv
import os



from routes.auth import auth_bp 
from routes.admin import admin_bp
from routes.user import user_bp

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','sqlite:///parking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)



@app.route('/')
def home():
    return render_template('home.html')



if __name__ == "__main__":
    with app.app_context():
        from models.models import *
        db.create_all()
        createadmin()

    app.run(debug=True)
