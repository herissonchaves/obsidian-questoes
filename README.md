# Banco de Questões — Obsidian + Antigravity

Sistema de conversão automática de questões de vestibular em notas estruturadas do Obsidian.

---

## Estrutura de arquivos

```
obsidian-questoes/
├── README.md
├── AGENT.md
├── Skill/
│   ├── SKILL-latex.md
│   ├── SKILL-metadata.md
│   └── SKILL-checklist.md
├── input/        ← coloque os arquivos aqui (PDF, imagem, Word)
└── output/       ← notas geradas pelo agente
    └── imagens/
```

---

## Como usar

1. Abra esta pasta no **Antigravity**
2. Coloque os arquivos com questões na pasta `input/`
3. No chat envie o prompt específico
4. O agente gera as notas em `output/`
5. Copie os `.md` para `05 - questoes/` e as imagens para `01 - Sources/imagens/` no Obsidian

---

## Prompts úteis

**Conversão padrão**
```
Leia o AGENT.md.
Processe os arquivos em input/.
Prefixo: fis, começando em 047. Disciplina: Fisica.
```

**Quando a banca/ano não estão no arquivo**
```
Leia o AGENT.md.
Processe os arquivos em input/.
Prefixo: fis, começando em 012. Disciplina: Fisica.
A banca e o ano não estão explícitos — pesquise pelo enunciado de cada questão.
```

**Corrigir uma nota específica**
```
Corrija fis049: o assunto deveria ser Queda Livre.
```

**Revisar LaTeX de notas geradas**
```
Leia Skill/SKILL-latex.md e Skill/SKILL-checklist.md.
Revise o LaTeX de todas as notas em output/ e corrija os erros encontrados.
```

**Corrigir metadados em lote**
```
Leia Skill/SKILL-metadata.md.
Revise o frontmatter de todas as notas em output/ e corrija campos com acento, listas fora do padrão ou wikilinks sem aspas.
```

---

## Dicas

- Pode processar vários arquivos de uma vez
- Se não houver gabarito no arquivo, o agente pesquisa automaticamente
- Questões discursivas recebem linhas de escrita que aparecem corretamente ao exportar para Word
- Para exportar: selecione as questões no dashboard do Obsidian e use o Enhancing Export
