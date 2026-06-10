# Contact Protocol Links

This skill defines patterns for implementing "zero-infrastructure" contact channels on static websites using native URI protocols.

## Protocol Link Formats

All protocols support pre-filling data. Message bodies MUST be URL-encoded (`%20` for space, `%2C` for comma).

### Email (`mailto:`)
```html
<a href="mailto:info@example.com?subject=Inquiry&body=Hello%2C%20I%20have%20a%20question.">
  info@example.com
</a>
```

### Phone (`tel:`)
Always use E.164 format (with `+` and country code):
```html
<a href="tel:+17342723161">+1 734 272 3161</a>
```

### SMS (`sms:`)
```html
<a href="sms:+17342723161?body=Hello%20there.">SMS</a>
```

### WhatsApp (`wa.me/`)
Do NOT include the `+` sign in the phone number:
```html
<a href="https://wa.me/17342723161?text=Hello%20there.">WhatsApp</a>
```

## Audience-Appropriate Channel Selection

| Factor | SMS | WhatsApp |
|--------|-----|----------|
| Works without app install | Yes | No |
| Works without data/WiFi | Yes | No |
| Familiar to older users | Yes | Mostly |
| Fails gracefully if unavailable | Yes | No (redirects to app store) |
| Cost to sender | Trivial per-message fee | Free |

**Recommendation:** Offer Email + Phone + SMS as primary channels. WhatsApp as a secondary/fallback channel (dimmed icon, smaller).

## UI Pattern

Establish visual hierarchy — strong icons for primary channels, dimmed for secondary:

```html
<div class="contact-row">
  <span class="label" data-i18n="footer_contact">KONTAKT</span>
  
  <!-- Primary -->
  <a href="mailto:info@example.com" title="E-Mail">✉ info@example.com</a>
  <a href="tel:+17342723161" title="Anrufen">☎ +1 734 272 3161</a>
  <a href="sms:+17342723161?body=Hello" title="SMS">💬 SMS</a>
  
  <!-- Secondary (dimmed) -->
  <a href="https://wa.me/17342723161?text=Hello" title="WhatsApp" style="opacity: 0.5;">
    <img src="whatsapp-icon.svg" alt="WA">
  </a>
</div>
```

## Placement

1. **Global Footer**: A compact row (see `static-site-i18n` for footer propagation rules).
2. **Dedicated Page**: A prominent card on the "About" or "Committee" page.

## Related Skills

| Need | Skill |
|------|-------|
| Propagating footer changes across all pages | `static-site-i18n` (Section 2: Propagation Rule) |
| Adding i18n labels to contact elements | `static-site-i18n` (Section 1: String Dictionary) |
