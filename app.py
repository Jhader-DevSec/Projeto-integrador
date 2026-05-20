from flask import Flask, render_template, request, redirect, url_for, session, flash

# ===================================================
# 1. CONFIGURAÇÕES E INICIALIZAÇÃO DO APP
# ===================================================
app = Flask(__name__)

# CHAVE SECRETA: Necessária para o Flask gerenciar as sessões de login com segurança
app.secret_key = 'chave_super_secreta_para_a_faculdade'


# ===================================================
# 2. "BANCO DE DADOS" EM MEMÓRIA
# ===================================================
usuarios_fake = {
    "admin@brasas.com": "senha123",
    "teste@brasas.com": "123456"
}


# ===================================================
# 3. BLOCO DE AUTENTICAÇÃO (Login, Validação e Sair)
# ===================================================

@app.route('/login')
def login_page():
    # Se já estiver logado, não deixa ir pra tela de login, manda direto pro lugar certo
    if 'usuario_logado' in session:
        if session['usuario_logado'] == 'admin@brasas.com':
            return redirect(url_for('admin_panel'))
        return redirect(url_for('index'))
        
    return render_template('login_page.html')


@app.route('/autenticar', methods=['POST'])
def autenticar():
    email = request.form.get('email')
    senha = request.form.get('password') # Busca o name="password" do HTML

    # Verifica se o email e a senha batem com o nosso dicionário
    if email in usuarios_fake and usuarios_fake[email] == senha:
        session['usuario_logado'] = email
        
        # Divisão de águas: Admin vai para o painel, usuário comum vai para as vendas
        if email == 'admin@brasas.com':
            return redirect(url_for('admin_panel'))
            
        return redirect(url_for('index'))
    else:
        flash('E-mail ou senha incorretos!', 'erro')
        return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    flash('Você saiu do sistema com sucesso.', 'sucesso')
    return redirect(url_for('login_page'))


# ===================================================
# 4. BLOCO OPERACIONAL (O Core do App / Tela de Vendas)
# ===================================================

@app.route('/')
def index():
    # Barreira de Segurança: Se não fez login, é chutado de volta para a tela de login
    if 'usuario_logado' not in session:
        flash('Por favor, faça o login para acessar o sistema.', 'erro')
        return redirect(url_for('login_page'))
    
    # Se a sessão estiver ativa, carrega o painel principal com o efeito de slide
    return render_template('projeto.html')


# ===================================================
# 5. BLOCO ADMINISTRATIVO (Gestão de Usuários)
# ===================================================

@app.route('/admin')
def admin_panel():
    usuario_atual = session.get('usuario_logado')
    
    # Barreira de Segurança do Admin: só o e-mail master entra aqui
    if usuario_atual != 'admin@brasas.com':
        flash('Acesso negado! Área restrita para administradores.', 'erro')
        return redirect(url_for('index'))

    return render_template('admin_page.html', usuarios=usuarios_fake)


@app.route('/admin/criar', methods=['POST'])
def admin_criar():
    if session.get('usuario_logado') != 'admin@brasas.com':
        return redirect(url_for('login_page'))

    email = request.form.get('email')
    senha = request.form.get('senha')

    if email in usuarios_fake:
        flash(f'O usuário {email} já existe no sistema.', 'erro')
    else:
        usuarios_fake[email] = senha
        flash(f'Usuário {email} criado com sucesso!', 'sucesso')

    return redirect(url_for('admin_panel'))


@app.route('/admin/deletar/<email>')
def admin_deletar(email):
    if session.get('usuario_logado') != 'admin@brasas.com':
        return redirect(url_for('login_page'))

    if email == 'admin@brasas.com':
        flash('Você não pode deletar o administrador principal!', 'erro')
    elif email in usuarios_fake:
        del usuarios_fake[email]
        flash(f'Usuário {email} removido com sucesso.', 'sucesso')

    return redirect(url_for('admin_panel'))


# ===================================================
# 6. EXECUÇÃO DO SERVIDOR LOCAL
# ===================================================
if __name__ == '__main__':
    app.run(debug=True)