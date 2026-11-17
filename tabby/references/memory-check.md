# Check the saved section against the code

Before new work (a feature, a refactor, a release), compare the `## Tabby` section with the code: commits since `reviewed:` (`git rev-list --count <sha>..HEAD`) and whether `pyproject.toml`, `Cargo.toml`, `Makefile` or `.github` changed (`git diff --stat <sha>..HEAD -- ...`). Report the evidence and ask only about changed facts.

Also check the section against what the code already has: a `growth:` item that is built (a Rust crate, a second data source, an endpoint) belongs in `goals:`, and `map:` must describe the modules that exist. Fix those lines from the code without asking; the code is the record. Ask only where the code cannot say (whether a goal changed).

At the end of the task, update the lines your work made untrue, add decisions the user made in the conversation to `decided:`, and set `reviewed:`.
