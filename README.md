# Banco de Questões — Obsidian + Antigravity

Converte questões de vestibular em notas `.md` estruturadas para o Obsidian.

```
obsidian-questoes/
├── AGENT.md
├── Skills/
│   ├── SKILL-latex.md
│   ├── SKILL-metadata.md
│   └── SKILL-checklist.md
├── Input/     ← PDFs, imagens ou Word com as questões
└── Output/    ← notas geradas
    └── imagens/
```

---

## Como usar

1. Abra a pasta no Antigravity
2. Coloque os arquivos em `Input/`
3. Envie o prompt no chat

---

## Prompts

**Conversão padrão**
```
Leia AGENT.MD. Processe Input/. Prefixo: fis, começando em 047. Disciplina: Fisica.
```

**Banca/ano não estão no arquivo**
```
Processe Input/. Prefixo: fis, começando em 012. Disciplina: Fisica.
Banca e ano não estão explícitos — pesquise pelo enunciado.
```

**Corrigir uma nota**
```
Corrija fis049: assunto deve ser Queda Livre.
```

**Revisar LaTeX em lote**
```
Revise o LaTeX de todas as notas em Output/ usando SKILL-latex.md e SKILL-checklist.md.
```

**Corrigir metadados em lote**
```
Revise o frontmatter de Output/ usando SKILL-metadata.md. Corrija acentos, listas fora do padrão e wikilinks sem aspas.
```
