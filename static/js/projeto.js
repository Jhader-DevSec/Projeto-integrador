// =========================================================================
// HISTÓRICO: ABRIR MODAL COM DETALHES (Escopo Global)
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

// =========================================================================
// FUNÇÕES GLOBAIS DE FILTRAGEM E EXPURGO GERENCIAL
// =========================================================================
window.filtrarHistoricoTela = function() {
    const termoBusca = document.getElementById("busca-historico-id").value.toLowerCase();
    const filtroPagamento = document.getElementById("busca-historico-pagamento").value;
    const blocosDias = document.querySelectorAll(".bloco-dia");

    blocosDias.forEach(bloco => {
        const linhas = bloco.querySelectorAll(".linha-pedido-historico");
        let linhasVisiveisNoDia = 0;

        linhas.forEach(linha => {
            const id = Apparentemente = linha.getAttribute("data-id").toLowerCase();
            const mesa = linha.getAttribute("data-mesa").toLowerCase();
            const pagamento = linha.getAttribute("data-pagamento");

            const bateIdOuMesa = id.includes(termoBusca) || mesa.includes(termoBusca);
            const batePagamento = !filtroPagamento || pagamento === filtroPagamento;

            if (bateIdOuMesa && batePagamento) {
                linha.style.display = "";
                linhasVisiveisNoDia++;
            } else {
                linha.style.display = "none";
            }
        });

        if (linhasVisiveisNoDia === 0) {
            bloco.style.display = "none";
        } else {
            bloco.style.display = "";
        }
    });
};

window.limparHistoricoGeral = function() {
    const confirmacao = confirm("⚠️ ATENÇÃO!\n\nEsta ação irá apagar permanentemente todos os pedidos concluídos e cancelados do banco de dados.\n\nUm relatório consolidado em PDF será gerado e baixado automaticamente no seu PC como backup.\n\nDeseja prosseguir?");
    if (confirmacao) {
        window.location.href = '/admin/historico/limpar-e-exportar';
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    }
};

window.realizarFechamentoCaixa = function() {
    const confirmacao = confirm("🔒 ATENÇÃO: FECHAMENTO DE CAIXA\n\nEsta ação irá encerrar o turno atual, zerar o saldo de todos os métodos de pagamento e limpar as estatísticas do painel.\n\nUm relatório oficial consolidado em PDF será gerado e baixado automaticamente no computador.\n\nDeseja confirmar o fechamento?");
    if (confirmacao) {
        window.location.href = '/admin/caixa/zerar-e-exportar';
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    }
};

