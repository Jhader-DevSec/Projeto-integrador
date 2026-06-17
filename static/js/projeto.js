// static/js/projeto.js

document.addEventListener("DOMContentLoaded", () => {

    // =========================================================================
    // 1. SELEÇÃO DE ELEMENTOS GLOBAIS
    // =========================================================================
    const cardsProdutos = document.querySelectorAll('.produto-card');
    const exibidorTotal = document.querySelector('#valor-total');

    // =========================================================================
    // 2. FUNÇÃO MATEMÁTICA (CALCULAR O TOTAL DO PEDIDO)
    // =========================================================================
    function atualizarValorTotal() {
        let somaTotal = 0;
        cardsProdutos.forEach(card => {
            const preco = parseFloat(card.getAttribute('data-preco'));
            const quantidade = parseInt(card.querySelector('.qtd-item').textContent);
            somaTotal += quantidade * preco;
        });
        exibidorTotal.textContent = `R$ ${somaTotal.toFixed(2).replace('.', ',')}`;
    }

    // =========================================================================
    // 3. MAPEAMENTO DOS BOTÕES E TRATAMENTO DE ESTOQUE
    // =========================================================================
    cardsProdutos.forEach(card => {
        const btnMais = card.querySelector('.btn-mais');
        const btnMenos = card.querySelector('.btn-menos');
        const txtQuantidade = card.querySelector('.qtd-item');
        const estoqueMaximo = parseInt(card.getAttribute('data-estoque'));

        btnMais.addEventListener('click', () => {
            let qtdAtual = parseInt(txtQuantidade.textContent);
            if (qtdAtual < estoqueMaximo) {
                qtdAtual++;
                txtQuantidade.textContent = qtdAtual;
                atualizarValorTotal();
            } else {
                alert(`Ação bloqueada! Só restam ${estoqueMaximo} unidades deste item.`);
            }
        });

        btnMenos.addEventListener('click', () => {
            let qtdAtual = parseInt(txtQuantidade.textContent);
            if (qtdAtual > 0) {
                qtdAtual--;
                txtQuantidade.textContent = qtdAtual;
                atualizarValorTotal();
            }
        });
    });

    // =========================================================================
    // 4. PROCESSAMENTO DO PEDIDO
    // =========================================================================
    const btnFecharPedido = document.getElementById("btn-fechar-pedido");
    const selectPagamento = document.getElementById("metodo-pagamento");

    if (btnFecharPedido) {
        btnFecharPedido.addEventListener("click", () => {
            const formaPagamento = selectPagamento.value;
            if (!formaPagamento) {
                alert("Por favor, selecione a Forma de Pagamento!");
                return;
            }

            let itensCarrinho = [];
            cardsProdutos.forEach(card => {
                const idProduto = card.getAttribute("data-id");
                const quantidade = parseInt(card.querySelector(".qtd-item").textContent);
                if (quantidade > 0) {
                    itensCarrinho.push({ id: idProduto, quantidade: quantidade });
                }
            });

            if (itensCarrinho.length === 0) {
                alert("Seu pedido está vazio!");
                return;
            }

            fetch('/pedidos/criar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ forma_pagamento: formaPagamento, itens: itensCarrinho })
            })
            .then(res => res.json())
            .then(data => {
                if (data.sucesso) {
                    alert(`Pedido #${data.pedido_id} enviado para a cozinha!`);
                    window.location.reload();
                } else {
                    alert(`Erro: ${data.erro}`);
                }
            });
        });
    }

    // =========================================================================
    // 5. CONTROLE DINÂMICO DOS BOTÕES DA COZINHA
    // =========================================================================
    function atualizarStatusPedidoNoBanco(id, statusAlvo, elementoCardDOM) {
        fetch(`/pedidos/${id}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: statusAlvo })
        })
        .then(res => res.json())
        .then(data => {
            if (data.sucesso) {
                elementoCardDOM.style.transition = "all 0.4s ease";
                elementoCardDOM.style.opacity = "0";
                setTimeout(() => {
                    elementoCardDOM.remove();
                    window.location.reload(); // Recarrega para atualizar a aba histórico automaticamente
                }, 400);
            } else {
                alert(`Erro: ${data.erro}`);
            }
        });
    }

    document.querySelectorAll(".btn_confirmar").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const card = e.target.closest(".validacao_pedidos");
            atualizarStatusPedidoNoBanco(card.dataset.id, "Concluído", card);
        });
    });

    document.querySelectorAll(".btn_cancelar").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const card = e.target.closest(".validacao_pedidos");
            atualizarStatusPedidoNoBanco(card.dataset.id, "Cancelado", card);
        });
    });

    // =========================================================================
    // 6. HISTÓRICO: ABRIR MODAL COM DETALHES
    // =========================================================================
    window.verDetalhes = function(id) {
        fetch(`/pedidos/${id}/detalhes`)
        .then(res => res.json())
        .then(itens => {
            const lista = document.getElementById('modal-itens');
            lista.innerHTML = '';
            itens.forEach(item => {
                lista.innerHTML += `<li>${item.qtd} x ${item.nome}</li>`;
            });
            document.getElementById('modal-id').textContent = id;
            document.getElementById('modal-historico').style.display = 'flex';
        });
    };
});

// Monitora clique no link "Caixa"
document.querySelector('a[href="#caixa"]').addEventListener('click', () => {
    fetch('/caixa/resumo')
    .then(res => res.json())
    .then(data => {
        document.getElementById('total-geral').textContent = `R$ ${data.total_geral.toFixed(2).replace('.', ',')}`;
        
        let htmlPagamentos = '<h4>Por Pagamento:</h4><ul>';
        for (const [meio, qtd] of Object.entries(data.pagamentos)) {
            htmlPagamentos += `<li>${meio}: ${qtd} vendas</li>`;
        }
        htmlPagamentos += '</ul>';
        document.getElementById('detalhes-pagamento').innerHTML = htmlPagamentos;
    });
});