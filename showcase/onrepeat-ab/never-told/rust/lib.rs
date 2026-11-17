//! songkey: decide when two track listings are "the same song".
//!
//! The one public idea is [`song_key`]: give it a title and an artist as a
//! service shows them, get back a canonical key. Two listings are the same
//! song exactly when their keys are equal, so the Python side can just use
//! the key as a dictionary key.
//!
//! The rules, in one place:
//!
//! * Case, accents, curly vs straight quotes, and punctuation don't matter.
//! * Boilerplate in the title is dropped: `(feat. X)`, `- Remastered 2020`,
//!   `(Deluxe)`, `- Single Version`, ...
//! * Only *known* boilerplate is dropped. Anything else in brackets stays, so
//!   `Espresso (Sped Up)` keeps its own key, as do remixes, live versions, etc.
//! * Only the first credited artist counts, so `Lady Gaga & Bruno Mars`
//!   (Apple) and `Lady Gaga` (Spotify) match.

use std::sync::LazyLock;

use regex::Regex;
use unicode_normalization::{char::is_combining_mark, UnicodeNormalization};

#[cfg(feature = "python")]
mod py;

/// A bracketed group with no brackets inside it: `(like this)` or `[this]`.
static BRACKETED: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[(\[]([^()\[\]]*)[)\]]").unwrap());

/// Text that is pure boilerplate, matched against a whole bracket or ` - suffix`.
/// Written in verbose mode (`x`) so each alternative can carry a comment.
static NOISE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?x)^(?:
            (?:feat|featuring|ft|with)\b.*                      # collaborator credits
          | (?:\d{4}\s+)?(?:digital\s+)?re-?master(?:ed)?       # remaster variants...
                (?:\s+(?:version|edition))?(?:\s+\d{4})?        #   ...with the year either side
          | (?:mono|stereo)(?:\s+(?:version|mix))?
          | (?:single|album|radio)\s+(?:version|edit|mix)
          | (?:deluxe|expanded)(?:\s+(?:version|edition))?
          | \d+(?:st|nd|rd|th)\s+anniversary(?:\s+(?:version|edition))?
          | bonus\s+track
          | (?:explicit|clean)(?:\s+version)?
        )$",
    )
    .unwrap()
});

/// Separators between credited artists. `x` and `and` need spaces around them.
static ARTIST_SPLIT: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\s+(?:feat\.?|featuring|ft\.?|with|and|x)\s+|\s*[&,;/]\s*").unwrap()
});

/// The canonical key for a song: `"<title>|<primary artist>"`.
pub fn song_key(title: &str, artist: &str) -> String {
    format!("{}|{}", normalize_title(title), primary_artist(artist))
}

/// Title with boilerplate removed and spelling flattened.
pub fn normalize_title(title: &str) -> String {
    let folded = fold(title);
    let stripped = strip_noise(&folded);
    let squashed = squash(&stripped);
    if !squashed.is_empty() {
        return squashed;
    }
    // Nothing left (e.g. a title that is only "(Remastered)", or only
    // symbols). Better to keep *something* than merge every such title.
    let fallback = squash(&folded);
    if fallback.is_empty() {
        folded.trim().to_string()
    } else {
        fallback
    }
}

/// The first credited artist, flattened the same way as titles.
pub fn primary_artist(artist: &str) -> String {
    let folded = fold(artist);
    let mut end = folded.len();
    for m in ARTIST_SPLIT.find_iter(&folded) {
        // "Tyler, The Creator" is one artist, not "Tyler" plus a guest.
        let is_comma = folded[m.range()].trim() == ",";
        if is_comma && folded[m.end()..].starts_with("the ") {
            continue;
        }
        end = m.start();
        break;
    }
    let first = squash(&folded[..end]);
    if first.is_empty() {
        squash(&folded)
    } else {
        first
    }
}

/// Lowercase, strip accents from Latin letters, and straighten punctuation
/// that Apple and Spotify spell differently (curly quotes, en/em dashes).
fn fold(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.nfd() {
        // Drop an accent only when it sits on an ASCII letter: "é" -> "e".
        // Japanese か + ゙ (dakuten) is a different letter, so it must stay.
        if is_combining_mark(c) && out.chars().last().is_some_and(|p| p.is_ascii_alphabetic()) {
            continue;
        }
        match c {
            '\u{2018}' | '\u{2019}' | '\u{02BC}' | '`' | '\u{00B4}' => out.push('\''),
            '\u{2013}' | '\u{2014}' | '\u{2212}' => out.push('-'),
            _ => out.extend(c.to_lowercase()),
        }
    }
    // Glue kept marks back onto their letters (か + ゙ -> が) so later steps
    // see one letter, not a letter plus stray punctuation.
    out.nfc().collect()
}

/// Remove boilerplate brackets anywhere, and boilerplate ` - suffix`es at the end.
fn strip_noise(s: &str) -> String {
    let no_brackets = BRACKETED.replace_all(s, |caps: &regex::Captures| {
        if NOISE.is_match(caps[1].trim()) {
            String::new()
        } else {
            caps[0].to_string() // not boilerplate: leave it exactly as it was
        }
    });

    let mut rest = no_brackets.trim();
    // "Song - Remastered 2011 - Mono": peel suffixes off the end one by one.
    while let Some(i) = rest.rfind(" - ") {
        if NOISE.is_match(rest[i + 3..].trim()) {
            rest = rest[..i].trim_end();
        } else {
            break;
        }
    }
    rest.to_string()
}

