from app import app  # Substitui 'your_project' pelo nome do teu módulo Flask
from models import db, User

def create_tables():
    """Cria as tabelas no banco de dados."""
    with app.app_context():
        db.create_all()
        print("Tabelas criadas com sucesso!")

def create_admin():
    """Cria um utilizador administrador inicial."""
    with app.app_context():
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@teste.local")
            admin.set_password("207509W8KF0rm")  # Altere "senha_segura" para algo forte
            db.session.add(admin)
            db.session.commit()
            print("Administrador criado com sucesso!")
        else:
            print("Administrador já existe.")

if __name__ == "__main__":
    create_tables()
    create_admin()
