//! Canonical song keys: the rules for "are these two plays the same song?".
//!
//! The big idea is a *whitelist*. We strip only tags we know are noise
//! ("Remastered 2020", "feat. X", "Explicit", ...). Any other tag stays in the
//! key, so "Espresso (sped up)" and "Espresso" are different songs, and so are
//! live versions, remixes, acoustic versions, and anything we've never heard of.
//! The failure mode is "two entries that could have merged", never "two
//! different songs wrongly merged".

use unicode_normalization::UnicodeNormalization;
use unicode_normalization::char::is_combining_mark;

/// Two plays with equal `SongKey`s are the same song.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct SongKey {
    pub artist: String,
    pub title: String,
}

pub fn song_key(artist: &str, track: &str) -> SongKey {
    SongKey {
        artist: artist_key(artist),
        title: title_key(track),
    }
}

/// Lowercase, strip accents and apostrophes, turn all other punctuation into
/// single spaces. "Don’t Stop Me Now!" and "Don't stop me now" both become
/// "dont stop me now".
fn fold(s: &str) -> String {
    let s = s.replace('&', " and ");
    let mut out = String::with_capacity(s.len());
    let mut pending_space = false;
    // nfkd() splits "é" into "e" + a combining accent, which we then drop.
    for c in s.nfkd().filter(|c| !is_combining_mark(*c)) {
        if matches!(c, '\'' | '’' | '‘' | 'ʼ' | '`' | '´') {
            continue; // apostrophes vanish: don't -> dont
        }
        if c.is_alphanumeric() {
            if pending_space && !out.is_empty() {
                out.push(' ');
            }
            pending_space = false;
            out.extend(c.to_lowercase());
        } else {
            pending_space = true;
        }
    }
    out
}

/// A title is a run of plain text and "tags": `(...)`, `[...]`, or ` - ...`.
enum Piece<'a> {
    Text(&'a str),
    Tag(&'a str),
}

fn split_title(title: &str) -> Vec<Piece<'_>> {
    fn push<'a>(pieces: &mut Vec<Piece<'a>>, s: &'a str, is_tag: bool) {
        if s.trim().is_empty() {
            return;
        }
        pieces.push(if is_tag {
            Piece::Tag(s)
        } else {
            Piece::Text(s)
        });
    }

    let mut pieces = Vec::new();
    let mut start = 0; // where the piece we're currently reading began
    let mut depth = 0u32; // bracket nesting
    let mut in_dash_tag = false;

    for (i, c) in title.char_indices() {
        let after = i + c.len_utf8();
        match c {
            '(' | '[' => {
                if depth == 0 {
                    push(&mut pieces, &title[start..i], in_dash_tag);
                    start = after;
                    in_dash_tag = false;
                }
                depth += 1;
            }
            ')' | ']' if depth > 0 => {
                depth -= 1;
                if depth == 0 {
                    pieces.push(Piece::Tag(&title[start..i]));
                    start = after;
                }
            }
            // " - " with spaces on both sides (so "Spider-Man" is untouched).
            '-' | '–' | '—'
                if depth == 0
                    && title[..i].ends_with(char::is_whitespace)
                    && title[after..].starts_with(char::is_whitespace) =>
            {
                push(&mut pieces, &title[start..i], in_dash_tag);
                start = after;
                in_dash_tag = true;
            }
            _ => {}
        }
    }
    push(&mut pieces, &title[start..], in_dash_tag);
    pieces
}

/// Words allowed inside a "remaster" tag: "2011 Remaster", "Remastered Version",
/// "Digitally Remastered 2009", "Stereo Remaster" ...
const REMASTER_WORDS: &[&str] = &[
    "remaster",
    "remastered",
    "remastering",
    "digitally",
    "version",
    "edition",
    "mono",
    "stereo",
];

/// Tags that are exactly one of these phrases (after folding) are noise.
const NOISE_PHRASES: &[&str] = &[
    "explicit",
    "clean",
    "album version",
    "deluxe",
    "deluxe edition",
    "expanded edition",
    "bonus track",
];

fn is_year(w: &str) -> bool {
    w.len() == 4 && w.bytes().all(|b| b.is_ascii_digit())
}

/// Is this tag one of the ones that doesn't change which song it is?
fn is_noise(tag: &str) -> bool {
    let folded = fold(tag);
    let words: Vec<&str> = folded.split(' ').filter(|w| !w.is_empty()).collect();
    let Some(first) = words.first() else {
        return true; // "()" or "[ ]"
    };
    if matches!(*first, "feat" | "ft" | "featuring") {
        return true;
    }
    if NOISE_PHRASES.contains(&folded.as_str()) {
        return true;
    }
    // "Remastered Live" must NOT match, so *every* word has to be allowed.
    words.iter().any(|w| w.starts_with("remaster"))
        && words
            .iter()
            .all(|w| REMASTER_WORDS.contains(w) || is_year(w))
}

