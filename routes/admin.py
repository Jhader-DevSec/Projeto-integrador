# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_panel():
    # BARREIRA DE SEGURANÇA REAL: Bloqueia qualquer usuário que não seja admin
    if session.get('nivel_acesso') != 'admin':
        flash('Acesso negado! Área restrita para administradores.', 'erro')
        return redirect(url_for('vendas.index'))

    from app import Usuario
    try:
        # Busca a lista completa de funcionários direto da nuvem
        usuarios_banco = Usuario.query.all()
        return render_template('admin_page.html', usuarios=usuarios_banco)
    except Exception as e:
        print(f"Erro ao carregar painel administrativo: {e}")
        flash("Erro ao conectar com a tabela de funcionários.", "erro")
        return redirect(url_for('vendas.index'))


@admin_bp.route('/admin/criar', methods=['POST'])
def admin_criar():
    if session.get('nivel_acesso') != 'admin':
        return redirect(url_for('auth.login_page'))

    email = request.form.get('email')
    senha = request.form.get('senha')
    cargo = request.form.get('cargo') 

    # Padroniza os cargos da interface para o nível de acesso aceito no banco
    nivel_acesso = 'admin' if cargo == 'Gerente' else 'funcionario'

    from app import db, Usuario

    try:
        # Impede e-mails duplicados na base de dados
        usuario_existe = Usuario.query.filter_by(email=email).first()
        if usuario_existe:
            flash(f'O usuário {email} já existe no sistema.', 'erro')
        else:
            # Como a coluna 'nome' é NOT NULL no banco, geramos um nome com base no e-mail
            nome_padrao = email.split('@')[0].capitalize()
            
            novo_usuario = Usuario(nome=nome_padrao, email=email, senha=senha, nivel_acesso=nivel_acesso)
            db.session.add(novo_usuario)
            db.session.commit()
            flash(f'Usuário {email} cadastrado com sucesso!', 'sucesso')
            
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar novo funcionário: {e}")
        flash("Erro interno ao tentar salvar os dados.", "erro")

    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/admin/deletar/<email>')
def admin_deletar(email):
    if session.get('nivel_acesso') != 'admin':
        return redirect(url_for('auth.login_page'))

    # Impede que o administrador exclua a si mesmo comparando com a sessão ativa
    if email == session.get('usuario_logado'):
        flash('Você não pode deletar a si mesmo!', 'erro')
        return redirect(url_for('admin.admin_panel'))

    from app import db, Usuario

    try:
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            flash(f'Usuário {email} removido com sucesso.', 'sucesso')
        else:
            flash('Usuário não encontrado na base de dados.', 'erro')
            
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao deletar registro: {e}")
        flash("Erro ao processar a exclusão no banco de dados.", "erro")

    return redirect(url_for('admin.admin_panel'))