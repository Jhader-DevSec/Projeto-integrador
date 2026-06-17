# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

admin_bp = Blueprint('admin', __name__)

# --- PAINEL PRINCIPAL ---
@admin_bp.route('/admin')
def admin_panel():
    # Barreira de segurança: Acesso restrito a admin
    if session.get('nivel_acesso') != 'admin':
        flash('Acesso negado! Área restrita para administradores.', 'erro')
        return redirect(url_for('vendas.index'))

    from app import Usuario, Produto
    try:
        # Busca ambas as listas para exibir no painel
        usuarios_banco = Usuario.query.all()
        produtos_banco = Produto.query.all()
        return render_template('admin_page.html', usuarios=usuarios_banco, produtos=produtos_banco)
    except Exception as e:
        print(f"Erro ao carregar painel administrativo: {e}")
        flash("Erro ao conectar com o banco de dados.", "erro")
        return redirect(url_for('vendas.index'))

# --- ROTAS DE USUÁRIOS ---
@admin_bp.route('/admin/criar', methods=['POST'])
def admin_criar():
    if session.get('nivel_acesso') != 'admin': return redirect(url_for('auth.login_page'))

    email = request.form.get('email')
    senha = request.form.get('senha')
    cargo = request.form.get('cargo') 
    nivel_acesso = 'admin' if cargo == 'Gerente' else 'funcionario'

    from app import db, Usuario
    try:
        if Usuario.query.filter_by(email=email).first():
            flash(f'O usuário {email} já existe.', 'erro')
        else:
            nome_padrao = email.split('@')[0].capitalize()
            novo_usuario = Usuario(nome=nome_padrao, email=email, senha=senha, nivel_acesso=nivel_acesso)
            db.session.add(novo_usuario)
            db.session.commit()
            flash(f'Usuário {email} cadastrado com sucesso!', 'sucesso')
    except Exception as e:
        db.session.rollback()
        flash("Erro interno ao salvar usuário.", "erro")
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/deletar/<email>')
def admin_deletar(email):
    if session.get('nivel_acesso') != 'admin': return redirect(url_for('auth.login_page'))

    if email == session.get('usuario_logado'):
        flash('Você não pode deletar a si mesmo!', 'erro')
        return redirect(url_for('admin.admin_panel'))

    from app import db, Usuario
    try:
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            flash(f'Usuário {email} removido.', 'sucesso')
    except Exception:
        db.session.rollback()
        flash("Erro ao excluir usuário.", "erro")
    return redirect(url_for('admin.admin_panel'))

# --- ROTAS DE PRODUTOS ---
@admin_bp.route('/admin/produto/cadastrar', methods=['POST'])
def admin_cadastrar_produto():
    if session.get('nivel_acesso') != 'admin': return redirect(url_for('auth.login_page'))
    
    from app import db, Produto
    try:
        nome = request.form.get('nome')
        preco = request.form.get('preco')
        estoque = request.form.get('estoque')
        
        novo_produto = Produto(nome=nome, preco=float(preco), estoque=int(estoque))
        db.session.add(novo_produto)
        db.session.commit()
        flash(f'Produto {nome} cadastrado!', 'sucesso')
    except Exception:
        db.session.rollback()
        flash("Erro ao cadastrar produto.", "erro")
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/produto/remover/<int:id>')
def admin_remover_produto(id):
    if session.get('nivel_acesso') != 'admin': return redirect(url_for('auth.login_page'))
    
    from app import db, Produto
    try:
        produto = Produto.query.get(id)
        if produto:
            db.session.delete(produto)
            db.session.commit()
            flash('Produto removido!', 'sucesso')
    except Exception:
        db.session.rollback()
        flash("Erro ao remover produto.", "erro")
    return redirect(url_for('admin.admin_panel'))