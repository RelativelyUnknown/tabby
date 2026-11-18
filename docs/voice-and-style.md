# Voice, style and AI writing patterns

Voice and content rules for any page, word choices, an editing pass and the patterns that mark generated text. A project's own style guide wins over this file.

## Voice and structure

The reader is mid-task and reads in order, looking for the next thing to do. Ask of each sentence: what does this let them do or understand, and is it the first thing they need? Put the point first, keep sentences single-purpose, and cut anything that announces instead of informing.

- Address the reader as "you". Present tense ("returns", not "will return"). Active voice; name who acts. Imperative for instructions ("Run", "Set").
- Lead with the point. A page's first sentence says what it is for; a section's first sentence answers its heading. No introductions that announce what follows.
- Sentence-case headings that name the task or topic: "Configure retries", not "Retries Configuration Options". Task headings start with a verb.
- Put the condition before the instruction: "To export a table, run ...". Put the goal before the location: "To change the schema, edit `config.toml`".
- Numbered lists for sequences, one action per step, with the expected result when the reader needs to check it. Bullets for unordered items. List items share a grammatical form.
- One idea per sentence; aim for under 25 words. Short paragraphs. Tables for options and comparisons with more than two attributes.
- Link text names its destination ("see [Authentication](#authentication)"); never "click here", "this" or a bare URL in prose.
- Code font for code, commands, file names, paths, parameters and literal values. Bold only for UI labels. Italics for a term at its definition, if at all.
- Use one term per concept, defined once, matching the API and UI exactly. Do not vary terms for style.

### Content rules

- **Be specific.** Numbers, versions, units, exact error messages, defaults. "Retries 3 times with exponential backoff starting at 1 s" beats "retries automatically".
- **Timeless.** No "currently", "now", "new", "recently", "soon", or promises about future features. History belongs in the changelog; plans belong in the issue tracker.
- **No minimizers, puffery or filler** ("simply", "just", "easy", "powerful", "seamless", "blazing fast", "in order to", "note that"). A speed claim comes with a benchmark or is cut.
- **Affirmative and calm.** Say what works and how to do it. Reserve warnings for data loss, security and crashes, and state the consequence: "Deletes the table and its history; this cannot be undone." Collect security considerations in their own section and link to it.
- **Global readers.** No idioms, jokes or Latin abbreviations (write "for example", "that is"). Expand an acronym on first use unless it is better known than its expansion (HTML, URL, API).
- **Inclusive and accessible.** "allowlist/denylist", "primary/replica"; "they" for an unknown person. Alt text that states what an image shows; never rely on color alone.
- **Honest scope.** State requirements, supported versions and known limitations where readers will look for them. Do not hide a limitation in a footnote.

## Word choice, headings, notes, dates

### Words to replace

| Instead of | Write |
| --- | --- |
| utilize, leverage, make use of | use |
| in order to | to |
| is able to, has the ability to | can |
| due to the fact that | because |
| prior to, subsequent to | before, after |
| in the event that | if |
| a number of | some, or the number |
| e.g., i.e., etc., via, vs. | for example, that is, and so on, through/by, versus |
| please (in instructions) | (delete) |
| simply, just, easily, obviously, of course | (delete) |
| we (meaning the product or the authors) | the name of the product, or rephrase |
| will (for behavior) | present tense |
| click on | click, or select |
| whitelist, blacklist, master/slave | allowlist, denylist, primary/replica |
| sanity check, dummy value | quick check, placeholder |

### Headings and titles

- Sentence case: capitalize the first word and proper nouns only.
- Task pages and sections: bare imperative verb ("Install the CLI"); conceptual pages: noun phrase ("Authentication model"); reference: the object's name.
- No punctuation at the end, no code-only headings where a phrase works, no emoji, no "Introduction" as the only first heading.
- Do not skip levels; one H1 per page.

### Notes and warnings

- Use admonitions rarely; when everything is a note, nothing is.
- Note: helpful but skippable. Important: needed for success. Warning or caution: risk of data loss, security exposure or a crash; say what happens and how to avoid it.
- Never put essential steps only inside a note.

### Numbers, dates and units

