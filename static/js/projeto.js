// static/js/projeto.js

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