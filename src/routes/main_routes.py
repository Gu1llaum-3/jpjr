from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models import db
from src.models.user import User
from src.models.item import Item
from src.models.borrow import Borrow
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from src.forms import LoginForm, ChangePasswordForm
from werkzeug.security import generate_password_hash

# Création du blueprint
main_bp = Blueprint('main', __name__)

# Initialisation de Flask-Login
login_manager = LoginManager()
# login_manager.init_app(app)  # À faire dans app.py
login_manager.login_view = 'main.index'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Route principale
@main_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Page d'accueil - Redirige vers le tableau de bord si l'utilisateur est connecté,
    ou vers la page de login sinon
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    users = db.session.query(User).order_by(User.name).all()
    return render_template('index.html', users=users, form=form)

# Page de connexion
@main_bp.route('/login', methods=['POST'])
def login():
    """
    Gère la connexion d'un utilisateur avec mot de passe
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(name=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Bienvenue, {user.name}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Nom ou mot de passe incorrect', 'danger')
    else:
        flash('Veuillez remplir tous les champs', 'danger')
    users = db.session.query(User).order_by(User.name).all()
    return render_template('index.html', users=users, form=form)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()
    if form.validate_on_submit():
        if db.session.query(User).filter_by(name=form.username.data).first():
            flash('Ce nom d\'utilisateur existe déjà.', 'danger')
        else:
            user = User(name=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Compte créé avec succès. Vous pouvez vous connecter.', 'success')
            return redirect(url_for('main.index'))
    return render_template('register.html', form=form)

# Connexion rapide avec ID
@main_bp.route('/login/<int:user_id>')
def login_with_id(user_id):
    """
    Connexion rapide avec l'ID de l'utilisateur
    """
    user = db.session.get(User, user_id)
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        return redirect(url_for('main.index'))
    
    session['user_id'] = user.id
    session['user_name'] = user.name
    
    flash(f'Bienvenue, {user.name}!', 'success')
    return redirect(url_for('main.dashboard'))

# Tableau de bord
@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Tableau de bord principal de l'application
    """
    if 'user_id' not in session:
        flash('Veuillez vous connecter', 'danger')
        return redirect(url_for('main.index'))
    
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        session.clear()
        return redirect(url_for('main.index'))
    
    # Récupérer les articles disponibles (non empruntés)
    subquery = db.session.query(Borrow.item_id).filter(Borrow.return_date == None)
    available_items = db.session.query(Item).filter(
        ~Item.id.in_(subquery)
    ).order_by(Item.name).all()
    
    return render_template('dashboard.html', 
                           user=user, 
                           available_items=available_items)

# Mes emprunts
@main_bp.route('/my-borrows')
@login_required
def my_borrows():
    """
    Page affichant tous les emprunts en cours de l'utilisateur
    """
    if 'user_id' not in session:
        flash('Veuillez vous connecter', 'danger')
        return redirect(url_for('main.index'))
    
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        session.clear()
        return redirect(url_for('main.index'))
    
    # Récupérer les emprunts en cours de l'utilisateur
    current_borrows = db.session.query(Borrow).filter(
        Borrow.user_id == user_id,
        Borrow.return_date == None
    ).all()
    
    return render_template('my_borrows.html', 
                           user=user, 
                           current_borrows=current_borrows)

# Déconnexion
@main_bp.route('/logout')
@login_required
def logout():
    """
    Déconnecte l'utilisateur et nettoie la session
    """
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('main.index'))

# Page Chat Inventaire
@main_bp.route('/chat-inventaire')
@login_required
def chat_inventaire():
    """
    Page pour interagir avec l'IA concernant l'inventaire.
    """
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder à cette fonctionnalité.', 'warning')
        return redirect(url_for('main.index'))
    return render_template('chat_inventaire.html')

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Mot de passe actuel incorrect.', 'danger')
        elif form.new_password.data == form.current_password.data:
            flash('Le nouveau mot de passe doit être différent de l\'ancien.', 'warning')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Mot de passe modifié avec succès.', 'success')
    return render_template('profile.html', form=form)
