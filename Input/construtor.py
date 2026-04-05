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

# ── Detector de Início de Questão ─────────────────────────────────────────────

# Regex para alternativas (não confundir com questão)
RE_ALTERNATIVA = re.compile(r'^[a-eA-E][\)\]\.]\s+')

# Padrão 1: "Questão N" / "Questao N" / "Q N" (isolado ou com texto após)
RE_QUESTAO_N = re.compile(
    r'^(?:Quest[aã]o|Q)\s+(0*\d{1,2})(?:[\.\-\)\:\s]|$)',
    re.IGNORECASE
)

# Padrão 2: "N." / "N)" / "N-" / "N:" seguido de conteúdo
# Aceita zeros à esquerda: 01., 03-, etc.
RE_NUMERO_SEP = re.compile(r'^(0*\d{1,2})[\.\)\-\:]\s+(.*)')

# Padrão 3: "(BANCA)" ou "(BANCA - ANO)" no início da linha (sem número)
RE_BANCA_INICIO = re.compile(r'^\(([A-Z]{2,10})\s*(?:[-–/]\s*(\d{4}))?\)\s*(.*)')

# Regex auxiliar para detectar marcador de banca em qualquer posição
RE_BANCA_ANO = re.compile(r'\(\s*([A-Z]{3,8})\s*(?:[-–]\s*(\d{4}))?\s*\)')


def detectar_inicio_questao(linha: str):
    """
    Testa se uma linha marca o início de uma nova questão.
    
    Retorna (numero, banca, ano) ou None.
    Prioridade: Questão N > N. texto > (BANCA) texto
    """
    linha_strip = linha.strip()
    if not linha_strip:
        return None
    
    # Rejeitar alternativas logo de cara
    if RE_ALTERNATIVA.match(linha_strip):
        return None
    
    # Padrão 1: "Questão 3", "Questao 03", "Q 1"
    m = RE_QUESTAO_N.match(linha_strip)
    if m:
        numero = m.group(1).lstrip('0') or '0'
        return (numero, '', '')
    
    # Padrão 2: "03- Texto...", "4. (UFRGS) Texto...", "1) Considere..."
    m = RE_NUMERO_SEP.match(linha_strip)
    if m:
        numero = m.group(1).lstrip('0') or '0'
        resto = m.group(2).strip()
        
        # Validação anti-falso-positivo:
        # Aceitar se: tem marcador de banca, OU texto >= 5 chars
        # Rejeitar se: texto muito curto e sem banca (provavelmente sub-item)
        tem_banca = bool(RE_BANCA_ANO.search(resto))
        if tem_banca or len(resto) >= 5:
            return (numero, '', '')
        # Texto curto sem banca — provavelmente sub-item, ignorar
        return None
    
    # Padrão 3: "(UFRGS) Texto...", "(ENEM - 2024) Considere..."
    m = RE_BANCA_INICIO.match(linha_strip)
    if m:
        banca = m.group(1)
        ano = m.group(2) or ''
        resto = m.group(3).strip()
        # Só aceitar se tem texto após a banca (não é um cabeçalho isolado)
        if len(resto) >= 3:
            return ('00', banca, ano)
    
    return None


# ── Segmentador Heurístico ────────────────────────────────────────────────────

class SegmentadorProvas:
    """Extrai fluxo de texto e agrupa em questões estruturadas."""

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
            
            # Tentar detectar início de nova questão
            resultado = detectar_inicio_questao(linha_strip)
            if resultado:
                numero, banca, ano = resultado
                
                # Fechar questão anterior
                if q_atual:
                    questoes.append(cls._fechar_questao(q_atual, img_refs))
                
                q_atual = {
                    "numero_detectado": numero,
                    "enunciado_bruto": [linha],
                    "alternativas": [],
                    "banca": banca,
                    "ano": ano,
                    "imagens_ref": [],
                    "em_alternativas": False
                }
                
                # Se não veio banca do detector, tentar extrair da linha
                if not banca:
                    m_banca = RE_BANCA_ANO.search(linha_strip)
                    if m_banca:
                        q_atual["banca"] = m_banca.group(1)
                        if m_banca.group(2):
                            q_atual["ano"] = m_banca.group(2)
                continue
                
            # Se não está em nenhuma questão ainda, criar fallback q00
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
            m_alt = RE_ALTERNATIVA.match(linha_strip)
            if m_alt:
                q_atual["em_alternativas"] = True
                letra = m_alt.group(1).upper()
                q_atual["alternativas"].append({
                    "letra": letra,
                    "texto": linha_strip[m_alt.end():].strip()
                })
            else:
                if q_atual["em_alternativas"]:
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
    """Tenta recortar a imagem. Retorna 'recortada', 'copiada' ou 'falhou'."""
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
            shutil.copy2(str(origem), str(destino))
            return "copiada"
    except Exception as e:
        print(f"  [Erro Oculto] Recorte falhou {origem.name}: {e}")
        try:
            shutil.copy2(str(origem), str(destino))
            return "copiada"
        except Exception:
            return "falhou"

# ── Motores Universais de Extração ────────────────────────────────────────────

