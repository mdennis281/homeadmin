from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from user_manager import UserManager
import uuid

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

user_manager = UserManager()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username')
        user = user_manager.get_user(username)
        if user and user['usertype'] == 2:
            return f(*args, **kwargs)
        else:
            flash('You need to be an admin to access this page.', 'warning')
            return redirect(url_for('auth.login'))
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_manager.authenticate_user(username, password):
            session['username'] = username
            flash('Logged in successfully.', 'success')
            return redirect(url_for('base.index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin/users', methods=['GET', 'POST'])
@admin_required
def user_management():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_user':
            username = request.form['username']
            password = request.form['password']
            usertype = int(request.form['usertype'])
            user_manager.add_user(username, password, usertype)
            flash(f'User {username} added successfully.', 'success')
        elif action == 'remove_user':
            username = request.form['username']
            user_manager.remove_user(username)
            flash(f'User {username} removed successfully.', 'success')
    users = user_manager.list_users()
    return render_template('auth/admin.html', users=users)

@auth_bp.route('/user/api_keys', methods=['GET', 'POST'])
@login_required
def api_keys():
    username = session['username']
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'generate_api_key':
            new_api_key = str(uuid.uuid4())
            user_manager.add_api_key(username, new_api_key)
            flash('New API key generated.', 'success')
        elif action == 'revoke_api_key':
            api_key = request.form['api_key']
            user_manager.remove_api_key(api_key)
            flash('API key revoked.', 'success')
    api_keys = user_manager.list_api_keys_for_user(username)
    return render_template('auth/api_keys.html', api_keys=api_keys)
