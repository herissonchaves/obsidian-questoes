---
name: conversao-questoes
description: >
  Lógica de conversão dos JSONs granulares em notas .md do Obsidian. Carregar
  após executar o construtor.py. Define como iterar o manifest, montar o
  corpo da nota, posicionar imagens, lidar com OCR delegado, e distinguir
  questões objetivas de discursivas. Usar sempre que for gerar as notas
  finais a partir dos dados extraídos.
---

# SKILL — Conversão de JSONs para Notas Obsidian

## Objetivo

Transformar os JSONs granulares gerados pelo `construtor.py` em notas `.md`
prontas para o Obsidian, com frontmatter YAML correto e corpo formatado.

## Pré-requisitos

- `construtor.py` já foi executado (ver `SKILL-construtor.md`)
- `Output/manifest.json` existe e foi lido
- Skills `SKILL-latex.md` e `SKILL-checklist.md` carregadas

## Passo a passo

### 1. Ler o manifest

Abrir `Output/manifest.json` e iterar a chave `arquivos` → `lista_questoes`.

### 2. Para cada questão no manifest

1. Ler o `arquivo_detalhe` correspondente em `Output/questoes/`
2. Usar o conteúdo do JSON (`enunciado`, `alternativas`, `imagens`) como fonte
3. Verificar o campo `necessita_ocr_ia` do arquivo-pai no manifest

### 3. Montar o frontmatter

Consultar `SKILL-metadata.md` para o schema completo. Preencher com:
- `id` → valor de `id_local` do JSON
- `disciplina` → informada pelo usuário
- `banca`, `ano` → de `metadados_extraidos` do JSON; se vazio, pesquisar externamente
- `tipo` → de `tipo_detectado` do JSON
- `topico`, `conteudo`, `assunto` → classificar com base no conteúdo do enunciado
- `dificuldade` → avaliar conforme critérios do `SKILL-metadata.md`
- `gabarito` → extrair do documento ou pesquisar; se incerto, deixar vazio
- `resolucao_link` → sempre `""`
- `selecionada` → sempre `false`

### 4. Montar o corpo da nota

#### Cabeçalho

```
1. (BANCA - ANO) Enunciado completo
```

- Sempre numeral `1.`, independente da ordem no original
- Se banca/ano desconhecidos, omitir o parêntese

#### Alternativas (objetiva)

```
a) Texto da alternativa

b) Texto da alternativa
```

- Letra minúscula seguida de `)` e espaço
- Uma linha em branco entre alternativas

#### Espaço de resposta (discursiva)

Após o enunciado (ou após cada sub-item), inserir 3–4 linhas de underscores escapados:

```
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
```

**Nunca usar `<br>`** — não funciona na exportação `.docx`.

### 5. Posicionar imagens

#### Quando a lista `imagens` do JSON está vazia

Não inserir nenhum `![[...]]`. Prosseguir sem referências visuais.

#### Quando há imagens

1. Localizar os marcadores `[IMG:nome.png]` no `enunciado` ou nas `alternativas`
2. Renomear a imagem na pasta `Output/imagens/`:
   - De `{nome_tecnico}.png` → para `{id_local}.png`
   - Se múltiplas: `{id_local}_1.png`, `{id_local}_2.png`, etc.
3. Inserir na posição correspondente ao marcador:

```
![[01 - Sources/imagens/{id_local}.png]]
```

4. Se o marcador `[IMG:...]` não existir mas a lista `imagens` estiver preenchida,
   usar `marcadores_fluxo` como pista. Se ainda ambíguo, inserir após o enunciado
   e antes das alternativas — nunca inventar posições irreais.

## OCR delegado

Quando `necessita_ocr_ia = true` no manifest:

1. Ativar visão do agente sobre o arquivo original em `Input/`
2. Não confiar cegamente no `enunciado` do JSON — ele pode estar vazio ou incompleto
3. Complementar/reescrever o enunciado com base no que o agente "enxerga"
4. Manter cautela elevada na segmentação

## Imagens avulsas (processamento direto VLM)

Quando o manifest contém `"processamento_direto_vlm": true`:

1. **Não existe JSON granular** — o script não gera `Output/questoes/*.json`
2. Usar o `id_reservado` do manifest como `id` da nota
3. Abrir a imagem em `Output/imagens/` diretamente com visão do agente
4. Montar enunciado, alternativas e metadados a partir do que o agente "enxerga"
5. Renomear a imagem para `{id_reservado}.png`

## Árvore de decisão — Objetiva vs Discursiva

```
alternativas[] tem >= 2 itens?
├── SIM → tipo: objetiva
│   └── gabarito: letra maiúscula (A–E)
└── NÃO → tipo: discursiva
    └── gabarito: resposta resumida ou vazio
    └── Inserir linhas de underscores escapados
```

## Formato de referência da nota final

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

1. (ENEM - 2024) Enunciado completo extraído do JSON e/ou visão delegada.

![[01 - Sources/imagens/fis047.png]]

a) Alternativa a

b) Alternativa b

c) Alternativa c

d) Alternativa d

e) Alternativa e
```
