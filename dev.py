"""Reinicia o servidor local quando arquivos Python do projeto são alterados."""

import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent


def estado_arquivos(pasta):
    return {
        arquivo: arquivo.read_bytes()
        for arquivo in pasta.glob("*.py")
        if arquivo.is_file()
    }


def encerrar(processo):
    if processo.poll() is None:
        processo.terminate()
        try:
            processo.wait(timeout=5)
        except subprocess.TimeoutExpired:
            processo.kill()
            processo.wait()


def executar(pasta=BASE):
    estado = estado_arquivos(pasta)
    processo = None
    try:
        print(
            "Modo de desenvolvimento: salve um arquivo Python para reiniciar. "
            "Atualize o navegador para visualizar. Ctrl+C para encerrar.",
            flush=True,
        )
        processo = subprocess.Popen([sys.executable, str(pasta / "app.py")], cwd=pasta)
        while True:
            time.sleep(0.5)
            novo_estado = estado_arquivos(pasta)
            if novo_estado != estado:
                # Aguarda o editor terminar de salvar antes de reiniciar.
                time.sleep(0.3)
                estado = estado_arquivos(pasta)
                encerrar(processo)
                print("Alteração detectada. Reiniciando a aplicação...", flush=True)
                processo = subprocess.Popen(
                    [sys.executable, str(pasta / "app.py")],
                    cwd=pasta,
                )
    except KeyboardInterrupt:
        print("\nServidor de desenvolvimento encerrado.", flush=True)
    finally:
        if processo is not None:
            encerrar(processo)


if __name__ == "__main__":
    executar()
