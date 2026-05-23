# 🍢 Espetinho do Edir — Sistema de Gestão Comercial e PDV

> 🚀 **Projeto Integrador / Trabalho Final de Curso (Em Desenvolvimento)**
> 
> Embora concebido como um projeto de conclusão de curso para consolidação de conhecimentos, este sistema foi **planejado, estruturado e arquitetado para atender a uma operação comercial real**. Toda a especificação de requisitos e regras de negócio foi baseada nas necessidades diárias e dores práticas observadas diretamente no comércio de amigos próximos, focado estritamente no **uso e gerenciamento interno da empresa**.

O sistema foi pensado sob medida para a operação de uma espetaria, abrangendo desde a frente de caixa reativa (PDV) até o fluxo operacional da cozinha e auditoria gerencial.

---

## 🛠️ Tecnologias e Ferramentas

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

---

## 💼 Validação no Mundo Real & Diferencial Prático

Diferente de projetos acadêmicos puramente teóricos, o desenvolvimento do **Espetinho do Edir** foi guiado por um mapeamento de processos de um negócio ativo. Isso se reflete diretamente nas escolhas de design de código:
* **Foco em Gestão Interna:** O sistema foi desenhado para uso exclusivo dos colaboradores e gerentes (operação interna), otimizando a comunicação entre o balcão de vendas e a churrasqueira/cozinha.
* **Resolução de Dores Reais:** Funcionalidades como a trava física de estouro de estoque no botão `+`, o sumiço automático de produtos esgotados e o estorno automático em caso de cancelamento foram implementadas para resolver problemas reais de furos de caixa e desperdício de insumos.

---

## 📱 Demonstração da Interface (Preview)

https://github.com/user-attachments/assets/ff3a1f2a-03f1-4ea8-906f-8902d1cf588f

<p align="center">
  <img src="static/img/logo.png" alt="Espetinho do Edir" width="160px">
</p>

---

## 🔐 Credenciais de Teste

Para navegar pelas diferentes camadas do sistema (PDV e Painel Administrativo), utilize os seguintes acessos simulados em memória:

| Perfil | Usuário | Senha |
| :--- | :--- | :--- |
| **Administrador / Gerente** | `"admin@brasas.com"` | `admin123` |
| **Operador de Caixa / PDV** | `teste@brasas.com` | `123456` |

---

## 🧠 Desafios Técnicos & Aprendizados

Como desenvolvedor focado em compreender profundamente o ecossistema de back-end, arquitetura de software e segurança, o projeto trouxe desafios complexos que exigiram soluções maduras:

### 1. Desfazer o Monolito (Modularização)
* **Desafio:** Manter rotas de autenticação, vendas e administração no mesmo arquivo torna o código insustentável.
* **Solução:** Implementação de **Flask Blueprints** isolando os contextos. Isso me permitiu compreender como estruturar pastas de nível profissional, organizando rotas, estáticos e templates de forma desacoplada.

### 2. Sincronização de Estoque Vivo no Front-end (Sem Banco SQL)
* **Desafio:** Impedir que o operador venda itens acima do estoque real e ocultar produtos esgotados instantaneamente sem sobrecarregar o servidor com requisições HTTP a cada clique.
* **Solução:** Uso de injeção de contexto via Jinja estruturando blocos condicionais (`{% if produto.estoque > 0 %}`) para limpar a interface. Para os botões de ação, injetei metadados estruturados (`data-preco`, `data-estoque`) no DOM HTML. O JavaScript Vanilla (ES6) captura essas pistas e faz as validações em memória de forma reativa e segura.

### 3. Proteção de Sessão e Controle de Acesso
* **Desafio:** Garantir que um operador de caixa comum não consiga acessar as rotas de administração alterando manualmente a URL do navegador.
* **Solução:** Utilização de gerenciamento de sessões nativas do Flask (`flask.session`), aplicando validações nos endpoints administrativos para verificar ativamente o nível de privilégio e autenticação do usuário logado antes de renderizar os templates.

### 🔄 Fluxo de Dados do Carrinho de Vendas
```mermaid
graph TD
    A[Clique no Botão +] --> B{Qtd Atual < data-estoque?}
    B -- Sim --> C[Incrementa Qtd na Tela]
    B -- Não --> D[Dispara Alerta de Bloqueio]
    C --> E[JS Varre os Cards & Multiplica Valores]
    E --> F[Atualiza ID #valor-total no Rodapé]
