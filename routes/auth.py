# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_bp = Blueprint('auth', __name__)

# Rota para renderizar a página visual de Login
@auth_bp.route('/login')
def login_page():
    return render_template('login_page.html')

# Rota que processa os dados digitados no formulário
@auth_bp.route('/autenticar', methods=['POST'])
def autenticar():
    # 1. PEGA OS DADOS DIGITADOS PELO UTILIZADOR NO HTML
    email_digitado = request.form.get('email')
    senha_digitada = request.form.get('senha')

    # 💡 EVITA IMPORTAÇÃO CIRCULAR: Importa o modelo Usuario aqui dentro
    from app import Usuario

    try:
        # 2. BUSCA NO BANCO: Procura se existe algum usuário com o email digitado
        usuario = Usuario.query.filter_by(email=email_digitado).first()

        # 3. VALIDAÇÃO DE CREDENCIAIS
        # Verifica se o usuário existe E se a senha coincide com a do banco
        if usuario and usuario.senha == senha_digitada:
            
            # Cria a sessão do utilizador com o email (para o teu projeto.html linha 18 funcionar)
            session['usuario_logado'] = usuario.email
            session['nome_usuario'] = usuario.nome
            session['nivel_acesso'] = usuario.nivel_acesso
            
            flash(f'Bem-vindo de volta, {usuario.nome}!', 'sucesso')

            # 4. REDIRECIONAMENTO POR NÍVEL DE ACESSO
            if usuario.nivel_acesso == 'admin':
                return redirect(url_for('admin.admin_panel')) # Vai para o Painel Admin se for o Edir
            else:
                return redirect(url_for('vendas.index')) # Vai para a tela de Vendas se for funcionário/cliente
        
        else:
            # Se o email não existir ou a senha estiver errada
            flash('Utilizador ou senha incorretos!', 'erro')
            return redirect(url_for('auth.login_page'))

    except Exception as e:
        print(f"Erro ao autenticar no banco de dados: {e}")
        flash("Erro técnico ao tentar conectar ao servidor de login.", "erro")
        return redirect(url_for('auth.login_page'))

# Rota para fazer Logout (Sair do Sistema)
@auth_bp.route('/logout')
def logout():
    session.clear() # Limpa todas as variáveis salvas na sessão
    flash('Sessão encerrada com sucesso.', 'sucesso')
    return redirect(url_for('auth.login_page'))