- Numerals for 10 and up and any measurement; spell out one to nine in prose. Units with a space: `500 ms`, `16 GB`.
- Unambiguous dates: `2026-11-03` in technical text, "November 3, 2026" in prose; never `11/03/26`. Time zones explicit (UTC).

## Editing pass

### An editing pass

0. Before cutting, mark what must survive: names, numbers and units, commands, paths, links, conditions, trade-offs, stated uncertainty, and every "not", "only" and "except". After the pass, compare with the original and restore any that were lost.
1. Read only the headings and first sentences. Do they tell the story? Fix the outline before the prose.
2. For each paragraph: delete the sentence that adds least. Repeat until deleting hurts.
3. For each sentence: find the actor and the action; make the actor the subject and the action the verb.
4. For each word: replace long words with short ones, and delete the ones that carry nothing.
5. Read it aloud and fix what trips you.

## AI writing patterns

Language models drift toward the statistical middle: safe, inflated, generic phrasing that reads as filler. This file lists the patterns that matter most in technical documentation. It condenses Wikipedia's "Signs of AI writing" editor guide, as packaged in softaworks' *writing-clearly-and-concisely*, and adapts it to docs. the word-level patterns come first; the structural ones need a careful read.

### Word level

- **Puffery**: powerful, robust, seamless, cutting-edge, comprehensive, pivotal, crucial, game-changing, blazing fast.
- **AI vocabulary**: delve, leverage, utilize, foster, realm, tapestry, multifaceted, embark, elevate, unlock, empower, streamline, harness, holistic, landscape, ever-evolving.
- **Hedging stacks**: "may potentially", "can help to", "generally tends to".
- **Empty -ing tails**: "..., ensuring reliability", "..., highlighting its flexibility", "..., making it ideal for".

### Sentence level

- **Negative parallelism**: "It's not just a parser, it's a platform." State what it is.
- **Rule of three**: lists padded to three items or three adjectives ("fast, flexible, and reliable") regardless of content.
- **False range**: "from small scripts to enterprise pipelines" when nothing in the docs is about either end.
- **Elegant variation**: calling one thing "the client", "the connector" and "the tool" in one page. Docs need one term.
- **Signposting**: "Let's dive in", "In this section, we will explore", "Now that we've covered X, let's look at Y".
- **Summary echo**: "In summary", "Overall", "In conclusion" followed by a restatement of the page.
- **Vague attribution**: "is widely regarded as", "many developers find". Name the source or cut it.

### Structure and formatting

- Bold sprinkled on phrases in every paragraph.
- Bulleted lists where each item is a bold label, a colon and a sentence ("**Speed:** It is fast."). Use a table or prose.
- Headings in Title Case, often with emoji.
- Em dashes as the default punctuation.
- Sections that exist because a template has them: "Key features", "Benefits", "Conclusion", "Future enhancements".
- Every section the same length, regardless of how much there is to say.

### Content

- **Invented facts**: options, flags, defaults, version numbers or API names that do not exist. Check each against the code or `--help` output.
- **Fake specifics**: benchmark numbers or "99.9%" claims without a source.
- **Generic advice** that applies to any software ("follow best practices", "ensure proper error handling").
- **Conversation residue**: "As requested", "Here is the updated documentation", "I hope this helps", "Let me know if".
- **Unrequested sections**: troubleshooting, FAQ or roadmap pages invented to look complete.
- **Knowledge-cutoff hedges**: "as of my last update". Documentation states facts verified now, or links to the source.

### Rewrites

| Generated | Rewritten |
| --- | --- |
| "This powerful library seamlessly integrates with your existing workflow, empowering developers to unlock new possibilities." | "The library reads and writes Parquet files that pandas, Polars and DuckDB can open." |
| "It's important to note that the cache may potentially become stale." | "The cache is not invalidated when the source file changes. Call `cache.clear()` after editing it." |
| "In this section, we'll delve into configuration options." | (delete; the heading says it) |
| "**Fast:** Optimized for performance." | "Loads a 1 GB file in 2 s on an M2 laptop ([benchmark](https://example.com/benchmarks))." or delete |
| "Whether you're a beginner or an expert, this guide has you covered." | (delete) |
