# routes/vendas.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from datetime import datetime
from sqlalchemy import func

vendas_bp = Blueprint('vendas', __name__)

@vendas_bp.route('/')
def index():
    if 'usuario_logado' not in session:
        return redirect(url_for('auth.login_page'))
    
    from app import Produto, Pedido
    
    # 1. Busca produtos
    produtos_do_banco = Produto.query.all()
    produtos_reais = {p.id: {"nome": p.nome, "preco": float(p.preco), "estoque": p.estoque} for p in produtos_do_banco}
    
    # 2. Busca Pendentes (Cozinha)
    pedidos_banco = Pedido.query.filter_by(status='Pendente').all()
    pedidos_cozinha = [{"id": ped.id, "forma_pagamento": ped.forma_pagamento, "total": float(ped.total), "itens": [{"quantidade": i.quantidade, "nome": i.produto.nome} for i in ped.itens]} for ped in pedidos_banco]
    
    # 3. Busca Histórico (Concluídos)
    pedidos_concluidos = Pedido.query.filter_by(status='Concluído').order_by(Pedido.data_hora.desc()).all()
    lista_historico = [{"id": ped.id, "total": float(ped.total), "data": ped.data_hora.strftime('%d/%m/%Y %H:%M'), "pagamento": ped.forma_pagamento} for ped in pedidos_concluidos]
            
    return render_template(
        'projeto.html', 
        produtos=produtos_reais, 
        pedidos_pendentes_fake=pedidos_cozinha,
        pedidos_historico=lista_historico  # <--- Isso é o que faz a tabela preencher!
    )
        
# --- ROTAS DE AÇÃO (CRIAÇÃO E STATUS) ---

@vendas_bp.route('/pedidos/criar', methods=['POST'])
def criar_pedido():
    if 'usuario_logado' not in session: return jsonify({"erro": "Não autorizado"}), 401
    from app import db, Pedido, ItensPedido, Produto
    data = request.get_json()
    try:
        total_calculado = 0
        novo_pedido = Pedido(data_hora=datetime.now(), total=0, status='Pendente', forma_pagamento=data.get('forma_pagamento'))
        db.session.add(novo_pedido)
        db.session.flush()

        for item in data.get('itens'):
            produto = Produto.query.get(int(item['id']))
            if not produto or produto.estoque < int(item['quantidade']):
                db.session.rollback()
                return jsonify({"erro": "Estoque insuficiente"}), 400
            produto.estoque -= int(item['quantidade'])
            total_calculado += (float(produto.preco) * int(item['quantidade']))
            db.session.add(ItensPedido(pedido_id=novo_pedido.id, produto_id=produto.id, quantidade=item['quantidade'], preco_unitario=produto.preco))

        novo_pedido.total = total_calculado
        db.session.commit()
        return jsonify({"sucesso": True, "pedido_id": novo_pedido.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500

@vendas_bp.route('/pedidos/<int:pedido_id>/status', methods=['POST'])
def atualizar_status(pedido_id):
    from app import db, Pedido
    data = request.get_json()
    pedido = Pedido.query.get(pedido_id)
    if not pedido: return jsonify({"erro": "Não encontrado"}), 404
    
    if data.get('status') == 'Cancelado':
        for item in pedido.itens: item.produto.estoque += item.quantidade
    
    pedido.status = data.get('status')
    db.session.commit()
    return jsonify({"sucesso": True})

@vendas_bp.route('/pedidos/<int:pedido_id>/detalhes')
def detalhes_pedido(pedido_id):
    from app import Pedido
    pedido = Pedido.query.get_or_404(pedido_id)
    return jsonify([{"nome": i.produto.nome, "qtd": i.quantidade} for i in pedido.itens])

@vendas_bp.route('/caixa/resumo')
def caixa_resumo():
    from app import Pedido, db
    total = db.session.query(func.sum(Pedido.total)).filter_by(status='Concluído').scalar() or 0
    pagamentos = db.session.query(Pedido.forma_pagamento, func.count(Pedido.id)).filter_by(status='Concluído').group_by(Pedido.forma_pagamento).all()
    return jsonify({"total_geral": float(total), "pagamentos": dict(pagamentos)})