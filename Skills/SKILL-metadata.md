---
name: metadata-obsidian
description: >
  Schema completo de metadados (frontmatter YAML) para notas de questões do
  Obsidian. Carregar quando houver dúvida sobre campos obrigatórios, formato
  de wikilinks, valores permitidos ou hierarquia topico/conteudo/assunto.
  Também usar quando revisar ou corrigir frontmatter de notas existentes.
---

# SKILL — Metadados

## Schema completo

| Campo | Tipo | Regra |
|-------|------|-------|
| `id` | string | Mesmo nome do arquivo sem extensão |
| `disciplina` | string | Sem acento: `Fisica`, `Quimica`, `Biologia`, `Matematica`, `Geografia`, `Historia`, `Portugues`, etc |
| `topico` | lista YAML | Tema amplo. Sem acentos. `- "[[Nome]]"` |
| `conteudo` | lista YAML | Tema intermediário. Sem acentos. `- "[[Nome]]"` |
| `assunto` | lista YAML | Tema específico. Sem acentos. `- "[[Nome]]"` |
| `banca` | wikilink | `"[[ENEM]]"`, `"[[FUVEST]]"`, `"[[UNICAMP]]"` etc. |
| `ano` | número ou string | `2024` ou `"2025/2"` |
| `tipo` | string | `objetiva` ou `discursiva` |
| `dificuldade` | wikilink | `"[[facil]]"`, `"[[media]]"` ou `"[[dificil]]"` |
| `gabarito` | string | Letra maiúscula (objetiva) ou resposta resumida (discursiva) |
| `resolucao_link` | string | Sempre `""` |
| `selecionada` | boolean | Sempre `false` |

---

## Regras para topico / conteudo / assunto

- **SEMPRE listas YAML** (com `- `), mesmo com apenas 1 item
- **Formato obrigatório:** `- "[[Nome]]"` — com aspas duplas e wikilink
- **NUNCA usar acentos** nos valores (ex: `Mecanica`, não `Mecânica`)
- **Múltiplos valores** apenas quando a questão genuinamente exige mais de uma área
- **Hierarquia:** `topico` (amplo) → `conteudo` (intermediário) → `assunto` (específico)

### Exemplos de hierarquia

| topico | conteudo | assunto |
|--------|----------|---------|
| `Mecanica` | `Cinematica` | `Queda Livre` |
| `Mecanica` | `Dinamica` | `Leis de Newton` |
| `Eletricidade` | `Eletrostatica` | `Lei de Coulomb` |
| `Termologia` | `Gases` | `Lei de Boyle` |
| `Ondulatoria` | `Som` | `Efeito Doppler` |

---

## Critérios de dificuldade

| Nível | Critério |
|-------|----------|
| `facil` | Aplicação direta de uma fórmula ou definição de conceito |
| `media` | Combina 2+ conceitos ou requer interpretação de gráfico/tabela |
| `dificil` | Raciocínio em múltiplas etapas, conexão entre áreas ou alto grau de abstração |

---

## Exemplo completo de frontmatter

```yaml
---
id: fis047
disciplina: Fisica
topico:
  - "[[Mecanica]]"
conteudo:
  - "[[Dinamica]]"
assunto:
  - "[[Leis de Newton]]"
banca: "[[ENEM]]"
ano: 2024
tipo: objetiva
dificuldade: "[[media]]"
gabarito: B
resolucao_link: ""
selecionada: false
---
```
