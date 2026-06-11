# routes/vendas.py
from flask import Blueprint, render_template, redirect, url_for, session, flash

vendas_bp = Blueprint('vendas', __name__)

@vendas_bp.route('/')
def index():
    # Proteção de Rota
    if 'usuario_logado' not in session:
        flash('Por favor, faça o login para acessar o sistema.', 'erro')
        return redirect(url_for('auth.login_page'))
    
    # Importação interna estratégica para neutralizar a Importação Circular
    from app import Produto, Pedido
    
    try:
        # 1. ATUALIZAÇÃO DO CARDÁPIO DE VENDAS
        produtos_do_banco = Produto.query.all()
        produtos_reais = {}
        for p in produtos_do_banco:
            produtos_reais[p.id] = {
                "nome": p.nome,
                "preco": float(p.preco),
                "estoque": p.estoque,
                "categoria": p.categoria
            }
        
        # 2. ATUALIZAÇÃO DA FILA DA COZINHA
        pedidos_banco = Pedido.query.filter(Pedido.status.in_(['Pendente', 'Em Preparo'])).all()
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
            
        # Retorna o painel integrado alimentado 100% com dados reais
        return render_template('projeto.html', produtos=produtos_reais, pedidos_pendentes_fake=pedidos_reais_cozinha)
        
    except Exception as e:
        print(f"Erro crítico de sincronização com a Clever Cloud: {e}")
        return "Erro de sincronização com o banco de dados remoto.", 500