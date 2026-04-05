#!/usr/bin/env python3
"""
construtor.py — Extrator universal e segmentador inteligente de questões.

Redesenhado para economia massiva de tokens:
- Converte grandes documentos brutos (PDF/DOCX) em um `manifest.json` leve.
- Segmenta automaticamente as questões em arquivos JSON granulares.
- Lida com Imagens (auto-recorte) e OCR Delegado (caso sejam apenas scans).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ── Dependências ──────────────────────────────────────────────────────────────

DEPS = {
    "fitz": "PyMuPDF",
    "docx": "python-docx",
    "PIL": "Pillow",
    "numpy": "numpy",
}

def garantir_dependencias():
    faltando = []
    for modulo, pacote in DEPS.items():
        try:
            if modulo == "PIL":
                import PIL
            else:
                __import__(modulo)
        except ImportError:
            faltando.append(pacote)
    if faltando:
        print(f"Instalando dependências: {', '.join(faltando)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *faltando])

garantir_dependencias()

import fitz  # PyMuPDF
from docx import Document

# ── Configuracoes ─────────────────────────────────────────────────────────────

EXT_PDF = {".pdf"}
EXT_DOCX = {".docx"}
EXT_IMG = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
EXT_TXT = {".txt", ".md", ".csv"}
IGNORAR = {"construtor.py", "manifest.json", ".ds_store", "thumbs.db", "__pycache__"}

# ── Segmentador Heurístico ────────────────────────────────────────────────────

class SegmentadorProvas:
    """Extrai fluxo de texto e agrupa em questões estruturadas."""
    
    # FIX: regex mais preciso para evitar falsos positivos
    # Grupo 1: "Questão 01" / "Q 1" — exige fim de linha ou seguido de parêntese/espaço de banca
    # Grupo 2: "1. " / "01) " — exige que o restante da linha tenha conteúdo substancial (>10 chars)
    REGEX_Q_FORMAL = re.compile(
        r'^(?:Questão|QUESTÃO|Q)\s+(0?[1-9]|[1-9][0-9])(?:[\.\-\)]|\s|$)',
        re.IGNORECASE
    )
    REGEX_Q_NUMERAL = re.compile(r'^([1-9][0-9]?)[\.\-\)]\s+(.+)')
    REGEX_ALT = re.compile(r'^([a-eA-E])[\)\]\.]\s+')
    
    # Regex para extração pre-metadados (ex: "(FUVEST - 2024)", "UERJ")
    REGEX_BANCA_ANO = re.compile(r'\(\s*([A-Z]{3,8})\s*(?:[-–]\s*(\d{4}))?\s*\)')

    # Comprimento mínimo do restante da linha para aceitar match numeral como questão
    MIN_CONTEUDO_QUESTAO = 10

    @classmethod
    def segmentar(cls, texto_completo: str, imagens: list) -> list:
        linhas = texto_completo.split('\n')
        questoes = []
        q_atual = None
        img_refs = {img["arquivo"]: img for img in imagens}
        
        for linha in linhas:
            linha_strip = linha.strip()
            if not linha_strip:
                if q_atual:
                    q_atual["enunciado_bruto"].append(linha)
                continue
            
            # Tentar match formal: "Questão 1", "Q 01"
            m_formal = cls.REGEX_Q_FORMAL.match(linha_strip)
            # Tentar match numeral: "1. Texto..." — só aceita se restante é substancial
            m_numeral = cls.REGEX_Q_NUMERAL.match(linha_strip)
            
            nova_questao = False
            numero = None
            
            if m_formal:
                nova_questao = True
                numero = m_formal.group(1).lstrip('0')
            elif m_numeral:
                restante = m_numeral.group(2).strip()
                # FIX: só aceita como questão nova se o restante tem conteúdo real
                # Evita "2. alternativa..." ser interpretado como questão
                if len(restante) >= cls.MIN_CONTEUDO_QUESTAO and not cls.REGEX_ALT.match(restante):
                    nova_questao = True
                    numero = m_numeral.group(1).lstrip('0')
            
            if nova_questao and numero:
                # Fechar questão anterior
                if q_atual:
                    questoes.append(cls._fechar_questao(q_atual, img_refs))
                    
                q_atual = {
                    "numero_detectado": numero,
                    "enunciado_bruto": [linha],
                    "alternativas": [],
                    "banca": "",
                    "ano": "",
                    "imagens_ref": [],
                    "em_alternativas": False
                }
                
                # Tentar extrair banca/ano logo na primeira linha
                m_banca = cls.REGEX_BANCA_ANO.search(linha_strip)
                if m_banca:
                    q_atual["banca"] = m_banca.group(1)
                    if m_banca.group(2):
                        q_atual["ano"] = m_banca.group(2)
                continue
                
            # Se não está em nenhuma questão ainda, fallback para q00
            if not q_atual:
                q_atual = {
                    "numero_detectado": "00",
                    "enunciado_bruto": [],
                    "alternativas": [],
                    "banca": "",
                    "ano": "",
                    "imagens_ref": [],
                    "em_alternativas": False
                }
                
            # Identificação de alternativas
            m_alt = cls.REGEX_ALT.match(linha_strip)
            if m_alt:
                q_atual["em_alternativas"] = True
                letra = m_alt.group(1).upper()
                q_atual["alternativas"].append({
                    "letra": letra,
                    "texto": linha_strip[m_alt.end():].strip()
                })
            else:
                if q_atual["em_alternativas"]:
                    # Se começou alternativas, tentar agrupar linhas extras à última alternativa
                    if q_atual["alternativas"]:
                        q_atual["alternativas"][-1]["texto"] += "\n" + linha_strip
                    else:
                        q_atual["enunciado_bruto"].append(linha)
                else:
                    q_atual["enunciado_bruto"].append(linha)
                    
        # Fechar a última
        if q_atual:
            questoes.append(cls._fechar_questao(q_atual, img_refs))
            
        return questoes

    @classmethod
    def _fechar_questao(cls, raw: dict, img_refs: dict) -> dict:
        enunciado_txt = "\n".join(raw["enunciado_bruto"]).strip()
        
        # Encontrar quais imagens foram usadas no enunciado/alternativas
        imgs_usadas = []
        for img_nome, img_data in img_refs.items():
            if f"[IMG:{img_nome}]" in enunciado_txt:
                imgs_usadas.append(img_data)
            else:
                for alt in raw["alternativas"]:
                    if f"[IMG:{img_nome}]" in alt["texto"]:
                        imgs_usadas.append(img_data)
                        break

        tipo = "objetiva" if len(raw["alternativas"]) >= 2 else "discursiva"
        
        return {
            "numero_detectado": raw["numero_detectado"],
            "tipo_detectado": tipo,
            "banca": raw["banca"],
            "ano": raw["ano"],
            "enunciado": enunciado_txt,
            "alternativas": raw["alternativas"],
            "imagens": imgs_usadas,
            "confianca_segmentacao": "alta" if raw["numero_detectado"] != "00" else "baixa",
        }

# ── Extração Imagem ───────────────────────────────────────────────────────────

def recortar_imagem(origem: Path, destino: Path) -> str:
    """Tenta recortar a imagem. Retorna 'recortada', 'copiada' ou 'falha'."""
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        shutil.copy2(str(origem), str(destino))
        return "copiada"

    try:
        img = Image.open(origem).convert("RGB")
        arr = np.array(img)
        bg_color = np.median(arr, axis=(0, 1))
        
        diff = np.linalg.norm(arr - bg_color, axis=2)
        active = diff > 20
        active_rows = np.any(active, axis=1)

        smoothed_active = np.copy(active_rows)
        for i in range(len(active_rows)):
            if not active_rows[i]:
                min_idx = max(0, i-15)
                max_idx = min(len(active_rows), i+15)
                if np.any(active_rows[min_idx:i]) and np.any(active_rows[i:max_idx]):
                    smoothed_active[i] = True

        in_block = False
        blocks = []
        start = 0
        for i, val in enumerate(smoothed_active):
            if val and not in_block:
                start = i
                in_block = True
            elif not val and in_block:
                blocks.append((start, i))
                in_block = False
        if in_block:
            blocks.append((start, len(smoothed_active)))

        if len(blocks) >= 1:
            max_block = max(blocks, key=lambda b: b[1] - b[0])
            height = max_block[1] - max_block[0]
            
            if height < 120:
                # Provavelmente apenas texto, sem diagrama visual relevante
                # FIX: ainda assim copia a imagem original como fallback
                shutil.copy2(str(origem), str(destino))
                return "copiada"

            fig_top = max(0, max_block[0] - 20)
            fig_bottom = min(arr.shape[0], max_block[1] + 20)

            slice_active = active[fig_top:fig_bottom, :]
            active_cols = np.any(slice_active, axis=0)
            if len(active_cols) > 0:
                col_indices = np.where(active_cols)[0]
                if len(col_indices) > 0:
                    fig_left = max(0, col_indices[0] - 20)
                    fig_right = min(arr.shape[1], col_indices[-1] + 20)
                else:
                    fig_left, fig_right = 0, arr.shape[1]
            else:
                 fig_left, fig_right = 0, arr.shape[1]

            cropped = img.crop((fig_left, fig_top, fig_right, fig_bottom))
            cropped.save(destino)
            return "recortada"
        else:
            # Nenhum bloco encontrado — copia original
            shutil.copy2(str(origem), str(destino))
            return "copiada"
    except Exception as e:
        print(f"  [Erro Oculto] Recorte falhou {origem.name}: {e}")
        # FIX: em caso de erro, copia o original em vez de descartar
        try:
            shutil.copy2(str(origem), str(destino))
            return "copiada"
        except Exception:
            return "falha"

# ── Motores Universais de Extração ────────────────────────────────────────────

def extrair_pdf(caminho: Path, dir_imgs: Path) -> dict:
    doc = fitz.open(str(caminho))
    paginas_texto = []
    imagens = []
    img_count = 0
    necessita_ocr = False
    total_texto_chars = 0

    for num_pag in range(len(doc)):
        page = doc.load_page(num_pag)
        
        # FIX: intercalar texto e imagens usando blocos ordenados geometricamente
        blocks = page.get_text("dict")["blocks"]
        # Ordenar por posição vertical (y0), depois horizontal (x0)
        blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
        
        partes_pagina = []
        
        for b in blocks:
            if b["type"] == 0:  # Bloco de texto
                linhas_bloco = []
                for line in b.get("lines", []):
                    spans_text = "".join(span["text"] for span in line.get("spans", []))
                    if spans_text.strip():
                        linhas_bloco.append(spans_text)
                if linhas_bloco:
                    texto_bloco = "\n".join(linhas_bloco)
                    partes_pagina.append(texto_bloco)
                    total_texto_chars += len(texto_bloco)
                    
            elif b["type"] == 1:  # Bloco de imagem
                # Imagem embutida no bloco — extrair via xref se disponível
                img_count += 1
                xref = b.get("image", None)
                if xref:
                    # Tentar extrair diretamente do bloco
                    pass  # Imagens de bloco nem sempre têm xref acessível
                    
        # Extrair imagens via get_images (mais confiável) e inserir marcadores
        # após o texto da página, mas antes da próxima página
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
            
            # FIX: inserir marcador de imagem intercalado com o texto
            partes_pagina.append(f"[IMG:{nome_img}]")
            imagens.append({
                "arquivo": nome_img,
                "pagina": num_pag + 1,
                "caminho": str(destino),
            })
            
        paginas_texto.append("\n".join(partes_pagina))

    doc.close()
    
    # FIX: decisão de OCR baseada em proporção texto/imagens
    if total_texto_chars < 50 and img_count > 0:
        necessita_ocr = True
    
    texto_total = "\n\n".join(paginas_texto)
    questoes = SegmentadorProvas.segmentar(texto_total, imagens)
    
    return {
        "tipo_fonte": "pdf",
        "total_paginas": len(paginas_texto),
        "necessita_ocr_ia": necessita_ocr,
        "texto_bruto": texto_total,
        "questoes": questoes,
        "imagens": imagens,
    }

def extrair_docx(caminho: Path, dir_imgs: Path) -> dict:
    from docx.oxml.ns import qn

    doc = Document(str(caminho))
    body = doc.element.body

    imagens = []
    img_count = 0
    partes_texto = []

    rel_map = {}
    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
            rel_map[rel.rId] = (rel.target_part.blob, rel.target_part.content_type)

    def _processar_paragrafo(para_elem):
        nonlocal img_count
        fragmentos = []
        for child in para_elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "r":
                drawings = child.findall(f".//{{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}}inline")
                if drawings:
                    for draw in drawings:
                        blip = draw.findall(f".//{{http://schemas.openxmlformats.org/drawingml/2006/main}}blip")
                        for b in blip:
                            embed = b.get(qn("r:embed"))
                            if embed and embed in rel_map:
                                blob, content_type = rel_map[embed]
                                img_count += 1
                                ext = content_type.split("/")[-1].replace("jpeg", "jpg")
                                nome_img = f"{caminho.stem}_{img_count}.{ext}"
                                destino = dir_imgs / nome_img
                                destino.write_bytes(blob)
                                imagens.append({
                                    "arquivo": nome_img,
                                    "pagina": None,
                                    "caminho": str(destino),
                                })
                                fragmentos.append(f"[IMG:{nome_img}]")
                else:
                    for t_elem in child.findall(qn("w:t")):
                        if t_elem.text:
                            fragmentos.append(t_elem.text)
        return "".join(fragmentos)

    for elem in body:
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if tag == "p":
            linha = _processar_paragrafo(elem)
            if linha.strip():
                partes_texto.append(linha)
        elif tag == "tbl":
            # Tabela simples
            for tr in elem.findall(qn("w:tr")):
                celulas = []
                for tc in tr.findall(qn("w:tc")):
                    t_parts = [_processar_paragrafo(p) for p in tc.findall(qn("w:p"))]
                    celulas.append(" ".join(t_parts).strip())
                partes_texto.append(" | ".join(celulas))

    texto_total = "\n\n".join(partes_texto)
    questoes = SegmentadorProvas.segmentar(texto_total, imagens)

    return {
        "tipo_fonte": "docx",
        "total_paginas": None,
        "necessita_ocr_ia": False,
        "texto_bruto": texto_total,
        "questoes": questoes,
        "imagens": imagens,
    }

def extrair_imagem(caminho: Path, dir_imgs: Path) -> dict:
    destino = dir_imgs / caminho.name
    
    # FIX: sempre inclui a imagem na lista, independente do resultado do recorte
    resultado = "falha"
    if caminho.resolve() != destino.resolve():
        resultado = recortar_imagem(caminho, destino)
    else:
        resultado = "copiada"  # já está no destino
        
    imagens_lista = []
    if resultado != "falha":
        imagens_lista.append({
            "arquivo": caminho.name,
            "pagina": None,
            "caminho": str(destino),
        })

    # Em imagens, dependemos do OCR delegado pelo VLM
    return {
        "tipo_fonte": "imagem",
        "total_paginas": None,
        "necessita_ocr_ia": True,
        "texto_bruto": f"Necessita OCR da IA.\n[IMAGEM: {caminho.name}]",
        "questoes": [{
            "numero_detectado": "00",
            "tipo_detectado": "incerto",
            "banca": "",
            "ano": "",
            "enunciado": f"Processamento via visão do agente LLM pendente. [IMG:{caminho.name}]" if imagens_lista else "Processamento de texto via agente.",
            "alternativas": [],
            "imagens": imagens_lista,
            "confianca_segmentacao": "baixa"
        }],
        "imagens": imagens_lista,
    }

def extrair_texto(caminho: Path) -> dict:
    texto = caminho.read_text(encoding="utf-8", errors="ignore")
    questoes = SegmentadorProvas.segmentar(texto, [])
    return {
        "tipo_fonte": "texto",
        "total_paginas": None,
        "necessita_ocr_ia": False,
        "texto_bruto": texto,
        "questoes": questoes,
        "imagens": [],
    }

# ── Workflow ──────────────────────────────────────────────────────────────────

def processar_arquivo(caminho: Path, dir_imgs: Path) -> dict | None:
    ext = caminho.suffix.lower()
    try:
        if ext in EXT_PDF: return extrair_pdf(caminho, dir_imgs)
        elif ext in EXT_DOCX: return extrair_docx(caminho, dir_imgs)
        elif ext in EXT_IMG: return extrair_imagem(caminho, dir_imgs)
        elif ext in EXT_TXT: return extrair_texto(caminho)
        else: return None
    except Exception as e:
        print(f"  ✗ Erro em {caminho.name}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser("Construtor de Questões Otimizado")
    parser.add_argument("-i", "--input", default="Input")
    parser.add_argument("-o", "--output", default="Output")
    parser.add_argument("--prefixo", default="q")
    parser.add_argument("--inicio", type=int, default=1)
    parser.add_argument("--compat", action="store_true", help="Gera os arquivos extraido.txt (Modo legado)")
    parser.add_argument("--compacto", action="store_true", help="Reduz radicalmente o manifest.json")
    parser.add_argument("--debug", action="store_true", help="Mostra saídas detalhadas.")
    args = parser.parse_args()

    dir_saida = Path(args.output)
    dir_imgs = dir_saida / "imagens"
    dir_questoes = dir_saida / "questoes"
    
    dir_imgs.mkdir(parents=True, exist_ok=True)
    dir_questoes.mkdir(parents=True, exist_ok=True)

    arquivos = [a for a in Path(args.input).iterdir() if a.is_file() and a.name.lower() not in IGNORAR]
    
    global_manifest = {
        "config": {"prefixo": args.prefixo, "numero_inicial": args.inicio, "modo": "compacto" if args.compacto else "padrao"},
        "arquivos": []
    }
    
    counter_global = args.inicio

    for arq in sorted(arquivos):
        print(f"→ Processando: {arq.name}")
        dados = processar_arquivo(arq, dir_imgs)
        if not dados: continue
        
        # FIX: tem_ocr reflete se houve extração textual significativa
        texto_extraido = dados.get("texto_bruto", "")
        tem_texto_util = len(texto_extraido.strip()) > 100
        
        # Manifest Level Data
        mini_manifest = {
            "arquivo_origem": arq.name,
            "tipo_fonte": dados["tipo_fonte"],
            "total_paginas": dados["total_paginas"],
            "tem_ocr": tem_texto_util,
            "necessita_ocr_ia": dados["necessita_ocr_ia"],
            "questoes_detectadas": len(dados["questoes"]),
            "status_extracao": "ok",
            "lista_questoes": []
        }
        
        # Salvar legado compat?
        if args.compat and not args.compacto:
            caminho_txt = dir_saida / f"{arq.stem}_extraido.txt"
            caminho_txt.write_text(dados["texto_bruto"], encoding="utf-8")
        
        for q in dados["questoes"]:
            id_gen = f"{args.prefixo}{counter_global:03d}"
            
            # Dados que vão pro manifesto leve
            mini_manifest["lista_questoes"].append({
                "id_local": id_gen,
                "numero_detectado": q["numero_detectado"],
                "tipo_detectado": q["tipo_detectado"],
                "confianca_segmentacao": q["confianca_segmentacao"],
                "arquivo_detalhe": f"questoes/{arq.stem}_{id_gen}.json"
            })
            
            # FIX: removido texto_bruto_curto redundante (enunciado já está presente)
            q_json = {
                "id_local": id_gen,
                "arquivo_origem": arq.name,
                "numero_detectado": q["numero_detectado"],
                "tipo_detectado": q["tipo_detectado"],
                "enunciado": q["enunciado"],
                "alternativas": q["alternativas"],
                "imagens": q["imagens"],
                "marcadores_fluxo": "Dependência visual do VLM" if dados["necessita_ocr_ia"] else "Encontrado fluxo normal",
                "confianca_segmentacao": q["confianca_segmentacao"],
                "metadados_extraidos": {
                    "banca": q.get("banca", ""),
                    "ano": q.get("ano", ""),
                    "disciplina": "" 
                }
            }
            
            caminho_q_json = dir_questoes / f"{arq.stem}_{id_gen}.json"
            caminho_q_json.write_text(json.dumps(q_json, ensure_ascii=False, indent=2), encoding="utf-8")
            counter_global += 1

        # Fallback text se não for modo compacto explícito
        if not args.compacto:
             mini_manifest["texto_bruto"] = dados["texto_bruto"][:1500] + "..."

        global_manifest["arquivos"].append(mini_manifest)
        if args.debug:
            print(f"  ✓ Gerou {len(dados['questoes'])} chunks granulares (JSON).")

    # Salvar Master Manifest
    (dir_saida / "manifest.json").write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nFinalizado! Custo preditivo de tokens drasticamente reduzido. IDs alocados até {counter_global - 1}.")

if __name__ == "__main__":
    main()
