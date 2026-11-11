# Desafio Técnico — Analista de Desenvolvimento Júnior

Aplicação web para cadastrar e consultar demandas internas de uma casa de repouso.

## Arquivos da aplicação

A entrega contém `app.py`, `banco.py`, `regras.py` e a pasta `static/`, necessários para executar a aplicação. Inclui também testes e o modo de desenvolvimento em `dev.py`.

## Como abrir o sistema pelo ZIP

1. Salve o arquivo ZIP recebido por e-mail e extraia todo o conteúdo para uma pasta.
2. Tenha Python 3.12 ou superior instalado. Não é necessário usar Git ou baixar o projeto pelo GitHub.
3. Abra o terminal na pasta extraída que contém `app.py` e escolha um dos modos abaixo.

### Opção 1 — Execução normal

```bash
python3 app.py
```

No Windows, se o comando `python3` não estiver disponível:

```bash
python app.py
```


Nesse modo, o servidor reinicia automaticamente ao salvar um arquivo Python na raiz do projeto. Atualize o navegador para visualizar as alterações.

Em ambos os modos, abra **http://127.0.0.1:8000** no navegador e mantenha o terminal aberto. Use apenas um modo por vez. Para encerrar ou trocar de modo, pressione **Ctrl+C** no terminal.

## Como abrir o sistema pelo GitHub

Com Git e Python 3.12 ou superior instalados, execute no terminal:

```bash
git clone https://github.com/raf-rodrigo/seniorexpert.git
cd seniorexpert
python3 app.py
```

Para usar o modo de desenvolvimento, execute `python3 dev.py` no lugar de `python3 app.py`. No Windows, use `python` se `python3` não estiver disponível.

Abra **http://127.0.0.1:8000** e mantenha o terminal aberto. Para encerrar, pressione **Ctrl+C**. Se o repositório for privado, será necessário ter acesso a ele.

O clone recebe os arquivos enviados ao GitHub. Se `dados/demandas.sqlite3` não estiver no repositório, a aplicação criará um banco novo com os cinco setores e sem demandas.

## Tecnologia utilizada

Python com biblioteca padrão, SQLite para armazenamento e HTML, CSS e JavaScript para a interface. Não é necessário instalar pacotes adicionais.

## Estrutura da solução

- `app.py`: servidor, formulário, consulta e resumo das demandas.
- `regras.py`: validação dos campos e cálculo da prioridade.
- `banco.py`: criação do banco, cadastro dos setores e operações com demandas.
- `static/`: estilos, ícone e atualização da prioridade na tela.
- `tests/test_app.py`: testes das regras e do cadastro.
- `dev.py`: reinício automático do servidor durante o desenvolvimento.

## Regra de prioridade

Se a descrição contiver a palavra inteira **urgente** ou **erro**, a prioridade será **Alta**. Caso contrário, será **Normal**. A verificação ignora maiúsculas e minúsculas. O formulário exibe o resultado enquanto o usuário digita e o servidor recalcula a prioridade ao salvar.

## Principais decisões

- Interface simples e responsiva, com cadastro, consulta, filtros e resumo geral.
- Campos obrigatórios e data validados no servidor.
- Cinco setores de uma casa de repouso cadastrados automaticamente, sem duplicação.
- Dados salvos em `dados/demandas.sqlite3`, preservados após reiniciar a aplicação. O banco é criado automaticamente se não existir.
- Consultas SQL parametrizadas e textos exibidos com escape de HTML.
- Aplicação para uso local, sem login, edição ou exclusão de demandas.
