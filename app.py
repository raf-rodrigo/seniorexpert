"""Aplicação web local, executada apenas com a biblioteca padrão do Python."""

import os
import secrets
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

import banco
from regras import STATUS, prioridade_automatica, validar_demanda

BASE = Path(__file__).resolve().parent
BANCO = BASE / "dados" / "demandas.sqlite3"
TOKEN = secrets.token_urlsafe(32)


def h(valor):
    return escape(str(valor), quote=True)


def pagina(caminho, valores=None, erro="", sucesso=False, busca="", status=""):
    valores = valores or {"data_solicitacao": date.today().isoformat()}
    demandas = banco.listar(caminho, busca, status)
    todas = banco.listar(caminho)
    opcoes_setores = '<option value="">Selecione um setor</option>' + "".join(
        f'<option value="{h(setor)}" '
        f'{"selected" if setor == valores.get("setor") else ""}>'
        f'{h(setor)}</option>'
        for setor in banco.listar_setores(caminho)
    )

    def opcoes(atual, incluir_todos=False):
        return (
            '<option value="">Todos</option>' if incluir_todos else ""
        ) + "".join(
            f'<option value="{h(s)}" {"selected" if s == atual else ""}>'
            f'{h(s)}</option>'
            for s in STATUS
        )

    def campo(nome, rotulo, tipo="text", limite=None):
        return f'''
            <label>
                {rotulo}
                <input
                    name="{nome}"
                    type="{tipo}"
                    value="{h(valores.get(nome, ""))}"
                    required
                    {f"maxlength={limite}" if limite else ""}
                >
            </label>
        '''

    categorias_resumo = {
        "status": STATUS,
        "setor": sorted(
            set(banco.listar_setores(caminho)) | {d["setor"] for d in todas}
        ),
        "prioridade": ("Alta", "Normal"),
    }
    contagens = {
        coluna: Counter(d[coluna] for d in todas)
        for coluna in categorias_resumo
    }
    resumos = "".join(
        f'''
            <section class="resumo-{coluna} cartao-resumo">
                <div class="cabecalho-cartao">
                    <span class="icone-resumo" aria-hidden="true">{icone}</span>
                    <h3>Por {nome}</h3>
                </div>
                <ul class="lista-resumo">
                    {"".join(
                        f'<li><span>{h(chave)}</span>'
                        f'<strong class="contador-resumo">{contagens[coluna][chave]}</strong></li>'
                        for chave in categorias_resumo[coluna]
                    )}
                </ul>
            </section>
        '''
        for nome, coluna, icone in (
            ("status", "status", "◷"),
            ("setor", "setor", "⌂"),
            ("prioridade", "prioridade", "!"),
        )
    )
    classes_status = {
        "Aberta": "status-aberta",
        "Em andamento": "status-andamento",
        "Concluída": "status-concluida",
    }
    linhas = "".join(
        f'''
            <tr>
                <td><span class="id-demanda">#{d['id']:03d}</span></td>
                <td class="celula-demanda">
                    <strong>{h(d['titulo'])}</strong>
                    <details>
                        <summary>Ver descrição</summary>
                        <p class="descricao">{h(d['descricao'])}</p>
                    </details>
                </td>
                <td>
                    {date.fromisoformat(d['data_solicitacao']).strftime('%d/%m/%Y')}
                </td>
                <td>{h(d['setor'])}</td>
                <td>
                    <span class="etiqueta {classes_status[d['status']]}">
                        {h(d['status'])}
                    </span>
                </td>
                <td>
                    <span class="etiqueta {'prioridade-alta' if d['prioridade'] == 'Alta' else 'prioridade-normal'}">
                        {h(d['prioridade'])}
                    </span>
                </td>
            </tr>
        '''
        for d in demandas
    )
    return f'''<!doctype html>
<html lang="pt-BR">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Demandas internas</title>
        <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
        <link rel="stylesheet" href="/static/style.css?v=2">
        <script src="/static/prioridade.js" defer></script>
    </head>
    <body>
        <main>
            <h1>Demandas internas</h1>
            <p>Cadastre e consulte as solicitações dos setores.</p>
            {'<p role="status" class="sucesso">Demanda cadastrada com sucesso.</p>' if sucesso else ''}
            {f'<p role="alert" class="erro">{h(erro)}</p>' if erro else ''}

            <section>
                <h2>Nova demanda</h2>
                <form method="post" action="/demandas">
                    <input type="hidden" name="token" value="{TOKEN}">
                    {campo('titulo', 'Título', limite=150)}
                    <label>
                        Descrição
                        <textarea name="descricao" required maxlength="5000" rows="4">{h(valores.get('descricao', ''))}</textarea>
                    </label>
                    <div class="grade">
                        {campo('data_solicitacao', 'Data de solicitação', 'date')}
                        <label>
                            Setor
                            <select name="setor" required>
                                {opcoes_setores}
                            </select>
                        </label>
                        <label>
                            Status
                            <select name="status" required>
                                {opcoes(valores.get('status', 'Aberta'))}
                            </select>
                        </label>
                        <label>
                            Prioridade
                            <input
                                id="prioridade"
                                name="prioridade"
                                value="{prioridade_automatica(valores.get('descricao', ''))}"
                                readonly
                                aria-describedby="regra-prioridade"
                                aria-live="polite"
                            >
                        </label>
                    </div>
                    <p id="regra-prioridade" class="aviso-prioridade">
                        A prioridade será <strong>Alta</strong> se a descrição
                        contiver a palavra <strong>“urgente”</strong> ou
                        <strong>“erro”</strong>; caso contrário,
                        <strong>Normal</strong>.
                    </p>
                    <button>Cadastrar demanda</button>
                </form>
            </section>

            <section class="painel-resumo">
                <span class="sobretitulo">ACOMPANHAMENTO</span>
                <h2>Resumo geral</h2>
                <p class="subtitulo-painel">Uma visão das solicitações da casa de repouso.</p>
                <div class="total-resumo">
                    <span>Total de demandas</span>
                    <strong>{len(todas)}</strong>
                    <span>registradas no sistema</span>
                </div>
                <div class="grade grade-resumos">
                    {resumos}
                </div>
            </section>

            <section class="painel-consulta">
                <span class="sobretitulo">REGISTROS</span>
                <h2>Consultar demandas</h2>
                <p class="subtitulo-painel">Encontre uma solicitação e acompanhe os detalhes.</p>
                <form method="get" action="/" class="grade filtros">
                    <label>
                        Buscar por título, descrição ou setor
                        <input name="busca" value="{h(busca)}" maxlength="200" placeholder="Ex.: compra de materiais">
                    </label>
                    <label>
                        Status
                        <select name="status">
                            {opcoes(status, True)}
                        </select>
                    </label>
                    <button>Filtrar</button>
                    <a href="/">Limpar filtros</a>
                </form>
                <div class="resultado-consulta">
                    <p><strong>{len(demandas)}</strong> demanda(s) encontrada(s)</p>
                    <span>O resumo geral considera todos os registros.</span>
                </div>
                <div class="tabela">
                    <table>
                        <thead>
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Título e descrição</th>
                                <th scope="col">Solicitação</th>
                                <th scope="col">Setor</th>
                                <th scope="col">Status</th>
                                <th scope="col">Prioridade</th>
                            </tr>
                        </thead>
                        <tbody>
                            {linhas or '<tr><td colspan="6" class="estado-vazio">Nenhuma demanda encontrada. Cadastre uma solicitação ou ajuste os filtros.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </section>
        </main>
    </body>
</html>'''


