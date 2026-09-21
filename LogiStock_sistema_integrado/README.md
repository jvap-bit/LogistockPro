# LogiStock PRO Web

Versão em HTML, CSS, JavaScript, Node.js e SQLite do projeto Python enviado. Requer Node.js 22.13 ou superior. Execute `npm install` uma vez e depois `npm start` nesta pasta e abra `http://localhost:3000`.

## Contas e ligação entre telas

Crie uma conta para cada perfil na página de cadastro. Cada login abre o painel do perfil correspondente. Use "Trocar conta" para entrar em outra conta ou abra o endereço em navegadores distintos para ver duas contas ao mesmo tempo. Todas as contas acessam as mesmas ordens guardadas no banco do servidor (`data/producao.db`); as telas atualizam automaticamente a cada quatro segundos.

- PCP: cria OP, vê Kanban e avança A Fazer → Em Andamento → Qualidade → Finalizado.
- Produção: acompanha em painel próprio as ordens e o andamento no Kanban.
- Gestão: vê painel com contagens de todas as etapas, consulta histórico e remove ordens finalizadas.
- Entregador: painel de logística separado com ordens Finalizado → Em Rota → Entregue, busca de OP e leitor de QR Code quando o navegador oferece `BarcodeDetector` e câmera autorizada. Também pode digitar a OP.

Os quatro perfis têm navegação para as ferramentas pertinentes. Exemplo: uma OP criada no PCP aparece na Produção e Gestão; depois de finalizada aparece no painel do Entregador; ao entregar, o novo status aparece para os outros perfis. Registros das ações ficam no histórico.

## Diferenças do programa Python

A exportação gera CSV compatível com Excel; PDF usa a impressão do navegador. O frete usa a fórmula do projeto original (peso × R$ 12,50), sem calcular distância pelos CEPs. O QR por câmera depende do suporte do navegador; a consulta digitada funciona em todos. Este pacote começa com o banco de dados vazio. Cadastre novas contas na página de cadastro. O cadastro livre de perfis acompanha o projeto original e é adequado para demonstração em rede de confiança; para uso externo, acrescente cadastro administrado, HTTPS, proteção de login e banco de dados transacional.

## Banco SQLite

O arquivo `data/producao.db` contém as tabelas `pedidos`, `usuarios`, `logs` e `sessoes`. As senhas de novas contas são guardadas com scrypt e salt; sessões são guardadas como hashes e expiram em sete dias. Faça uma cópia do arquivo `producao.db` para guardar os dados. Os arquivos `.json` antigos não são usados nesta versão.

## QR Code no comprovante de entrega

O botão **PDF + QR** gera um comprovante com um QR de **link**. A câmera normal do celular abre uma página de consulta com OP, produto, quantidade, cliente, endereço, prioridade e status atual. A página permite entrar na conta do Entregador para alterar a etapa. O link usa um identificador aleatório guardado no SQLite; qualquer pessoa que tenha acesso ao QR pode consultar os dados do comprovante. Não compartilhe o PDF fora da equipe responsável.

O link precisa chegar ao computador que está executando o servidor. Para testar, deixe `npm start` aberto e conecte celular e computador à mesma rede Wi-Fi. Configure o endereço IPv4 do computador (consulte `ipconfig` no Windows) no PowerShell **antes** de iniciar:

```powershell
$env:APP_BASE_URL = "http://192.168.1.10:3000"
npm start
```

Substitua `192.168.1.10` pelo IP real. Digite `http://SEU-IP:3000` no navegador do celular **antes** de gerar o PDF; se essa página não abrir, o QR também não abrirá. Permita o Node.js na rede privada no Firewall do Windows. Só então gere **um PDF novo** e confira o link impresso abaixo do QR. Caso tenha domínio com HTTPS, também pode usá-lo em APP_BASE_URL.

O comprovante é operacional e não substitui nota fiscal eletrônica. Execute `npm install` para instalar a dependência `qrcode` na primeira execução.
