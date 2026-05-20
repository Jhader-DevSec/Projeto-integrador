from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

# CHAVE SECRETA: Necessária para o Flask gerenciar as sessões de login
app.secret_key = 'chave_super_secreta_para_a_faculdade'

# --- NOSSO NOVO "BANCO DE DADOS" EM MEMÓRIA ---
# Agora guardamos a senha E o cargo de cada usuário
usuarios_fake = {
    "admin@brasas.com": {"senha": "senha123", "cargo": "Gerente"},
    "vendedor@brasas.com": {"senha": "123", "cargo": "Vendedor"},
    "estoque@brasas.com": {"senha": "123", "cargo": "Estoquista"}
}
# ----------------------------------------------


# 1. ROTA DA TELA DE LOGIN
@app.route('/login')
def login_page():
    if 'usuario_logado' in session:
        if session.get('cargo_logado') == 'Gerente':
            return redirect(url_for('admin_panel'))
        return redirect(url_for('index'))
        
    return render_template('login_page.html')


# 2. ROTA DE AUTENTICAÇÃO (Onde o formulário do HTML bate)
@app.route('/autenticar', methods=['POST'])
def autenticar():
    email = request.form.get('email')
    senha = request.form.get('password') 

    # Verifica se o email existe e se a senha interna bate
    if email in usuarios_fake and usuarios_fake[email]['senha'] == senha:
        session['usuario_logado'] = email
        # SALVA O CARGO NA SESSÃO para usarmos depois
        session['cargo_logado'] = usuarios_fake[email]['cargo']
        
        # Se for Gerente, vai direto para o Painel Admin
        if session['cargo_logado'] == 'Gerente':
            return redirect(url_for('admin_panel'))
            
        # Se for Vendedor ou Estoquista, vai direto para o Espetinho do Edir (rota index)
        return redirect(url_for('index'))
    else:
        flash('E-mail ou senha incorretos!', 'erro')
        return redirect(url_for('login_page'))


# 3. ROTA PRINCIPAL DO PROJETO / ESPETINHO DO EDIR (Protegida)
@app.route('/')
def index():
    if 'usuario_logado' not in session:
        flash('Por favor, faça o login para acessar o sistema.', 'erro')
        return redirect(url_for('login_page'))
    
    # Renderiza o seu HTML principal da barraca
    return render_template('projeto.html')


# 4. ROTA DE SAIR DO SISTEMA
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
    usuario_atual = session.get('usuario_logado')
    cargo_atual = session.get('cargo_logado')
    
    # Apenas Gerentes podem acessar este painel
    if cargo_atual != 'Gerente':
        flash('Acesso negado! Área restrita para Gerentes.', 'erro')
        return redirect(url_for('index'))

    return render_template('admin_page.html', usuarios=usuarios_fake)


# 6. CRIAR USUÁRIO PELO PAINEL (Com Cargo)
@app.route('/admin/criar', methods=['POST'])
def admin_criar():
    if session.get('cargo_logado') != 'Gerente':
        return redirect(url_for('login_page'))

    email = request.form.get('email')
    senha = request.form.get('senha')
    cargo = request.form.get('cargo') # Pega o cargo selecionado no <select> do HTML

    if email in usuarios_fake:
        flash(f'O usuário {email} já existe no sistema.', 'erro')
    else:
        # Salva usando a nova estrutura de dicionário
        usuarios_fake[email] = {"senha": senha, "cargo": cargo}
        flash(f'Usuário {email} criado com sucesso como {cargo}!', 'sucesso')

    return redirect(url_for('admin_panel'))


# 7. DELETAR USUÁRIO PELO PAINEL
@app.route('/admin/deletar/<email>')
def admin_deletar(email):
    if session.get('cargo_logado') != 'Gerente':
        return redirect(url_for('login_page'))

    # Proteção para o admin principal não se auto-deletar
    if email == 'admin@brasas.com':
        flash('Você não pode deletar o administrador principal!', 'erro')
    elif email in usuarios_fake:
        del usuarios_fake[email]
        flash(f'Usuário {email} removido com sucesso.', 'sucesso')

    return redirect(url_for('admin_panel'))


if __name__ == '__main__':
    app.run(debug=True)