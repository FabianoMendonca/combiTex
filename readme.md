# 🧱 Projeto: Compilação de LaTeX via Docker com Python

Este projeto permite compilar documentos **LaTeX** de forma totalmente isolada, dentro de um **container Docker**, garantindo que todas as dependências estejam corretas e o ambiente seja reprodutível.

---

## 📁 Estrutura do projeto

```
combiTex/
│
├── Dockerfile
├── furgmpu.cls
├── compile_latex_docker.py
└── text/
    ├── main.tex
    ├── refs.bib
    └── ...
```

---

## 🚀 1. Construir a imagem Docker

A imagem é baseada no [`texlive/texlive`](https://hub.docker.com/r/texlive/texlive), e adiciona o arquivo de classe `furgmpu.cls`.

### 🔧 Dockerfile

```Dockerfile
FROM texlive/texlive:latest
WORKDIR /compilation

# Copia o arquivo .cls para o diretório de pacotes locais do TeX Live
COPY furgmpu.cls /usr/local/texlive/texmf-local/tex/latex/furgmpu/

# Atualiza o índice do TeX Live para reconhecer a nova classe
RUN texhash

CMD ["/bin/bash"]
```

### 🏗️ Construir a imagem

No diretório onde está o `Dockerfile`, execute:

```bash
docker build -t meu-latex-furg .
```

Isso criará a imagem **meu-latex-furg**, usada pelo script Python.

Verifique se foi criada com sucesso:

```bash
docker images
```

---

## 🐍 2. Configurar o script Python Escolhendo a versão do Python para o ambiente virtual

Por padrão, o comando `python -m venv .venv` usa a **versão padrão** do Python configurada no sistema.  
Mas é possível escolher **explicitamente** qual versão será usada, se você tiver várias instaladas.

```bash
Versão recomendada: Python 3.11.4
```
---

### 🪟 **No Windows**

Se você possui mais de uma versão (por exemplo, Python 3.10 e 3.12), use o *Python Launcher* (`py`) para especificar:

```bash
# Cria o ambiente com Python 3.10
py -3.10 -m venv .venv
```
### Ativar o ambiente:

Windows (PowerShell):
```bash
.\.venv\Scripts\Activate
```

Windows (CMD):
```bash
.venv\Scripts\activate.bat
```

Linux / macOS:
```bash
source .venv/bin/activate
```

 Quando o ambiente estiver ativo, o terminal mostrará algo como: 
```bash
(.venv) D:\combiTex>
```
Atualizar o pip:
```bash
pip install --upgrade pip
```

Depois, instale tudo com:

```bash
pip install -r requirements.txt
```


O arquivo principal é **`compile_latex_docker.py`**, responsável por:

- Invocar o container Docker
- Rodar `pdflatex → bibtex → pdflatex → pdflatex`
- Exibir barra de progresso e tempo total
- Limpar arquivos temporários

### 🧩 Configuração principal

Edite no topo do script:

```python
DOCKER_IMAGE = "meu-latex-furg"
USER_PROJECT_PATH = Path(r"D:\combiTex\text")
TEX_FILE_NAME = "main.tex"
```

Certifique-se de apontar `USER_PROJECT_PATH` para o diretório onde está o seu arquivo `.tex`.

---

## ▶️ 3. Executar a compilação

Com o Docker rodando, execute:

```bash
python compile_latex_docker.py
```

O script:

1. Verifica se o Docker está acessível  
2. Monta a pasta local dentro do container (`/compilation`)  
3. Executa a sequência de compilações (`pdflatex → bibtex → pdflatex x2`)  
4. Mostra uma **barra de progresso colorida**  
5. Exibe o caminho final do PDF compilado  

Exemplo de saída:

```
==============================================
Iniciando processo de compilação LaTeX via Docker
==============================================

Compilando etapas: 100%|████████████████████████████████| 4/4
✅ Compilação concluída em 12.83s.
📄 PDF final disponível em: D:/combiTex/text/main.pdf
🧹 6 arquivos temporários removidos.
```

---

## ⚙️ 4. Personalizações úteis

### ➕ Ativar `--shell-escape`

Se o seu projeto usa pacotes como `minted` (que executam Python/Pygments), adicione:

```python
'--shell-escape'
```
nos comandos `pdflatex` dentro do script.

---

### 🧽 Desativar limpeza automática

Para manter os arquivos auxiliares (`.aux`, `.log`, `.bbl`, etc.), comente a linha:

```python
clean_aux_files()
```

---

### 🧾 Gerar logs completos

Para salvar logs da compilação em arquivo:

```python
with open("latex_build.log", "a", encoding="utf-8") as log:
    log.write(result.stdout)
```
coloque isso dentro da função `run_compilation_step()` após a execução do `subprocess`.

---

## 🧩 5. Depuração

### Verificar se o Docker está ativo:
```bash
docker info
```

### Acessar o container manualmente:
```bash
docker run -it --rm -v D:/combiTex/text:/compilation meu-latex-furg /bin/bash
```
Dentro do container, você pode testar comandos manualmente:
```bash
pdflatex main.tex
bibtex main
```

---
