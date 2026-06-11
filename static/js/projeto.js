// static/js/projeto.js

document.addEventListener("DOMContentLoaded", () => {

    // =========================================================================
    // 1. SELEÇÃO DE ELEMENTOS GLOBAIS
    // =========================================================================

    // Captura todos os cards de produtos que o Jinja renderizou na tela
    const cardsProdutos = document.querySelectorAll('.produto-card');

    // Captura o elemento do rodapé onde o valor total acumulado será exibido
    const exibidorTotal = document.querySelector('#valor-total');


    // =========================================================================
    // 2. FUNÇÃO MATEMÁTICA (CALCULAR O TOTAL DO PEDIDO)
    // =========================================================================

    // Esta função varre a tela inteira, lê o estado atual de cada card e calcula a soma
    function atualizarValorTotal() {
        let somaTotal = 0;

        // Passa olhando card por card de maneira independente
        cardsProdutos.forEach(card => {
            // Puxa o preço que deixamos guardado no atributo 'data-preco' (converte o texto para número decimal)
            const preco = parseFloat(card.getAttribute('data-preco'));
            
            // Puxa a quantidade que o funcionário selecionou na tela (converte o texto para número inteiro)
            const quantidade = parseInt(card.querySelector('.qtd-item').textContent);

            // Multiplica a quantidade selecionada pelo preço do espetinho e acumula no total
            somaTotal += quantidade * preco;
        });

        // Injeta o valor somado de volta no rodapé, formatando com duas casas decimais e trocando o ponto por vírgula
        exibidorTotal.textContent = `R$ ${somaTotal.toFixed(2).replace('.', ',')}`;
    }


    // =========================================================================
    // 3. MAPEAMENTO DOS BOTÕES E TRATAMENTO DE ESTOQUE
    // =========================================================================

    // Para cada espetinho individual na tela, precisamos ativar seus respectivos botões
    cardsProdutos.forEach(card => {
        const btnMais = card.querySelector('.btn-mais');
        const btnMenos = card.querySelector('.btn-menos');
        const txtQuantidade = card.querySelector('.qtd-item');
        
        // Puxa o teto máximo de estoque que deixamos guardado no atributo 'data-estoque'
        const estoqueMaximo = parseInt(card.getAttribute('data-estoque'));

        // Ouvinte de Evento para o botão de MAIS (+)
        btnMais.addEventListener('click', () => {
            let qtdAtual = parseInt(txtQuantidade.textContent);

            // BARREIRA DE SEGURANÇA: Só deixa subir a quantidade se ela for menor que o estoque real no banco
            if (qtdAtual < estoqueMaximo) {
                qtdAtual++;
                txtQuantidade.textContent = qtdAtual; // Atualiza o número exibido no card
                atualizarValorTotal();                // Dispara o recálculo do rodapé imediatamente
            } else {
                // Alerta visual caso o funcionário tente vender mais do que o espetinho físico disponível
                alert(`Ação bloqueada! Só restam ${estoqueMaximo} unidades deste item no estoque.`);
            }
        });

        // Ouvinte de Evento para o botão de MENOS (-)
        btnMenos.addEventListener('click', () => {
            let qtdAtual = parseInt(txtQuantidade.textContent);

            // BARREIRA DE SEGURANÇA: Impede que a quantidade fique negativa (-1, -2 espetinhos...)
            if (qtdAtual > 0) {
                qtdAtual--;
                txtQuantidade.textContent = qtdAtual; // Atualiza o número exibido no card
                atualizarValorTotal();                // Dispara o recálculo do rodapé imediatamente
            }
        });
    });


    // =========================================================================
    // 4. PROCESSAMENTO DO PEDIDO (FECHAR PEDIDO VIA REQUISIÇÃO API)
    // =========================================================================

    const btnFecharPedido = document.getElementById("btn-fechar-pedido");
    const selectPagamento = document.getElementById("metodo-pagamento");

    if (btnFecharPedido) {
        btnFecharPedido.addEventListener("click", () => {
            const formaPagamento = selectPagamento.value;
            
            // Validação 1: Exige que a forma de pagamento tenha sido selecionada no HTML
            if (!formaPagamento) {
                alert("Por favor, selecione a Forma de Pagamento antes de fechar o pedido!");
                return;
            }

            // Captura dinamicamente apenas os produtos que possuem quantidade maior que zero
            let itensCarrinho = [];
            cardsProdutos.forEach(card => {
                const idProduto = card.getAttribute("data-id");
                const quantidade = parseInt(card.querySelector(".qtd-item").textContent);
                if (quantidade > 0) {
                    itensCarrinho.push({ id: idProduto, quantidade: quantidade });
                }
            });

            // Validação 2: Impede o envio de pedidos totalmente vazios
            if (itensCarrinho.length === 0) {
                alert("Seu pedido está vazio! Adicione pelo menos 1 item para fechar.");
                return;
            }

            // Dispara os dados via JSON para a API do Flask que criamos nas rotas
            fetch('/pedidos/criar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    forma_pagamento: formaPagamento,
                    itens: itensCarrinho
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.sucesso) {
                    alert(`Pedido #${data.pedido_id} enviado para a cozinha com sucesso!`);
                    window.location.reload(); // Recarrega a tela para zerar os contadores e atualizar os estoques visuais
                } else {
                    alert(`Erro ao salvar: ${data.erro}`);
                }
            })
            .catch(err => console.error("Erro na comunicação de fechamento:", err));
        });
    }


    // =========================================================================
    // 5. CONTROLE DINÂMICO DOS BOTÕES DA COZINHA
    // =========================================================================

    // Mapeia todos os pedidos pendentes que estão na esteira da cozinha
    const cardsPedidosCozinha = document.querySelectorAll(".validacao_pedidos");

    cardsPedidosCozinha.forEach(card => {
        const idPedido = card.getAttribute("data-id");
        const btnConfirmar = card.querySelector(".btn_confirmar");
        const btnCancelar = card.querySelector(".btn_cancelar");

        // Clique em Confirmar (Pedido Concluído ➔ Some da cozinha)
        btnConfirmar.addEventListener("click", () => {
            if (confirm(`Deseja confirmar e marcar como CONCLUÍDO o Pedido #${idPedido}?`)) {
                atualizarStatusPedidoNoBanco(idPedido, "Concluído", card);
            }
        });

        // Clique em Cancelar (Pedido Cancelado ➔ Estorna estoque no banco ➔ Some da cozinha)
        btnCancelar.addEventListener("click", () => {
            if (confirm(`Atenção: Deseja mesmo CANCELAR o Pedido #${idPedido}? Isto devolverá os produtos ao estoque.`)) {
                atualizarStatusPedidoNoBanco(idPedido, "Cancelado", card);
            }
        });
    });

    // Função auxiliar que faz o fetch de status para a rota do Flask
    function atualizarStatusPedidoNoBanco(id, statusAlvo, elementoCardDOM) {
        fetch(`/pedidos/${id}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: statusAlvo })
        })
        .then(res => res.json())
        .then(data => {
            if (data.sucesso) {
                // Efeito de transição suave CSS para sumir com o card da tela sem precisar dar reload
                elementoCardDOM.style.transition = "all 0.4s ease";
                elementoCardDOM.style.opacity = "0";
                elementoCardDOM.style.transform = "scale(0.8) translateY(-20px)";
                setTimeout(() => elementoCardDOM.remove(), 400);
            } else {
                alert(`Erro técnico na atualização: ${data.erro}`);
            }
        })
        .catch(err => console.error("Erro ao enviar alteração de status:", err));
    }
});