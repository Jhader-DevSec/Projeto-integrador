# app.py
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Importação dos módulos (Blueprints) especializados de cada arquivo de rotas
from routes.auth import auth_bp
from routes.vendas import vendas_bp
from routes.admin import admin_bp

# Criação e inicialização do servidor Flask
app = Flask(__name__)

# Definição da assinatura criptográfica das sessões (Chave Secreta obrigatória do Flask)
app.secret_key = 'chave_super_secreta_para_a_faculdade'

# Configuração do Middleware de Segurança contra ataques automatizados (DDoS / Força Bruta)
limiter = Limiter(
    get_remote_address, # Rastreia as requisições baseando-se no IP do computador do cliente
    app=app,
    default_limits=["200 per day", "50 per hour"] # Limita a segurança global do servidor
)

# Acoplamento e ativação dos módulos de código no motor principal do Flask
app.register_blueprint(auth_bp)
app.register_blueprint(vendas_bp)
app.register_blueprint(admin_bp)

# Inicia o servidor local caso este arquivo seja executado diretamente
if __name__ == '__main__':
    app.run(debug=True) # debug=True faz o servidor reiniciar automaticamente ao salvar alterações