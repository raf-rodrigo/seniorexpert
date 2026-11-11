"""Validação e regras de negócio das demandas."""

import re
from datetime import date

STATUS = ("Aberta", "Em andamento", "Concluída")
CAMPOS = ("titulo", "descricao", "data_solicitacao", "setor", "status")


def prioridade_automatica(descricao):
    """Considera palavras inteiras, sem distinguir maiúsculas e minúsculas."""
    return "Alta" if re.search(
        r"\b(urgente|erro)\b",
        descricao,
        re.IGNORECASE
    ) else "Normal"


def validar_demanda(dados):
    demanda = {campo: dados.get(campo, "").strip() for campo in CAMPOS}
    if any(not valor for valor in demanda.values()):
        raise ValueError("Preencha todos os campos obrigatórios.")
    try:
        data = date.fromisoformat(demanda["data_solicitacao"])
    except ValueError:
        raise ValueError("Informe uma data de solicitação válida.") from None
    demanda["data_solicitacao"] = data.isoformat()
    if demanda["status"] not in STATUS:
        raise ValueError("Selecione um status válido.")
    for campo, limite in (("titulo", 150), ("descricao", 5000), ("setor", 100)):
        if len(demanda[campo]) > limite:
            raise ValueError(f"O campo {campo} deve ter no máximo {limite} caracteres.")
    demanda["prioridade"] = prioridade_automatica(demanda["descricao"])
    return demanda
