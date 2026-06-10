# bieri-{pillar}

{Pillar description} tools and skills — Prof. David Bieri, Virginia Tech SPIA.

Private repository. Part of the [Bieri Claude ecosystem](./BIERI_CLAUDE.md).
Universal tools synced from [bieri-claude](../bieri-claude/).

---

## Repository structure

```
bieri-{pillar}/
├── README.md
├── BIERI_CLAUDE.md              ← synced from bieri-claude
├── sync-meta.sh                 ← pull updates from bieri-claude
│
├── shared/                      ← synced from bieri-claude
│   ├── session-handover/
│   │   └── SKILL.md
│   ├── audit_skill.py
│   └── architecture/
│
├── skills/                      ← {pillar}-domain skills (source)
│   └── {namespace}-{skill}/
│       └── SKILL.md
│
├── scripts/                     ← standalone scripts
│
├── manifests/
│   └── {PILLAR}_MANIFEST.md
│
└── dist/                        ← .gitignored; .skill files built by package.sh
```

---

## Packaging skills

```bash
./package.sh                     # package all skills
./package.sh {skill-name}        # package one skill
```

Each run audits the packaged file. Failed audit = blocked install.

---

## Syncing from bieri-claude

```bash
./sync-meta.sh                   # pull latest universal tools + templates
```

---

## Installing skills

```
Claude Desktop → Cowork → Customize → Skills → + → upload from dist/
```

---

## The update loop

1. Edit `skills/{name}/SKILL.md`
2. Bump `version` + `updated` in frontmatter
3. `./package.sh {name}`
4. Install via Claude Customize
5. Update `manifests/{PILLAR}_MANIFEST.md`
6. `git add -A && git commit -m "{namespace}:{name} vX.Y.Z: change description"`
