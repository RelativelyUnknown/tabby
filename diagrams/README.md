# diagrams

A skill of the Tabby plugin for pictures of how a system works: a static diagram (SVG) or a short explainer animation (one self-contained HTML file). It loads when you ask for a diagram, flowchart, architecture picture, state or entity-relationship diagram, deployment picture or animation. A screen, dashboard or docs site is [`frontend`](../frontend/).

**Entry point:** [`SKILL.md`](SKILL.md). The two quickstarts are [`diagrams/quickstart.md`](diagrams/quickstart.md) and [`animation/quickstart.md`](animation/quickstart.md).

## The problem it solves

An agent asked for a diagram usually hand-writes SVG coordinates. The result overlaps labels, hides arrows behind boxes, prints text too small to read in a README column, and draws parts that the code does not have. Tabby instead writes a small JSON spec, builds the SVG with a script, and runs a checker that fails on those faults. Content comes from the code: a part or arrow nobody can point to is left out or marked `(assumed)`.

## What you get

The built diagram for one of the shipped examples ([`assets/diagram/examples/service-request.json`](assets/diagram/examples/service-request.json)), 9 lines of spec per node and edge:

<p align="center"><img src="assets/diagram/examples/service-request.svg" width="760" alt="Diagram: a Client posts to an API, which enqueues to a Redis queue (the focal node); a Python worker consumes, writes to Postgres and retries to the queue. All inside a box labelled Your service."></p>

Diagram types: architecture, dependency graph, deployment, entity-relationship, flowchart, layer stack, sequence, state machine, swimlane and timeline ([`diagrams/types.md`](diagrams/types.md)). One type per picture, at most 9 nodes, 12 connections and one focal node; more than that is two pictures.

## How it works

```bash
node assets/diagram/make.mjs spec.json docs/diagram.svg     # build from the spec
python3 assets/diagram/check.py docs/diagram.svg            # exit 0 is required; fix the spec, not the SVG
node assets/diagram/render.mjs docs/diagram.svg --scale 2   # optional: light and dark PNGs, to look at
```

The builder places nothing by guesswork: nodes sit on a 4 px grid in zones, icons come from the Tabler set (`make.mjs --icons <word>` lists them), and the look comes from one-accent tokens. If the repository has a `design.md`, the agent reads it first, maps its colours and font into the spec, and says what it did not apply.

### What the checker fails on

`check.py` reads the structure the builder writes. Run on a spec where a node was moved too close to its neighbour:

```
FAIL pill-clearance bad.svg: label client>api overlaps node client
FAIL pill-clearance bad.svg: label client>api overlaps node api
FAIL pill-clearance bad.svg: label client>api is within 16 px of its arrowhead; widen the gap or shorten the label
```

(exit code 2). The full list: a missing title or description for screen readers, anything outside the viewBox, diagonal lines, overlapping nodes, a line crossing a node it does not connect, a label on top of a node or too near an arrowhead, text under 10 px as shown in a README column, too many nodes, connections or focal nodes, contrast below the minimum in light or dark, and (warning) a node off the grid.

## Animations

The same spec plus a `story` of at most 8 steps, every step with a `why`, at most 2 running at once. Steps are `reveal`, `draw`, `packet` (a dot along a path), `pulse`, `badge`, `active` and `hide`.

```bash
node assets/animation/animate.mjs spec.json docs/flow.html
node assets/animation/check-motion.mjs docs/flow.html       # exit 0 required; needs Playwright
```

The page is complete without JavaScript and makes no network request. Under `prefers-reduced-motion` it shows the finished picture and offers "Play once". `check-motion.mjs` fails a step with no purpose, more than 8 steps or 2 at once, anything still moved at the loop's start or end (a jump when it restarts), a page that does not stand on its finished picture under reduced motion, any non-local request, a script error and missing controls. It writes a contact sheet of stills (start, 25%, 50%, 75%, end and the last frame of the loop) to open and look at. On the shipped `flow.json` template all checks pass. Video is made only on request ([`animation/pipeline-and-formats.md`](animation/pipeline-and-formats.md), needs ffmpeg).

## Needs

- Node 22 for the builders. The checker `check.py` is Python standard library only.
- Playwright Chromium to render PNGs and to run `check-motion.mjs`; ffmpeg only for video. The agent asks before installing any of them. If Playwright is missing it says the picture was checked but not rendered, or the motion was not checked.
- Playwright here is the Node package; Python's `import playwright` says nothing about it.

## Limits

- The checker measures geometry and contrast. Whether the focal node reads first, whether the picture answers the reader's question and whether the words fit are for a person to look at.
- Hand-drawn SVG without the builder's data attributes gets only the accessibility, viewBox, text-size and contrast checks.
- The font falls back to a system stack unless `@fontsource/inter` is installed (the renderer prints a note).

## Layout

```
SKILL.md
diagrams/        quickstart, choosing the type, style and theme mapping, connectors and icons, one section per type
animation/       quickstart, motion principles, pipeline and formats
assets/diagram/  make.mjs (builder), check.py, render.mjs, selftest.py, examples/ (four specs with their SVGs)
assets/animation/ animate.mjs, check-motion.mjs, render-video.mjs, selftest-motion.mjs, templates/
assets/icons/    the Tabler outline icon set
SOURCE.md        the projects whose ideas this adapts, with licences
```
