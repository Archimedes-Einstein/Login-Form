from flask import Flask, render_template, request, flash, url_for,redirect, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column,DeclarativeBase
from sqlalchemy import String, Float, Integer
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,current_user,login_user,logout_user,login_required,UserMixin
from flask_gravatar import Gravatar
import os
from dotenv import load_dotenv
app = Flask(__name__)
class Base(DeclarativeBase):
    pass
load_dotenv()
login_manager = LoginManager()
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# initialize the app with the extension
db.init_app(app)
login_manager.init_app(app)
gravatar = Gravatar(app,
                    size=200,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

class Users(UserMixin,db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String,nullable=False)
    email: Mapped[str] = mapped_column(String,nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    user = db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()
    return user

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        print(request.form['email'])
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            flash('Invalid Password. Please input the correct password')
            return redirect(url_for('login'))
        flash('Invalid Email. The email provided is not registered.')
        return redirect(url_for('signup'))
    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == "POST":
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        already_a_user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
        if already_a_user:
            flash('Already a user, try loging in instead.')
            return redirect(url_for('login'))
        with app.app_context():
            new_user = Users(name=name,
                             email=email,
                             password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
        return redirect(url_for('home'))

    return render_template('signup.html')
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
if __name__ == '__main__':
    app.run(debug=True)