def extrair_pdf(caminho: Path, dir_imgs: Path) -> dict:
    doc = fitz.open(str(caminho))
    paginas_texto = []
    imagens = []
    img_count = 0
    texto_total_len = 0

    for num_pag in range(len(doc)):
        page = doc.load_page(num_pag)
        
        # Blocos ordenados por Y para intercalar texto e imagens
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[1], b[0]))
        
        # Extrair imagens da página
        img_list = page.get_images(full=True)
        page_images_extracted = []
        for img_info in img_list:
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
            
            imagens.append({
                "arquivo": nome_img,
                "pagina": num_pag + 1,
                "caminho": str(destino),
            })
            page_images_extracted.append(nome_img)
        
        # Reconstruir texto com imagens intercaladas via posição geométrica
        if page_images_extracted:
            texto_blocks = [(b[1], "text", b[4]) for b in blocks if b[6] == 0]
            img_block_positions = [(b[1], "img", None) for b in blocks if b[6] == 1]
            
            # Associar imagens extraídas aos blocos de imagem por ordem
            for i, (y, tipo, _) in enumerate(img_block_positions):
                if i < len(page_images_extracted):
                    img_block_positions[i] = (y, "img", page_images_extracted[i])
            
            all_elements = texto_blocks + [p for p in img_block_positions if p[2]]
            all_elements.sort(key=lambda e: e[0])
            
            texto_pag = ""
            for _, tipo, conteudo in all_elements:
                if tipo == "text":
                    texto_pag += conteudo + "\n"
                else:
                    texto_pag += f"\n[IMG:{conteudo}]\n"
        else:
            texto_pag = ""
            for b in blocks:
                if b[6] == 0:
                    texto_pag += b[4] + "\n"
        
        texto_total_len += len(texto_pag.strip())
        paginas_texto.append(texto_pag)

    doc.close()
    texto_total = "\n\n".join(paginas_texto)
    questoes = SegmentadorProvas.segmentar(texto_total, imagens)
    
    tem_texto_suficiente = texto_total_len > 100
    necessita_ocr = not tem_texto_suficiente and img_count > 0

    return {
        "tipo_fonte": "pdf",
        "total_paginas": len(paginas_texto),
        "tem_ocr_local": tem_texto_suficiente,
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
        "tem_ocr_local": len(texto_total.strip()) > 100,
        "necessita_ocr_ia": False,
        "texto_bruto": texto_total,
        "questoes": questoes,
        "imagens": imagens,
    }

def extrair_imagem(caminho: Path, dir_imgs: Path) -> dict:
    """Imagens avulsas: copiar/recortar e marcar para processamento direto VLM."""
    destino = dir_imgs / caminho.name
    if caminho.resolve() != destino.resolve():
        recortar_imagem(caminho, destino)

    imagem_existe = destino.exists()

    # Imagens avulsas não geram JSON granular — vão direto pro VLM
    return {
        "tipo_fonte": "imagem",
        "total_paginas": None,
        "tem_ocr_local": False,
        "necessita_ocr_ia": True,
        "processamento_direto_vlm": True,
        "texto_bruto": "",
        "questoes": [],
        "imagens": [{
            "arquivo": caminho.name,
            "pagina": None,
            "caminho": str(destino),
        }] if imagem_existe else [],
    }

def extrair_texto(caminho: Path) -> dict:
    texto = caminho.read_text(encoding="utf-8", errors="ignore")
    questoes = SegmentadorProvas.segmentar(texto, [])
    return {
        "tipo_fonte": "texto",
        "total_paginas": None,
        "tem_ocr_local": True,
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
        
        # Imagens avulsas: entrada leve no manifest, sem JSON granular
        if dados.get("processamento_direto_vlm"):
            id_gen = f"{args.prefixo}{counter_global:03d}"
            global_manifest["arquivos"].append({
                "arquivo_origem": arq.name,
                "tipo_fonte": "imagem",
                "processamento_direto_vlm": True,
                "necessita_ocr_ia": True,
                "id_reservado": id_gen,
                "imagens": [img["arquivo"] for img in dados["imagens"]],
                "status_extracao": "ok",
            })
            counter_global += 1
            if args.debug:
                print(f"  ✓ Imagem avulsa → VLM direto (ID reservado: {id_gen})")
            continue
        
        mini_manifest = {
            "arquivo_origem": arq.name,
            "tipo_fonte": dados["tipo_fonte"],
            "total_paginas": dados["total_paginas"],
            "tem_ocr_local": dados["tem_ocr_local"],
            "necessita_ocr_ia": dados["necessita_ocr_ia"],
            "questoes_detectadas": len(dados["questoes"]),
            "status_extracao": "ok",
            "lista_questoes": []
        }
        
        if args.compat and not args.compacto:
            caminho_txt = dir_saida / f"{arq.stem}_extraido.txt"
            caminho_txt.write_text(dados["texto_bruto"], encoding="utf-8")
        
        for q in dados["questoes"]:
            id_gen = f"{args.prefixo}{counter_global:03d}"
            
            mini_manifest["lista_questoes"].append({
                "id_local": id_gen,
                "numero_detectado": q["numero_detectado"],
                "tipo_detectado": q["tipo_detectado"],
                "confianca_segmentacao": q["confianca_segmentacao"],
                "arquivo_detalhe": f"questoes/{arq.stem}_{id_gen}.json"
            })
            
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

        if not args.compacto:
             mini_manifest["texto_bruto"] = dados["texto_bruto"][:1500] + "..."

        global_manifest["arquivos"].append(mini_manifest)
        if args.debug:
            print(f"  ✓ Gerou {len(dados['questoes'])} chunks granulares (JSON).")

    # Salvar Master Manifest
    (dir_saida / "manifest.json").write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nFinalizado! IDs alocados até {counter_global - 1}.")

if __name__ == "__main__":
    main()
