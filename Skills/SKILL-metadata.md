# SKILL — Metadados

## Schema

| Campo | Regra |
|-------|-------|
| `id` | Mesmo nome do arquivo sem extensão |
| `disciplina` | Sem acento: Fisica, Quimica, Biologia, Matematica, Geografia, Historia, Portugues |
| `topico` | Lista YAML. Tema amplo. Sem acentos. `- "[[Nome]]"` |
| `conteudo` | Lista YAML. Tema intermediário. Sem acentos. `- "[[Nome]]"` |
| `assunto` | Lista YAML. Tema específico. Sem acentos. `- "[[Nome]]"` |
| `banca` | Wikilink: `"[[ENEM]]"` |
| `ano` | Número: `2024` ou texto: `"2025/2"` |
| `tipo` | `objetiva` ou `discursiva` |
| `dificuldade` | `"[[facil]]"`, `"[[media]]"` ou `"[[dificil]]"` |
| `gabarito` | Letra (objetiva) ou resposta resumida (discursiva) |
| `resolucao_link` | Sempre `""` |
| `selecionada` | Sempre `false` |

## Regras para topico / conteudo / assunto

- SEMPRE listas YAML (com `- `), mesmo com 1 item
- Valores com aspas e wikilink: `- "[[Nome]]"`
- NUNCA acentos
- Múltiplos valores só quando a questão genuinamente exige mais de uma área
- Hierarquia: topico (amplo) → conteudo (intermediário) → assunto (específico)

## Dificuldade

| Nível | Critério |
|-------|----------|
| `facil` | Aplicação direta de uma fórmula ou conceito |
| `media` | Combina 2+ conceitos ou interpreta gráfico/tabela |
| `dificil` | Raciocínio complexo, múltiplas etapas, conexão entre áreas |
