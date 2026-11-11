# Desafio Técnico — Analista de Desenvolvimento Júnior

Aplicação web para cadastrar e consultar demandas internas de uma casa de repouso.

## Arquivos da aplicação

A entrega contém `app.py`, `banco.py`, `regras.py` e a pasta `static/`, necessários para executar a aplicação. Inclui também testes e o modo de desenvolvimento em `dev.py`.

Para executar, extraia o ZIP, abra o terminal na pasta do projeto e rode `python3 app.py` com Python 3.12 ou superior. No Windows, utilize `python app.py`. Acesse **http://127.0.0.1:8000** e mantenha o terminal aberto.

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
