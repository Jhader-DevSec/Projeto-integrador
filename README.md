<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Espetinho do Edir — PDV & Gestão Comercial</title>

  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <style>
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: #0f0f0f;
      color: #ffffff;
      line-height: 1.6;
    }

    header {
      padding: 80px 20px;
      text-align: center;
      background: linear-gradient(135deg, #ff4d4d, #ff9900);
    }

    header h1 {
      font-size: 40px;
      margin-bottom: 10px;
    }

    header p {
      max-width: 700px;
      margin: 0 auto;
      font-size: 18px;
      opacity: 0.9;
    }

    .container {
      max-width: 1000px;
      margin: auto;
      padding: 60px 20px;
    }

    h2 {
      margin-top: 50px;
      color: #ff9900;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
    }

    .card {
      background: #1a1a1a;
      padding: 20px;
      border-radius: 10px;
    }

    .tag {
      display: inline-block;
      background: #ff9900;
      color: black;
      padding: 5px 10px;
      margin: 5px 5px 0 0;
      border-radius: 5px;
      font-size: 12px;
    }

    footer {
      text-align: center;
      padding: 40px;
      background: #111;
      font-size: 14px;
      opacity: 0.7;
    }

    .btn {
      display: inline-block;
      margin-top: 20px;
      padding: 12px 20px;
      background: #ff9900;
      color: black;
      text-decoration: none;
      border-radius: 6px;
      font-weight: bold;
    }
  </style>
</head>

<body>

<header>
  <h1>🍢 Espetinho do Edir</h1>
  <p>
    Sistema de gestão comercial e PDV desenvolvido em Flask para simular uma operação real de vendas,
    controle de estoque e fluxo de cozinha em tempo real.
  </p>

  <a class="btn" href="#sobre">Ver Projeto</a>
</header>

<div class="container">

  <h2 id="sobre">📌 Sobre o Projeto</h2>
  <p>
    Sistema full-stack desenvolvido para simular um ambiente real de operação comercial.
    O sistema integra PDV, estoque, cozinha e painel administrativo com controle de acesso.
  </p>

  <h2>⚙️ Stack</h2>
  <div>
    <span class="tag">Python</span>
    <span class="tag">Flask</span>
    <span class="tag">JavaScript</span>
    <span class="tag">HTML5</span>
    <span class="tag">CSS3</span>
    <span class="tag">Blueprints</span>
    <span class="tag">Fetch API</span>
  </div>

  <h2>🚀 Funcionalidades</h2>

  <div class="grid">
    <div class="card">
      <h3>🧾 PDV</h3>
      <p>Carrinho dinâmico com validação de estoque em tempo real.</p>
    </div>

    <div class="card">
      <h3>📦 Estoque</h3>
      <p>Controle automático de inventário com atualização em vendas.</p>
    </div>

    <div class="card">
      <h3>🧑‍🍳 Cozinha</h3>
      <p>Fluxo de pedidos em tempo real com atualização de status.</p>
    </div>

    <div class="card">
      <h3>🛠️ Admin</h3>
      <p>Controle de usuários com RBAC e gestão de sistema.</p>
    </div>
  </div>

  <h2>🧠 Arquitetura</h2>
  <p>
    Sistema modular baseado em Flask Blueprints, separação de responsabilidades e fluxo orientado a eventos entre frontend e backend.
  </p>

  <h2>🔐 Segurança</h2>
  <p>
    Controle de sessão, proteção de rotas, rate limiting e estrutura preparada para hashing de senhas.
  </p>

  <h2>📊 Destaque Técnico</h2>
  <p>
    Sistema desenvolvido com foco em simular um ambiente real de operação comercial com consistência de dados e controle de fluxo entre módulos.
  </p>

  <h2>👤 Autor</h2>
  <p>
    Jhader Augusto — Backend & Arquitetura de Software
  </p>

  <a class="btn" href="https://github.com/seu-repo">Ver no GitHub</a>

</div>

<footer>
  Projeto desenvolvido para portfólio técnico e demonstração de habilidades em desenvolvimento web.
</footer>

</body>
</html>
