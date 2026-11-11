import io
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlencode

import banco
from app import TOKEN, criar_app
from regras import CAMPOS, prioridade_automatica, validar_demanda


class DemandasTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.db = Path(self.pasta.name) / "teste.sqlite3"
        self.app = criar_app(self.db)
        self.dados = dict(
            titulo="Acesso ao sistema",
            descricao="Solicitar acesso",
            data_solicitacao="2026-11-11",
            setor="Enfermagem",
            status="Aberta",
        )

    def requisicao(self, metodo="GET", rota="/", dados=None, query=""):
        corpo = urlencode(dados or {}).encode()
        resposta = {}

        def iniciar(status, headers):
            resposta.update(status=status, headers=dict(headers))

        resultado = self.app(
            dict(
                REQUEST_METHOD=metodo,
                PATH_INFO=rota,
                QUERY_STRING=query,
                CONTENT_LENGTH=str(len(corpo)),
                **{"wsgi.input": io.BytesIO(corpo)},
            ),
            iniciar,
        )
        resposta["corpo"] = b"".join(resultado).decode()
        return resposta

    def test_setores_iniciais_sem_duplicacao(self):
        banco.inicializar(self.db)
        self.assertEqual(
            set(banco.listar_setores(self.db)),
            set(banco.SETORES_INICIAIS),
        )
        self.assertEqual(len(banco.listar_setores(self.db)), 5)
        self.assertIn('name="setor" required', self.requisicao()["corpo"])

    def test_setor_nao_cadastrado_rejeitado(self):
        resposta = self.requisicao(
            "POST",
            "/demandas",
            self.dados | {"token": TOKEN, "setor": "Inexistente"},
        )
        self.assertTrue(resposta["status"].startswith("400"))
        self.assertEqual(len(banco.listar(self.db)), 0)

    def test_prioridade(self):
        for descricao in ["urgente", "ERRO no sistema", "Pedido URGENTE!", "Um erro."]:
            with self.subTest(descricao=descricao):
                self.assertEqual(prioridade_automatica(descricao), "Alta")
        for descricao in ["Acesso normal", "terror", "erros", "urgentemente"]:
            with self.subTest(descricao=descricao):
                self.assertEqual(prioridade_automatica(descricao), "Normal")

    def test_todos_campos_obrigatorios(self):
        for campo in CAMPOS:
            for valor in ["", "   "]:
                with self.subTest(campo=campo, valor=valor):
                    with self.assertRaises(ValueError):
                        validar_demanda(self.dados | {campo: valor})

    def test_data_status_e_limites(self):
        for alteracao in [
            {"data_solicitacao": "2026-02-30"},
            {"status": "Inválido"},
            {"titulo": "a" * 151},
            {"descricao": "a" * 5001},
            {"setor": "a" * 101},
        ]:
            with self.subTest(alteracao=alteracao):
                with self.assertRaises(ValueError):
                    validar_demanda(self.dados | alteracao)

    def test_cadastro_persistencia_consulta_e_filtro(self):
        resposta = self.requisicao(
            "POST",
            "/demandas",
            self.dados | {
                "token": TOKEN,
                "descricao": "ERRO no acesso",
                "prioridade": "Normal",
            },
        )
        self.assertTrue(resposta["status"].startswith("303"))
        self.assertEqual(banco.listar(self.db)[0]["prioridade"], "Alta")
        self.assertEqual(len(banco.listar(self.db, "Enfermagem", "Aberta")), 1)
        self.assertEqual(len(banco.listar(self.db, status="Concluída")), 0)
        nova_app = criar_app(self.db)
        self.assertIsNotNone(nova_app)
        self.assertEqual(len(banco.listar(self.db)), 1)
        self.assertIn("ERRO no acesso", self.requisicao()["corpo"])

    def test_invalido_nao_persiste(self):
        resposta = self.requisicao(
            "POST",
            "/demandas",
            self.dados | {"token": TOKEN, "titulo": " "},
        )
        self.assertTrue(resposta["status"].startswith("400"))
        self.assertEqual(len(banco.listar(self.db)), 0)

    def test_token_e_escape_html(self):
        self.assertTrue(
            self.requisicao("POST", "/demandas", self.dados)["status"].startswith("403")
        )
        self.requisicao(
            "POST",
            "/demandas",
            self.dados | {"token": TOKEN, "titulo": "<script>alert(1)</script>"},
        )
        corpo = self.requisicao()["corpo"]
        self.assertNotIn("<script>", corpo)
        self.assertIn("&lt;script&gt;", corpo)


if __name__ == "__main__":
    unittest.main()
