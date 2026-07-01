# 🍢 Espetinho do Edir — Sistema Integrado de Gestão Comercial, Pipeline Logístico & PDV Reativo

> **Enterprise Resource Planning (ERP) & Point of Sale (POS) System**
>
> Solução integrada de automação comercial focada na otimização de faturamento, controle transacional de inventário e gerenciamento de fluxo operacional ponta a ponta (Frente de Caixa, Esteira de Entrega, Preparo e Controladoria). Desenvolvido sob uma arquitetura modular de componentes em Flask, o sistema prioriza:
> - Desacoplamento Estrito e Separação de Conceitos (SoC)
> - Pipeline de Produção Multiestágios Resiliente
> - Consistência Transacional com Mecanismos de Fallback
> - Segurança Avançada via Controle de Acesso Baseado em Funções (RBAC)
> - Navegação SPA Otimizada contra Conflitos de Viewport

---

## 🎯 Escopo da Solução e Fluxo em Pipeline

O Espetinho do Edir orquestra o ciclo de vida completo da operação comercial em tempo real, estruturado em uma esteira logística de três estágios cronológicos (Pipeline):

1. **Frente de Caixa (PDV):** Captura de vendas através de interface reativa orientada a eventos. Permite a associação opcional a números de mesas ou atendimento direto no Balcão.
2. **Esteira de Preparo (Cozinha):** Recebimento instantâneo de comandas eletrônicas com status `Pendente`. O cozinheiro aciona o comando que avança o pedido assim que finalizado na churrasqueira.
3. **Esteira de Entrega (Andamento):** Isolamento visual de ordens com status `Pronto para retirada`. Garçons e entregadores monitoram e efetuam a entrega física ao cliente, finalizando o ciclo de vida da ordem para o estado `Concluído`.
4. **Controladoria & Auditoria:** Consolidação e processamento assíncrono imediato de faturamento bruto real em R$ segmentado, histórico imutável agrupado por datas civis e expurgo atômico seguro de caixa.

---

## 🛠️ Stack Tecnológica

* **Backend Core:** Python 3.11+, Flask Framework (Blueprint Architecture).
* **Camada de Dados & ORM:** SQLAlchemy, PyMySQL Driver.
* **Engine de Relatórios:** ReportLab Core (Compilação vetorial em memória via streams binários).
* **Segurança & Controle:** Flask-Limiter (Rate Limiting restritivo por IP remoto).
* **Frontend Engine:** HTML5 Semântico, Jinja2 Template Injection, JavaScript Vanilla ES6+ (Fetch API, History API, Event Interception), CSS3 Composto (Modern Flexbox, CSS Grid, Variáveis `:root`).
* **Infraestrutura Cloud:** Distribuição estável entre Render Web Services (Aplicação) e Clever Cloud (Banco de Dados MySQL dedicado).

---

## 📐 Engenharia e Arquitetura de Software

A aplicação rejeita arquiteturas monolíticas acopladas, organizando o fluxo de dados em camadas desacopladas através de Flask Blueprints para eliminar gargalos e garantir alta manutenibilidade:

* **Controladores de Rotas (`routes/`):** Isolamento completo de endpoints de regras de negócio divididos por contextos operacionais (`auth.py`, `vendas.py`, `admin.py`).
* **Modelos do ORM (`app.py`):** Abstração de persistência orientada a objetos com mapeamento de relacionamentos de Chaves Estrangeiras estritas para proteção de integridade referencial.
* **Interface Reativa Baseada em Hash (`static/`):** Simulação de comportamento SPA (Single Page Application) através de um trilho horizontal animado em CSS. O motor JS intercepta cliques de navegação nativos (`e.preventDefault()`), atualiza a URL via `history.pushState()` e gerencia o viewport aplicando `flex-shrink: 0`, eliminando o bug de duplo clique e desalinhamento vertical.

---

## 💼 Módulos Funcionais e Recursos

### Ponto de Venda (PDV)
* Montagem reativa de carrinhos de compra com totalização matemática instantânea no lado do cliente.
* Validação server-side concorrente que bloqueia requisições caso a quantidade solicitada estoure o limite real armazenado no inventário.

### Logística de Produção Bipartida (Cozinha & Andamento)
* Separação física de conceitos: o churrasqueiro foca estritamente nos itens a assar, enquanto a equipe de salão monitora os cards de bordas verdes prontos para servir, otimizando o tempo de resposta do estabelecimento.
* Mensagens dinâmicas de feedback visual (*Placeholders*) exibidas automaticamente caso as esteiras operacionais estejam limpas.

