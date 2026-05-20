from flask import Flask, render_template, request, redirect, url_for, flash
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

@app.route('/')
def login():
    return render_template('login_page.html')

# 2. Aplicando a regra de limite nesta rota específica
@app.route('/autenticar', methods=['POST'])
@limiter.limit("5 per 2 minutes") # Regra: 5 tentativas a cada 2 minutos
def autenticar():
    email_digitado = request.form.get('email')
    senha_digitada = request.form.get('password')

    if email_digitado == 'admin@gmail.com' and senha_digitada == 'admin':
        return redirect(url_for('projeto'))
    else:
        flash('E-mail ou senha incorretos. Tente novamente.')
        return redirect(url_for('login'))

# 3. Criando uma tela amigável caso o usuário passe do limite
@app.errorhandler(429)
def limite_excedido(e):
    # O código 429 significa "Too Many Requests" (Muitas requisições)
    flash("Você errou a senha muitas vezes. Por segurança, aguarde 2 minutos para tentar novamente.")
    return redirect(url_for('login'))

#Redirecionando para a página do projeto (após logar)
@app.route('/projeto')
def projeto():
    return render_template('projeto.html')

# Redirecionando para o recuperar senha
@app.route('/recuperar_senha')
def recuperar_senha():
    return render_template('recuperar_senha.html')

if __name__ == '__main__':
    app.run(debug=True)