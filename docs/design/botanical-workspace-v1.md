# Botanical workspace · theme arc 1

Baseline and rollback: immutable `v2.1.0`, commit `d2963c2380c359dff3ea2f23f4a702c6074cb642`.
No new release tag. This development arc changes presentation, browser QA and safe recognition of the existing milestone in CI.

## Design ownership

| Layer | Owner | Rule |
| --- | --- | --- |
| Palette, spacing, type, shape, surfaces | `assets/css/jp-theme-tokens.css` | Canonical `--jp-*` values; inherited aliases bridge legacy page palettes. |
| Header and common primitives | `assets/css/site-shell.css` | Global rules scoped to `body[data-jp-site]`; shadow rules scoped to `.jp-*`. |
| Header behavior | `assets/js/site-shell.js` | Single top-level Shadow DOM header; six routes, contextual tools, project FK preservation. |
| Environmental artwork | `assets/botanical/*.svg`, `assets/css/jp-botanical.css` | Small local SVGs, margin-only garden borders, hero sprig and checklist empty state. |
| Functional layout | Existing page styles, `app.css`, `guide.css` | Preserve map panes, guide page breaks and data-driven controls. |
| Mobile | Shared stylesheet media queries | Compact menu below 1121px; two columns below 768px. Smaller controls at 380px. |
| Print | Shared and guide print rules | Hide header, garden borders, sprigs, footer trees and empty-state art; preserve guide depths. |

The 20 active HTML pages load the three shared stylesheets in the head, after their existing page stylesheet. This avoids waiting for JavaScript to apply the theme. Tokens pass through the custom element host into the existing Shadow DOM. Page-local functional layout remains authoritative for map, tables and printing.

## Components and visual rules

Use forest-green text on warm white surfaces, pale sage backgrounds, 10/14/20px radii and subtle borders. Use the same fluid heading scale and visible warm-brown focus outline throughout. State warnings retain their amber meaning.

The header is a direct body child, independent of each content column. Its six route links remain in one row on wide screens. At narrower widths, Menu opens a grid with all six links; Escape closes it and returns focus. More tools is independently accessible. Selected project IDs follow supported field routes; developer pages do not inherit that context. Skip to content crosses the Shadow DOM boundary and focuses the main content. A ResizeObserver requests map reflow when the header changes size.

The personal checklist retains its 800px content measure; wider pages use a 1200px outer measure. Primary buttons and inputs have a 44px minimum height. Map zoom, filter, list and layer controls also receive practical touch areas. Mobile fit-bounds reserves space around these controls so site markers remain reachable. Tables retain local horizontal scrolling where needed rather than stretching the document.

Garden assets:

- `garden-left.svg`: leafy stems and flowers in wide left gutters.
- `garden-right.svg`: flowering shrubs in wide right gutters.
- `corner-sprig.svg`: subtle hero corner, outside the text measure on desktop.
- `empty-garden.svg`: small welcoming checklist illustration.
- `tree-silhouette.svg`: quiet footer grove.

Garden borders scale to the available gutter, are richer beside the checklist, lighter beside Progress/Resources/Developer, and disappear on phones. The map has no decorative overlay. Decorations have no pointer events, no motion, no semantic content, and disappear when printing. Native controls, text, markers and evidence remain foreground content.

## Deliberate exceptions

The map retains a viewport workspace and its mobile bottom sheet instead of adopting the reading-column layout. Its header uses the same light botanical palette. The homepage retains the existing construction canvas. Guide pages retain their print pagination. Memory Wall retains its poster layout with the shared light theme. The three compatibility URLs (`current-works.html`, `how-to.html`, `workspace.html`) remain redirects; archived HTML snapshots are excluded.

## Reproduction and QA

Run production validation from `.github/workflows/daily-ops-branch-preview.yml`, then:

```sh
python scripts/qa_field_ux_browser.py
python scripts/qa_botanical_theme.py
```

Install the pinned Playwright/axe versions from the visual workflow. The harness uses Chrome on the runner; a local headless shell can be selected with `CHROME_BIN`. Restricted local runtimes can enable `JP_QA_PROXY` using the environment proxy: only local QA-server requests are relayed through Python; remote CDN and OSM assets still use the browser network, with failures reported. No map imagery is invented or replaced with dummy tiles. Normal GitHub CI uses the browser network directly.

The theme harness covers 20 routes at 320, 375, 390, 430, 768, 1024, 1440 and 1920px, navigation/active state, menu/Escape, header dimensions, overflow, script/asset failures, axe serious/critical findings on all 20 pages at phone and desktop widths, clipboard/removal, print depths, reduced motion and decoration layering. Before screenshots are generated from the immutable baseline, with after screenshots at 390, 768 and 1440px. The original field harness continues to test checklist add/check/reload, project context, resource filters, progress, map tiles, site selection, list/filter/layer disclosures and mobile views. Actions archives the results and screenshots.

## Scope and next checkpoint

Canonical project data, resource identities, original Drive documents, project Progress and the paused Discord collector are unchanged. Existing Drive/Sheets/Control Tower integration work remains separate from this frontend arc. Frozen milestone tagging now skips subsequent development commits rather than attempting to move the existing `v2.1.0` tag.
