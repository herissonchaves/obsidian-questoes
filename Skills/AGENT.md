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

## Objetivo

Ler arquivos de questões de vestibular da pasta `Input/` e gerar uma nota `.md`
por questão na pasta `Output/`, seguindo o schema de metadados e as regras de
formatação definidas nas Skills de referência.

## Entradas esperadas

- PDFs, imagens (JPG/PNG) ou documentos Word com questões de vestibulares
- Prefixo e número inicial informados pelo usuário (ex: `fis047`)
- Disciplina informada pelo usuário (ex: `Fisica`, `Quimica`)

## Skills de referência — carregar antes de processar

| Situação | Carregar |
|----------|----------|
| Conversão padrão | `Skills/SKILL-latex.md` + `Skill/SKILL-checklist.md` |
| Dúvida sobre metadados | `Skills/SKILL-metadata.md` |
| Revisão de notas existentes | `Skills/SKILL-checklist.md` |

---

## Passo a passo

### Etapa 0 — Coletar configuração

Se ainda não foram informados, perguntar ao usuário:
1. **Prefixo e número inicial** — ex: `fis047` (prefixo `fis`, começa em `047`)
2. **Disciplina** — ex: `Fisica`, `Quimica`, `Biologia`, `Matematica`

Se o usuário já informou na mensagem, não perguntar de novo.

### Etapa 1 — Ler e carregar skills

1. Ler `Skills/SKILL-latex.md` → regras de formatação LaTeX
2. Ler `Skills/SKILL-checklist.md` → checklist de validação pré-save
3. Se houver dúvida sobre metadados → ler `Skills/SKILL-metadata.md`

### Etapa 2 — Ler os arquivos de entrada

- Processar todos os arquivos presentes em `Input/`
- Identificar e separar cada questão individualmente
- Determinar o tipo de cada questão (ver árvore de decisão abaixo)

### Etapa 3 — Gerar as notas

- Uma nota `.md` por questão
- Nomenclatura: `{prefixo}{número com zeros}.md` — ex: `fis047.md`, `fis048.md`
- Salvar em `Output/`
- Salvar imagens em `Output/imagens/`

### Etapa 4 — Validar antes de salvar

Rodar o checklist de `Skills/SKILL-checklist.md` em cada nota antes de salvar.

---

## Árvore de decisão

```
Questão identificada
│
├─ Tem alternativas (a, b, c...)? ──→ OBJETIVA
│    └─ tipo: objetiva
│    └─ gabarito: letra (A/B/C/D/E)
│
└─ Sem alternativas / pede "calcule", "determine", "explique"? ──→ DISCURSIVA
     └─ tipo: discursiva
     └─ gabarito: resposta resumida ou ""
     └─ Adicionar 3–4 linhas de underscores após enunciado ou após cada sub-item
     └─ NUNCA usar <br> — não funciona no .docx exportado pelo Enhancing Export
```

```
Questão tem imagem/figura?
│
├─ SIM ──→ Extrair e salvar em output/imagens/
│    └─ Nome: {id}.png (ex: fis047.png)
│    └─ Múltiplas: {id}_1.png, {id}_2.png...
│    └─ Referência no corpo: ![[01 - Sources/imagens/{id}.png]]
│    └─ Inserir na posição exata em que aparece no original
│
└─ NÃO ──→ Sem bloco de imagem
```

---

## Formato de cada nota

```markdown
---
id: fis047
disciplina: Fisica
topico:
  - "[[Mecanica]]"
conteudo:
  - "[[Cinematica]]"
assunto:
  - "[[Queda Livre]]"
banca: "[[ENEM]]"
ano: 2024
tipo: objetiva
dificuldade: "[[media]]"
gabarito: C
resolucao_link: ""
selecionada: false
---

1. (ENEM - 2024) Enunciado completo da questão.

a) Alternativa a

b) Alternativa b

c) Alternativa c
```

### Questão discursiva com sub-itens

```markdown
1. (FUVEST - 2023) Enunciado da questão.

a) Calcule a força de atrito.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

b) Determine a aceleração.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
```

> `\_` escapa o underscore para evitar itálico no Obsidian.

---

## Regra de pesquisa — OBRIGATÓRIA

Quando qualquer metadado não estiver explícito no documento:

1. **Primeiro:** buscar no próprio documento (cabeçalho, rodapé, contexto)
2. **Segundo:** pesquisar na internet, sites das bancas
3. **Último recurso:** deixar `""` e informar o usuário

**NUNCA inventar metadados.** Se não encontrar após pesquisa, deixar vazio e avisar.
