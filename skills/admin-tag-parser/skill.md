# admin:tag-parser

Parse structured subject-line tags of the form `#TAG @Name1 @Name2 Subject text` to classify incoming messages by category and assignee.

---

## When to invoke

Trigger on: "classify this email by tag", "parse the subject line", "extract the category from this subject", "set up tag routing", "build an inbox classifier", any request to route messages based on `#TAG @Name` syntax, or any email pipeline that needs to distinguish category and recipients before LLM fallback.

---

## Tag syntax

```
#TAG @Name1 @Name2 Subject text here
```

- `#TAG` — first token, defines category (case-insensitive)
- `@Name` — zero or more, defines assignees (resolved against a known roster via prefix match)
- Remainder — free-text subject/title

**Examples:**
```
#CAMP @Clara @Airlie Registration deadline June 30
#MED @Heidi Vaccine reminder — MMR booster
#PAY @Cole Soccer league payment due
#SPORT @Greta Practice schedule update
```

---

## Tag registry

Extend this table for your domain. The parser is data-driven — adding a tag only requires a registry entry.

| Tag | Category | Event type |
|-----|----------|------------|
| `#CAMP` | camp | registration |
| `#SPORT` | sports | event |
| `#SCHOOL` | school | event |
| `#MED` | medical | appointment |
| `#PAY` | payment | payment |
| `#REG` | other | registration |
| `#PET` | pets | appointment |
| `#FAM` | family | event |

---

## Workflow

### Step 1 — Fast-path extraction

Check for `#TAG` at position 0 of the trimmed subject:

```typescript
const TAG_REGISTRY: Record<string, {category: string; eventType: string}> = {
  CAMP:   { category: 'camp',    eventType: 'registration' },
  SPORT:  { category: 'sports',  eventType: 'event' },
  SCHOOL: { category: 'school',  eventType: 'event' },
  MED:    { category: 'medical', eventType: 'appointment' },
  PAY:    { category: 'payment', eventType: 'payment' },
  REG:    { category: 'other',   eventType: 'registration' },
  PET:    { category: 'pets',    eventType: 'appointment' },
  FAM:    { category: 'family',  eventType: 'event' },
};

function parseSubject(subject: string, roster: string[]) {
  const m = subject.trim().match(/^#([A-Za-z]+)/);
  if (!m) return null;
  const entry = TAG_REGISTRY[m[1].toUpperCase()];
  if (!entry) return null;
  const mentions = [...subject.matchAll(/@(\w+)/g)].map(x => x[1]);
  const assignees = mentions
    .map(mn => roster.find(n => n.toLowerCase().startsWith(mn.toLowerCase())))
    .filter(Boolean) as string[];
  const title = subject.replace(/^#\w+/, '').replace(/@\w+/g, '').trim();
  return { ...entry, assignees, title, source: 'tag-fast-path' };
}
```

### Step 2 — Name resolution

Match `@mention` to roster using case-insensitive prefix matching. This means `@Cla` matches `Clara`, `@Air` matches `Airlie`, etc. Unresolved mentions are dropped (not carried as raw strings).

### Step 3 — LLM fallback

If no `#TAG` found, pass subject + snippet to an LLM:

```
Extract from this email:
- category: one of [camp, sports, school, medical, payment, other, family, pets]
- assignees: list of names from this roster: {ROSTER}
- title: short event title (max 60 chars)
- date: ISO date if mentioned, else null
- amount: dollar amount if mentioned, else null

Subject: {subject}
Snippet: {snippet}

Respond as JSON only.
```

### Step 4 — Deduplication

Before inserting any extracted item, check for existing record by `gmail_id`. Skip if already imported.

---

## Python reference implementation

```python
import re
TAG_REGISTRY = {
    "CAMP":("camp","registration"), "SPORT":("sports","event"),
    "SCHOOL":("school","event"),    "MED":("medical","appointment"),
    "PAY":("payment","payment"),    "REG":("other","registration"),
    "PET":("pets","appointment"),   "FAM":("family","event"),
}
def parse_subject(subject: str, roster: list[str]) -> dict | None:
    m = re.match(r'^#([A-Za-z]+)', subject.strip())
    if not m or m.group(1).upper() not in TAG_REGISTRY: return None
    category, event_type = TAG_REGISTRY[m.group(1).upper()]
    assignees = [next((n for n in roster if n.lower().startswith(a.lower())),None)
                 for a in re.findall(r'@(\w+)', subject)]
    title = re.sub(r'^#\w+\s*','',subject); title = re.sub(r'@\w+\s*','',title).strip()
    return {"category":category,"event_type":event_type,
            "assignees":[a for a in assignees if a],"title":title,"source":"tag-fast-path"}
```

---

## Extending the registry

1. Add a row to `TAG_REGISTRY` in both TS and Python implementations
2. Add the corresponding category to the app's category list
3. Document the new tag in your team's forwarding guide

---

## QA checklist

- [ ] `#TAG` matched case-insensitively
- [ ] `@mention` resolved via prefix match (not exact match)
- [ ] Unresolved mentions dropped silently (not stored as raw strings)
- [ ] LLM fallback fires when no `#TAG` present
- [ ] `gmail_id` deduplication check runs before insert
