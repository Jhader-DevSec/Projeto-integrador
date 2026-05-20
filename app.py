from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_projeto' 

# 1. Configurando o sistema de limite (rastreando pelo IP do usuário)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"] # Limite de segurança geral para o site todo
)

# CHAVE SECRETA: Necessária para o Flask conseguir gerenciar o login do usuário com segurança
app.secret_key = 'chave_super_secreta_para_a_faculdade'

# --- NOSSO "BANCO DE DADOS" EM MEMÓRIA ---
# Adicionamos o admin padrão e um usuário comum para você testar na apresentação
usuarios_fake = {
    "admin@brasas.com": "senha123",
    "teste@brasas.com": "123456"
}
# ----------------------------------------------


# 1. ROTA DA TELA DE LOGIN
@app.route('/login')
def login_page():
    # Se já estiver logado, não deixa ir pra tela de login, manda direto pro sistema
    if 'usuario_logado' in session:
        if session['usuario_logado'] == 'admin@brasas.com':
            return redirect(url_for('admin_panel'))
        return redirect(url_for('index'))
        
    return render_template('login_page.html')


# 2. ROTA DE AUTENTICAÇÃO (Onde o formulário do HTML bate)
@app.route('/autenticar', methods=['POST'])
def autenticar():
    email = request.form.get('email')
    senha = request.form.get('password') # Busca exatamente o name="password" do seu HTML

    # Verifica se o email e a senha estão corretos no nosso dicionário
    if email in usuarios_fake and usuarios_fake[email] == senha:
        # Salva o usuário na sessão do Flask
        session['usuario_logado'] = email
        
        # Se for o administrador, vai para a aba do admin
        if email == 'admin@brasas.com':
            return redirect(url_for('admin_panel'))
            
        # Se for um usuário normal, vai para a página do projeto
        return redirect(url_for('index'))
    else:
        # Se errar, mostra a mensagem na tela e volta pro login
        flash('E-mail ou senha incorretos!', 'erro')
        return redirect(url_for('login_page'))


# 3. ROTA PRINCIPAL DO PROJETO (Protegida)
@app.route('/')
def index():
    # Se não fez login, barra o acesso
    if 'usuario_logado' not in session:
        flash('Por favor, faça o login para acessar o sistema.', 'erro')
        return redirect(url_for('login_page'))
    
    # Se passou, carrega a página do projeto da barraca
    return render_template('projeto.html')


# 4. ROTA DE SAIR DO SISTEMA
@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    flash('Você saiu do sistema com sucesso.', 'sucesso')
    return redirect(url_for('login_page'))


# --- ROTAS DO PAINEL ADMINISTRATIVO ---

# 5. ABRIR O PAINEL DO ADMIN
@app.route('/admin')
def admin_panel():
    usuario_atual = session.get('usuario_logado')
    
    # Barreira de Segurança: só o admin entra
    if usuario_atual != 'admin@brasas.com':
        flash('Acesso negado! Área restrita para administradores.', 'erro')
        return redirect(url_for('index'))

    return render_template('admin_page.html', usuarios=usuarios_fake)


# 6. CRIAR USUÁRIO PELO PAINEL
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


# 7. DELETAR USUÁRIO PELO PAINEL
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


# Roda o servidor
if __name__ == '__main__':
    app.run(debug=True)