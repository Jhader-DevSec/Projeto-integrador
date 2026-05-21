# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from banco import usuarios_fake  # Importa os usuários para validar o login

# Inicializa o Blueprint de Autenticação para modularizar as rotas de login
auth_bp = Blueprint('auth', __name__)

# Rota que renderiza a página de login
@auth_bp.route('/login')
def login_page():
    # BARREIRA DE SEGURANÇA: Se o usuário já tiver uma sessão ativa, impede que ele veja o login novamente
    if 'usuario_logado' in session:
        # Se for o administrador, manda direto para o painel administrativo
        if session['usuario_logado'] == 'admin@brasas.com':
            return redirect(url_for('admin.admin_panel'))
        # Se for usuário comum, manda para a tela de vendas
        return redirect(url_for('vendas.index'))
        
    # Se não estiver logado, carrega o HTML da tela de login normalmente
    return render_template('login_page.html')


# Rota do tipo POST que processa os dados digitados no formulário de login
@auth_bp.route('/autenticar', methods=['POST'])
def autenticar():
    email = request.form.get('email')        # Captura o e-mail digitado no HTML
    senha = request.form.get('password')     # Captura a senha digitada no HTML

    # Validação: Verifica se o e-mail existe no dicionário e se a senha bate
    if email in usuarios_fake and usuarios_fake[email] == senha:
        session['usuario_logado'] = email    # Cria a sessão de login salvando o e-mail do usuário
        
        # Redirecionamento baseado no nível de acesso (Role-Based Redirection)
        if email == 'admin@brasas.com':
            return redirect(url_for('admin.admin_panel')) # Admin vai gerenciar o sistema
            
        return redirect(url_for('vendas.index'))          # Funcionário comum vai vender
    else:
        # Se errar as credenciais, envia uma mensagem de alerta e joga de volta para o login
        flash('E-mail ou senha incorretos!', 'erro')
        return redirect(url_for('auth.login_page'))


# Rota provisória criada para resolver o erro de BuildError do botão "Esqueci a Senha"
@auth_bp.route('/recuperar-senha')
def recuperar_senha():
    return "<h3>Página de recuperação de senha em desenvolvimento... 🔥</h3>"


# Rota que finaliza a sessão do usuário (Logout)
@auth_bp.route('/logout')
def logout():
    session.pop('usuario_logado', None)      # Destrói a sessão ativa apagando o e-mail salvo
    flash('Você saiu do sistema com sucesso.', 'sucesso') # Alerta de sucesso
    return redirect(url_for('auth.login_page')) # Redireciona o usuário deslogado para o início