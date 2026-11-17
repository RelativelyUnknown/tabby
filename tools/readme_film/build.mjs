// build.mjs: record the README films to animated WebP, and the logo to PNG.
//   node tools/readme_film/build.mjs                    every film, both themes, plus the logo
//   node tools/readme_film/build.mjs hero               one film (hero, effect or quality)
//   node tools/readme_film/build.mjs effect --stills 0,1.2   contact frames only, into $OUT (default ./film-stills)
// Each page exposes window.DUR, window.render(t) and window.READY. Needs Playwright with Chromium, and ffmpeg with libwebp.
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { mkdtempSync, mkdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../..");
const FPS = 30;
// loop: true repeats forever (frames 0 .. DUR, end excluded, so the seam is clean); false plays once and holds the last frame.
const FILMS = {
  hero: { page: "hero.html", out: "tabby-meow", w: 1280, h: 360, loop: true, logo: true },
  effect: { page: "effect.html", out: "tabby-effect", w: 760, h: 384, loop: false },
  quality: { page: "quality.html", out: "tabby-quality", w: 760, h: 448, loop: false },
};
const require = createRequire(import.meta.url);
let pw;   // a local install first, then a global one
try { pw = require("playwright"); } catch { pw = require(path.join(execFileSync("npm", ["root", "-g"]).toString().trim(), "playwright")); }
const { chromium } = pw;
const args = process.argv.slice(2);
const stills = args.includes("--stills") ? args[args.indexOf("--stills") + 1].split(",").map(Number) : null;
const only = args.find((a) => FILMS[a]);

const browser = await chromium.launch();
async function open(file, q, w, h, dpr = 1) {
  const p = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: dpr });
  await p.goto("file://" + path.join(here, file) + "?" + q);
  await p.waitForFunction(() => window.READY === true);
  return p;
}
for (const [name, film] of Object.entries(FILMS)) {
  if (only && name !== only) continue;
  for (const theme of ["light", "dark"]) {
    const p = await open(film.page, `theme=${theme}&scale=1.5`, film.w, film.h);
    const canvas = await p.$("canvas");
    if (stills) {
      const dir = process.env.OUT || "film-stills"; mkdirSync(dir, { recursive: true });
      for (const t of stills) { await p.evaluate((t) => window.render(t), t); await canvas.screenshot({ path: `${dir}/${name}-${theme}-${t}.png`, omitBackground: true }); }
      continue;
    }
    const dir = mkdtempSync(path.join(tmpdir(), "tabby-film-"));
    const dur = await p.evaluate(() => window.DUR), n = Math.round(dur * FPS) + (film.loop ? 0 : 1);
    for (let i = 0; i < n; i++) {
      await p.evaluate((t) => window.render(t), Math.min(i / FPS, dur));
      await canvas.screenshot({ path: path.join(dir, `f${String(i).padStart(4, "0")}.png`), omitBackground: true });
    }
    const out = path.join(root, `assets/${film.out}-${theme}.webp`);
    execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", String(FPS), "-i", path.join(dir, "f%04d.png"),
      "-c:v", "libwebp_anim", "-lossless", "0", "-q:v", "82", "-compression_level", "6", "-loop", film.loop ? "0" : "1", "-pix_fmt", "yuva420p", out]);
    rmSync(dir, { recursive: true });
    if (film.logo) {
      const l = await open(film.page, `theme=${theme}&logo=1&scale=2`, 360, 360, 2);
      await l.evaluate(() => window.render(0));
      await (await l.$("canvas")).screenshot({ path: path.join(root, `assets/tabby-logo-${theme}.png`), omitBackground: true });
    }
    console.log("wrote", out);
  }
}
await browser.close();
