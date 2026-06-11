# routes/vendas.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from datetime import datetime

vendas_bp = Blueprint('vendas', __name__)

@vendas_bp.route('/')
def index():
    # Barreira de segurança: impede acesso sem login
    if 'usuario_logado' not in session:
        flash('Por favor, faça o login para acessar o sistema.', 'erro')
        return redirect(url_for('auth.login_page'))
    
    # Importação interna para evitar o erro de importação circular
    from app import Produto, Pedido
    
    try:
        # 1. BUSCA PRODUTOS NO BANCO (CARDÁPIO)
        produtos_do_banco = Produto.query.all()
        produtos_reais = {}
        for p in produtos_do_banco:
            produtos_reais[p.id] = {
                "nome": p.nome,
                "preco": float(p.preco),
                "estoque": p.estoque,
                "categoria": p.categoria
            }
        
        # 2. BUSCA PEDIDOS NA ESTEIRA DA COZINHA (Apenas com status 'Pendente')
        pedidos_banco = Pedido.query.filter_by(status='Pendente').all()
        pedidos_reais_cozinha = []
        for ped in pedidos_banco:
            itens_do_pedido = []
            for item in ped.itens:
                itens_do_pedido.append({
                    "quantidade": item.quantidade,
                    "nome": item.produto.nome
                })
                
            pedidos_reais_cozinha.append({
                "id": ped.id,
                "forma_pagamento": ped.forma_pagamento,
                "total": float(ped.total),
                "itens": itens_do_pedido
            })
            
        return render_template('projeto.html', produtos=produtos_reais, pedidos_pendentes_fake=pedidos_reais_cozinha)
        
    except Exception as e:
        print(f"Erro ao carregar dados do banco: {e}")
        return "Erro de sincronização com o banco de dados remoto.", 500


# 🔥 ROTA QUE SALVA O PEDIDO E ATUALIZA O ESTOQUE NO BANCO DE DADOS
@vendas_bp.route('/pedidos/criar', methods=['POST'])
def criar_pedido():
    if 'usuario_logado' not in session:
        return jsonify({"erro": "Não autorizado"}), 401

    from app import db, Pedido, ItensPedido, Produto
    
    data = request.get_json()
    forma_pagamento = data.get('forma_pagamento')
    itens_carrinho = data.get('itens')

    if not forma_pagamento or not itens_carrinho:
        return jsonify({"erro": "Preencha a forma de pagamento e adicione itens."}), 400

    try:
        total_calculado = 0
        
        # Cria o registro principal do pedido
        novo_pedido = Pedido(
            data_hora=datetime.now(),
            total=0,
            status='Pendente',
            forma_pagamento=forma_pagamento
        )
        db.session.add(novo_pedido)
        db.session.flush()  # Gera o ID do pedido temporariamente para vincular os itens

        # Processa cada item do carrinho vindo do JavaScript
        for item in itens_carrinho:
            prod_id = int(item['id'])
            qtd = int(item['quantidade'])
            
            produto = Produto.query.get(prod_id)
            if not produto or produto.estoque < qtd:
                db.session.rollback()
                return jsonify({"erro": f"Estoque insuficiente para o item: {produto.nome if produto else prod_id}"}), 400
            
            # Dá baixa no estoque real da nuvem
            produto.estoque -= qtd
            preco_fixado = float(produto.preco)
            total_calculado += (preco_fixado * qtd)

            # Salva o item individual do pedido
            vinculo_item = ItensPedido(
                pedido_id=novo_pedido.id,
                produto_id=prod_id,
                quantidade=qtd,
                preco_unitario=preco_fixado
            )
            db.session.add(vinculo_item)

        novo_pedido.total = total_calculado
        db.session.commit()
        return jsonify({"sucesso": True, "pedido_id": novo_pedido.id})

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar pedido na nuvem: {e}")
        return jsonify({"erro": "Erro interno ao salvar pedido."}), 500


# 🍳 ROTA QUE A COZINHA USA VIA JAVASCRIPT PARA ALTERAR STATUS (CONCLUIR OU CANCELAR)
@vendas_bp.route('/pedidos/<int:pedido_id>/status', methods=['POST'])
def atualizar_status(pedido_id):
    if 'usuario_logado' not in session:
        return jsonify({"erro": "Não autorizado"}), 401

    from app import db, Pedido
    data = request.get_json()
    novo_status = data.get('status')

    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({"erro": "Pedido não encontrado."}), 404

        # Se for um cancelamento, devolve os itens comprados de volta para o estoque
        if novo_status == 'Cancelado' and pedido.status != 'Cancelado':
            for item in pedido.itens:
                item.produto.estoque += item.quantidade

        pedido.status = novo_status
        db.session.commit()
        return jsonify({"sucesso": True})

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao alterar status do pedido {pedido_id}: {e}")
        return jsonify({"erro": "Erro ao atualizar status."}), 500