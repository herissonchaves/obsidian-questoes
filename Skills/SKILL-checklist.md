---
name: checklist-questoes
description: >
  Checklist de validação pré-save para notas de questões do Obsidian. Executar
  obrigatoriamente antes de salvar cada nota gerada. Cobre frontmatter YAML,
  formatação do corpo, LaTeX e questões discursivas. Usar também ao revisar
  notas existentes que apresentem erros de formatação ou metadados incompletos.
---

# SKILL — Checklist pré-save

Verificar cada item antes de salvar a nota. Um item falhando pode quebrar o
DataviewJS, a exportação Word ou a renderização no Obsidian.

---

## 1. Frontmatter

- [ ] Delimitado por `---` no início e no fim
- [ ] `id` idêntico ao nome do arquivo (sem extensão)
- [ ] `disciplina` sem acento e com inicial maiúscula (`Fisica`, não `Física`)
- [ ] `topico`, `conteudo` e `assunto` são **listas YAML** — mesmo com 1 item usa `- `
- [ ] Wikilinks com **aspas duplas**: `"[[Nome]]"` — sem aspas quebra o DataviewJS
- [ ] Nenhum valor de topico/conteudo/assunto tem acento
- [ ] `selecionada: false` presente (campo usado pelo filtro do painel)
- [ ] `banca` preenchido — pesquisar se não estiver no documento
- [ ] `ano` preenchido — pesquisar se não estiver no documento
- [ ] `gabarito` preenchido — pesquisar se não estiver no documento

## 2. Corpo da nota

- [ ] Enunciado começa com `1.` — sempre numeral `1`, independente da ordem no original
- [ ] Formato do cabeçalho: `1. (BANCA - ANO) Enunciado completo`
- [ ] Imagens referenciadas com `![[01 - Sources/imagens/NOME.png]]`
- [ ] Imagem inserida na posição exata em que aparece no original

## 3. Questões discursivas

- [ ] `tipo: discursiva` no frontmatter
- [ ] 3–4 linhas de underscores escapados após enunciado (sem sub-itens) ou após **cada** sub-item
- [ ] Underscores escapados com `\_`: `\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_`
- [ ] **Nenhum `<br>`** — não funciona na exportação `.docx` do Enhancing Export

## 4. LaTeX

- [ ] Toda variável isolada dentro de `$...$` — ex: `$m$`, `$v_0$`, `$F$`
- [ ] Toda unidade dentro de `$...$` com `\text{}` — ex: `$\text{m/s}$`
- [ ] Número + unidade com `\,` separando — ex: `$10 \, \text{m/s}^2$`
- [ ] Vírgula decimal com `{,}` — ex: `$3{,}14$` (nunca `$3,14$`)
- [ ] Nenhum `~texto~` (vira tachado) nem `^texto^` (markdown instável)
- [ ] Nenhum `\(...\)` ou `\[...\]` — não renderiza no Obsidian
- [ ] Cada expressão em bloco `$` separado — não misturar variáveis distintas num único `$`
