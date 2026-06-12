# Teaching Skills Manifest
*Registry of active Claude skills for the teaching domain.*

## Installed Skills
| Skill | Namespace | Purpose |
|-------|-----------|---------|
| `session-handover` | (universal) | Universal session state management |
| `news-hooks` | `teaching` | "In the news" slide search and formatting |
| `build-kb` | `teaching` | PPTX → KB extraction via build_kb.py |
| `video-scripts` | `teaching` | Narration script generation (130 wpm) |
| `compose-slides` | `teaching` | Lecture deck composition in house style |
| `assess-from-kb` | `teaching` | Assessment generation from KB content |
| `skill-builder` | `teaching` | Library creation and maintenance |

## Candidate Skills
*(Add skills identified during sessions but not yet built)*

| Skill Idea | Trigger Condition | Status |
|------------|-------------------|--------|
| — | — | — |

## Update Log
| Date | Version | Changes |
|------|---------|---------|
| 2026-06-10 | 2.0.0 | Migrated to unified bieri-ai monorepo architecture |
| 2026-06-11 | 2.1.0 | Contract normalization — `course:`→`teaching:`, no-frontmatter + `metadata.yaml` sidecars, skill-builder aligned to the bieri-ai contract |
| 2026-06-11 | 2.1.1 | `teaching:skill-builder` → v1.1.0: `audit_skill.py` realigned to the bieri-ai contract (audits `skill.md` + `metadata.yaml`, validates derived identity); Manus adapter brought to Claude-adapter parity (derived colon name, sidecar metadata, graph) |
