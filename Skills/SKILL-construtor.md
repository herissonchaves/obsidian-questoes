---
name: construtor-referencia
description: >
  Referência de uso do script construtor.py — o extrator e segmentador de
  questões. Carregar quando precisar executar o script, interpretar o
  manifest.json, entender a estrutura dos JSONs granulares ou diagnosticar
  problemas de extração. Também usar quando o agente precisar decidir entre
  modos de operação (compacto vs compat).
---

# SKILL — Referência do `construtor.py`

## O que é

Script Python que extrai texto e imagens de documentos brutos (PDF, DOCX,
imagens) e os segmenta automaticamente em JSONs granulares por questão.
Projetado para minimizar o consumo de tokens do agente.

## Regras invioláveis

- **NUNCA recriar, sobrescrever ou excluir** `Input/construtor.py`
- Se o script não existir em `Input/`, avise o usuário e interrompa
- Sempre executar o script ANTES de tentar ler documentos brutos

## Execução

### Modo padrão (recomendado)

```bash
python3 Input/construtor.py -i Input -o Output --prefixo fis --inicio 47 --compacto
```

### Flags disponíveis

| Flag | Efeito |
|------|--------|
| `-i`, `--input` | Pasta de entrada (default: `Input`) |
| `-o`, `--output` | Pasta de saída (default: `Output`) |
| `--prefixo` | Prefixo dos IDs gerados (ex: `fis`, `qui`) |
| `--inicio` | Número inicial da sequência (ex: `47` → `fis047`) |
| `--compacto` | **Prioritário.** Manifest leve sem texto bruto |
| `--compat` | Gera `*_extraido.txt` legado. Usar apenas como fallback |
| `--debug` | Saída detalhada no console |

### Escolha do modo

- **Sempre usar `--compacto`** em operação normal
- Usar `--compat` **somente** se o PDF for completamente ilegível para a segmentação JSON
- Nunca combinar `--compacto` com `--compat`

## Estrutura de saída

```
Output/
├── manifest.json                  ← índice leve de navegação
├── questoes/
│   ├── {stem}_{id}.json           ← JSON granular por questão
│   └── ...
└── imagens/
    ├── {stem}_p{pag}_{n}.{ext}    ← imagens de PDF (com página)
    ├── {stem}_{n}.{ext}           ← imagens de DOCX
    └── {nome_original}.{ext}      ← imagens avulsas (recortadas)
```

## Esquema do `manifest.json`

```json
{
  "config": {
    "prefixo": "fis",
    "numero_inicial": 47,
    "modo": "compacto"
  },
  "arquivos": [
    {
      "arquivo_origem": "prova.pdf",
      "tipo_fonte": "pdf",
      "total_paginas": 4,
      "tem_ocr_local": true,
      "necessita_ocr_ia": false,
      "questoes_detectadas": 3,
      "status_extracao": "ok",
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

### Campos-chave do manifest

| Campo | Significado |
|-------|-------------|
| `necessita_ocr_ia` | `true` = texto extraído insuficiente, agente deve usar visão |
| `confianca_segmentacao` | `alta` = regex identificou número; `baixa` = questão genérica (q00) |
| `arquivo_detalhe` | Caminho relativo ao JSON granular da questão |
| `tem_ocr_local` | `true` = extração textual local foi bem-sucedida |
| `processamento_direto_vlm` | `true` = imagem avulsa, sem JSON granular (ver abaixo) |

### Imagens avulsas (processamento direto VLM)

Imagens soltas (PNG/JPG enviados pelo usuário) **não geram JSON granular**.
O manifest registra uma entrada leve:

```json
{
  "arquivo_origem": "foto_questao.png",
  "tipo_fonte": "imagem",
  "processamento_direto_vlm": true,
  "necessita_ocr_ia": true,
  "id_reservado": "fis047",
  "imagens": ["foto_questao.png"],
  "status_extracao": "ok"
}
```

O agente deve usar sua visão nativa diretamente sobre o arquivo em
`Output/imagens/` e montar a nota a partir do que "enxerga", sem procurar
JSON em `Output/questoes/`.

## Esquema do JSON granular (`questoes/*.json`)

```json
{
  "id_local": "fis047",
  "arquivo_origem": "prova.pdf",
  "numero_detectado": "1",
  "tipo_detectado": "objetiva",
  "enunciado": "Texto completo com marcadores [IMG:nome.png]",
  "alternativas": [
    {"letra": "A", "texto": "Texto da alternativa"}
  ],
  "imagens": [
    {"arquivo": "prova_p1_1.png", "pagina": 1, "caminho": "Output/imagens/prova_p1_1.png"}
  ],
  "marcadores_fluxo": "Encontrado fluxo normal",
  "confianca_segmentacao": "alta",
  "metadados_extraidos": {
    "banca": "ENEM",
    "ano": "2024",
    "disciplina": ""
  }
}
```

### Como interpretar os campos

| Campo | Significado para o agente |
|-------|--------------------------|
| `enunciado` | Texto principal. Pode conter `[IMG:nome.png]` indicando posição de figuras |
| `alternativas` | Lista vazia `[]` → questão discursiva |
| `imagens` | Lista vazia `[]` → sem figuras; NÃO inserir `![[...]]` na nota |
| `marcadores_fluxo` | `"Dependência visual do VLM"` → complementar com visão do agente |
| `metadados_extraidos` | Pré-extração via regex; pode estar vazio — não confiar cegamente |

## Padrões de numeração suportados

O detector reconhece os seguintes formatos de início de questão:

| Padrão | Exemplo |
|--------|---------|
| `Questão N` / `Questao N` / `Q N` | `Questão 3.`, `Questao 01`, `Q 7` |
| `N.` / `N)` / `N-` / `N:` + texto | `1. Um corpo...`, `03- Um bloco...`, `5) Calcule...` |
| `(BANCA)` + texto | `(UFRGS) Uma partícula...` |
| `(BANCA - ANO)` + texto | `(ENEM - 2024) Considere...` |

Zeros à esquerda são aceitos e removidos (`03` → `3`).
Linhas curtas após número (< 5 chars, sem banca) são ignoradas como sub-itens.

## Diagnóstico de problemas

| Sintoma | Causa provável | Ação |
|---------|---------------|------|
| `manifest.json` não gerado | Erro de dependência ou pasta inexistente | Verificar logs, instalar deps |
| Todas as questões com `q00` | Regex não reconheceu numeração | Verificar formato do PDF original |
| `necessita_ocr_ia: true` | PDF é scan/imagem sem texto | Usar visão do agente sobre o original |
| Imagens ausentes | Recorte descartou (< 120px altura) | Verificar original manualmente |