fn title_key(title: &str) -> String {
    let kept: Vec<String> = split_title(title)
        .into_iter()
        .filter_map(|p| match p {
            Piece::Text(t) => Some(t),
            Piece::Tag(t) if !is_noise(t) => Some(t),
            Piece::Tag(_) => None,
        })
        .map(fold)
        .filter(|s| !s.is_empty())
        .collect();
    if kept.is_empty() {
        // The whole title was "noise" (e.g. a song literally called "(Clean)").
        return fold(title);
    }
    kept.join(" ")
}

/// Spotify says "Lady Gaga", Apple says "Lady Gaga & Bruno Mars". Compare only
/// the first-listed artist. This is applied to both sides, so the only cost is
/// that "Simon & Garfunkel" is keyed as "simon", which can't collide in practice.
fn artist_key(artist: &str) -> String {
    const SEPARATORS: &[&str] = &[
        ", ",
        ";",
        " & ",
        " feat. ",
        " feat ",
        " ft. ",
        " ft ",
        " featuring ",
        " x ",
        " / ",
    ];
    let lower = artist.to_lowercase();
    let end = SEPARATORS
        .iter()
        .filter_map(|sep| lower.find(sep))
        .min()
        .unwrap_or(lower.len());
    fold(&lower[..end])
}

#[cfg(test)]
mod tests {
    use super::*;

    fn same(a: (&str, &str), b: (&str, &str)) -> bool {
        song_key(a.0, a.1) == song_key(b.0, b.1)
    }

    #[test]
    fn remasters_merge() {
        let w = "The Weeknd";
        assert!(same(
            (w, "Blinding Lights"),
            (w, "Blinding Lights - Remastered 2020")
        ));
        assert!(same(
            (w, "Blinding Lights"),
            (w, "Blinding Lights (Remastered)")
        ));
        assert!(same(
            (w, "Blinding Lights"),
            (w, "Blinding Lights [2011 Remaster]")
        ));
        assert!(same(
            (w, "Blinding Lights"),
            (w, "Blinding Lights - Digitally Remastered 2009")
        ));
    }

    #[test]
    fn features_merge_across_services() {
        assert!(same(
            ("Lady Gaga & Bruno Mars", "Die With A Smile"),
            ("Lady Gaga", "Die With A Smile (feat. Bruno Mars)"),
        ));
        assert!(same(("A", "Song"), ("A", "Song - feat. B")));
        assert!(same(("A", "Song"), ("A", "Song [ft. B]")));
    }

    #[test]
    fn curly_apostrophes_and_case_merge() {
        assert!(same(
            ("Queen", "Don’t Stop Me Now"),
            ("Queen", "Don't Stop Me Now")
        ));
        assert!(same(
            ("Queen", "Don't Stop Me Now"),
            ("QUEEN", "don't stop me now")
        ));
    }

    #[test]
    fn accents_and_ampersands_merge() {
        assert!(same(("Beyoncé", "Halo"), ("Beyonce", "Halo")));
        assert!(same(("A", "Rock & Roll"), ("A", "Rock and Roll")));
    }

    #[test]
    fn different_versions_stay_separate() {
        let s = "Sabrina Carpenter";
        assert!(!same((s, "Espresso"), (s, "Espresso (sped up)")));
        assert!(!same((s, "Espresso"), (s, "Espresso - Sped Up")));
        assert!(!same((s, "Espresso"), (s, "Espresso (Live)")));
        assert!(!same((s, "Espresso"), (s, "Espresso (Remix)")));
        assert!(!same((s, "Espresso"), (s, "Espresso - Remastered Live")));
        assert!(!same((s, "Espresso"), (s, "Espresso (Acoustic)")));
    }

    #[test]
    fn sped_up_spellings_match_each_other() {
        let s = "Sabrina Carpenter";
        assert!(same((s, "Espresso (sped up)"), (s, "Espresso - Sped Up")));
        assert!(same(
            (s, "Espresso (Sped Up)"),
            (s, "Espresso [sped up] (Remastered)")
        ));
    }

    #[test]
    fn different_songs_stay_separate() {
        assert!(!same(("X", "Home"), ("Y", "Home")));
        assert!(!same(("X", "Home"), ("X", "Homes")));
    }

    #[test]
    fn titles_with_meaningful_brackets_and_hyphens_survive() {
        // Not noise, so kept: these must not collapse into one another.
        assert!(!same(
            ("Stones", "(I Can't Get No) Satisfaction"),
            ("Stones", "Satisfaction")
        ));
        assert!(same(("A", "Spider-Man"), ("A", "Spider Man")));
        assert!(!same(("A", "Stay (With Me)"), ("A", "Stay")));
    }

    #[test]
    fn all_noise_title_falls_back() {
        assert_eq!(title_key("(Clean)"), "clean");
    }

    #[test]
    fn title_keys_look_right() {
        assert_eq!(
            title_key("Blinding Lights - Remastered 2020"),
            "blinding lights"
        );
        assert_eq!(title_key("Espresso (sped up)"), "espresso sped up");
        assert_eq!(artist_key("Lady Gaga & Bruno Mars"), "lady gaga");
        assert_eq!(artist_key("Tyler, The Creator"), "tyler");
        assert_eq!(artist_key("AC/DC"), "ac dc");
    }
}
