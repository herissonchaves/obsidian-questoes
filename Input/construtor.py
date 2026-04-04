#!/usr/bin/env python3
"""
construtor.py — Extrator universal para o workflow de questões do Obsidian.

Lê todos os arquivos de Input/ (PDF, DOCX, imagens, TXT), extrai texto e
imagens, e gera um manifesto JSON estruturado que o agente Antigravity
consome para criar as notas .md.

Uso:
    python construtor.py                          # processa Input/, saída em Output/
    python construtor.py -i minha_pasta            # pasta de entrada customizada
    python construtor.py -i Input -o Resultado     # pastas customizadas
    python construtor.py --arquivo prova.pdf       # processa um único arquivo
    python construtor.py --prefixo fis --inicio 47 # pré-configura prefixo e número
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ── Dependências ──────────────────────────────────────────────────────────────

DEPS = {
    "fitz": "PyMuPDF",
    "docx": "python-docx",
}


def garantir_dependencias():
    """Instala dependências faltantes uma única vez."""
    faltando = []
    for modulo, pacote in DEPS.items():
        try:
            __import__(modulo)
        except ImportError:
            faltando.append(pacote)
    if faltando:
        print(f"Instalando dependências: {', '.join(faltando)}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", *faltando]
        )


garantir_dependencias()

import fitz  # PyMuPDF  # noqa: E402
from docx import Document  # noqa: E402

# ── Extensões suportadas ──────────────────────────────────────────────────────

EXT_PDF = {".pdf"}
EXT_DOCX = {".docx"}
EXT_IMG = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
EXT_TXT = {".txt", ".md", ".csv"}
IGNORAR = {"construtor.py", "manifest.json", ".ds_store", "thumbs.db", "__pycache__"}

# ── Extratores ────────────────────────────────────────────────────────────────


def extrair_pdf(caminho: Path, dir_imgs: Path) -> dict:
    """Extrai texto e imagens de um PDF."""
    doc = fitz.open(str(caminho))
    paginas = []
    imagens = []
    img_count = 0

    for num_pag in range(len(doc)):
        page = doc.load_page(num_pag)
        paginas.append(page.get_text())

        for img_info in page.get_images(full=True):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue
            img_bytes = base_image["image"]
            ext = base_image.get("ext", "png")
            img_count += 1
            nome_img = f"{caminho.stem}_p{num_pag + 1}_{img_count}.{ext}"
            destino = dir_imgs / nome_img
            destino.write_bytes(img_bytes)
            imagens.append(
                {
                    "arquivo": nome_img,
                    "pagina": num_pag + 1,
                    "caminho": str(destino),
                }
            )

    doc.close()
    return {
        "tipo_fonte": "pdf",
        "total_paginas": len(paginas),
        "texto": "\n\n--- PAGE BREAK ---\n\n".join(paginas),
        "imagens": imagens,
    }


def extrair_docx(caminho: Path, dir_imgs: Path) -> dict:
    """Extrai texto e imagens de um DOCX."""
    doc = Document(str(caminho))
    paragrafos = [p.text for p in doc.paragraphs if p.text.strip()]

    imagens = []
    img_count = 0
    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
            img_count += 1
            blob = rel.target_part.blob
            content_type = rel.target_part.content_type
            ext = content_type.split("/")[-1].replace("jpeg", "jpg")
            nome_img = f"{caminho.stem}_{img_count}.{ext}"
            destino = dir_imgs / nome_img
            destino.write_bytes(blob)
            imagens.append(
                {
                    "arquivo": nome_img,
                    "pagina": None,
                    "caminho": str(destino),
                }
            )

    # Tabelas
    tabelas_texto = []
    for i, table in enumerate(doc.tables):
        linhas = []
        for row in table.rows:
            celulas = [cell.text.strip() for cell in row.cells]
            linhas.append(" | ".join(celulas))
        tabelas_texto.append(f"[TABELA {i + 1}]\n" + "\n".join(linhas))

    texto_final = "\n\n".join(paragrafos)
    if tabelas_texto:
        texto_final += "\n\n" + "\n\n".join(tabelas_texto)

    return {
        "tipo_fonte": "docx",
        "total_paginas": None,
        "texto": texto_final,
        "imagens": imagens,
    }


def extrair_imagem(caminho: Path, dir_imgs: Path) -> dict:
    """Copia uma imagem para a pasta de imagens."""
    destino = dir_imgs / caminho.name
    if caminho.resolve() != destino.resolve():
        shutil.copy2(str(caminho), str(destino))
    return {
        "tipo_fonte": "imagem",
        "total_paginas": None,
        "texto": f"[IMAGEM: {caminho.name}]",
        "imagens": [
            {
                "arquivo": caminho.name,
                "pagina": None,
                "caminho": str(destino),
            }
        ],
    }


def extrair_texto(caminho: Path) -> dict:
    """Lê um arquivo de texto puro."""
    texto = caminho.read_text(encoding="utf-8", errors="ignore")
    return {
        "tipo_fonte": "texto",
        "total_paginas": None,
        "texto": texto,
        "imagens": [],
    }


# ── Processamento em lote ─────────────────────────────────────────────────────


def listar_arquivos(pasta: Path) -> list[Path]:
    """Lista arquivos válidos da pasta, ignorando arquivos internos."""
    arquivos = []
    for item in sorted(pasta.iterdir()):
        if item.is_file() and item.name.lower() not in IGNORAR:
            arquivos.append(item)
    return arquivos


def processar_arquivo(caminho: Path, dir_imgs: Path) -> dict | None:
    """Processa um único arquivo e retorna os dados extraídos."""
    ext = caminho.suffix.lower()
    try:
        if ext in EXT_PDF:
            return extrair_pdf(caminho, dir_imgs)
        elif ext in EXT_DOCX:
            return extrair_docx(caminho, dir_imgs)
        elif ext in EXT_IMG:
            return extrair_imagem(caminho, dir_imgs)
        elif ext in EXT_TXT:
            return extrair_texto(caminho)
        else:
            print(f"  ⚠ Formato não suportado: {caminho.name}")
            return None
    except Exception as e:
        print(f"  ✗ Erro ao processar {caminho.name}: {e}")
        return None


def processar_lote(dir_entrada: Path, dir_saida: Path, prefixo: str, inicio: int):
    """Processa todos os arquivos de entrada e gera o manifesto."""
    dir_imgs = dir_saida / "imagens"
    dir_imgs.mkdir(parents=True, exist_ok=True)
    dir_saida.mkdir(parents=True, exist_ok=True)

    arquivos = listar_arquivos(dir_entrada)
    if not arquivos:
        print(f"Nenhum arquivo encontrado em {dir_entrada}/")
        return

    print(f"Encontrados {len(arquivos)} arquivo(s) em {dir_entrada}/\n")

    manifesto = {
        "config": {
            "prefixo": prefixo,
            "numero_inicial": inicio,
            "dir_entrada": str(dir_entrada),
            "dir_saida": str(dir_saida),
        },
        "arquivos": [],
    }

    for arq in arquivos:
        print(f"  → {arq.name}")
        dados = processar_arquivo(arq, dir_imgs)
        if dados:
            dados["arquivo_origem"] = arq.name
            manifesto["arquivos"].append(dados)
            n_imgs = len(dados.get("imagens", []))
            print(f"    ✓ {dados['tipo_fonte']} | {n_imgs} imagem(ns)")

    # Salvar texto extraído por arquivo (facilita leitura pelo agente)
    for item in manifesto["arquivos"]:
        nome_txt = Path(item["arquivo_origem"]).stem + "_extraido.txt"
        caminho_txt = dir_saida / nome_txt
        caminho_txt.write_text(item["texto"], encoding="utf-8")
        item["arquivo_texto"] = str(caminho_txt)

    # Salvar manifesto
    caminho_manifest = dir_saida / "manifest.json"
    caminho_manifest.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\n{'=' * 50}")
    print(f"Extração concluída!")
    print(f"  Arquivos processados: {len(manifesto['arquivos'])}")
    total_imgs = sum(len(a.get("imagens", [])) for a in manifesto["arquivos"])
    print(f"  Imagens extraídas:    {total_imgs}")
    print(f"  Manifesto salvo em:   {caminho_manifest}")
    print(f"  Textos salvos em:     {dir_saida}/")
    print(f"  Imagens salvas em:    {dir_imgs}/")
    print(f"{'=' * 50}")


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Extrator universal de questões para o workflow Obsidian.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python construtor.py                              # Input/ → Output/
  python construtor.py -i provas -o resultado       # pastas customizadas
  python construtor.py --arquivo prova.pdf           # arquivo único
  python construtor.py --prefixo fis --inicio 47    # define prefixo e número
        """,
    )
    parser.add_argument(
        "-i", "--input", default="Input", help="Pasta de entrada (padrão: Input)"
    )
    parser.add_argument(
        "-o", "--output", default="Output", help="Pasta de saída (padrão: Output)"
    )
    parser.add_argument(
        "--arquivo", help="Processar um único arquivo em vez de toda a pasta"
    )
    parser.add_argument(
        "--prefixo", default="q", help="Prefixo para os IDs das notas (padrão: q)"
    )
    parser.add_argument(
        "--inicio", type=int, default=1, help="Número inicial para os IDs (padrão: 1)"
    )

    args = parser.parse_args()

    dir_saida = Path(args.output)

    if args.arquivo:
        arq = Path(args.arquivo)
        if not arq.exists():
            print(f"Arquivo não encontrado: {arq}")
            sys.exit(1)
        dir_imgs = dir_saida / "imagens"
        dir_imgs.mkdir(parents=True, exist_ok=True)
        dir_saida.mkdir(parents=True, exist_ok=True)
        print(f"Processando arquivo único: {arq.name}\n")
        dados = processar_arquivo(arq, dir_imgs)
        if dados:
            dados["arquivo_origem"] = arq.name
            nome_txt = arq.stem + "_extraido.txt"
            caminho_txt = dir_saida / nome_txt
            caminho_txt.write_text(dados["texto"], encoding="utf-8")
            dados["arquivo_texto"] = str(caminho_txt)
            manifesto = {
                "config": {
                    "prefixo": args.prefixo,
                    "numero_inicial": args.inicio,
                    "dir_entrada": str(arq.parent),
                    "dir_saida": str(dir_saida),
                },
                "arquivos": [dados],
            }
            caminho_manifest = dir_saida / "manifest.json"
            caminho_manifest.write_text(
                json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"\n✓ Texto salvo em: {caminho_txt}")
            print(f"✓ Manifesto salvo em: {caminho_manifest}")
    else:
        dir_entrada = Path(args.input)
        if not dir_entrada.exists():
            print(f"Pasta de entrada não encontrada: {dir_entrada}")
            sys.exit(1)
        processar_lote(dir_entrada, dir_saida, args.prefixo, args.inicio)


if __name__ == "__main__":
    main()
