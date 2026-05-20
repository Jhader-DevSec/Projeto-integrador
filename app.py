from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

# CHAVE SECRETA: Necessária para o Flask gerenciar as sessões de login com segurança
app.secret_key = 'chave_super_secreta_para_a_faculdade'

# --- BANCO DE DADOS EM MEMÓRIA ---
usuarios_fake = {
    "admin@brasas.com": {"senha": "senha123", "cargo": "Gerente"},
    "vendedor@brasas.com": {"senha": "123", "cargo": "Vendedor"},
    "estoque@brasas.com": {"senha": "123", "cargo": "Estoquista"}
}

# 1. ROTA DA TELA DE LOGIN
@app.route('/login')
def login_page():
    if 'usuario_logado' in session:
        if session.get('cargo_logado') == 'Gerente':
            return redirect(url_for('admin_panel'))
        return redirect(url_for('index'))
    return render_template('login_page.html')

# 2. ROTA DE AUTENTICAÇÃO
@app.route('/autenticar', methods=['POST'])
def autenticar():
    email = request.form.get('email')
    senha = request.form.get('password') 

    if email in usuarios_fake and usuarios_fake[email]['senha'] == senha:
        session['usuario_logado'] = email
        session['cargo_logado'] = usuarios_fake[email]['cargo']
        
        if session['cargo_logado'] == 'Gerente':
            return redirect(url_for('admin_panel'))
        return redirect(url_for('index'))
    else:
        flash('E-mail ou senha incorretos!', 'erro')
        return redirect(url_for('login_page'))

# 3. ROTA PRINCIPAL DO PROJETO / ESPETINHO DO EDIR
@app.route('/')
def index():
    if 'usuario_logado' not in session:
        flash('Por favor, faça o login para acessar o sistema.', 'erro')
        return redirect(url_for('login_page'))
    return render_template('projeto.html')

# 4. ROTA DE LOGOUT
@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    session.pop('cargo_logado', None)
    flash('Você saiu do sistema com sucesso.', 'sucesso')
    return redirect(url_for('login_page'))

# --- ROTAS DO PAINEL ADMINISTRATIVO ---

# 5. ABRIR O PAINEL DO ADMIN
@app.route('/admin')
def admin_panel():
    cargo_atual = session.get('cargo_logado')
    
    if cargo_atual != 'Gerente':
        flash('Acesso negado! Área restrita para Gerentes.', 'erro')
        return redirect(url_for('index'))

    return render_template('admin_page.html', usuarios=usuarios_fake)

# 6. CRIAR USUÁRIO PELO PAINEL
@app.route('/admin/criar', methods=['POST'])
def admin_criar():
    if session.get('cargo_logado') != 'Gerente':
        return redirect(url_for('login_page'))

    email = request.form.get('email')
    senha = request.form.get('senha')
    cargo = request.form.get('cargo') 

    if email in usuarios_fake:
        flash(f'O usuário {email} já existe no sistema.', 'erro')
    else:
        usuarios_fake[email] = {"senha": senha, "cargo": cargo}
        flash(f'Usuário {email} criado com sucesso como {cargo}!', 'sucesso')

    return redirect(url_for('admin_panel'))

# 7. DELETAR USUÁRIO PELO PAINEL
@app.route('/admin/deletar/<email>')
def admin_deletar(email):
    if session.get('cargo_logado') != 'Gerente':
        return redirect(url_for('login_page'))

    if email == 'admin@brasas.com':
        flash('Você não pode deletar o administrador principal!', 'erro')
    elif email in usuarios_fake:
        del usuarios_fake[email]
        flash(f'Usuário {email} removido com sucesso.', 'sucesso')

    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)