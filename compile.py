import subprocess
import os
import shutil
import time
from pathlib import Path
from tqdm import tqdm  # pip install tqdm

# --- CONFIGURAÇÕES DO PROJETO ---
DOCKER_IMAGE = "meu-latex-furg"
TEX_FILE_NAME = "main.tex"
BASE_NAME = Path(TEX_FILE_NAME).stem
USER_PROJECT_PATH = Path(r"D:\combiTex\text\Trabalho_Individual___qualé")

# Se o usuário esquecer de configurar o caminho
if str(USER_PROJECT_PATH) == r"D:\caminho\para\seu\projeto":
    raise RuntimeError(
        "ERRO: Você deve alterar a variável USER_PROJECT_PATH para o caminho real do seu projeto antes de executar o script."
    )

# Diretórios e variáveis auxiliares
PROJECT_DIR_CONTAINER = "/compilation"
TEX_FILE_CONTAINER = Path(PROJECT_DIR_CONTAINER) / TEX_FILE_NAME

# Comando base do Docker
DOCKER_RUN_BASE = [
    "docker", "run",
    "--rm",
    "-v", f"{USER_PROJECT_PATH.resolve().as_posix()}:{PROJECT_DIR_CONTAINER}",
    DOCKER_IMAGE,
]


# --- FUNÇÕES AUXILIARES ---

def print_color(msg, color="default"):
    """Imprime mensagens coloridas no terminal."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m",
    }
    code = colors.get(color, "")
    reset = colors["reset"]
    print(f"{code}{msg}{reset}")


def run_compilation_step(command_parts, step_name):
    """Executa um comando Docker no subprocess e verifica o código de retorno."""
    full_command = DOCKER_RUN_BASE + command_parts
    print_color(f"\n--- {step_name} ---", "blue")

    try:
        start_time = time.time()
        result = subprocess.run(
            full_command,
            check=True,
            capture_output=True,
            text=True
        )
        duration = time.time() - start_time

        # Exibe as últimas linhas do log
        stdout_lines = result.stdout.strip().splitlines()
        tail = "\n".join(stdout_lines[-5:]) if stdout_lines else "(sem saída)"
        print_color(f"✔ Sucesso em {duration:.2f}s. Últimas linhas:\n{tail}", "green")

    except subprocess.CalledProcessError as e:
        print_color(f"\n✖ ERRO FATAL DURANTE: {step_name}", "red")
        print_color("\nSaída (stdout):", "yellow")
        print(e.stdout or "(vazio)")
        print_color("\nLog de erro (stderr):", "yellow")
        print(e.stderr or "(vazio)")
        print(f"\nComando executado: {' '.join(full_command)}")
        raise


def clean_aux_files():
    """Remove arquivos temporários gerados pelo LaTeX."""
    extensions = [".aux", ".bbl", ".blg", ".log", ".out", ".toc", ".lof", ".lot"]
    removed = 0
    for ext in extensions:
        file_path = USER_PROJECT_PATH / f"{BASE_NAME}{ext}"
        if file_path.exists():
            file_path.unlink()
            removed += 1
    if removed:
        print_color(f"🧹 {removed} arquivos temporários removidos.", "yellow")


# --- FUNÇÃO PRINCIPAL ---

def compile_latex_document():
    """Gerencia a sequência de compilações LaTeX dentro do container Docker."""

    # Verificações iniciais
    if not USER_PROJECT_PATH.is_dir():
        print_color(f"ERRO: Diretório inexistente: {USER_PROJECT_PATH.as_posix()}", "red")
        return
    if not (USER_PROJECT_PATH / TEX_FILE_NAME).exists():
        print_color(f"ERRO: Arquivo '{TEX_FILE_NAME}' não encontrado.", "red")
        return

    steps = [
        ("PASSO 1/4: Compilação Inicial (pdflatex)",
         ['pdflatex', '-output-directory', PROJECT_DIR_CONTAINER, str(TEX_FILE_CONTAINER.as_posix())]),
        ("PASSO 2/4: Processamento da Bibliografia (bibtex)",
         ['bibtex', BASE_NAME]),
        ("PASSO 3/4: Compilação Final (pdflatex) - Rodada 1",
         ['pdflatex', '-output-directory', PROJECT_DIR_CONTAINER, str(TEX_FILE_CONTAINER.as_posix())]),
        ("PASSO 4/4: Compilação Final (pdflatex) - Rodada 2",
         ['pdflatex', '-output-directory', PROJECT_DIR_CONTAINER, str(TEX_FILE_CONTAINER.as_posix())]),
    ]

    print_color("==============================================", "blue")
    print_color("Iniciando processo de compilação LaTeX via Docker", "yellow")
    print_color("==============================================\n", "blue")

    start_total = time.time()

    try:
        for step_name, command in tqdm(steps, desc="Compilando etapas", ncols=80):
            run_compilation_step(command, step_name)
            time.sleep(0.5)  # pausa estética

        total_time = time.time() - start_total
        print_color("\n==============================================", "blue")
        print_color(f"✅ Compilação concluída em {total_time:.2f}s.", "green")

        final_pdf_path = USER_PROJECT_PATH / f"{BASE_NAME}.pdf"
        if final_pdf_path.exists():
            print_color(f"📄 PDF final disponível em: {final_pdf_path.as_posix()}", "green")
        else:
            print_color("⚠ AVISO: O PDF não foi encontrado após a compilação.", "yellow")

        clean_aux_files()

    except Exception as e:
        print_color(f"\n❌ O processo de compilação falhou: {e}", "red")

    finally:
        print_color("\nCompilação finalizada. Consulte os logs acima.", "blue")


# --- EXECUÇÃO ---

if __name__ == "__main__":
    try:
        subprocess.run(['docker', 'info'], check=True, capture_output=True)
    except Exception:
        print_color("ERRO: O Docker não está rodando ou não está acessível.", "red")
        print("Certifique-se de que o Docker Desktop ou o serviço Docker está ativo.")
        exit(1)

    compile_latex_document()
