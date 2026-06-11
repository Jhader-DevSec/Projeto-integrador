# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 1. CRIAÇÃO DO APP
app = Flask(__name__)
app.secret_key = 'chave_super_secreta_para_a_faculdade'

# 2. CONFIGURAÇÃO DO BANCO DE DADOS (CLEVER CLOUD)
USUARIO = "ua7ena8hoi5elyvo"
SENHA = "AFZEmdIewHuPCt1UQH2I" 
HOST = "bb5xdtk17gidsyrp3fky-mysql.services.clever-cloud.com"
PORTA = "3306"
NOME_BANCO = "bb5xdtk17gidsyrp3fky"

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{NOME_BANCO}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELOS DO BANCO DE DADOS (MAPEAMENTO)
# ==========================================

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    estoque = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nivel_acesso = db.Column(db.String(20), nullable=False)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Pendente')
    forma_pagamento = db.Column(db.String(50), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Relação para carregar os itens internos do pedido automaticamente
    itens = db.relationship('ItensPedido', backref='pedido_pai', lazy=True)

class ItensPedido(db.Model):
    __tablename__ = 'itens_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    # Permite extrair dados como item.produto.nome diretamente
    produto = db.relationship('Produto')

# 3. CONFIGURAÇÃO DE SEGURANÇA (LIMITER)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# 4. IMPORTAÇÃO E REGISTRO DOS BLUEPRINTS
from routes.auth import auth_bp
from routes.vendas import vendas_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(vendas_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True)