### Histórico Avançado com Filtros Dinâmicos
* Estruturação cronológica inteligente: os pedidos concluídos ou cancelados são agrupados automaticamente por blocos de dias civis no servidor.
* Mecanismo de busca ativa executado em tempo de execução no cliente, permitindo a filtragem imediata por ID ou número da mesa sem recarregamentos de página.

### Dashboard Financeiro de Caixa
* Substituição de contagem simples por somatório monetário bruto real em R$.
* Distribuição exata dos valores arrecadados mapeados de forma independente para cada método de pagamento (PIX, Crédito, Débito e Dinheiro).

---

## 🔐 Matriz de Permissões Rígida (RBAC)

O privilégio de acesso às informações e ações críticas é validado de forma intransigível no servidor, limpando elementos visuais via Jinja2 e bloqueando requisições não autorizadas com retorno HTTP `403 Forbidden`:

| Recurso / Módulo Operacional | Administrador (Gerente) | Estoquista | Operador (Vendedor) |
| :--- | :---: | :---: | :---: |
| **Gestão de Usuários e RH** | Acesso Total | ❌ Bloqueado | ❌ Bloqueado |
| **Zerar Caixa / Expurgo de Turno** | Acesso Total | ❌ Bloqueado | ❌ Bloqueado |
| **Limpar Histórico Geral** | Acesso Total | ❌ Bloqueado | ❌ Bloqueado |
| **Dashboard de Faturamento (R$)** | Acesso Total | ❌ Bloqueado | ❌ Bloqueado |
| **Cadastrar / Remover Produtos** | Acesso Total | Permitido | ❌ Bloqueado |
| **Esteiras Operacionais (Andamento/Cozinha)** | Permitido | Permitido | Permitido |
| **Terminal de Vendas (PDV)** | Permitido | Permitido | Permitido |

---

## 🛡️ Segurança Aplicada (Application Security - AppSec)

Desenvolvimento blindado focado em mitigações estruturais alinhadas às diretrizes globais do OWASP Top 10:

* **Broken Object Level Authorization (BOLA) Protection:** Verificação hierárquica severa em cada endpoint REST, impedindo que colaboradores burlem o sistema manipulando IDs ou acessando URLs diretas pelo navegador.
* **Fechamento Atômico Transacional:** O processo de encerramento de caixa opera sob uma trava atômica. O Python compila o relatório gerencial em memória RAM via `io.BytesIO`, despacha o fluxo binário para download forçado em formato PDF no computador do gerente e só então executa a exclusão física em lote das vendas concluídas, sob a proteção de `db.session.rollback()` em caso de interrupção de rede.
* **Integridade Relacional de Banco:** A remoção de produtos possui tratamento prévio de interceptação. Se o insumo possuir histórico de vendas ativas, o sistema bloqueia a exclusão via código para impedir a corrupção de chaves estrangeiras (`Foreign Keys`) do MySQL, emitindo alertas amigáveis na interface.
* **Rate Limiting Ativo:** Camada de defesa acoplada via `Flask-Limiter` restringindo a vazão de requisições excessivas por IP para prevenir ataques de negação de serviço (DoS) e brute-force em formulários de login.

---

## 📂 Estrutura do Repositório

```text
espetinho-do-edir/
│
├── routes/          # Camada de Controladores (Blueprints modularizados por contexto)
│   ├── auth.py      # Autenticação de sessões, segurança e RBAC
│   ├── vendas.py    # Operações de PDV, esteiras REST e fluxo do Caixa
│   └── admin.py     # Gestão administrativa de RH, Catálogo e compilação ReportLab PDF
│
├── static/          # Ativos de Performance Client-Side
│   ├── css/         # Estilização unificada em Dark Mode e travas de Viewport
│   └── js/          # Interceptação de eventos, carrinhos assíncronos e anti-duplo clique
│
├── templates/       # Camada de Visualização (Engine de injeção Jinja2)
│   ├── projeto.html # Painel operacional unificado reativo
│   └── admin_page.html
│
├── app.py           # Pooling de conexões ORM, Modelos do Banco e Inicialização Core
└── requirements.txt # Manifesto estrito de dependências do ecossistema

---

## 🚀 Guia de Instalação e Execução Local

Clonar o repositório e aceder ao diretório mestre:

```bash
git clone https://github.com/Jhader-DevSec/Projeto-integrador.git
cd Projeto-integrador
```

Provisionar e ativar o ambiente virtual isolado (Venv):

* **Em sistemas Linux/macOS:**
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

* **Em sistemas Windows (Prompt de Comando):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate
  ```

Instalar dependências listadas e iniciar o servidor de aplicação:

```bash
pip install -r requirements.txt
python app.py
```

> **Acesso Local:** Abra o navegador e aceda ao endereço [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📄 Licença

Este software é distribuído sob os termos da licença MIT. Para mais detalhes, consulte o arquivo `LICENSE`.
