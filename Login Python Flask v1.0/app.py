from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from config import Config
from models import db, User
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash
import pytz  # Adicionado para lidar com fuso horário

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
mail = Mail(app)

# Sessão expira após 10 minutos
app.permanent_session_lifetime = timedelta(minutes=10)

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
    if request.endpoint not in ['login', 'reset_password', 'handle_reset', 'static']:
        if not is_logged_in():
            flash("Acesso restrito. Se não tiver acesso, contacte a equipa de suporte em suportecrao@gmail.com. Obrigado.", "warning")
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
            return redirect(url_for('dashboard'))
        else:
            flash('Utilizador e/ou senha incorretos.', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Página principal após login."""
    return render_template('dashboard.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """Página para recuperação de senha."""
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
    return render_template('reset_password.html')

@app.route('/handle_reset', methods=['GET', 'POST'])
def handle_reset():
    """Página para o admin redefinir a senha."""
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
    """Logout e destruição da sessão."""
    session.clear()
    flash("Sessão encerrada com sucesso!", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
