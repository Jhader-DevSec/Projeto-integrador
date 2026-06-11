# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_page():
    return render_template('login_page.html')

@auth_bp.route('/autenticar', methods=['POST'])
def autenticar():
    # 1. PEGA OS DADOS DIGITADOS BASEADO NO 'NAME' DO SEU FORMULÁRIO HTML
    email_digitado = request.form.get('email')
    senha_digitada = request.form.get('password') # Corrigido para dar match com name="password"

    from app import Usuario

    try:
        # 2. BUSCA NO BANCO
        usuario = Usuario.query.filter_by(email=email_digitado).first()

        # 3. VALIDAÇÃO DE CREDENCIAIS REAIS
        if usuario and usuario.senha == senha_digitada:
            session['usuario_logado'] = usuario.email
            session['nome_usuario'] = usuario.nome
            session['nivel_acesso'] = usuario.nivel_acesso
            
            flash(f'Bem-vindo de volta, {usuario.nome}!', 'sucesso')

            # 4. REDIRECIONAMENTO INTELIGENTE POR NÍVEL
            if usuario.nivel_acesso == 'admin':
                return redirect(url_for('admin.admin_panel'))
            else:
                return redirect(url_for('vendas.index'))
        
        else:
            flash('Usuário ou senha incorretos!', 'erro')
            return redirect(url_for('auth.login_page'))

    except Exception as e:
        print(f"Erro de autenticação no servidor MySQL: {e}")
        flash("Erro técnico de comunicação com o servidor de dados.", "erro")
        return redirect(url_for('auth.login_page'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'sucesso')
    return redirect(url_for('auth.login_page'))