"""Persistência local em SQLite; consultas usam parâmetros."""
import sqlite3
from pathlib import Path


SETORES_INICIAIS = (
    "Enfermagem",
    "Cuidados e Assistência aos Idosos",
    "Nutrição e Cozinha",
    "Higiene e Limpeza",
    "Administração",
)


def conectar(caminho):
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar(caminho):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with conectar(caminho) as conexao:
        conexao.execute('''CREATE TABLE IF NOT EXISTS setores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE CHECK(length(trim(nome)) > 0)
        )''')
        conexao.executemany(
            'INSERT OR IGNORE INTO setores (nome) VALUES (?)',
            [(nome,) for nome in SETORES_INICIAIS],
        )
        conexao.execute('''CREATE TABLE IF NOT EXISTS demandas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL CHECK(length(trim(titulo)) > 0),
            descricao TEXT NOT NULL CHECK(length(trim(descricao)) > 0),
            data_solicitacao TEXT NOT NULL,
            setor TEXT NOT NULL CHECK(length(trim(setor)) > 0),
            status TEXT NOT NULL CHECK(status IN ('Aberta', 'Em andamento', 'Concluída')),
            prioridade TEXT NOT NULL CHECK(prioridade IN ('Alta', 'Normal'))
        )''')


def cadastrar(caminho, demanda):
    with conectar(caminho) as conexao:
        conexao.execute('''INSERT INTO demandas
            (titulo, descricao, data_solicitacao, setor, status, prioridade)
            VALUES (:titulo, :descricao, :data_solicitacao, :setor, :status, :prioridade)''', demanda)


def listar(caminho, busca="", status=""):
    with conectar(caminho) as conexao:
        return conexao.execute('''SELECT * FROM demandas
            WHERE (? = '' OR instr(lower(titulo || ' ' || descricao || ' ' || setor), lower(?)) > 0)
              AND (? = '' OR status = ?)
            ORDER BY data_solicitacao DESC, id DESC''', (busca, busca, status, status)).fetchall()


def listar_setores(caminho):
    with conectar(caminho) as conexao:
        return [linha["nome"] for linha in conexao.execute(
            "SELECT nome FROM setores ORDER BY nome"
        ).fetchall()]
