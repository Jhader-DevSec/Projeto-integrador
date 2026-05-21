# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from banco import usuarios_fake, produtos_fake  # Importa os dados que o admin pode manipular

# Inicializa o Blueprint das funcionalidades administrativas
admin_bp = Blueprint('admin', __name__)

# Rota que carrega a tela do Painel de Controle do Administrador
@admin_bp.route('/admin')
def admin_panel():
    usuario_atual = session.get('usuario_logado')
    
    # BARREIRA DE SEGURANÇA MÁXIMA: Bloqueia usuários comuns de acessarem o painel de gestão
    if usuario_atual != 'admin@brasas.com':
        flash('Acesso negado! Área restrita para administradores.', 'erro')
        return redirect(url_for('vendas.index'))

    # Se for o administrador principal, carrega a tela enviando as listas de usuários e produtos
    return render_template('admin_page.html', usuarios=usuarios_fake, produtos=produtos_fake)


# Rota POST para criar novas credenciais de funcionários no sistema
@admin_bp.route('/admin/criar', methods=['POST'])
def admin_criar():
    # Proteção de redundância caso tentem enviar dados fora da interface
    if session.get('usuario_logado') != 'admin@brasas.com':
        return redirect(url_for('auth.login_page'))

    email = request.form.get('email')
    senha = request.form.get('senha')

    # Verifica se o funcionário já está cadastrado para evitar duplicidade
    if email in usuarios_fake:
        flash(f'O usuário {email} já existe no sistema.', 'erro')
    else:
        usuarios_fake[email] = senha # Insere as novas credenciais no dicionário em memória
        flash(f'Usuário {email} criado com sucesso!', 'sucesso')

    return redirect(url_for('admin.admin_panel'))


# Rota para excluir funcionários cadastrados através do e-mail recebido pela URL
@admin_bp.route('/admin/deletar/<email>')
def admin_deletar(email):
    # Proteção de segurança na rota de exclusão
    if session.get('usuario_logado') != 'admin@brasas.com':
        return redirect(url_for('auth.login_page'))

    # Regra de Negócio: Impede que o administrador acabe excluindo a si mesmo do sistema
    if email == 'admin@brasas.com':
        flash('Você não pode deletar o administrador principal!', 'erro')
    elif email in usuarios_fake:
        del usuarios_fake[email] # Remove o registro do dicionário
        flash(f'Usuário {email} removido com sucesso.', 'sucesso')

    return redirect(url_for('admin.admin_panel'))


# Rota POST para cadastrar novos produtos e quantidades no estoque
@admin_bp.route('/admin/produto/criar', methods=['POST'])
def admin_criar_produto():
    # Proteção de segurança na rota de estoque
    if session.get('usuario_logado') != 'admin@brasas.com':
        return redirect(url_for('auth.login_page'))

    nome = request.form.get('nome')
    preco = float(request.form.get('preco'))    # Converte o preço vindo do HTML para número decimal
    estoque = int(request.form.get('estoque'))  # Converte a quantidade vindo do HTML para número inteiro

    # Gera um ID automático sequencial para o produto baseado no tamanho do estoque atual
    novo_id = str(len(produtos_fake) + 1)
    
    # Cria a estrutura do produto dentro do dicionário centralizado
    produtos_fake[novo_id] = {"nome": nome, "preco": preco, "estoque": estoque}
    
    flash(f'Produto {nome} cadastrado com sucesso!', 'sucesso')
    return redirect(url_for('admin.admin_panel'))