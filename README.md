# 🍢 Espetinho do Edir — Sistema Integrado de Gestão Comercial & PDV Reativo

> **Enterprise Resource Planning (ERP) & Point of Sale (POS) System**
>
> Solução integrada de gestão comercial focada na otimização de faturamento, controle transacional de inventário e automação do fluxo operacional de ponta a ponta (Frente de Caixa, Cozinha e Controladoria). Desenvolvido sob uma arquitetura de componentes modulares em Flask, o sistema prioriza:
> - Desacoplamento e Separação de Conceitos (SoC)
> - Consistência Transacional Estrita
> - Segurança via Controle de Acesso Baseado em Funções (RBAC)
> - Comunicação Assíncrona Orientada a APIs REST

---

## 🎯 Escopo da Solução

O Espetinho do Edir gerencia o ciclo de vida completo da operação comercial em tempo real:
1. **Frente de Caixa (PDV):** Captura e processamento imediato de vendas.
2. **Camada de Validação:** Verificação server-side automatizada de inventário em tempo de execução.
3. **Orquestração de Produção:** Despacho dinâmico de pedidos para a linha de preparação.
4. **Sincronização de Status:** Atualização de prontidão e entrega sem latência.
5. **Auditoria e Controladoria:** Consolidação e fechamento financeiro imediato para a gestão.

A arquitetura foi projetada com foco em alta disponibilidade de lógica e isolamento de processos, garantindo a manutenibilidade e a escalabilidade do ecossistema.

---

## 🛠️ Stack Tecnológica

* **Backend:** Python 3.11+, Flask (Blueprint Architecture), SQLAlchemy ORM.
* **Frontend:** HTML5 Engine, Jinja2 Template Injection, JavaScript ES6+ (Fetch API), CSS Composto Modular.
* **Infraestrutura:** Ambientes isolados (Virtualenv), manifesto de dependências (`requirements.txt`), pronto para deploy automatizado em ambientes Linux / VPS / Cloud.

---

## 📐 Engenharia e Arquitetura de Software

A aplicação foi estruturada em camadas desacopladas utilizando o padrão Flask Blueprints para eliminar gargalos de código e facilitar o desenvolvimento paralelo:

* **Controladores de Rotas (Controllers):** Isolamento de endpoints e segmentação das regras de negócio por contexto operacional.
* **Camada de Serviço (Core Logic):** Motores de processamento de dados, validações e regras transacionais internas.
* **Persistência de Dados (Data Layer):** Abstração de banco de dados orientada a objetos via ORM, mitigando o acoplamento direto com o motor SQL.
* **Interface Reativa (User Interface):** Renderização dinâmica server-side otimizada com Jinja2 combinada a componentes reativos via JavaScript assíncrono.

---

## 💼 Módulos Funcionais e Recursos

### Ponto de Venda (PDV)
* Lógica orientada a eventos (*event-driven UI*) para agilidade no atendimento ao cliente.
* Bloqueios nativos na interface e validação *server-side* concorrente para impedir vendas sem estoque físico.

### Gestão de Produção (Cozinha)
* Painel operacional alimentado por requisições assíncronas assentes em endpoints REST.
* Monitorização activa de status (Fila, Preparo, Concluído) com atualização em tempo real para controle de tempo de resposta.

### Controle de Inventário Automatizado
* Dedução dinâmica de insumos vinculada diretamente ao fechamento da venda no PDV.
* Mecanismos de *rollback* e estorno automatizado de estoque em caso de cancelamento de itens ou quebra de fluxo.

### Auditoria Financeira & Business Intelligence
* Agregação e consolidação inteligente de faturamento segmentado por meio de pagamento (PIX, Crédito, Débito, Dinheiro).
* Histórico completo e imutável de transações para auditorias de caixa e prevenção de fraudes.

---

## 🔐 Matriz de Permissões (RBAC)

O controle de privilégios de acesso é validado ao nível do servidor, restringindo a exposição de dados críticos de acordo com a função do colaborador:

| Módulo / Endpoint | Administrador | Estoquista | Operador (Venda) |
| :--- | :---: | :---: | :---: |
| **Gestão de Usuários / Permissões** | Acesso Total | ❌ | ❌ |
| **Fechamento e Auditoria de Caixa** | Acesso Total | ❌ | ❌ |
| **Modificação de Preços e Catálogo** | Acesso Total | Escrita Parcial | ❌ |
| **Linha de Produção (Cozinha)** | Supervisão | ❌ | Atualização de Status |
| **Terminal de Vendas (PDV)** | Permitido | Permitido | Permitido |

---

## 🛡️ Segurança Aplicada (Application Security - AppSec)

O desenvolvimento da solução considerou controles e mitigações alinhados às diretrizes globais do OWASP Top 10:

* **State and Session Management:** Controle de sessão eamp; persistência de identidade criptografada via `flask.session`.
* **Broken Object Level Authorization (BOLA) Mitigation:** Validação server-side de privilégios em cada endpoint administrativo, impedindo desvios de acesso por manipulação direta de URLs.
* **Integridade Transacional:** Rollback automático de transações em cenários de interrupção ou falha de rede para evitar corrupção de registros.
* **Secrets Management:** Isolamento estrito de chaves criptográficas e variáveis de ambiente usando arquivos de configuração `.env`.
* **Data Protection:** Lógica nativa preparada para persistência de credenciais sob criptografia de via única (*Hashing* via `bcrypt`).

---

## 🧠 Soluções para Desafios de Engenharia

### 1. Consistência e Estado Síncrono sem Latência
Desenvolvimento de uma arquitetura assíncrona no front-end para comunicação reativa entre o operador do caixa e a equipe de produção. Garante que os dados financeiros e operacionais permaneçam idênticos em todas as frentes de trabalho sem a necessidade de recarregar a interface.

### 2. Concorrência e Conflitos de Inventário
Implementação de regras transacionais para mitigar a concorrência de requisições simultâneas, impedindo que múltiplos operadores consumam o mesmo produto físico além do limite real do inventário.

### 3. Eliminação de Monolitos de Código
Refatoração intensiva para migrar rotas acopladas para módulos isolados, gerando uma base de código limpa, passível de testes unitários e de fácil manutenção por equipas de desenvolvimento.

---

## 📂 Estrutura do Repositório

```text
espetinho-do-edir/
│
├── routes/          # Camada de Controladores (Blueprints desacoplados por módulo)
├── static/          # Ativos de Performance da Aplicação (JS Moderno, CSS Estruturado)
├── templates/       # Camada de Visualização (Engine Jinja2)
├── app.py           # Orquestrador Central e Inicialização do Servidor
├── requirements.txt # Manifesto de Dependências do Ambiente
└── README.md        # Documentação Técnica do Sistema
```

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

## 🗺️ Roadmap de Desenvolvimento e Próximas Atualizações

### Core & Infraestrutura
- [x] Modularização completa do backend via Blueprints.
- [ ] Implementação de logs estruturados em formato JSON para auditoria corporativa.
- [ ] Camada de cache em memória para otimização de consultas de alto tráfego.

### Application Security (AppSec)
- [ ] Integração de encriptação robusta de senhas via bcrypt.
- [ ] Implementação de tokens de validação contra ataques CSRF.
- [ ] Configuração de políticas estritas de segurança de cabeçalhos HTTP.

### Client Side / UX
- [ ] Refatoração da biblioteca de scripts para módulos puros ES6.
- [ ] Dashboard gerencial avançado com suporte a gráficos analíticos responsivos.

---

## 📄 Licença

Este software é distribuído sob os termos da licença MIT. Para mais detalhes, consulte o arquivo `LICENSE`.
