# routes/vendas.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from datetime import datetime
from sqlalchemy import func
from collections import defaultdict

vendas_bp = Blueprint('vendas', __name__)

@vendas_bp.route('/')
def index():
    if 'usuario_logado' not in session:
        return redirect(url_for('auth.login_page'))
    
    from app import Produto, Pedido
    
    try:
        # 1. BUSCA PRODUTOS (CARDÁPIO REATIVO)
        produtos_do_banco = Produto.query.all()
        produtos_reais = {p.id: {"nome": p.nome, "preco": float(p.preco), "estoque": p.estoque} for p in produtos_do_banco}
        
        # 2. BUSCA PEDIDOS PENDENTES (ESTEIRA DA COZINHA)
        pedidos_banco = Pedido.query.filter_by(status='Pendente').all()
        pedidos_cozinha = []
        for ped in pedidos_banco:
            pedidos_cozinha.append({
                "id": ped.id,
                "forma_pagamento": ped.forma_pagamento,
                "total": float(ped.total),
                "numero_mesa": ped.numero_mesa,  # Repassa o número da mesa para a cozinha
                "itens": [{"quantidade": i.quantidade, "nome": i.produto.nome} for i in ped.itens]
            })
        
        # 3. BUSCA HISTÓRICO (AGRUPADO POR DIA)
        # Traz tanto concluídos quanto cancelados ordenados dos mais recentes para os mais antigos
        pedidos_historico_banco = Pedido.query.filter(Pedido.status.in_(['Concluído', 'Cancelado'])).order_by(Pedido.data_hora.desc()).all()
        
        historico_por_dia = defaultdict(list)
        for ped in pedidos_historico_banco:
            # Cria a chave do grupo por data (DD/MM/AAAA)
            dia = ped.data_hora.strftime('%d/%m/%Y')
            historico_por_dia[dia].append({
                "id": ped.id,
                "total": float(ped.total),
                "data_hora": ped.data_hora.strftime('%H:%M'),  # Exibe apenas o horário dentro do grupo
                "pagamento": ped.forma_pagamento,
                "numero_mesa": ped.numero_mesa,
                "status": ped.status
            })
        
        # Ordena os blocos de dias de forma decrescente para o Jinja2
        lista_historico_agrupada = sorted(
            historico_por_dia.items(), 
            key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'), 
            reverse=True
        )
            
        return render_template(
            'projeto.html', 
            produtos=produtos_reais, 
            pedidos_pendentes_fake=pedidos_cozinha,
            pedidos_historico=lista_historico_agrupada
        )
        
    except Exception as e:
        print(f"Erro ao carregar painel operacional: {e}")
        return "Erro de sincronização com o ecossistema do banco de dados.", 500


# --- ROTAS DE AÇÃO (CRIAÇÃO E STATUS) ---

@vendas_bp.route('/pedidos/criar', methods=['POST'])
def criar_pedido():
    if 'usuario_logado' not in session: 
        return jsonify({"erro": "Não autorizado"}), 401
        
    from app import db, Pedido, ItensPedido, Produto
    data = request.get_json()
    
    try:
        total_calculado = 0
        forma_pagamento = data.get('forma_pagamento')
        itens_carrinho = data.get('itens')
        numero_mesa = data.get('numero_mesa')

        if not forma_pagamento or not itens_carrinho:
            return jsonify({"erro": "Preencha a forma de pagamento e adicione itens."}), 400

        # Sanitização do input da mesa: se vazio ou nulo, armazena como None (Balcão)
        mesa_final = int(numero_mesa) if numero_mesa else None

        # Instancia o pedido guardando a mesa tratada
        novo_pedido = Pedido(
            data_hora=datetime.now(), 
            total=0, 
            status='Pendente', 
            forma_pagamento=forma_pagamento,
            numero_mesa=mesa_final
        )
        db.session.add(novo_pedido)
        db.session.flush()

        for item in itens_carrinho:
            produto = Produto.query.get(int(item['id']))
            if not produto or produto.estoque < int(item['quantidade']):
                db.session.rollback()
                return jsonify({"erro": f"Estoque insuficiente para o produto: {produto.nome if produto else 'Item'}"}), 400
                
            produto.estoque -= int(item['quantidade'])
            total_calculado += (float(produto.preco) * int(item['quantidade']))
            
            db.session.add(ItensPedido(
                pedido_id=novo_pedido.id, 
                produto_id=produto.id, 
                quantidade=item['quantidade'], 
                preco_unitario=produto.preco
            ))

        novo_pedido.total = total_calculado
        db.session.commit()
        return jsonify({"sucesso": True, "pedido_id": novo_pedido.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500


@vendas_bp.route('/pedidos/<int:pedido_id>/status', methods=['POST'])
def atualizar_status(pedido_id):
    if 'usuario_logado' not in session: 
        return jsonify({"erro": "Não autorizado"}), 401
        
    from app import db, Pedido
    data = request.get_json()
    
    pedido = Pedido.query.get(pedido_id)
    if not pedido: 
        return jsonify({"erro": "Pedido não encontrado"}), 404
    
    # Se for um cancelamento operacional, devolve a quantidade exata ao estoque
    if data.get('status') == 'Cancelado' and pedido.status != 'Cancelado':
        for item in pedido.itens: 
            item.produto.estoque += item.quantidade
    
    pedido.status = data.get('status')
    db.session.commit()
    return jsonify({"sucesso": True})


@vendas_bp.route('/pedidos/<int:pedido_id>/detalhes')
def detalhes_pedido(pedido_id):
    if 'usuario_logado' not in session: 
        return jsonify({"erro": "Não autorizado"}), 401
        
    from app import Pedido
    pedido = Pedido.query.get_or_404(pedido_id)
    return jsonify([{"nome": i.produto.nome, "qtd": i.quantidade} for i in pedido.itens])


@vendas_bp.route('/caixa/resumo')
def caixa_resumo():
    # BARREIRA DE SEGURANÇA RBAC: Apenas o Gerente (admin) pode auditar o faturamento
    if session.get('nivel_acesso') != 'admin':
        return jsonify({"erro": "Acesso não autorizado. Área restrita a gerentes."}), 403
        
    from app import Pedido, db
    try:
        total = db.session.query(func.sum(Pedido.total)).filter_by(status='Concluído').scalar() or 0
        pagamentos = db.session.query(
            Pedido.forma_pagamento, 
            func.count(Pedido.id)
        ).filter_by(status='Concluído').group_by(Pedido.forma_pagamento).all()
        
        return jsonify({"total_geral": float(total), "pagamentos": dict(pagamentos)})
    except Exception as e:
        return jsonify({"erro": f"Erro interno de processamento: {str(e)}"}), 500