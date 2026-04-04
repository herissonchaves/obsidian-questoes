---
name: latex-obsidian
description: >
  Regras de formatação LaTeX para notas do Obsidian. Carregar sempre que for
  converter ou revisar questões de vestibular. Define sintaxe correta para
  variáveis, unidades, frações, vírgula decimal e letras gregas. Lista padrões
  proibidos que causam erros de renderização no Obsidian.
---

# SKILL — LaTeX para Obsidian

## Regra principal

**Todo elemento matemático, científico ou técnico vai dentro de `$...$` (inline) ou `$$...$$` (bloco). Sem exceções.**

Isso inclui: variáveis, unidades, expoentes, índices, frações, letras gregas, fórmulas, setas de reação, números com vírgula decimal.

---

## Sintaxe correta

| Elemento | Forma correta |
|----------|--------------|
| Variável com índice | `$m_1$`, `$v_0$`, `$F_A$` |
| Expoente | `$x^2$`, `$10^3$` |
| Número + unidade | `$10 \, \text{m/s}^2$` |
| Fração | `$\frac{a}{b}$` |
| Vírgula decimal | `$3{,}14$` |
| Letras gregas | `$\alpha$`, `$\Delta$`, `$\theta$` |
| Equação em bloco | `$$F = ma$$` |

## Número + unidade — padrão obrigatório

```
$NÚMERO \, \text{UNIDADE}$
```

| Exemplos corretos |
|-------------------|
| `$140 \, \text{g}$` |
| `$15 \, \text{cm}^2$` |
| `$162 \, \text{km/h}$` |
| `$324{,}0 \, \text{N}$` |
| `$9{,}8 \, \text{m/s}^2$` |
| `$6{,}02 \times 10^{23} \, \text{mol}^{-1}$` |

---

## Padrões proibidos

| Proibido | Problema | Correto |
|----------|----------|---------|
| `~1~` | Vira tachado no Obsidian | `$_1$` ou `$m_1$` |
| `^2^` | Markdown instável | `$x^2$` |
| `\(...\)` e `\[...\]` | Não renderiza no Obsidian | `$...$` e `$$...$$` |
| `$3,0$` | LaTeX lê vírgula como separador de argumento | `$3{,}0$` |
| Unidade fora do `$` | Fica sem formatação | Sempre dentro do `$` |
| Unidade sem `\text{}` | Fica em itálico (parece variável) | `\text{m/s}` |
| Número grudado na unidade | Ilegível | Sempre `\,` entre número e unidade |
| Múltiplas variáveis em um `$` só | Gera lixo LaTeX | Um bloco `$` por expressão |
| `^` ou `_` fora de `$` | Markdown puro, não LaTeX | Sempre dentro de `$...$` |
