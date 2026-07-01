# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from datetime import datetime
import io

# Dependências necessárias para a exportação de relatórios gerenciais em PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

admin_bp = Blueprint('admin', __name__)

# --- PAINEL PRINCIPAL ---
@admin_bp.route('/admin')
def admin_panel():
    # Permite a entrada apenas de Gerentes (admin) e Estoquistas
    nivel = session.get('nivel_acesso')
    if nivel not in ['admin', 'estoquista']:
        flash('Acesso negado! Área restrita.', 'erro')
        return redirect(url_for('vendas.index'))

    from app import Usuario, Produto
    try:
        usuarios_banco = Usuario.query.all()
        produtos_banco = Produto.query.all()
        return render_template('admin_page.html', usuarios=usuarios_banco, produtos=produtos_banco)
    except Exception as e:
        print(f"Erro ao carregar painel administrativo: {e}")
        flash("Erro ao conectar com o banco de dados.", "erro")
        return redirect(url_for('vendas.index'))


# --- ROTAS DE USUÁRIOS (Acesso exclusivo do Gerente) ---

@admin_bp.route('/admin/criar', methods=['POST'])
def admin_criar():
    if session.get('nivel_acesso') != 'admin':
        flash('Acesso negado! Permissão restrita a gerentes.', 'erro')
        return redirect(url_for('vendas.index'))

    email = request.form.get('email')
    senha = request.form.get('senha')
    cargo = request.form.get('cargo') 

    # Mapeia as opções literais do formulário HTML para os escopes de RBAC do sistema
    cargo_map = {
        'Gerente': 'admin',
        'Estoquista': 'estoquista',
        'Vendedor': 'vendedor'
    }
    nivel_acesso = cargo_map.get(cargo, 'vendedor')

    from app import db, Usuario
    try:
        if Usuario.query.filter_by(email=email).first():
            flash(f'O usuário {email} já existe no sistema.', 'erro')
        else:
            nome_padrao = email.split('@')[0].capitalize()
            novo_usuario = Usuario(nome=nome_padrao, email=email, senha=senha, nivel_acesso=nivel_acesso)
            db.session.add(novo_usuario)
            db.session.commit()
            flash(f'Usuário {email} cadastrado com sucesso!', 'sucesso')
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar usuário: {e}")
        flash("Erro interno ao salvar usuário.", "erro")
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/admin/deletar/<email>')
def admin_deletar(email):
    if session.get('nivel_acesso') != 'admin':
        flash('Acesso negado! Permissão restrita a gerentes.', 'erro')
        return redirect(url_for('vendas.index'))

    if email == session.get('usuario_logado'):
        flash('Você não pode deletar a sua própria conta ativa!', 'erro')
        return redirect(url_for('admin.admin_panel'))

    from app import db, Usuario
    try:
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            flash(f'Usuário {email} removido do sistema.', 'sucesso')
        else:
            flash('Usuário não encontrado.', 'erro')
    except Exception:
        db.session.rollback()
        flash("Erro ao excluir usuário.", "erro")
    return redirect(url_for('admin.admin_panel'))


# --- ROTAS DE PRODUTOS (Acesso permitido para Gerente e Estoquista) ---

@admin_bp.route('/admin/produto/cadastrar', methods=['POST'])
def admin_cadastrar_produto():
    if session.get('nivel_acesso') not in ['admin', 'estoquista']:
        flash('Acesso negado! Nível de privilégios insuficiente.', 'erro')
        return redirect(url_for('vendas.index'))
    
    from app import db, Produto
    try:
        nome = request.form.get('nome')
        preco = request.form.get('preco')
        estoque = request.form.get('estoque')
        
        novo_produto = Produto(nome=nome, preco=float(preco), estoque=int(estoque))
        db.session.add(novo_produto)
        db.session.commit()
        flash(f'Produto {nome} cadastrado com sucesso!', 'sucesso')
    except Exception:
        db.session.rollback()
        flash("Erro ao cadastrar produto.", "erro")
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/admin/produto/remover/<int:id>')
def admin_remover_produto(id):
    if session.get('nivel_acesso') not in ['admin', 'estoquista']:
        flash('Acesso negado! Nível de privilégios insuficiente.', 'erro')
        return redirect(url_for('vendas.index'))
    
    from app import db, Produto
    try:
        produto = Produto.query.get(id)
        if produto:
            db.session.delete(produto)
            db.session.commit()
            flash('Produto removido do catálogo com sucesso!', 'sucesso')
    except Exception:
        db.session.rollback()
        flash("Erro ao remover produto.", "erro")
    return redirect(url_for('admin.admin_panel'))


# --- ROTA DE AUDITORIA: LIMPEZA DE BANCO E EXPURGO EM PDF (Apenas Gerente) ---

