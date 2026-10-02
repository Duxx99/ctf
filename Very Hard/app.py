from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import base64
import hashlib
import requests  # To handle HTTP requests
import json
from urllib.parse import urlparse, urlunparse

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database model for User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Database model for Chat
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    visible = db.Column(db.Boolean, default=True)

# Database model for Messages in a chat room
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Load user callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to construct chat ID with double encoding
def construct_chat_id(chat_id):
    base64_id = base64.b64encode(str(chat_id).encode()).decode()
    sha256_hash = hashlib.sha256(base64_id.encode()).hexdigest()
    constructed_id = f"{base64_id}.{sha256_hash}"
    double_encoded_id = base64.b64encode(constructed_id.encode()).decode()
    return double_encoded_id

# Helper function to decode and validate the chat ID
def decode_chat_id(double_encoded_id):
    try:
        constructed_id = base64.b64decode(double_encoded_id).decode()
        base64_id, sha256_hash = constructed_id.split('.')
        if hashlib.sha256(base64_id.encode()).hexdigest() != sha256_hash:
            return None
        chat_id = int(base64.b64decode(base64_id).decode())
        return chat_id
    except (ValueError, IndexError, TypeError):
        return None

# Home route that redirects to login or dashboard based on authentication
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Dashboard to display all public chat rooms for authenticated users
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        title = request.form.get('title')
        visibility = request.form.get('visibility') == 'public'
        if title:
            new_chat = Chat(owner_id=current_user.id, title=title, visible=visibility)
            db.session.add(new_chat)
            db.session.commit()
            chat_id = construct_chat_id(new_chat.id)
            if not visibility:
                return jsonify({'chat_id': chat_id})
            return redirect(url_for('dashboard'))
    
    chats = Chat.query.filter_by(visible=True).all()
    chats_with_ids = [(chat, construct_chat_id(chat.id)) for chat in chats]
    return render_template('dashboard.html', chats=chats_with_ids)

# Route to view and participate in individual chat rooms by constructed ID
@app.route('/chat/<constructed_id>', methods=['GET', 'POST'])
@login_required
def view_chat(constructed_id):
    chat_id = decode_chat_id(constructed_id)
    if chat_id is None:
        flash('Invalid chat ID.')
        return redirect(url_for('dashboard'))
    
    chat = Chat.query.get(chat_id)
    if not chat:
        flash('Chat not found.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_message = Message(chat_id=chat.id, user_id=current_user.id, content=content)
            db.session.add(new_message)
            db.session.commit()
            return redirect(url_for('view_chat', constructed_id=constructed_id))
    
    messages = Message.query.filter_by(chat_id=chat.id).all()
    return render_template('view_chat.html', chat=chat, messages=messages)

# Route to query internal Keycloak API with raw HTTP requests
@app.route('/queryKeycloak', methods=['GET', 'POST'])
@login_required
def query_keycloak():
    response_data = None
    if request.method == 'POST':
        raw_request = request.form.get('raw_request')  # Get raw HTTP request from the form

        # Parsing the raw HTTP request
        try:
            # Split request lines
            lines = raw_request.splitlines()
            # Extract method, path, and version from the first line
            method, path, _ = lines[0].split(maxsplit=2)
            
            headers = {}
            body = ''
            header_mode = True
            host = None

            # Parse headers and body
            for line in lines[1:]:
                line = line.strip()
                if header_mode:
                    if line == '':  # End of headers
                        header_mode = False
                    else:
                        # Split headers into key-value pairs
                        key, value = line.split(":", 1)
                        headers[key.strip()] = value.strip()
                        if key.strip().lower() == 'host':
                            host = value.strip()  # Extract the host from headers
                else:
                    # Capture body after headers
                    body += line + '\n'

            body = body.strip()  # Remove extra newline at the end of the body

            # Ensure the host is present
            if not host:
                raise ValueError("Host header is missing from the request.")

            # Construct the full URL
            url = f"http://{host}{path}"

            # Send the parsed request
            response = requests.request(method, url, headers=headers, data=body if body else None)
            response_data = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text
            }

        except Exception as e:
            flash(f"Error processing request: {str(e)}")
            response_data = f"Error processing request: {str(e)}"
    
    return render_template('query_keycloak.html', response_data=response_data)

# Register route to create new users
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')

# Initialize database
with app.app_context():
    db.create_all()

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
