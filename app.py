# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 1. CRIAÇÃO DO APP
app = Flask(__name__)
app.secret_key = 'chave_super_secreta_para_a_faculdade'

# 2. CONFIGURAÇÃO DO BANCO DE DADOS (Deve vir antes das rotas!)
USUARIO = "ua7ema8hoi5elyvo"
SENHA = "SUA_SENHA_DO_CADEADO_LARANJA" # Insira aqui a senha real da Clever Cloud
HOST = "bb5xdtk17gidsyrp3fky-mysql.services.clever-cloud.com"
PORTA = "3306"
NOME_BANCO = "bb5xdtk17gidsyrp3fky"

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{NOME_BANCO}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELO DOS PRODUTOS
class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    estoque = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    
    # --- MODELO DOS USUÁRIOS (Mapeamento da Tabelausuarios) ---
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nivel_acesso = db.Column(db.String(20), nullable=False)

# 3. CONFIGURAÇÃO DE SEGURANÇA (LIMITER)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# 4. IMPORTAÇÃO E REGISTRO DOS BLUEPRINTS (SÓ AGORA QUE O DB JÁ EXISTE)
from routes.auth import auth_bp
from routes.vendas import vendas_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(vendas_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True)