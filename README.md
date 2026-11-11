# Demandas internas

Solução para o Desafio Técnico — Analista de Desenvolvimento Júnior. Permite cadastrar e consultar demandas internas, com persistência local e prioridade automática.

## Executar

Requer Python 3.10 ou superior. Não exige instalação de pacotes.

Para baixar o projeto, copie a URL do repositório no GitHub e execute (substitua `URL_DO_REPOSITORIO` pela URL real):

```bash
git clone URL_DO_REPOSITORIO seniorexpert
cd seniorexpert
```

Se já possui os arquivos, abra o terminal na pasta do projeto. Para subir a aplicação localmente:

```bash
python3 app.py
```

Acesse **http://127.0.0.1:8000** no navegador. Para encerrar, pressione `Ctrl+C` no terminal. No Windows, use `python` no lugar de `python3`, se necessário.

Para usar outra porta:

```bash
PORT=8001 python3 app.py
```

## Persistência do SQLite

O arquivo `dados/demandas.sqlite3` guarda as demandas e os setores. Ele é criado automaticamente na primeira execução. Os cinco setores iniciais são inseridos sem duplicação.

| Situação | O que acontece com os dados |
| --- | --- |
| Recarregar a página ou reiniciar a aplicação | Os dados permanecem no mesmo arquivo SQLite. |
| Atualizar o código sem apagar a pasta `dados/` | Os dados permanecem. |
| Enviar o código ao GitHub | O banco local permanece, mas não é enviado: `dados/` está no `.gitignore`. |
| Clonar em outro computador | Um novo banco é criado, com os setores iniciais e sem as demandas anteriores. |
| Apagar o arquivo SQLite ou perder o disco sem backup | Os registros são perdidos. |
| Hospedar em ambiente com disco temporário | Os dados podem desaparecer quando o ambiente for recriado; use armazenamento persistente e backup. |

### Backup e restauração

Encerre a aplicação com `Ctrl+C` antes de copiar ou substituir o banco.

No Linux/macOS, para criar uma cópia fora da pasta do projeto:

```bash
mkdir -p ../backup-seniorexpert
cp dados/demandas.sqlite3 "../backup-seniorexpert/demandas-$(date +%Y%m%d-%H%M%S).sqlite3"
```

Guarde uma cópia também em outro dispositivo ou armazenamento de sua escolha. No Windows, copie o arquivo pelo Explorador de Arquivos.

Para transferir os registros a outro computador ou restaurar uma cópia, com o servidor parado, crie a pasta `dados/` e copie o backup para `dados/demandas.sqlite3`. Antes de substituir um banco existente, faça uma cópia dele. Depois execute `python3 app.py`.

O GitHub versiona o código deste projeto e não funciona como backup do banco local.

## Criar o repositório no GitHub

Execute no seu terminal, dentro da pasta do projeto. Requer Git e GitHub CLI (`gh`) instalados. Se a autenticação estiver inválida, execute novamente o login:

```bash
gh auth login --hostname github.com
git init -b main
git add .gitignore README.md app.py banco.py regras.py static tests
git commit -m "Implementa cadastro e consulta de demandas internas"
gh repo create seniorexpert --private --source=. --remote=origin --push
```

O comando cria um repositório privado; para uma entrega pública, escolha `--public` no lugar de `--private`. Se o nome já existir na sua conta, escolha outro nome. Se o Git pedir nome e e-mail de autoria, configure seus próprios dados antes de repetir o commit.

O banco SQLite fica fora do commit. Compartilhe o repositório com o avaliador conforme a visibilidade escolhida. Publicar o código no GitHub não inicia o servidor nem hospeda a aplicação Python; quem baixar deve seguir as instruções de execução acima.

## Como usar

1. Preencha título, descrição, data de solicitação, setor e status.
2. O campo **Prioridade**, somente leitura, mostra **Alta** ou **Normal** enquanto você digita a descrição. Clique em **Cadastrar demanda**; o servidor recalcula a prioridade ao salvar. Sem JavaScript, o cálculo continua funcionando ao salvar.
3. Consulte os registros na tabela e clique em **Descrição** para expandir o texto.
4. Busque por título, descrição ou setor e/ou filtre pelo status.

Cadastro, resumo geral e consulta são apresentados em uma única coluna, com layout adaptável à largura da tela.

O resumo geral apresenta total e quantidades por status, setor e prioridade, independentemente dos filtros. É um complemento na própria aplicação; não inclui arquivo Excel ou Power BI.

## Regras e decisões

- Todos os cinco campos informados pelo usuário são obrigatórios. Valores vazios ou contendo apenas espaços são rejeitados também no servidor.
- A prioridade é **Alta** quando a descrição contém a palavra inteira `urgente` ou `erro`, independentemente de maiúsculas/minúsculas e mesmo junto a pontuação. Caso contrário, é **Normal**. Por interpretar o enunciado como palavras inteiras, `erros`, `terror` e `urgentemente` não acionam prioridade Alta.
- O cliente não define a prioridade: mesmo que envie esse campo manualmente, o servidor recalcula o valor.
- Status disponíveis: **Aberta**, **Em andamento** e **Concluída**. O status é escolhido no cadastro; alteração e exclusão de registros ficam fora do escopo desta entrega.
- A data deve ser válida; datas futuras são aceitas porque o enunciado não estabelece restrição.
- Título: até 150 caracteres; descrição: até 5.000; setor: até 100. O setor é selecionado entre os registros da tabela `setores`: Enfermagem, Cuidados e Assistência aos Idosos, Nutrição e Cozinha, Higiene e Limpeza e Administração. Esses cinco setores são cadastrados automaticamente na inicialização, sem duplicações. Demandas anteriores são preservadas.
- A consulta apresenta primeiro as solicitações mais recentes, com desempate pelo ID.
- A busca usa a função `lower` do SQLite, que não oferece normalização completa de maiúsculas e acentos Unicode. Para nomes acentuados, prefira a grafia cadastrada.
- Consultas SQL parametrizadas, saída HTML escapada e token de formulário protegem operações básicas. Após reiniciar o servidor, recarregue a página para renovar o token.
- O servidor da biblioteca padrão é adequado à demonstração local e escuta apenas em `127.0.0.1`. A solução não implementa autenticação, implantação em produção ou uso concorrente em escala.

## Tecnologia e estrutura

Python com biblioteca padrão, SQLite para armazenamento e HTML/CSS para a interface. A escolha evita dependências externas e mantém a lógica fácil de inspecionar.

```text
app.py                Rotas HTTP, formulário, consulta e resumo
regras.py             Validação e cálculo de prioridade
banco.py              Criação do banco, inclusão e consulta
static/style.css      Estilos da interface
static/prioridade.js  Prévia automática da prioridade
tests/test_app.py     Testes de regras e integração
dados/                Banco gerado em execução (ignorado pelo Git)
```

## Verificação

```bash
python3 -m unittest discover -s tests -v
```

Os testes usam bancos temporários e verificam obrigatoriedade, datas/status inválidos, limites, palavras de prioridade, persistência, filtros, prioridade enviada manualmente, rejeição de formulário inválido e escape de HTML.

Exemplos para demonstração:

| Descrição | Prioridade esperada |
| --- | --- |
| Solicito acesso ao relatório mensal | Normal |
| Erro ao emitir relatório | Alta |
| Pedido URGENTE para o financeiro | Alta |

Para demonstrar a validação no navegador, tente cadastrar sem título. Para demonstrar a persistência, cadastre uma demanda, reinicie o servidor e consulte a tabela.