@admin_bp.route('/admin/historico/limpar-e-exportar')
def limpar_historico_pdf():
    if session.get('nivel_acesso') != 'admin':
        flash('Acesso negado! Apenas gerentes podem expurgar dados financeiros.', 'erro')
        return redirect(url_for('vendas.index'))

    from app import db, Pedido
    try:
        pedidos = Pedido.query.filter(Pedido.status.in_(['Concluído', 'Cancelado'])).order_by(Pedido.data_hora.desc()).all()
        
        if not pedidos:
            flash('Não existem registros no histórico para exportação.', 'erro')
            return redirect(url_for('admin.admin_panel'))

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elementos = []
        
        styles = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('TituloRelatorio', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor('#E37D22'), spaceAfter=15)
        
        elementos.append(Paragraph("🍢 Espetinho do Edir - Relatório de Fechamento", estilo_titulo))
        elementos.append(Paragraph(f"Backup de Histórico extraído em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", styles['Normal']))
        elementos.append(Spacer(1, 20))
        
        dados_tabela = [['ID Pedido', 'Data / Hora', 'Atendimento', 'Forma Pagto', 'Status', 'Valor Total']]
        for p in pedidos:
            local = f"Mesa {p.numero_mesa}" if p.numero_mesa else "Balcão"
            dados_tabela.append([
                f"#{p.id}",
                p.data_hora.strftime('%d/%m/%Y %H:%M'),
                local,
                p.forma_pagamento,
                p.status,
                f"R$ {p.total:.2f}"
            ])
            
        tabela = Table(dados_tabela, colWidths=[60, 110, 90, 100, 80, 90])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E37D22')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#444444')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')])
        ]))
        elementos.append(tabela)
        doc.build(elementos)
        
        for p in pedidos:
            db.session.delete(p)
        db.session.commit()
        
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=Historico_Espetinho_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        return response

    except Exception as e:
        db.session.rollback()
        print(f"Erro crítico no expurgo do histórico: {e}")
        flash("Erro ao processar a exclusão e geração do backup.", "erro")
        return redirect(url_for('admin.admin_panel'))


# --- ROTA DE AUDITORIA: FECHAMENTO E ZERAGEM DO CAIXA DIÁRIO (Apenas Gerente) ---

@admin_bp.route('/admin/caixa/zerar-e-exportar')
def zerar_caixa_pdf():
    if session.get('nivel_acesso') != 'admin':
        flash('Acesso negado! Apenas gerentes podem fechar o caixa.', 'erro')
        return redirect(url_for('vendas.index'))

    from app import db, Pedido
    try:
        pedidos = Pedido.query.filter_by(status='Concluído').order_by(Pedido.data_hora.asc()).all()
        
        if not pedidos:
            flash('Não há vendas registradas no caixa atual para fechamento.', 'erro')
            return redirect(url_for('admin.admin_panel'))

        total_geral = 0
        resumo_metodos = {'Dinheiro': 0.0, 'Pix': 0.0, 'Cartão de Crédito': 0.0, 'Cartão de Débito': 0.0}
        
        for p in pedidos:
            total_geral += float(p.total)
            if p.forma_pagamento in resumo_metodos:
                resumo_metodos[p.forma_pagamento] += float(p.total)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elementos = []
        
        styles = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('TituloRelatorio', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor('#E37D22'), spaceAfter=15)
        estilo_sub = ParagraphStyle('SubRelatorio', parent=styles['Normal'], fontSize=11, leading=14, spaceAfter=5)
        
        elementos.append(Paragraph("🍢 Espetinho do Edir - Fechamento de Caixa Oficial", estilo_titulo))
        elementos.append(Paragraph(f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", styles['Normal']))
        elementos.append(Spacer(1, 15))
        
        elementos.append(Paragraph("<b>RESUMO DE FATURAMENTO POR MÉTODO:</b>", styles['Normal']))
        for metodo, valor in resumo_metodos.items():
            elementos.append(Paragraph(f"• {metodo}: R$ {valor:.2f}", estilo_sub))
        elementos.append(Paragraph(f"<b>FATURAMENTO TOTAL DO TURNO: R$ {total_geral:.2f}</b>", styles['Normal']))
        elementos.append(Spacer(1, 20))
        
        dados_tabela = [['ID Pedido', 'Horário', 'Atendimento', 'Forma Pagto', 'Valor']]
        for p in pedidos:
            local = f"Mesa {p.numero_mesa}" if p.numero_mesa else "Balcão"
            dados_tabela.append([f"#{p.id}", p.data_hora.strftime('%H:%M'), local, p.forma_pagamento, f"R$ {p.total:.2f}"])
            
        tabela = Table(dados_tabela, colWidths=[80, 100, 110, 130, 110])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2D2D2D')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#E37D22')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#444444')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')])
        ]))
        elementos.append(tabela)
        doc.build(elementos)
        
        for p in pedidos:
            db.session.delete(p)
        db.session.commit()
        
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=Fechamento_Caixa_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        return response

    except Exception as e:
        db.session.rollback()
        print(f"Erro no fechamento do caixa: {e}")
        flash("Erro operacional ao tentar fechar o caixa.", "erro")
        return redirect(url_for('admin.admin_panel'))