//! Group plays by song and pick a name to show for each group.

use std::collections::HashMap;

use crate::canon::{SongKey, song_key};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MergedSong {
    pub artist: String,
    pub track: String,
    pub plays: usize,
}

/// One bucket of plays that all share a `SongKey`.
#[derive(Default)]
struct Group<'a> {
    total: usize,
    /// How often each exact (artist, track) spelling appeared.
    spellings: Vec<((&'a str, &'a str), usize)>,
}

impl<'a> Group<'a> {
    /// Show the spelling you heard most; on a tie prefer the shorter title
    /// (so "Song" beats "Song - Remastered 2020"), then alphabetical.
    fn display(&self) -> (&'a str, &'a str) {
        self.spellings
            .iter()
            .min_by_key(|((artist, track), n)| {
                (std::cmp::Reverse(*n), track.len(), *track, *artist)
            })
            .map(|(pair, _)| *pair)
            .expect("a group always has at least one spelling")
    }
}

/// `plays` has one `(artist, track)` entry per play. Returns the `n` most-played
/// songs after merging, most-played first.
pub fn top_songs(plays: &[(String, String)], n: usize) -> Vec<MergedSong> {
    // Count identical spellings first, so we only compute each key once even
    // if you played one song 500 times.
    let mut spelling_counts: HashMap<(&str, &str), usize> = HashMap::new();
    for (artist, track) in plays {
        *spelling_counts.entry((artist, track)).or_default() += 1;
    }

    let mut groups: HashMap<SongKey, Group> = HashMap::new();
    for (pair, count) in spelling_counts {
        let group = groups.entry(song_key(pair.0, pair.1)).or_default();
        group.total += count;
        group.spellings.push((pair, count));
    }

    let mut merged: Vec<MergedSong> = groups
        .values()
        .map(|g| {
            let (artist, track) = g.display();
            MergedSong {
                artist: artist.to_string(),
                track: track.to_string(),
                plays: g.total,
            }
        })
        .collect();

    // HashMap order is random, so break ties by name to keep output stable.
    merged.sort_by(|a, b| {
        b.plays
            .cmp(&a.plays)
            .then_with(|| a.artist.cmp(&b.artist))
            .then_with(|| a.track.cmp(&b.track))
    });
    merged.truncate(n);
    merged
}

#[cfg(test)]
mod tests {
    use super::*;

    fn plays(items: &[(&str, &str, usize)]) -> Vec<(String, String)> {
        items
            .iter()
            .flat_map(|(a, t, n)| std::iter::repeat_n((a.to_string(), t.to_string()), *n))
            .collect()
    }

    #[test]
    fn merges_counts_and_shows_most_played_spelling() {
        let p = plays(&[
            ("The Weeknd", "Blinding Lights", 3),
            ("The Weeknd", "Blinding Lights - Remastered 2020", 2),
            ("Queen", "Don’t Stop Me Now", 1),
            ("Queen", "Don't Stop Me Now", 1),
        ]);
        let top = top_songs(&p, 5);
        assert_eq!(top.len(), 2);
        assert_eq!(
            top[0],
            MergedSong {
                artist: "The Weeknd".into(),
                track: "Blinding Lights".into(),
                plays: 5
            }
        );
        assert_eq!(top[1].plays, 2);
        assert_eq!(top[1].track, "Don't Stop Me Now"); // tie -> alphabetical, ' < ’
    }

    #[test]
    fn sped_up_is_its_own_entry() {
        let p = plays(&[
            ("Sabrina Carpenter", "Espresso", 4),
            ("Sabrina Carpenter", "Espresso (sped up)", 2),
        ]);
        let top = top_songs(&p, 5);
        assert_eq!(top.iter().map(|s| s.plays).collect::<Vec<_>>(), vec![4, 2]);
        assert_eq!(top[1].track, "Espresso (sped up)");
    }

    #[test]
    fn truncates_and_handles_empty() {
        assert!(top_songs(&[], 5).is_empty());
        let p = plays(&[("A", "1", 3), ("A", "2", 2), ("A", "3", 1)]);
        assert_eq!(top_songs(&p, 2).len(), 2);
    }
}
