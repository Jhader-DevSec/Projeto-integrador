# routes/vendas.py
from flask import Blueprint, render_template, redirect, url_for, session, flash
from banco import pedidos_pendentes_fake  # Mantido temporariamente para a fila da cozinha

# Inicializa o Blueprint operacional das vendas
vendas_bp = Blueprint('vendas', __name__)

# Rota da página principal (Painel do Espetinho do Edir)
@vendas_bp.route('/')
def index():
    # 1. BARREIRA DE SEGURANÇA: Impede que qualquer pessoa acesse o sistema digitando a URL direta
    if 'usuario_logado' not in session:
        flash('Por favor, faça o login para acessar o sistema.', 'erro')
        return redirect(url_for('auth.login_page'))
    
    # 💡 QUEBRA DE IMPORTAÇÃO CIRCULAR: Importamos o modelo aqui dentro da função.
    # Isso garante que o 'db' e o 'app' já foram criados antes do Python tentar ler esta linha.
    from app import Produto 
    
    try:
        # 2. BUSCA NO BANCO DE DADOS REAL: Puxa todos os produtos cadastrados na Clever Cloud
        produtos_do_banco = Produto.query.all()
        
        # 3. MAPEAMENTO DO DICIONÁRIO: Converte os objetos do banco no formato exato que seu 'projeto.html' espera
        produtos_reais = {}
        for p in produtos_do_banco:
            produtos_reais[p.id] = {
                "nome": p.nome,
                "preco": float(p.preco),  # Converte Decimal do MySQL para Float do Python
                "estoque": p.estoque,
                "categoria": p.categoria
            }
            
        # Se o banco responder com sucesso, renderiza o painel com os dados reais da nuvem
        return render_template('projeto.html', produtos=produtos_reais, pedidos_pendentes_fake=pedidos_pendentes_fake)
        
    except Exception as e:
        # Caso ocorra algum erro de conexão com a nuvem, avisa no terminal para podermos debugar
        print(f"Erro crítico ao conectar à Clever Cloud: {e}")
        return "Erro de conexão com o banco de dados. Verifique o terminal do VS Code.", 500