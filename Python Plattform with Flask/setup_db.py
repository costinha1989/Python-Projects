import os
from models import db, User
from flask import Flask
import sqlalchemy
from sqlalchemy import text
import pymysql
import tkinter as tk
from tkinter import messagebox
import json

# Configuração básica do Flask
app = Flask(__name__)


class DatabaseInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurador utilizadores plataforma")
        self.root.resizable(False, False)  # Impede a maximização da janela

        # Variáveis
        self.config_file = "db_config.json"
        self.db_verified = False

        # Interface do utilizador
        tk.Label(root, text="Username:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(root, text="Password:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Label(root, text="IP/Nome host:").grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.user_entry = tk.Entry(root)
        self.password_entry = tk.Entry(root, show="*")
        self.host_entry = tk.Entry(root)

        self.user_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        self.host_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(root, text="Verificar Base Dados", command=self.check_or_create_db).grid(row=3, column=0, padx=5,
                                                                                           pady=10)
        self.create_user_btn = tk.Button(root, text="Criar utilizador", command=self.open_admin_window,
                                         state=tk.DISABLED)
        self.create_user_btn.grid(row=3, column=1, padx=5, pady=10)

        self.start_platform_btn = tk.Button(root, text="Iniciar Plataforma", command=self.start_platform,
                                            state=tk.DISABLED)
        self.start_platform_btn.grid(row=3, column=2, padx=5, pady=10)

        self.output = tk.Text(root, height=10, width=60)
        self.output.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        self.load_config()

    def log(self, message):
        self.output.insert(tk.END, message + "\n")
        self.output.see(tk.END)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.user_entry.insert(0, config.get("username", ""))
                self.password_entry.insert(0, config.get("password", ""))
                self.host_entry.insert(0, config.get("host", ""))

    def save_config(self, user, password, host):
        config = {"username": user, "password": password, "host": host}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def check_or_create_db(self):
        user = self.user_entry.get().strip()
        password = self.password_entry.get().strip()
        host = self.host_entry.get().strip() or "localhost"

        self.log("A conectar à Base de Dados 'main.db'...")
        try:
            engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{password}@{host}")
            with engine.connect() as connection:
                result = connection.execute(text("SHOW DATABASES;"))
                databases = [row[0] for row in result]
                if 'main_db' not in databases:
                    self.log("Base de dados 'main_db' não encontrada. A criar...")
                    connection.execute(text("CREATE DATABASE main_db;"))
                    self.log("Base de Dados 'main_db' criada com sucesso!")
                else:
                    self.log("Base de Dados 'main_db' já existe.")

            app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{password}@{host}/main_db"
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            db.init_app(app)

            with app.app_context():
                db.create_all()
                self.log("Tabelas verificadas e atualizadas, se necessário.")

            self.save_config(user, password, host)
            self.db_verified = True
            self.create_user_btn.config(state=tk.NORMAL)
            self.start_platform_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Sucesso", "Base de Dados configurada com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar à Base de Dados:\n{e}")
            self.log(f"Erro: {e}")

    def open_admin_window(self):
        if not self.db_verified:
            messagebox.showerror("Erro", "É necessário verificar a Base de Dados primeiro.")
            return

        admin_window = tk.Toplevel(self.root)
        admin_window.title("Criar utilizador")

        tk.Label(admin_window, text="Nome Utilizador:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(admin_window, text="Senha:").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(admin_window, text="Confirmar a senha:").grid(row=2, column=0, padx=5, pady=5)

        username_entry = tk.Entry(admin_window)
        password_entry = tk.Entry(admin_window, show="*")
        confirm_password_entry = tk.Entry(admin_window, show="*")
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)

        with app.app_context():
            admin_exists = User.query.filter_by(username="admin").first() is not None
            if not admin_exists:
                messagebox.showwarning("Aviso",
                                       "O utilizador 'admin' ainda não foi criado. Por favor, crie-o primeiro.")
                username_entry.insert(0, "admin")
                username_entry.config(state=tk.DISABLED)

        def create_admin():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            confirm_password = confirm_password_entry.get().strip()

            if not username or not password:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
                return

            if password != confirm_password:
                messagebox.showerror("Erro", "As senhas não correspondem.")
                return

            self.log(f"Tentando criar o utilizador '{username}'...")
            try:
                with app.app_context():
                    if not User.query.filter_by(username=username).first():
                        user = User(username=username, email=f"{username}@teste.local")
                        user.set_password(password)
                        db.session.add(user)
                        db.session.commit()
                        self.log(f"Utilizador '{username}' criado com sucesso!")
                        messagebox.showinfo("Sucesso", f"Utilizador '{username}' criado com sucesso!")
                        admin_window.destroy()
                    else:
                        self.log(f"Um utilizador com o nome '{username}' já existe.")
                        messagebox.showinfo("Informação", f"Utilizador '{username}' já existe.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar utilizador:\n{e}")
                self.log(f"Erro: {e}")

        tk.Button(admin_window, text="Criar Utilizador", command=create_admin).grid(row=3, column=0, columnspan=2,
                                                                                    pady=10)

    def start_platform(self):
        if not self.db_verified:
            messagebox.showerror("Erro", "É necessário verificar a Base de Dados primeiro.")
            return

        self.log("A iniciar a plataforma...")
        os.system("python app.py")


if __name__ == "__main__":
    root = tk.Tk()
    app_gui = DatabaseInstallerApp(root)
    root.mainloop()
