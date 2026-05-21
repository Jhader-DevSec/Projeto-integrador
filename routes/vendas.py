# routes/vendas.py
from flask import Blueprint, render_template, redirect, url_for, session, flash
from banco import produtos_fake  # Importa o estoque de produtos para exibir na tela

# Inicializa o Blueprint operacional das vendas
vendas_bp = Blueprint('vendas', __name__)

# Rota da página principal (Painel do Espetinho do Edir)
@vendas_bp.route('/')
def index():
    # BARREIRA DE SEGURANÇA: Impede que qualquer pessoa acesse o sistema digitando a URL direta
    if 'usuario_logado' not in session:
        flash('Por favor, faça o login para acessar o sistema.', 'erro')
        return redirect(url_for('auth.login_page'))
    
    # Se estiver logado, renderiza o painel de vendas e envia o estoque de produtos atualizado
    return render_template('projeto.html', produtos=produtos_fake)