import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "chave_super_secreta_para_a_faculdade"
)

# ==========================
# CONFIGURAÇÃO MYSQL
# ==========================

USUARIO = os.getenv("MYSQL_USER")
SENHA = os.getenv("MYSQL_PASSWORD")
HOST = os.getenv("MYSQL_HOST")
PORTA = os.getenv("MYSQL_PORT", "3306")
NOME_BANCO = os.getenv("MYSQL_DATABASE")

print("MYSQL_USER =", USUARIO)
print("MYSQL_HOST =", HOST)
print("MYSQL_DATABASE =", NOME_BANCO)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{NOME_BANCO}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==========================
# MODELOS
# ==========================

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
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=True
    )

    itens = db.relationship(
        'ItensPedido',
        backref='pedido_pai',
        lazy=True
    )


class ItensPedido(db.Model):
    __tablename__ = 'itens_pedido'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey('pedidos.id'),
        nullable=False
    )
    produto_id = db.Column(
        db.Integer,
        db.ForeignKey('produtos.id'),
        nullable=False
    )
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    produto = db.relationship('Produto')


# ==========================
# LIMITER
# ==========================

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# ==========================
# BLUEPRINTS
# ==========================

from routes.auth import auth_bp
from routes.vendas import vendas_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(vendas_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)