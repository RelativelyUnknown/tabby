# frontend

A skill of the Tabby plugin for anything a person sees in a browser from a Python project: a page, a form, a table, a dashboard, an internal tool, a Jinja or Django template or admin screen, a Streamlit, Dash or Gradio app, a docs site or a README picture. A diagram or explainer animation is [`diagrams`](../diagrams/).

**Entry point:** [`SKILL.md`](SKILL.md), which sends the agent to [`interfaces/index.md`](interfaces/index.md) for the method.

## The problem it solves

An agent building a screen with no brief drifts into the same defaults: cards inside cards, a hero number, gradient text, a glow on everything, low-contrast grey on white, tap targets too small to hit, no visible focus, a page that scrolls sideways on a phone. Tabby makes the agent decide first and then measure the result.

## What the agent does

1. **Context before looks.** It reads `design.md` (or `DESIGN.md`) and `## Tabby`, and the project's existing pages, CSS framework and theme config, and matches them. A redesign only when you ask.
2. **A five-line brief in the reply:** who comes, the one job they came to do, the one thing the screen must make easy, the content that really exists (no invented figures, names or logos), and the limits.
3. **A mode from the visitor's job:** *persuade* (landing page, project site), *operate* (dashboard, admin, internal tool) or *read* (documentation, reference).
4. **Build with the project's own tools.** A project on Tailwind, Bootstrap, Pico, Streamlit's theme or MkDocs Material stays on it; tokens go through that tool's settings, not a second styling system. One page per surface: [server-rendered](interfaces/server-rendered.md), [data apps](interfaces/data-apps.md), [docs and README](interfaces/docs-and-readme.md).
5. **Refuse the known defaults** in [`interfaces/refuse.md`](interfaces/refuse.md) (scaffolds, surfaces, type and colour) unless the brief earns one.
6. **Check by measuring, then look.** `ui-check.mjs`, then the page at 390 px and 1280 px, in light and dark, with the keyboard.

## The checker

```
node assets/interfaces/ui-check.mjs <url or file.html> [--waivers waivers.json] [--json]
```

It loads the page at 390x844 and 1280x800 in Chromium. Exit 0 means no failures, 2 means at least one, 1 means it could not run. On the shipped clean fixture it prints `OK`. On the shipped bad fixture ([`assets/interfaces/fixtures/bad.html`](assets/interfaces/fixtures/bad.html)):

```
FAIL document html @390/1280: the <html> element has no lang
FAIL overflow-x html @390: the page is 700px wide in a 390px window
FAIL contrast p.low @390/1280: 1.90:1, needs 4.5:1
FAIL refuse-gradient-text p.grad @390/1280: text filled with a gradient
FAIL tiny-text p.small @390/1280: 10px text
FAIL tap-size button.tiny-btn @390: 16x16px, needs 24
FAIL heading-order h3 @390/1280: h1 is followed by h3
FAIL img-alt img @390/1280: no alt attribute (use alt="" for decoration)
FAIL form-label input @390/1280: no label
FAIL refuse-hard-shadow div.hard @390/1280: hard offset shadow 6px 6px
FAIL focus-visible button.tiny-btn @390/1280: Tab lands here and nothing shows it
FAIL reduced-motion page @1280: 1 infinite animation(s) still run under prefers-reduced-motion
```

(18 findings in all, trimmed here.) What it checks: contrast (4.5:1 for text, 3:1 for large), sideways scrolling, tap size under 24 px, heading order, visible keyboard focus, image alt text, form labels, `lang` and `title`, text under 12 px, infinite animation under reduced motion, page errors, and four of the refused defaults (gradient text, hard shadow, one-sided stripe, glow). It warns on lines over about 90 characters, tap targets under 44 px and heavy glass blur.

A finding is fixed, or waived with a reason of at least 12 characters in `.tabby-ui-waivers.json`; a waiver prints as `WAIVED` so it stays visible.

## Needs

Playwright Chromium (the Node package) for `ui-check.mjs`. The agent asks before installing it; if it is missing the report says the page was not measured. A page change that was not measured is not done.

## Limits

- The checker measures what a machine can. It does not see hierarchy, fit, voice or whether the page does its job; that is why the agent also looks at it at two sizes, in both themes and by keyboard, and says what it looked at.
- Contrast is skipped where the background is an image or gradient.
- It does not choose the project's framework. It works inside the one you have.

## Layout

```
SKILL.md
interfaces/index.md              the method, step by step
interfaces/layout-and-states.md  the three modes; empty, loading, error and full states
interfaces/tokens-and-type.md    one-accent palette shared with the diagrams, type scale
interfaces/refuse.md             the defaults to refuse; (c) marks what the checker detects
interfaces/server-rendered.md, data-apps.md, docs-and-readme.md   one page per surface
assets/interfaces/               ui-check.mjs, selftest-ui.mjs, fixtures/ (clean.html, bad.html)
```