// =========================================================================
// INICIALIZAÇÃO DO ECOSSISTEMA OPERACIONAL (DOM)
// =========================================================================
document.addEventListener("DOMContentLoaded", () => {

    // 1. SELEÇÃO DE ELEMENTOS GLOBAIS
    const cardsProdutos = document.querySelectorAll('.produto-card');
    const exibidorTotal = document.querySelector('#valor-total');
    const btnFecharPedido = document.getElementById("btn-fechar-pedido");
    const selectPagamento = document.getElementById("metodo-pagamento");
    const inputMesa = document.getElementById("numero-mesa");
    const linksNavegacao = document.querySelectorAll("nav a");

    // 2. FUNÇÃO MATEMÁTICA (CALCULAR O TOTAL DO PEDIDO)
    function atualizarValorTotal() {
        let somaTotal = 0;
        cardsProdutos.forEach(card => {
            const preco = parseFloat(card.getAttribute('data-preco'));
            const quantidade = parseInt(card.querySelector('.qtd-item').textContent);
            somaTotal += quantidade * preco;
        });
        exibidorTotal.textContent = `R$ ${somaTotal.toFixed(2).replace('.', ',')}`;
    }

    // 3. MAPEAMENTO DOS BOTÕES E TRATAMENTO DE ESTOQUE
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
                alert(`Ação bloqueada! Só restam ${estoqueMaximo} unidades deste item no estoque físico.`);
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

    // 4. PROCESSAMENTO E ENVIO DO PEDIDO (PDV)
    if (btnFecharPedido) {
        btnFecharPedido.addEventListener("click", () => {
            const formaPagamento = selectPagamento.value;
            const numeroMesa = inputMesa ? inputMesa.value : '';

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
                alert("Seu carrinho de compras está vazio!");
                return;
            }

            fetch('/pedidos/criar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    forma_pagamento: formaPagamento, 
                    itens: itensCarrinho,
                    numero_mesa: numeroMesa
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.sucesso) {
                    alert(`Pedido #${data.pedido_id} enviado com sucesso para a esteira da cozinha!`);
                    window.location.reload();
                } else {
                    alert(`Erro operacional: ${data.erro}`);
                }
            });
        });
    }

    // 5. CONTROLE DINÂMICO DOS BOTÕES DAS ESTEIRAS (COZINHA E ANDAMENTO)
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
                    window.location.reload(); 
                }, 400);
            } else {
                alert(`Erro ao processar transição de estado: ${data.erro}`);
            }
        });
    }

    // Gatilho 1: Cozinheiro avança o pedido para a esteira de entrega
    document.querySelectorAll(".btn_pronto_retirada").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const card = e.target.closest(".validacao_pedidos");
            atualizarStatusPedidoNoBanco(card.dataset.id, "Pronto para retirada", card);
        });
    });

    // Gatilho 2: Entregador/Garçom finaliza e encerra o ciclo de vida do pedido
    document.querySelectorAll(".btn_concluir_entrega").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const card = e.target.closest(".validacao_pedidos");
            atualizarStatusPedidoNoBanco(card.dataset.id, "Concluído", card);
        });
    });

    // Gatilho 3: Cancelamento de pedido em aberto
    document.querySelectorAll(".btn_cancelar").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const card = e.target.closest(".validacao_pedidos");
            atualizarStatusPedidoNoBanco(card.dataset.id, "Cancelado", card);
        });
    });

    // 6. DASHBOARD FINANCEIRO ASYNC: MONITORAMENTO DA ABA CAIXA
    function carregarDadosResumoCaixa() {
        fetch('/caixa/resumo')
        .then(res => res.json())
        .then(data => {
            if (data.erro) {
                console.error(data.erro);
                return;
            }
            
            const txtTotalGeral = document.getElementById('caixa-total-geral');
            if (txtTotalGeral) {
                txtTotalGeral.textContent = `R$ ${data.total_geral.toFixed(2).replace('.', ',')}`;
            }
            
            const containerMetodos = document.getElementById("caixa-pagamentos-detalhes");
            if (containerMetodos) {
                containerMetodos.innerHTML = ""; 
                
                const metodosSuportados = [
                    { chave: "Dinheiro", label: "💵 Dinheiro" },
                    { chave: "Pix", label: "⚡ Pix" },
                    { chave: "Cartão de Crédito", label: "💳 Cartão de Crédito" },
                    { chave: "Cartão de Débito", label: "💳 Cartão de Débito" }
                ];
                
                metodosSuportados.forEach(metodo => {
                    const valorFaturado = data.pagamentos[metodo.chave] || 0.0;
                    containerMetodos.innerHTML += `
                        <div class="card-metodo-faturamento">
                            <span>${metodo.label}</span>
                            <strong>R$ ${valorFaturado.toFixed(2).replace('.', ',')}</strong>
                        </div>
                    `;
                });
            }
        });
    }

    const linkCaixa = document.querySelector('a[href="#caixa"]');
    if (linkCaixa) {
        linkCaixa.addEventListener('click', carregarDadosResumoCaixa);
    }

    // =========================================================================
    // 7. GERENCIAMENTO DE ABAS ATIVAS E MOVIMENTAÇÃO DO TRILHO (5 SEÇÕES)
    // =========================================================================
    function gerenciarIndicadorAba() {
        const hashAtual = window.location.hash || "#vendas";
        
        // Mapeia rigidamente a ordem física das abas para calcular o deslizamento
        const abasOrdem = ["#vendas", "#cozinha", "#andamento", "#historico", "#caixa"];
        const index = abasOrdem.indexOf(hashAtual);
        
        // Desliza a tela principal fisicamente no eixo X
        const rail = document.querySelector(".rail");
        if (rail && index !== -1) {
            rail.style.transform = `translateX(-${index * 100}vw)`;
        }

        // Altera as tags ativas para laranja
        linksNavegacao.forEach(link => {
            if (link.getAttribute("href") === hashAtual) {
                link.classList.add("active");
            } else {
                link.classList.remove("active");
            }
        });
    }

    linksNavegacao.forEach(link => {
        link.addEventListener("click", () => {
            setTimeout(gerenciarIndicadorAba, 50);
        });
    });

    gerenciarIndicadorAba();
    window.addEventListener("hashchange", gerenciarIndicadorAba);
    
    const modalHistorico = document.getElementById('modal-historico');
    if (modalHistorico) {
        modalHistorico.addEventListener('click', (e) => {
            if (e.target === modalHistorico) modalHistorico.style.display = 'none';
        });
    }
});