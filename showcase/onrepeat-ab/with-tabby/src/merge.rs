//! Decides which plays are the same song.
//!
//! Two plays match when their titles agree after dropping remaster and
//! "feat." tags, and their first artist agrees. Anything else in a title
//! ("sped up", "live", "remix") makes it a different song.
//! Mirrors `tests/reference_merge.py`.

const FEAT_WORDS: [&str; 5] = ["feat", "feat.", "ft", "ft.", "featuring"];

/// Words split on whitespace, which like Python includes `\x1c`..`\x1f`.
fn words(text: &str) -> impl Iterator<Item = &str> {
    text.split(|c: char| c.is_whitespace() || ('\x1c'..='\x1f').contains(&c))
        .filter(|w| !w.is_empty())
}

/// Lowercase, straighten curly quotes and dashes, collapse whitespace.
fn fold(text: &str) -> String {
    let straight: String = text
        .chars()
        .map(|c| match c {
            '\u{2019}' | '\u{2018}' | '\u{02bc}' => '\'',
            '\u{201c}' | '\u{201d}' => '"',
            '\u{2013}' | '\u{2014}' => '-',
            other => other,
        })
        .collect();
    words(&straight.to_lowercase())
        .collect::<Vec<_>>()
        .join(" ")
}

/// "remastered", "2011 remaster", "remastered version": nothing else.
fn is_remaster(segment: &str) -> bool {
    let mut any = false;
    for w in words(segment) {
        if w.starts_with("remaster") {
            any = true;
        } else if !(w == "version"
            || w == "digital"
            || (w.len() == 4 && w.bytes().all(|b| b.is_ascii_digit())))
        {
            return false;
        }
    }
    any
}

/// A tag that names the same recording: a remaster, or "feat. x".
fn is_noise(segment: &str, in_brackets: bool) -> bool {
    let Some(first) = words(segment).next() else {
        return false;
    };
    is_remaster(segment) || FEAT_WORDS.contains(&first) || (in_brackets && first == "with")
}

/// Remove `(...)` and `[...]` groups that are only a noise tag.
fn strip_noisy_brackets(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut rest = text;
    while let Some(open) = rest.find(['(', '[']) {
        let (before, from_open) = rest.split_at(open);
        let after_open = from_open.get(1..).unwrap_or_default();
        let group = after_open
            .find(['(', '[', ')', ']'])
            .filter(|&i| {
                after_open
                    .get(i..)
                    .is_some_and(|s| s.starts_with([')', ']']))
            })
            .and_then(|i| Some((after_open.get(..i)?, from_open.get(..i + 2)?, i)));
        if let Some((inner, whole, i)) = group {
            if is_noise(inner, true) {
                out.push_str(before.trim_end());
            } else {
                out.push_str(before);
                out.push_str(whole);
            }
            rest = after_open.get(i + 1..).unwrap_or_default();
        } else {
            out.push_str(before);
            out.push_str(from_open.get(..1).unwrap_or_default());
            rest = after_open;
        }
    }
    out.push_str(rest);
    out
}

fn title_key(track: &str) -> String {
    let text = strip_noisy_brackets(&fold(track));
    let mut parts = text.split(" - ");
    let first = parts.next().unwrap_or_default();
    let kept: Vec<&str> = std::iter::once(first)
        .chain(parts.filter(|p| !is_noise(p, false)))
        .collect();
    let key = kept.join(" - ").trim().to_owned();
    if key.is_empty() { fold(track) } else { key }
}

/// First artist only: "Lady Gaga & Bruno Mars" and "Lady Gaga" match.
fn artist_key(artist: &str) -> String {
    let text = fold(artist);
    let head = text.get(..text.find([',', ';', '&']).unwrap_or(text.len()));
    let mut kept: Vec<&str> = Vec::new();
    for (i, word) in words(head.unwrap_or_default()).enumerate() {
        if i > 0 && (FEAT_WORDS.contains(&word) || word == "with" || word == "x") {
            break;
        }
        kept.push(word);
    }
    if kept.is_empty() {
        text
    } else {
        kept.join(" ")
    }
}

#[must_use]
pub fn song_key(track: &str, artist: &str) -> (String, String) {
    (title_key(track), artist_key(artist))
}

#[cfg(test)]
mod tests {
    use super::song_key;

    fn same(a: (&str, &str), b: (&str, &str)) -> bool {
        song_key(a.0, a.1) == song_key(b.0, b.1)
    }

    #[test]
    fn remaster_tags_are_dropped() {
        assert!(same(
            ("Blinding Lights", "The Weeknd"),
            ("Blinding Lights - Remastered 2020", "The Weeknd")
        ));
    }

    #[test]
    fn feat_and_curly_apostrophe_are_dropped() {
        assert!(same(
            ("Die With A Smile", "Lady Gaga"),
            (
                "Die With A Smile (feat. Bruno Mars)",
                "Lady Gaga & Bruno Mars"
            )
        ));
        assert!(same(
            ("Don\u{2019}t Stop Me Now", "Queen"),
            ("Don't Stop Me Now", "Queen")
        ));
    }

    #[test]
    fn sped_up_is_its_own_song() {
        assert!(!same(
            ("Espresso", "Sabrina Carpenter"),
            ("Espresso (sped up)", "Sabrina Carpenter")
        ));
    }
}