def criar_app(caminho=BANCO):
    banco.inicializar(caminho)

    def app(environ, start_response):
        def responder(status, corpo, tipo="text/html; charset=utf-8", headers=None):
            conteudo = corpo.encode("utf-8")
            start_response(
                status,
                [
                    ("Content-Type", tipo),
                    ("Content-Length", str(len(conteudo))),
                    ("X-Content-Type-Options", "nosniff"),
                    ("Cache-Control", "no-store"),
                ] + (headers or []),
            )
            return [conteudo]

        rota, metodo = environ.get("PATH_INFO", "/"), environ["REQUEST_METHOD"]

        if rota in ("/favicon.ico", "/static/favicon.svg") and metodo == "GET":
            return responder(
                "200 OK",
                (BASE / "static/favicon.svg").read_text(),
                "image/svg+xml",
            )

        if rota == "/static/style.css" and metodo == "GET":
            return responder(
                "200 OK",
                (BASE / "static/style.css").read_text(),
                "text/css; charset=utf-8",
            )

        if rota == "/static/prioridade.js" and metodo == "GET":
            return responder(
                "200 OK",
                (BASE / "static/prioridade.js").read_text(),
                "text/javascript; charset=utf-8",
            )

        if rota == "/" and metodo == "GET":
            query = parse_qs(environ.get("QUERY_STRING", ""))
            return responder(
                "200 OK",
                pagina(
                    caminho,
                    sucesso=query.get("sucesso") == ["1"],
                    busca=query.get("busca", [""])[0][:200],
                    status=query.get("status", [""])[0],
                ),
            )

        if rota == "/demandas" and metodo == "POST":
            try:
                tamanho = int(environ.get("CONTENT_LENGTH") or 0)
            except ValueError:
                return responder("400 Bad Request", "Requisição inválida.")

            if tamanho < 0 or tamanho > 65536:
                return responder("413 Content Too Large", "Formulário muito grande.")

            try:
                dados = {
                    k: v[0]
                    for k, v in parse_qs(
                        environ["wsgi.input"].read(tamanho).decode("utf-8"),
                        keep_blank_values=True,
                    ).items()
                }
            except UnicodeDecodeError:
                return responder("400 Bad Request", "Codificação inválida.")

            if not secrets.compare_digest(
                dados.get("token", "").encode("utf-8"),
                TOKEN.encode("utf-8"),
            ):
                return responder(
                    "403 Forbidden",
                    "Formulário expirado ou inválido. Recarregue a página inicial.",
                )

            try:
                demanda = validar_demanda(dados)
                if demanda["setor"] not in banco.listar_setores(caminho):
                    raise ValueError("Selecione um setor cadastrado.")
            except ValueError as erro:
                return responder("400 Bad Request", pagina(caminho, dados, str(erro)))

            banco.cadastrar(caminho, demanda)
            return responder(
                "303 See Other",
                "",
                headers=[("Location", "/?sucesso=1")],
            )

        return responder("404 Not Found", "Página não encontrada.")

    return app


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", "8000"))
    with make_server("127.0.0.1", porta, criar_app()) as servidor:
        print(
            f"Aplicação disponível em http://127.0.0.1:{porta} (Ctrl+C para encerrar)",
            flush=True,
        )
        servidor.serve_forever()