/// Keep only letters and digits, single-spaced. Apostrophes vanish ("don't" ->
/// "dont") rather than splitting the word, and `&` reads as "and".
fn squash(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut pending_space = false;
    for c in s.chars() {
        if c == '\'' {
            continue;
        }
        if c.is_alphanumeric() || c == '&' {
            if pending_space && !out.is_empty() {
                out.push(' ');
            }
            pending_space = false;
            if c == '&' {
                out.push_str("and");
            } else {
                out.push(c);
            }
        } else {
            pending_space = true;
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Assert that every listing has the same key as the first one.
    fn same(listings: &[(&str, &str)]) {
        let first = song_key(listings[0].0, listings[0].1);
        for (title, artist) in listings {
            assert_eq!(song_key(title, artist), first, "{title:?} by {artist:?}");
        }
    }

    fn different(a: (&str, &str), b: (&str, &str)) {
        assert_ne!(song_key(a.0, a.1), song_key(b.0, b.1), "{a:?} vs {b:?}");
    }

    #[test]
    fn remastered_is_the_same_song() {
        same(&[
            ("Blinding Lights", "The Weeknd"),
            ("Blinding Lights - Remastered 2020", "The Weeknd"),
            ("Blinding Lights (Remastered)", "The Weeknd"),
            ("Blinding Lights - 2011 Remaster", "The Weeknd"),
            ("Blinding Lights - Remastered 2011 - Mono", "The Weeknd"),
        ]);
    }

    #[test]
    fn featured_artist_is_the_same_song() {
        same(&[
            ("Die With A Smile", "Lady Gaga"),
            ("Die With A Smile (feat. Bruno Mars)", "Lady Gaga"),
            ("Die With A Smile", "Lady Gaga & Bruno Mars"),
            (
                "Die With A Smile [with Bruno Mars]",
                "Lady Gaga, Bruno Mars",
            ),
            ("Die With A Smile - feat. Bruno Mars", "LADY GAGA"),
        ]);
    }

    #[test]
    fn curly_apostrophe_is_the_same_song() {
        same(&[
            ("Don't Stop Me Now", "Queen"),
            ("Don\u{2019}t Stop Me Now", "Queen"),
            ("Dont Stop Me Now", "Queen"),
            ("DON'T STOP ME NOW", "Queen"),
        ]);
    }

    #[test]
    fn sped_up_is_its_own_song() {
        different(
            ("Espresso", "Sabrina Carpenter"),
            ("Espresso (sped up)", "Sabrina Carpenter"),
        );
        different(
            ("Espresso", "Sabrina Carpenter"),
            ("Espresso - Sped Up", "Sabrina Carpenter"),
        );
        // ...even when it also carries boilerplate, and that boilerplate still goes.
        same(&[
            ("Espresso (Sped Up)", "Sabrina Carpenter"),
            ("Espresso (feat. Someone) (Sped Up)", "Sabrina Carpenter"),
            ("Espresso (Sped Up) - Remastered 2024", "Sabrina Carpenter"),
        ]);
    }

    #[test]
    fn other_versions_stay_separate() {
        let t = |title| (title, "Artist");
        different(t("Song"), t("Song (Live)"));
        different(t("Song"), t("Song (Acoustic)"));
        different(t("Song"), t("Song (Remix)"));
        different(t("Song"), t("Song (Slowed + Reverb)"));
        different(t("Song"), t("Song (Instrumental)"));
    }

    #[test]
    fn different_artist_is_a_different_song() {
        different(("Intro", "A"), ("Intro", "B"));
        different(
            ("Intro", "Artist A & Friend"),
            ("Intro", "Artist B & Friend"),
        );
    }

    #[test]
    fn accents_and_punctuation_are_ignored() {
        same(&[
            ("Halo", "Beyoncé"),
            ("Halo", "Beyonce"),
            ("HALO!", "beyoncé"),
        ]);
        same(&[
            ("Rock & Roll", "X"),
            ("Rock and Roll", "X"),
            ("Rock \u{2013} & \u{2013} Roll", "X"),
        ]);
    }

    #[test]
    fn artist_names_with_commas_and_ampersands() {
        same(&[
            ("Song", "Tyler, The Creator"),
            ("Song", "Tyler, the Creator feat. Someone"),
        ]);
        different(("Song", "Tyler, The Creator"), ("Song", "Tyler"));
        same(&[
            ("Song", "Simon & Garfunkel"),
            ("Song", "Simon and Garfunkel"),
        ]);
    }

    #[test]
    fn non_latin_titles_survive() {
        same(&[
            ("夜に駆ける", "YOASOBI"),
            ("夜に駆ける - Remastered", "YOASOBI"),
        ]);
        different(("か", "A"), ("が", "A")); // dakuten must not be treated as an accent
        different(("夜に駆ける", "YOASOBI"), ("群青", "YOASOBI"));
    }

    #[test]
    fn titles_that_are_only_noise_or_symbols_do_not_all_collide() {
        different(("(Remastered)", "A"), ("(Deluxe)", "A"));
        different(("!!!", "A"), ("???", "A"));
        different(("", "A"), ("Song", "A"));
    }

    #[test]
    fn real_words_that_look_like_noise_are_kept() {
        different(("Stereo Love", "Edward Maya"), ("Love", "Edward Maya"));
        different(("Clean Bandit", "A"), ("Bandit", "A"));
        different(("Mono", "Otep"), ("", "Otep"));
        same(&[("Mono", "Otep"), ("mono", "OTEP")]);
    }
}
