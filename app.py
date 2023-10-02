from flask import Flask, flash, get_flashed_messages, jsonify, render_template, redirect, session, url_for, request
from flask_login import login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os

# Create a Flask app
app = Flask(__name__)

#-----------------DB ------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = 'techyon-automation9988776655@11223344' 
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username} : {self.id}>"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    document = db.Column(db.LargeBinary, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

#---------------------------------------------------------------------------------->

#-------------user login, logout and sign up---------------

#------login---------
@app.route('/login', methods=['GET','POST'])
def login():
    type = ""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        print(f"is authorised user: {bool(user) }")
        if bool(user):
            session['user_id'] = user.id  # Store user ID in session
            session['logged_in'] = True
            flash('Login successful!', 'success')
            messages = get_flashed_messages(with_categories=True)    
            type = messages[0][0]
            return redirect(url_for('home'))
        else:
            print("login failed")
            session['logged_in'] = False
            flash('Login failed. Please check your credentials and try again.', 'danger')
            messages = get_flashed_messages(with_categories=True)    
            type = messages[0][0]
    messages = get_flashed_messages(with_categories=True)    
    if(messages):
        type = messages[0][0]
    return render_template("login.html", type=type)
    
#------logout--------
@app.route('/logout')
def logout():
    type = ""
    if session['logged_in'] : 
        flash('User logged out successfully!', 'info')
        messages = get_flashed_messages(with_categories=True)    
        type = messages[0][0]
        session['logged_in'] = False
    else:
        flash('No user Logged in', 'danger')
        messages = get_flashed_messages(with_categories=True)    
        type = messages[0][0]
    return render_template("login.html", type=type)

#-----------------signup----------------------
@app.route('/signup', methods=['GET','POST'])
def signup():
    type = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"sign up - {username} : {password}")
        existing_user = User.query.filter_by(username=username).first()
        print(f"existing : {bool(existing_user)}")
        if existing_user:
            flash('Username already exists. Please choose another username.', 'danger')
        if len(password)<8:
            flash('password must be minimum of 8 charecters in length!', 'danger')
        else:
            print(f" creating user....")
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. You can now login.', 'success')
            return redirect(url_for('login'))
    messages = get_flashed_messages(with_categories=True)    
    if(messages):
        type = messages[0][0]
    return render_template("signup.html", type=type)



#-----------------------Home-----------------------
# Define a route and a function to handle the route
@app.route('/')
def home():
    type = ""
    if 'logged_in' in session and session['logged_in']:
        template = render_template('index.html')
    else:
        flash('Login required!', 'danger')
        return redirect(url_for('login'))
    
    return render_template('index.html', type=type)


#----------------check the users-------------------
@app.route('/users')
def list_users():
    # Query all users from the database
    if 'logged_in' in session and session['logged_in']:
        users = User.query.all()
        return render_template('users.html', users=users)
    else:
        return render_template("login.html")


#----------------START------------------
@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        project_name = request.form['project_name']
        description = request.form['description']

        # Perform database operations to store the project data
        # Example: Create a new project record in the database

        # Redirect to the manage projects page or another appropriate page
        return redirect(url_for('manage'))

    return render_template('start.html')


#-----------------project creation----------------
@app.route('/create_project', methods=['POST'])
def create_project():
    if request.method == 'POST':
        title = request.form['title']
        document_file = request.files['document']  # Access the uploaded file
        # Validate and process the form data here
        if title and document_file:
            # Save the uploaded file as binary data
            document_data = document_file.read()
            
            new_project = Project(
                title=title,
                document=document_data
            )
            db.session.add(new_project)
            db.session.commit()

            # Redirect to a success page or another appropriate page
            return redirect(url_for('manage_projects'))
        message = "unable to create a project"
    return render_template('start.html',message)

#---------------Manage-----------------
@app.route('/manage')
def manage_projects():
    # Retrieve a list of projects from the database
    projects = Project.query.all()
    return render_template('manage.html', projects=projects)

#-------------deleting-managing---------------
@app.route('/delete/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        # Find the project by ID and delete it from the database
        project = Project.query.get(project_id)
        if project:
            db.session.delete(project)
            db.session.commit()
            return jsonify({'message': 'Item deleted successfully'}), 200
        else:
            return jsonify({'message': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error deleting item', 'error': str(e)}), 500
    
#-------------updating-managing----------------
@app.route('/update/<int:project_id>', methods=['POST'])
def update_document(project_id):
    try:
        # Find the project by ID
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'message': 'Project not found'}), 404

        # Handle the uploaded file
        new_document = request.files['new_document']
        if new_document:
            # Save the new document to the 'uploads' folder
            filename = secure_filename(new_document.filename)
            new_document.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Update the project's document with the new file path
            project.document = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Commit the changes to the database
            db.session.commit()

            return jsonify({'message': 'Document updated successfully'}), 200
        else:
            return jsonify({'message': 'No file uploaded'}), 400
    except Exception as e:
        return jsonify({'message': 'Error updating document', 'error': str(e)}), 500
    

@app.route("/extract_endpoints")
def extract_endpoints():
    # Extract endpoints from the API document.
    # ...
    return "Endpoints extracted successfully."

# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
