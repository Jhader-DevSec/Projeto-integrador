# banco.py

# Dicionário que simula uma tabela de usuários do banco de dados (Chave: E-mail / Valor: Senha)
usuarios_fake = {
    "admin@brasas.com": "senha123",
    "teste@brasas.com": "123456"
}

# Dicionário que simula a tabela de produtos (estoque), pronto para ser exibido na aba de vendas
produtos_fake = {
    1: {
        "nome": "Espetinho de Carne",
        "preco": 9.50,
        "estoque": 45
    },
    2: {
        "nome": "Espetinho de Frango",
        "preco": 8.50,
        "estoque": 30
    },
    3: {
        "nome": "Queijo Coalho",
        "preco": 10.00,
        "estoque": 20
    },
    4: {
        "nome": "Espetinho de Coração",
        "preco": 9.00,
        "estoque": 15
    },
    5: {
        "nome": "Refrigerante Lata",
        "preco": 6.00,
        "estoque": 50
    },
    6: {
        "nome": "Água Mineral",
        "preco": 4.00,
        "estoque": 80
    }
}

# Dicionário qie simula a tabela de pedidos (confirmação de compra)

# Lista que simula a tabela de pedidos (confirmação de compra) na fila da cozinha
pedidos_pendentes_fake = [
    {
        "id": 1,
        "forma_pagamento": "Pix",
        "total": 45.00,
        "status": "Pendente",
        "itens": [
            {"nome": "Espetinho de Carne", "quantidade": 3},
            {"nome": "Queijo Coalho", "quantidade": 2}
        ]
    },
    {
        "id": 2,
        "forma_pagamento": "Cartão",
        "total": 36.00,
        "status": "Pendente",
        "itens": [
            {"nome": "Espetinho de Coração", "quantidade": 4}
        ]
    }
]