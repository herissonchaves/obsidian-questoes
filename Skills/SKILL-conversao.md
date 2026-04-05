---
name: conversao-questoes
description: >
  Lógica completa para montar notas .md do Obsidian a partir dos JSONs
  gerados pelo construtor.py. Carregar quando for iterar o manifest,
  ler JSONs granulares, montar corpo da nota, renomear imagens, ou decidir
  entre formato objetiva/discursiva. Também usar quando lidar com OCR
  delegado ou questões com confiança baixa de segmentação.
---

# SKILL — Conversão JSON → Nota Obsidian

## Objetivo

Transformar cada JSON granular em `Output/questoes/` numa nota `.md`
completa, com frontmatter YAML e corpo formatado.

## Passo a passo

### 1. Ler o manifest

```python
# Pseudocódigo do fluxo
manifest = ler("Output/manifest.json")
for arquivo in manifest["arquivos"]:
    for q in arquivo["lista_questoes"]:
        json_questao = ler(q["arquivo_detalhe"])
        nota = montar_nota(json_questao, arquivo)
        salvar(f"{q['id_local']}.md", nota)
```

### 2. Verificar OCR delegado

Se `arquivo["necessita_ocr_ia"] == true`:
1. Ative visão no documento original (PDF/imagem em `Input/`)
2. Não confie cegamente no `enunciado` do JSON — complemente com o que você enxerga
3. Mantenha cautela elevada na segmentação

### 3. Decidir tipo da questão

| Condição | Tipo | Ação |
|----------|------|------|
| `alternativas` tem ≥ 2 itens | `objetiva` | Formatar com letras a)–e) |
| `alternativas` está vazio `[]` | `discursiva` | Inserir linhas de resposta com underscores |
| `tipo_detectado: "incerto"` | Verificar visualmente | Usar visão no original |

### 4. Montar o frontmatter

Preencha todos os campos conforme `SKILL-metadata.md`. Fontes de dados:

| Campo | Fonte primária | Fallback |
|-------|---------------|----------|
| `id` | `id_local` do JSON | — |
| `disciplina` | Configuração do usuário | — |
| `banca` | `metadados_extraidos.banca` | Pesquisa externa |
| `ano` | `metadados_extraidos.ano` | Pesquisa externa |
| `tipo` | `tipo_detectado` | Análise visual |
| `gabarito` | Não extraído pelo script | Pesquisa externa |
| `topico/conteudo/assunto` | Análise semântica do enunciado | — |
| `dificuldade` | Análise do enunciado | Padrão `"[[media]]"` |

### 5. Montar o corpo

#### Questão objetiva

```markdown
1. (BANCA - ANO) Enunciado completo.

![[01 - Sources/imagens/fis047.png]]

a) Alternativa A

b) Alternativa B

c) Alternativa C

d) Alternativa D

e) Alternativa E
```

#### Questão discursiva (sem sub-itens)

```markdown
1. (BANCA - ANO) Enunciado completo.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
```

#### Questão discursiva (com sub-itens)

```markdown
1. (BANCA - ANO) Enunciado completo.

a) Sub-item A

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

b) Sub-item B

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
```

> **Proibido:** não use `<br>` — quebra a exportação `.docx` do Enhancing Export.

### 6. Gerenciar imagens

1. **Lista `imagens` vazia** → não insira nenhum `![[...]]` na nota
2. **Lista preenchida** → para cada imagem:
   - Renomeie de nome técnico para `{id}.png` (ou `{id}_1.png`, `{id}_2.png` se múltiplas)
   - Localize a posição via marcador `[IMG:nome.png]` no enunciado/alternativas
   - Insira `![[01 - Sources/imagens/{id}.png]]` na posição correspondente
   - Se não houver marcador claro, posicione com julgamento conservador

### 7. Aplicar formatação

- **LaTeX:** siga `SKILL-latex.md` rigorosamente
- **Checklist:** execute `SKILL-checklist.md` antes de salvar cada nota

## Regras de segurança

- **Nunca insira imagem sem confirmação** na lista `imagens` do JSON
- **Nunca invente banca/ano/gabarito** — deixe vazio e avise o usuário
- **Sempre numere como `1.`** — independente da numeração original
- **Cada nota é um arquivo** — nome do arquivo = `id_local` (ex: `fis047.md`)
