# JSON Data Enrichment

This skill defines patterns for safely transforming, validating, and enriching static JSON datasets used by frontend applications.

## Core Principles

1. **Pre-compute for the frontend**: If a value is needed by the UI (like a sorted name), compute it once in the JSON rather than on the fly in the browser.
2. **Non-destructive additions**: Add new fields rather than mutating existing ones, ensuring backwards compatibility.
3. **Deterministic transformations**: Use Python scripts to apply transformations consistently across the entire dataset.

## 1. Particle-Aware Name Inversion

Convert "Firstname Lastname" to "Lastname, Firstname" for UI dropdowns. European names with particles (von, van, de, di) require special handling.

```python
import json

PARTICLES = {'von', 'van', 'de', 'di', 'du', 'le', 'la', 'der', 'den'}

def to_sort_name(full_name):
    parts = full_name.strip().split()
    if len(parts) < 2:
        return full_name
    last_name_start = len(parts) - 1
    for i in range(len(parts) - 1):
        if parts[i].lower() in PARTICLES:
            last_name_start = i
            break
    last_name = " ".join(parts[last_name_start:])
    first_name = " ".join(parts[:last_name_start])
    return f"{last_name}, {first_name}"

def enrich(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for node in data.get('nodes', []):
        if 'id' in node and 'sortName' not in node:
            node['sortName'] = to_sort_name(node['id'])
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

## 2. Network Integrity Validation

When enriching network data, validate that all edges point to valid nodes:

```python
def validate_network(data):
    node_ids = {node['id'] for node in data.get('nodes', [])}
    errors = []
    for edge in data.get('links', []):
        if edge['source'] not in node_ids:
            errors.append(f"Invalid source: {edge['source']}")
        if edge['target'] not in node_ids:
            errors.append(f"Invalid target: {edge['target']}")
    return errors
```

## 3. Safe Migration Pattern

When adding a new field to a JSON file consumed by the frontend:

1. **Analyze consumers**: `grep -rn "filename.json" *.js` to find all JS files that load the data.
2. **Run enrichment**: Execute the Python script to add the new field.
3. **Update UI code**: Modify the JS files to use the new field.
4. **Atomic commit**: Commit data and code changes together.

## Related Skills

| Need | Skill |
|------|-------|
| Using enriched `sortName` in dropdowns | `d3-analytics-modules` (Section 2) |
| Verifying the UI after a data migration | `cross-browser-smoke-test` |
