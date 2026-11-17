# Pilot: the interview for an image editor

The first idea I tried before switching to my own project: a Python image editor where the user mentions other formats, SVG and Rust for later. Only the interview ran. It shows how Tabby reacts when the user names future features: SVG went into `growth:` with a layout that keeps the edits format-agnostic, and Rust got a measure-first plan.

## Round 1

**Me:**

> /tabby:interview
>
> ok so context: i'm pretty new to coding (like a few months of python, did some tutorials). i wanna build a lil image editing app in python. nothing crazy, just a simple one for now. go

**Agent** *(tools: Bash 1, Read 2; $0.08)*:

The folder is empty: no commits, no files. So this is a new project and there's no code to research. I did see Python 3.13 and `uv` installed here, which matters for a later round.

Round 1 has three questions. Each has a suggested answer, so you can reply "all good" or change any of them.

1. **What should the app do first?**
   Suggested: open a photo, then do 3 or 4 basic edits (rotate, crop, brightness, grayscale), then save it. Evidence: you said "simple", and this list is small enough to finish. Others could be resize, filters or text.

2. **Who is it for, and how will they run it?**
   Suggested: just you, as a learning project. It runs on your own computer, and you can show it to friends later. Evidence: nothing in the folder says otherwise. This choice affects whether it should have a window, or be a command you type, or run in a browser.

3. **What counts as "done" for version 1?**
   Suggested: you can edit one of your own photos with it and save the result without breaking the original. Evidence: a goal you can check by hand suits a first project.

Later rounds will cover the shape of the app (window vs. command line vs. browser) and the tools. I'm leaning toward `uv` with `Pillow`, the standard Python image library, but I'll ask about that then. I've written no code and no `AGENTS.md` yet.

## Round 2

**Me:**

> 1. yeah ur list is fire. rotate, crop, resize, brightness, grayscale. maybe a blur too bc that's fun
> 2. just me for now, learning project. ngl i'd love it to be a command i type first (feels hacker-y lol), maybe a window later
> 3. yep that's it, original never gets overwritten
>
> oh also lowkey important: rn it's jpg/png but i wanna edit other formats too, like webp and maybe heic from my iphone. and in the future i def want SVG support (i do some logo stuff). and someone on tiktok said rust makes python stuff fast so maybe i'll put some rust in it later for the heavy filters? idk if that's dumb

**Agent** *(tools: none; $0.10)*:

Got it. Your list is rotate, crop, resize, brightness, grayscale and blur, and the original never gets overwritten. It's just for you, as a command first. Rust isn't dumb, and I've answered it below.

**Your format questions**
- **WebP:** the image library I suggested, Pillow, handles it out of the box.
- **HEIC:** it needs one small add-on (`pillow-heif`), but it's doable.
- **SVG:** SVG is different from the others. JPG, PNG and WebP are grids of pixels. SVG is a set of shapes and paths, so "blur" or "crop" doesn't mean the same thing. Pillow can't edit it. You could convert it to pixels and edit that, but you'd lose the logo-friendly scaling. Real SVG editing is a separate project, so I'd leave it for later.
- **Rust:** Pillow is already written in C, so your filters will be fast enough at first. Rust makes sense once you've measured something slow, not before. I'd write it down as a "maybe later" and move on.

Round 2 has three questions:

1. **What form should it take?**
   Suggested: a command like `pic input.jpg --rotate 90 --blur 2 -o out.jpg`, built with `argparse`, which comes with Python so it adds nothing to install. Keep the editing code separate from the command-line part, so a window can reuse it later. Evidence: you want a command first and a window later, and this is what makes that cheap.

2. **Which formats come first?**
   Suggested: version 1 is JPG, PNG and WebP. Then add HEIC. SVG goes in `out-of-scope` for now, as a possible separate project. Evidence: Pillow covers the first three with no extras. The folder has nothing that says otherwise.

3. **Which tools?**
   Suggested: `uv` to manage the project, Pillow for images, `pytest` for tests and `ruff` to tidy the code. Evidence: `uv` is already installed here (`/root/.local/bin/uv`) and Python is 3.13. The other option is plain `pip` with `venv`, which is more familiar from tutorials but slower to set up.

Reply "all good" or change any of them. Round 3 will be about the rules for the project, like asking before adding a dependency and never touching your originals. I still haven't written any code.

## Round 3

**Me:**

> 1. yes the pic command thing is exactly the vibe. separate editing code from cli bc window later
> 2. jpg png webp first, then heic. but pls don't put svg in out-of-scope 😭 i'm not doing it now but i DO want it eventually, like open an svg, resize/rotate it, export to png. i don't want to have to rewrite everything when i get there
> 3. uv + pillow + pytest + ruff, all good. never used uv but down to learn
>
> and ok fair on rust, measure first. but i actually wanna learn rust thru this so keep it on the list, blur seems like the obvious one

**Agent** *(tools: none; $0.12)*:

