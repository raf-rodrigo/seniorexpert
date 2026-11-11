"""Aplicação web local, executada apenas com a biblioteca padrão do Python."""
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
import os
import secrets

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
    opcoes_setores = '<option value="">Selecione um setor</option>' + ''.join(
        f'<option value="{h(setor)}" {"selected" if setor == valores.get("setor") else ""}>{h(setor)}</option>'
        for setor in banco.listar_setores(caminho)
    )
    def opcoes(atual, incluir_todos=False):
        return ('<option value="">Todos</option>' if incluir_todos else '') + ''.join(
            f'<option value="{h(s)}" {"selected" if s == atual else ""}>{h(s)}</option>' for s in STATUS)
    def campo(nome, rotulo, tipo="text", limite=None):
        return f'<label>{rotulo}<input name="{nome}" type="{tipo}" value="{h(valores.get(nome, ""))}" required {f"maxlength={limite}" if limite else ""}></label>'
    resumos = ''.join(
        f'<section class="resumo-{coluna}"><h3>Por {nome}</h3><ul>' + ''.join(f'<li>{h(chave)}: <strong>{total}</strong></li>' for chave, total in sorted(Counter(d[coluna] for d in todas).items())) + '</ul></section>'
        for nome, coluna in (("status", "status"), ("setor", "setor"), ("prioridade", "prioridade")))
    linhas = ''.join(f'''<tr><td>{d['id']}</td><td><strong>{h(d['titulo'])}</strong><details><summary>Descrição</summary><p class="descricao">{h(d['descricao'])}</p></details></td>
        <td>{date.fromisoformat(d['data_solicitacao']).strftime('%d/%m/%Y')}</td><td>{h(d['setor'])}</td><td>{h(d['status'])}</td><td class="{'alta' if d['prioridade'] == 'Alta' else ''}">{h(d['prioridade'])}</td></tr>''' for d in demandas)
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Demandas internas</title><link rel="stylesheet" href="/static/style.css"><script src="/static/prioridade.js" defer></script></head>
    <body><main><h1>Demandas internas</h1><p>Cadastre e consulte as solicitações dos setores.</p>
    {'<p role="status" class="sucesso">Demanda cadastrada com sucesso.</p>' if sucesso else ''}
    {f'<p role="alert" class="erro">{h(erro)}</p>' if erro else ''}
    <section><h2>Nova demanda</h2><form method="post" action="/demandas">
    <input type="hidden" name="token" value="{TOKEN}">
    {campo('titulo', 'Título', limite=150)}
    <label>Descrição<textarea name="descricao" required maxlength="5000" rows="4">{h(valores.get('descricao', ''))}</textarea></label>
    <div class="grade">{campo('data_solicitacao', 'Data de solicitação', 'date')}<label>Setor<select name="setor" required>{opcoes_setores}</select></label>
    <label>Status<select name="status" required>{opcoes(valores.get('status', 'Aberta'))}</select></label>
    <label>Prioridade<input id="prioridade" name="prioridade" value="{prioridade_automatica(valores.get('descricao', ''))}" readonly aria-describedby="regra-prioridade" aria-live="polite"></label></div>
    <p id="regra-prioridade">A prioridade será Alta se a descrição contiver a palavra “urgente” ou “erro”; caso contrário, Normal.</p><button>Cadastrar demanda</button></form></section>
    <section><h2>Resumo geral</h2><p>Total de demandas: <strong>{len(todas)}</strong></p><div class="grade">{resumos}</div></section>
    <section><h2>Consultar demandas</h2><form method="get" action="/" class="grade"><label>Buscar por título, descrição ou setor<input name="busca" value="{h(busca)}" maxlength="200"></label><label>Status<select name="status">{opcoes(status, True)}</select></label><button>Filtrar</button><a href="/">Limpar filtros</a></form>
    <p>{len(demandas)} demanda(s) encontrada(s). O resumo geral considera todos os registros.</p>
    <div class="tabela"><table><thead><tr><th>ID</th><th>Título e descrição</th><th>Solicitação</th><th>Setor</th><th>Status</th><th>Prioridade</th></tr></thead><tbody>{linhas or '<tr><td colspan="6">Nenhuma demanda encontrada.</td></tr>'}</tbody></table></div></section>
    </main></body></html>'''


def criar_app(caminho=BANCO):
    banco.inicializar(caminho)
    def app(environ, start_response):
        def responder(status, corpo, tipo="text/html; charset=utf-8", headers=None):
            conteudo = corpo.encode('utf-8')
            start_response(status, [('Content-Type', tipo), ('Content-Length', str(len(conteudo))), ('X-Content-Type-Options', 'nosniff')] + (headers or []))
            return [conteudo]
        rota, metodo = environ.get('PATH_INFO', '/'), environ['REQUEST_METHOD']
        if rota == '/static/style.css' and metodo == 'GET':
            return responder('200 OK', (BASE / 'static/style.css').read_text(), 'text/css; charset=utf-8')
        if rota == '/static/prioridade.js' and metodo == 'GET':
            return responder('200 OK', (BASE / 'static/prioridade.js').read_text(), 'text/javascript; charset=utf-8')
        if rota == '/' and metodo == 'GET':
            query = parse_qs(environ.get('QUERY_STRING', ''))
            return responder('200 OK', pagina(caminho, sucesso=query.get('sucesso') == ['1'], busca=query.get('busca', [''])[0][:200], status=query.get('status', [''])[0]))
        if rota == '/demandas' and metodo == 'POST':
            try:
                tamanho = int(environ.get('CONTENT_LENGTH') or 0)
            except ValueError:
                return responder('400 Bad Request', 'Requisição inválida.')
            if tamanho < 0 or tamanho > 65536:
                return responder('413 Content Too Large', 'Formulário muito grande.')
            try:
                dados = {k: v[0] for k, v in parse_qs(environ['wsgi.input'].read(tamanho).decode('utf-8'), keep_blank_values=True).items()}
            except UnicodeDecodeError:
                return responder('400 Bad Request', 'Codificação inválida.')
            if not secrets.compare_digest(dados.get('token', '').encode('utf-8'), TOKEN.encode('utf-8')):
                return responder('403 Forbidden', 'Formulário expirado ou inválido. Recarregue a página inicial.')
            try:
                demanda = validar_demanda(dados)
                if demanda["setor"] not in banco.listar_setores(caminho):
                    raise ValueError("Selecione um setor cadastrado.")
            except ValueError as erro:
                return responder('400 Bad Request', pagina(caminho, dados, str(erro)))
            banco.cadastrar(caminho, demanda)
            return responder('303 See Other', '', headers=[('Location', '/?sucesso=1')])
        return responder('404 Not Found', 'Página não encontrada.')
    return app


if __name__ == '__main__':
    porta = int(os.environ.get('PORT', '8000'))
    with make_server('127.0.0.1', porta, criar_app()) as servidor:
        print(f'Aplicação disponível em http://127.0.0.1:{porta} (Ctrl+C para encerrar)', flush=True)
        servidor.serve_forever()
