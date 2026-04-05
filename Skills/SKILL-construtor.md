---
name: construtor-questoes
description: >
  Referência de uso do script construtor.py — extrator e segmentador de
  questões. Carregar sempre que for executar o construtor.py, interpretar
  seus outputs (manifest.json, JSONs granulares, imagens) ou diagnosticar
  erros de extração. Também usar ao decidir entre modo compacto e compat.
---

# SKILL — construtor.py

## Objetivo

O `construtor.py` é o núcleo de extração. Ele converte documentos brutos
(PDF, DOCX, imagens, texto) em JSONs estruturados prontos para o agente
montar as notas do Obsidian. **Deve ser executado ANTES de qualquer leitura
manual dos documentos.**

## Comando padrão

```bash
python3 Input/construtor.py -i Input -o Output --prefixo fis --inicio 47 --compacto
```

## Flags disponíveis

| Flag | Efeito |
|------|--------|
| `--compacto` | **Modo prioritário.** Manifest leve sem texto bruto embutido |
| `--compat` | Gera `*_extraido.txt` legado (fallback para PDFs ilegíveis) |
| `--debug` | Saídas detalhadas no console |

> **Regra:** use `--compacto` sempre. Use `--compat` apenas se a segmentação
> JSON falhar completamente no PDF.

## Estrutura de output

```
Output/
├── manifest.json                  ← índice leve
├── questoes/
│   ├── nomeoriginal_fis047.json   ← JSON granular por questão
│   └── nomeoriginal_fis048.json
└── imagens/
    ├── nomeoriginal_p1_1.png      ← nome técnico da extração
    └── nomeoriginal_2.png
```

## manifest.json — estrutura

```json
{
  "config": { "prefixo": "fis", "numero_inicial": 47, "modo": "compacto" },
  "arquivos": [
    {
      "arquivo_origem": "prova.pdf",
      "tipo_fonte": "pdf",
      "total_paginas": 4,
      "necessita_ocr_ia": false,
      "questoes_detectadas": 5,
      "lista_questoes": [
        {
          "id_local": "fis047",
          "numero_detectado": "1",
          "tipo_detectado": "objetiva",
          "confianca_segmentacao": "alta",
          "arquivo_detalhe": "questoes/prova_fis047.json"
        }
      ]
    }
  ]
}
```

**Campos-chave do manifest:**
- `necessita_ocr_ia`: se `true`, o texto extraído é insuficiente — ative visão
- `arquivo_detalhe`: caminho relativo ao JSON granular da questão
- `confianca_segmentacao`: `"alta"` (match de regex) ou `"baixa"` (fallback)

## JSON granular da questão — estrutura

```json
{
  "id_local": "fis047",
  "arquivo_origem": "prova.pdf",
  "numero_detectado": "1",
  "tipo_detectado": "objetiva",
  "enunciado": "Texto completo do enunciado com [IMG:nome.png] se houver",
  "alternativas": [
    { "letra": "A", "texto": "Texto da alternativa A" },
    { "letra": "B", "texto": "Texto da alternativa B" }
  ],
  "imagens": [
    { "arquivo": "prova_p1_1.png", "pagina": 1, "caminho": "Output/imagens/prova_p1_1.png" }
  ],
  "confianca_segmentacao": "alta",
  "metadados_extraidos": { "banca": "ENEM", "ano": "2024", "disciplina": "" }
}
```

**Campos-chave do JSON granular:**
- `enunciado`: texto principal — fonte oficial para o corpo da nota
- `alternativas`: lista vazia `[]` indica questão discursiva
- `imagens`: lista vazia `[]` indica ausência de figuras — **não insira** `![[...]]`
- `metadados_extraidos`: pré-extração heurística de banca/ano (pode estar vazio)

## Marcadores de imagem

O script insere `[IMG:nome.png]` no texto para indicar onde uma figura aparece.
Use esses marcadores como guia de posição ao inserir `![[01 - Sources/imagens/{id}.png]]`
na nota final. Se não houver marcador claro, use julgamento conservador.

## Diagnóstico de problemas

| Sintoma | Causa provável | Ação |
|---------|---------------|------|
| `manifest.json` não gerado | Erro de dependência ou path | Verificar log e reinstalar deps |
| `questoes_detectadas: 0` | Texto do PDF é pura imagem | Reexecutar com `--compat`; usar visão |
| `confianca_segmentacao: baixa` | Regex não encontrou padrão de questão | Revisar visualmente o documento |
| `necessita_ocr_ia: true` | Pouco texto extraído vs imagens | Ativar visão do agente no original |
