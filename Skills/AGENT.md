# Instruções do Agente — Conversor de Questões para Obsidian

## Sua função

Converter listas de exercícios de vestibulares em notas do Obsidian.

1. Ler todos os arquivos da pasta `input/`
2. Extrair as questões de cada arquivo
3. Gerar uma nota `.md` por questão na pasta `output/`
4. Extrair/salvar imagens na pasta `output/imagens/`

## Antes de processar

Pergunte ao usuário no chat:
1. **Qual o prefixo e número inicial?** (ex: "fis047" → prefixo `fis`, começa em 047)
2. **Qual a disciplina?** (ex: Fisica, Quimica, Biologia)

Se o usuário já informou esses dados na mensagem, não pergunte de novo.

## Estrutura do projeto

```
obsidian-questoes/
├── AGENT.md
├── Skill/
│   ├── SKILL-metadata.md
│   ├── SKILL-latex.md
│   └── SKILL-checklist.md
├── input/
└── output/
    └── imagens/
```

## Skills — carregar antes de processar

Os arquivos de skill estão na página/pasta `Skill/`.

| Tarefa | Carregar |
|--------|----------|
| Converter questões (padrão) | `Skill/SKILL-latex.md` + `Skill/SKILL-checklist.md` |
| Corrigir metadados | `Skill/SKILL-metadata.md` |
| Revisar notas existentes | `Skill/SKILL-checklist.md` |

---

## Formato de cada nota

```markdown
---
id: fis001
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

---
1. (ENEM - 2024) Enunciado completo da questão.

a) Alternativa a

b) Alternativa b

c) Alternativa c
```

---

## Pesquisa de informações — REGRA OBRIGATÓRIA

Quando não encontrar qualquer metadado no documento, pesquisar na internet antes de deixar vazio. Prioridade:

1. Informação explícita no documento
2. Pesquisa na internet (questoesdevestibulares.com.br, sites das bancas, etc.)
3. Deixar `""` — **último recurso**

NUNCA inventar. Se não encontrar, deixar vazio e informar ao usuário.

---

## Questões discursivas

Identificar se é discursiva (sem alternativas, pede "calcule", "determine", "explique", tem sub-itens abertos).

Usar 3–4 linhas de underscores escapados após o enunciado (sem sub-itens) ou após **cada** sub-item (com sub-itens). Isso garante linhas de escrita visíveis no Word após exportação pelo Enhancing Export.

**Padrão de linha:** `\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_`

```markdown
1. (FUVEST - 2023) Enunciado...

a) Calcule a força de atrito.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

b) Determine a aceleração.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
```

> `\_` é necessário para escapar o underscore e evitar itálico no Obsidian.

---

## Imagens

- Nome = nome da nota: `fis001.png`
- Múltiplas: `fis001_1.png`, `fis001_2.png`
- Referência: `![[01 - Sources/imagens/fis001.png]]`
- Inserir na posição exata onde aparecem no original