The SVG plan changes how the code is laid out, so here is how I'll write it down.

- **SVG:** it goes in `growth`, not `out-of-scope`.
- **Structure:** the editing code works on one common in-memory image. Each file format gets its own small "open" and "save" piece. For SVG, that piece would open the file, draw it into pixels and hand it to the same editing code. Nothing in the edits has to change when SVG arrives.
- **Size caveat:** for the best quality, an SVG should be resized before it's drawn into pixels, not after. That's an SVG-time detail, but I'll note it in `gotchas` so it doesn't surprise you.

Rust stays on the list with blur as the first candidate. Blur will first be written with Pillow. Rust comes after, as a drop-in replacement with the same inputs and outputs, and a test that compares the two.

This is the last round, and it's about boundaries:

1. **How should it protect your originals?**
   Suggested: the output is named `photo_edited.jpg` by default. It refuses to write if the output path is the input file, or if the output file already exists, unless you add `--force`. Evidence: "original never gets overwritten" is your success test, and this is the usual way to enforce it.

2. **What should I check with you before doing it?**
   Suggested: adding a dependency, changing a command flag (since the `pic` command is what you'll be typing), and adding Rust or any build step. Evidence: you're learning, and each of these changes how the project works. I'd also write `always: run pytest and ruff before saying done`.

3. **What about your own photos?**
   Suggested: `.gitignore` common image files from the start, and only commit made-up test images that I generate. Evidence: iPhone photos can carry location data and other private details, and they're easy to commit by accident.

Next I'll restate everything in your words for a yes before I save it to `AGENTS.md`. I'll still write no code.

## Restate

**Me:**

> 1. yes --force thing is smart
> 2. yep all of those
> 3. omg didn't even think about location data. yes gitignore them

**Agent** *(tools: none; $0.14)*:

Here is the section as I'd save it. It isn't written yet. Reply "yes" to save it, or tell me which lines to change.

```markdown
## Tabby
reviewed: 2026-11-17 @ (no commits yet)
purpose: `pic`, a command-line image editor you learn Python (and later Rust) with
users: just you, on your own computer; a window later
goals: edit one of your own photos and save it without touching the original; rotate, crop, resize, brightness, grayscale, blur; the editing code works without the command line
growth: 1) HEIC  2) SVG (open, resize/rotate, export to PNG)  3) a window  4) Rust blur, after a Pillow version works
workload: one image at a time, run by hand; no server, no concurrency
map: (assumed, nothing exists yet) editing code in one package, with no command-line code in it; one small open/save piece per format; a thin `pic` command on top
conventions: edits work on one common in-memory image; each format is added as its own open/save piece, so edits never change when a format arrives
gotchas: SVG is shapes, not pixels. Resize it before drawing it into pixels, not after. HEIC needs `pillow-heif`. Photos can carry location data
out-of-scope: editing SVG as shapes (only open, resize/rotate, export to PNG); a server or web app
constraints: python 3.13; `argparse` for the command (nothing extra to install); formats JPG, PNG, WebP first
always: run pytest and ruff before saying done
ask-first: new dependency, change to a command flag, adding Rust or any build step
never: overwrite or write onto an original file; commit real photos
  default output is `<name>_edited.<ext>`; refuse if output is the input or already exists, unless `--force`
kind: code
modules: development, review, documentation
docs: README
commands: `uv run pytest` and `uv run ruff check`; targeted: `uv run pytest path::test`
open: how the Rust blur gets built into the project; when to start a window; release or sharing

## Python defaults
runner: uv
build: (assumed) uv's default
test: pytest
lint: ruff
types: none yet
ci: none
python: 3.13
```

Two things to check:
- **Marked as assumed:** `map`, `build`, `types: none`, `ci: none` and `docs: README`. They're my defaults, since nothing exists to confirm them.
- **`.gitignore`:** it will list image files like `*.jpg`, `*.png`, `*.webp` and `*.heic`. The made-up test images I generate will go in a `tests/samples/` folder, with a `!tests/samples/` exception so they're committed.

Is this right?

## Save

**Me:**

> yes save it 🙏

**Agent** *(tools: Write 2; $0.17)*:

I saved the `## Tabby` section and the `## Python defaults` section to `AGENTS.md`, exactly as you approved them. I also created a `.gitignore`, which you agreed to in question 3. It ignores `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic`, `.heif` and the usual Python and tool caches. The made-up test images in `tests/samples/` are exempt, so those can be committed. I haven't run or committed anything, and I wrote no source code.

The lines still marked as guesses are `map`, `build`, `types`, `ci` and `docs`. The `open:` list holds the questions I'll ask when they come up: how the Rust blur gets built, when to start the window, and sharing.

When you're ready, ask for the first piece of the app. I'd start with `uv init`, then the editing code with one edit and its test, then the `pic` command. Since you've never used `uv`, I'll explain each command as we go.
