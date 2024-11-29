from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from config import Config
from models import db, User
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash
import pytz

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
mail = Mail(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


app.permanent_session_lifetime = timedelta(minutes=10)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def is_logged_in():
    """Verifica se o utilizador está logado e a sessão é válida."""
    now = datetime.now(pytz.utc)  # Garantindo que `now` é offset-aware
    expires_at = session.get('expires_at')

    # Converte `expires_at` para offset-aware, se necessário
    if isinstance(expires_at, str):  # Se armazenado como string ISO 8601
        expires_at = datetime.fromisoformat(expires_at).replace(tzinfo=pytz.utc)

    return 'user_id' in session and expires_at > now


@app.before_request
def validate_session():
    """Valida sessão antes de cada pedido."""
    if request.endpoint not in ['login', 'reset_password', 'handle_reset', 'connected_users', 'static']:
        if not is_logged_in():
            flash(
                "Acesso restrito. Se não tiver acesso, contacte a equipa de suporte em suportecrao@gmail.com. Obrigado.",
                "warning")
            return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['expires_at'] = (datetime.now(pytz.utc) + timedelta(minutes=10)).isoformat()
            session.permanent = True  # Sessão será gerida pelo `app.permanent_session_lifetime`

            # Flash de boas-vindas
            flash(f'Bem-vindo(a), {username}!', 'success')

            login_user(user)  # Flask-Login: Loga o usuário
            return redirect(url_for('dashboard'))
        else:
            flash('Utilizador e/ou senha incorretos.', 'error')
    return render_template('login/login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Página principal após login."""
    return render_template('dashboard.html')


from datetime import datetime, timedelta

@app.route('/connected-users')
def connected_users():
    now = datetime.utcnow()
    inactivity_limit = timedelta(minutes=10)
    connected_users = User.query.filter(User.last_active >= now - inactivity_limit).all()
    return render_template('connected_users.html', users=connected_users)



@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            msg = Message('Pedido de Redefinição de Senha',
                          recipients=[Config.MAIL_USERNAME])
            msg.body = f"O utilizador '{username}' solicitou a redefinição de senha."
            msg.sender = Config.MAIL_USERNAME
            mail.send(msg)
            flash('Pedido solicitado à equipa de suporte. Aguarde resposta no seu e-mail utilizado.', 'info')
            return redirect(url_for('login'))
        else:
            flash('Utilizador não encontrado!', 'error')
    return render_template('login/reset_password.html')


@app.route('/handle_reset', methods=['GET', 'POST'])
def handle_reset():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        user = User.query.filter_by(username=username).first()
        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash(f'Senha do utilizador "{username}" foi redefinida com sucesso.', 'success')
        else:
            flash('Utilizador não encontrado!', 'danger')
    return render_template('handle_reset.html')


@app.route('/logout')
def logout():
    session.clear()
    logout_user()
    flash("Sessão encerrada com sucesso!", "info")
    return redirect(url_for('login'))


from flask import request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("Por favor, preencha todos os campos!", "danger")
            return render_template('create_user.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("O nome de utilizador já existe. Escolha outro.", "danger")
            return render_template('create_user.html')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email)
        new_user.password_hash = hashed_password  # Assumindo que o modelo User usa `password_hash`
        db.session.add(new_user)
        db.session.commit()

        flash("Utilizador criado com sucesso!", "success")
        return redirect(url_for('create_user'))

    return render_template('create_user.html')

@app.before_request
def update_last_active():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            user.last_active = datetime.utcnow()
            db.session.commit()



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
