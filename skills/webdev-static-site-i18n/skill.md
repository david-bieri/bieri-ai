# webdev:static-site-i18n

This skill defines the core architecture for managing a multi-page static website with client-side internationalization (i18n) and shared UI patterns. It is designed to keep the site entirely static (no backend) while maintaining consistency across pages.

## Core Principles

1. **Zero Backend**: The site must run entirely on static file hosting (e.g., GitHub Pages).
2. **Client-Side i18n**: Language switching happens in the browser via JavaScript and `localStorage`.
3. **Component Consistency**: Shared elements (like footers and navbars) must follow strict HTML patterns across all files since there is no server-side templating.

## 1. The Client-Side i18n System

The site uses a lightweight, vanilla JavaScript dictionary for translations, avoiding heavy dependencies like `i18next` for simple sites.

### The String Dictionary (`strings.js`)

All UI strings are stored in a global dictionary object.

```javascript
window.APP = window.APP || {};
window.APP.S = {
    nav_home: { de: 'Startseite', en: 'Home' },
    nav_about: { de: 'Über uns', en: 'About' },
    footer_contact: { de: 'Kontakt', en: 'Contact' },
    btn_read_more: { de: 'Weiterlesen', en: 'Read More' }
};

// Translation helper
window.APP.t = function(key, lang) {
    var l = lang || window.APP._lang || 'de';
    var entry = window.APP.S[key];
    if (!entry) return key;
    return entry[l] || entry.de || entry.en || key;
};
```

### HTML Implementation

Use the `data-i18n` attribute to mark elements that need translation:

```html
<a href="index.html" data-i18n="nav_home">Startseite</a>
```

The language toggle script queries all `[data-i18n]` elements and replaces their `textContent` based on the selected language.

## 2. Shared Footer & Cross-Page Propagation

Because static sites lack server-side includes, shared elements (footer, navbar) must be replicated across all `.html` files.

**Propagation Rule:** When updating ANY shared element (footer link, contact row, nav item), you MUST:
1. Use `grep -rn "search_term" *.html` to find all instances.
2. Apply the identical change to every file.
3. Update the string dictionary (`strings.js`) if the element has a `data-i18n` key.

**Standard Footer Structure:**
```html
<footer class="site-footer">
  <div class="footer-content">
    <div class="footer-links">
      <a href="index.html" data-i18n="nav_home">Startseite</a>
      <a href="guide.html#citation" data-i18n="footer_cite">Zitierweise</a>
    </div>
  </div>
  <div class="footer-bottom">
    <span data-i18n="footer_contact">KONTAKT</span>
    <a href="mailto:info@example.com">info@example.com</a>
  </div>
</footer>
```

## 3. GitHub Pages Deployment & Concurrency

The site is deployed via GitHub Actions. When pushing multiple commits in quick succession, GitHub Actions may fail with:

> *Deployment request failed for `commit-A` due to in progress deployment.*

**Fix:** Add a concurrency group to `.github/workflows/pages.yml`:

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: true
```

**If the error has already occurred:** It is self-resolving. The latest commit will deploy once the prior run finishes. Do not attempt code fixes; simply wait or advise the user.

## Related Skills

| Need | Skill |
|------|-------|
| Adding contact links to the footer | `contact-protocol-links` |
| Full release ceremony (merge, deploy, hotfix) | `web-release-workflow` |
