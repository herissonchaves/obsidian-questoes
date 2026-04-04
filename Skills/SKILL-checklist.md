# SKILL — Checklist pré-save

Verificar cada item antes de salvar a nota.

## Frontmatter
- [ ] Entre `---` correto
- [ ] `id` = nome do arquivo sem extensão
- [ ] `topico`, `conteudo`, `assunto` são listas YAML sem acentos
- [ ] Wikilinks com aspas duplas: `"[[Nome]]"`
- [ ] `selecionada: false`
- [ ] `banca` e `ano` preenchidos (pesquisar se necessário)
- [ ] `gabarito` preenchido (pesquisar se necessário)

## Corpo
- [ ] Inicia com `---` após o frontmatter
- [ ] Número do enunciado sempre `1.`
- [ ] Formato: `1. (BANCA - ANO) Enunciado`
- [ ] Imagens com caminho `![[01 - Sources/imagens/NOME.png]]`
- [ ] Se discursiva: 3–4 linhas de `\_\_\_\_...\_\_\_\_` após enunciado ou após cada sub-item (nunca `<br>` — não funciona no docx)

## LaTeX
- [ ] Toda variável e unidade dentro de `$...$`
- [ ] Número + unidade com `\,` e `\text{}`: `$10 \, \text{m/s}^2$`
- [ ] Vírgula decimal com `{,}`: `$3{,}14$`
- [ ] Nenhum `~`, `^` markdown, `\(...\)` ou `\[...\]`
- [ ] Cada expressão em bloco separado (não misturar variáveis em um `$` só)
