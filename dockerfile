FROM texlive/texlive:latest
WORKDIR /compilation

# Copia o arquivo .cls para um local onde o TeX Live possa encontrá-lo
# A pasta correta pode variar, mas este é um local comum para pacotes locais.
COPY furgmpu.cls /usr/local/texlive/texmf-local/tex/latex/furgmpu/

# Atualiza o índice de arquivos do TeX Live
RUN texhash

CMD ["/bin/bash"]