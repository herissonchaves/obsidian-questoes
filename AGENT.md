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

## Ferramenta obrigatória — `construtor.py`

O script `Input/construtor.py` é o extrator universal do projeto.
**Ele DEVE ser executado ANTES de qualquer processamento manual.**

> **REGRAS INVIOLÁVEIS:**
> - **NUNCA recriar, sobrescrever ou excluir** `Input/construtor.py`
> - **NUNCA extrair texto/imagens manualmente** — o script já faz isso
> - Se o script não existir em `Input/`, avisar o usuário e parar

### Como usar

```bash
# Processar toda a pasta Input/ (padrão)
python Input/construtor.py -i Input -o Output --prefixo fis --inicio 47

# Processar um arquivo específico
python Input/construtor.py --arquivo Input/prova.pdf -o Output --prefixo fis --inicio 47

# Ver ajuda completa
python Input/construtor.py --help
```

### O que o script produz

```
Output/
├── manifest.json               ← manifesto estruturado (ler este primeiro)
├── {nome}_extraido.txt          ← texto extraído de cada arquivo de entrada
└── imagens/
    ├── {nome}_p1_1.png          ← imagens extraídas de PDFs (com página)
    └── {nome}_1.jpg             ← imagens extraídas de DOCX
```

O `manifest.json` contém a config e os dados de cada arquivo processado,
incluindo texto extraído, lista de imagens com caminhos e páginas de origem.

## Skills de referência — carregar antes de processar

| Situação | Carregar |
|----------|----------|
| Conversão padrão | `Skills/SKILL-latex.md` + `Skills/SKILL-checklist.md` |
| Dúvida sobre metadados | `Skills/SKILL-metadata.md` |
| Revisão de notas existentes | `Skills/SKILL-checklist.md` |

---

## Passo a passo

### Etapa 0 — Coletar configuração

Se ainda não foram informados, perguntar ao usuário:
1. **Prefixo e número inicial** — ex: `fis047` (prefixo `fis`, começa em `047`)
2. **Disciplina** — ex: `Fisica`, `Quimica`, `Biologia`, `Matematica`

Se o usuário já informou na mensagem, não perguntar de novo.

### Etapa 1 — Executar `construtor.py`

1. Verificar que `Input/construtor.py` existe
2. Executar: `python Input/construtor.py -i Input -o Output --prefixo {prefixo} --inicio {numero}`
3. Confirmar que `Output/manifest.json` foi gerado com sucesso
4. Ler `Output/manifest.json` para obter os dados extraídos

> **Se o script falhar:** reportar o erro ao usuário e **não** tentar extrair manualmente.

### Etapa 2 — Carregar skills

1. Ler `Skills/SKILL-latex.md` → regras de formatação LaTeX
2. Ler `Skills/SKILL-checklist.md` → checklist de validação pré-save
3. Se houver dúvida sobre metadados → ler `Skills/SKILL-metadata.md`

### Etapa 3 — Processar o texto extraído

- Ler os arquivos `*_extraido.txt` gerados pelo `construtor.py`
- Identificar e separar cada questão individualmente
- Determinar o tipo de cada questão (ver árvore de decisão abaixo)
- Mapear imagens extraídas às questões correspondentes (usar `manifest.json`)

### Etapa 4 — Gerar as notas

- Uma nota `.md` por questão
- Nomenclatura: `{prefixo}{número com zeros}.md` — ex: `fis047.md`, `fis048.md`
- Salvar em `Output/`
- Renomear imagens de `Output/imagens/` para `{id}.png`, `{id}_1.png` etc.

### Etapa 5 — Validar antes de salvar

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
├─ SIM ──→ Usar imagem já extraída pelo construtor.py em Output/imagens/
│    └─ Renomear para: {id}.png (ex: fis047.png)
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
