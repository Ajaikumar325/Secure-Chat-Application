from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import rsa as rsa_lib
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    encrypted_message = db.Column(db.Text, nullable=False)

# RSA key generation
private_key, public_key = rsa_lib.newkeys(512)

# Encryption functions
def encrypt_message(message, pubkey):
    encrypted = rsa_lib.encrypt(message.encode('utf8'), pubkey)
    return base64.b64encode(encrypted).decode('utf8')  # Simulate encryption with base64 encoding

def decrypt_message(encrypted_message):
    encrypted_bytes = base64.b64decode(encrypted_message.encode('utf8'))
    return rsa_lib.decrypt(encrypted_bytes, private_key).decode('utf8')

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        session['user'] = username
        return redirect('/chat')
    return 'Login failed. Invalid username or password.'

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        message = request.form['message']
        receiver = request.form['receiver']
        encrypted_message = encrypt_message(message, public_key)
        msg = Message(sender=session['user'], receiver=receiver, encrypted_message=encrypted_message)
        db.session.add(msg)
        db.session.commit()
    
    messages = Message.query.all()
    return render_template('chat.html', messages=messages)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This ensures tables are created inside the app context
    app.run(debug=True)
