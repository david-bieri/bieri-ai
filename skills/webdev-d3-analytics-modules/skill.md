# webdev:d3-analytics-modules

This skill defines the architecture for building interactive, tab-driven analytics dashboards using D3.js (or React/D3 hybrids) without a backend.

## When to invoke

Trigger on: "build an analytics dashboard", "add a D3 chart or module", "tab-driven visualizations", "interactive charts without a backend", "mount/unmount chart modules", or any client-side analytics or dataviz work with D3 or React/D3.

---

## 1. Tab-Mounted Sub-Modules

Instead of loading all visualizations at once, use a tab system that mounts and unmounts modules dynamically.

**HTML Container Pattern:**
```html
<div class="analytics-tabs">
  <button data-target="module-network">Network</button>
  <button data-target="module-heatmap">Heatmap</button>
</div>

<div id="mount-network" class="module-container active"></div>
<div id="mount-heatmap" class="module-container"></div>
```

**JavaScript Mount Pattern:**
```javascript
function loadModule(target) {
    document.querySelectorAll('.module-container').forEach(c => c.classList.remove('active'));
    const container = document.getElementById('mount-' + target);
    container.classList.add('active');
    
    if (target === 'network' && !window.networkLoaded) {
        renderNetwork(container);
        window.networkLoaded = true;
    }
}
```

## 2. Dropdown and Name Sorting

When building dropdowns for people's names, ALWAYS sort and display by **Lastname, Firstname**.

**Particle-Aware Handling:** European names with particles (von, van, de, di) MUST be treated as part of the surname. "von Hayek" sorts under "v".

**The `toSortName` Helper** (use when data only provides full names):

```javascript
function toSortName(fullName) {
    const parts = fullName.trim().split(/\s+/);
    if (parts.length < 2) return fullName;
    
    const particles = ['von', 'van', 'de', 'di', 'du', 'le', 'la', 'der', 'den'];
    let lastNameStart = parts.length - 1;
    
    for (let i = 0; i < parts.length - 1; i++) {
        if (particles.includes(parts[i].toLowerCase())) {
            lastNameStart = i;
            break;
        }
    }
    
    const lastName = parts.slice(lastNameStart).join(' ');
    const firstName = parts.slice(0, lastNameStart).join(' ');
    return lastName + ', ' + firstName;
}
```

**Dropdown Rendering:**
```javascript
const options = nodes.sort((a, b) => a.sortName.localeCompare(b.sortName));
options.forEach(node => {
    const opt = document.createElement('option');
    opt.value = node.id;          // Keep original ID for data lookups
    opt.textContent = node.sortName; // Display "Lastname, Firstname"
    select.appendChild(opt);
});
```

## 3. Responsive SVG Sizing

```javascript
const svg = d3.select(container).append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("preserveAspectRatio", "xMidYMid meet");
```

## Related Skills

| Need | Skill |
|------|-------|
| Pre-computing `sortName` fields in JSON data | `json-data-enrichment` |
| Testing the dashboard before release | `cross-browser-smoke-test` |
| i18n for tab labels and UI strings | `static-site-i18n` |
