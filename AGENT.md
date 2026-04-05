---
name: obsidian-questoes
description: >
  Converte questões de vestibular (PDFs, imagens, Word) em notas estruturadas
  do Obsidian. Use esta skill quando o usuário enviar arquivos de questões e
  pedir para converter, processar ou gerar notas .md. Também ative quando o
  usuário mencionar "banco de questões", "converter questões", "gerar notas"
  ou qualquer variação de processamento de questões para Obsidian.
---

# Agente — Conversor de Questões para Obsidian

## Papel do agente

Ler arquivos de questões de vestibular da pasta `Input/` e gerar notas `.md`
estruturadas na pasta `Output/`, seguindo as regras de formatação e schema de
metadados definidos nas Skills do repositório.

## Entradas esperadas

- PDFs, imagens (JPG/PNG) ou documentos Word com questões de vestibulares
- Prefixo e número inicial informados pelo usuário (ex: `fis047`)
- Disciplina informada pelo usuário (ex: `Fisica`, `Quimica`)

## Regras globais invioláveis

1. **NUNCA recriar, sobrescrever ou excluir** `Input/construtor.py`.
2. **NUNCA adivinhar texto ou imagens** — use os JSONs gerados pelo script.
3. Se `construtor.py` não existir em `Input/`, avise o usuário e interrompa.

## Cadeia de prioridade de fontes

Ao montar qualquer campo da nota, siga esta ordem rigorosa:

1. `Output/questoes/*.json` — fonte principal e oficial
2. `Output/manifest.json` — verificação de OCR e visão geral
3. Visão direta do agente sobre o arquivo original — se `necessita_ocr_ia = true`
4. `*_extraido.txt` — fallback legado apenas em modo `--compat`
5. Pesquisa externa — apenas para `banca`, `ano`, `gabarito` ausentes

## Regra de ouro — Rigidez factual

Em NENHUM cenário invente, divague ou assuma `banca`, `ano` ou `gabarito`.
Se a busca falhar ou o texto for incerto, deixe vazio e comunique explicitamente.

## Estrutura de pastas

```
Input/              ← arquivos do usuário + construtor.py
Output/
├── manifest.json
├── questoes/       ← JSONs granulares por questão
└── imagens/        ← figuras extraídas
Skills/             ← skills de referência do projeto
```

## Workflow resumido

1. **Coletar configuração** — prefixo, número inicial, disciplina
2. **Executar `construtor.py`** — consultar `SKILL-construtor.md`
3. **Carregar skills** — `SKILL-latex.md` + `SKILL-checklist.md` (sempre); `SKILL-metadata.md` (para dúvidas de YAML)
4. **Converter questões** — consultar `SKILL-conversao.md`
5. **Validar** — aplicar `SKILL-checklist.md` antes de salvar cada nota

## Skills disponíveis

| Skill | Função |
|-------|--------|
| `SKILL-construtor.md` | Como executar o `construtor.py` e interpretar seus outputs |
| `SKILL-conversao.md` | Lógica de iteração, montagem de notas e tratamento de imagens/OCR |
| `SKILL-metadata.md` | Schema YAML completo do frontmatter |
| `SKILL-latex.md` | Regras de formatação LaTeX para Obsidian |
| `SKILL-checklist.md` | Checklist pré-save obrigatório |
