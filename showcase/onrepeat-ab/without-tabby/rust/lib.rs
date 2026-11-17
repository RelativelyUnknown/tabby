//! songmatch: decides when two plays are the same song.
//!
//! `canon` and `merge` are plain Rust. Everything Python-specific lives in the
//! `python` module at the bottom, which only compiles with `--features python`.

pub mod canon;
pub mod merge;

#[cfg(feature = "python")]
mod python {
    use pyo3::prelude::*;

    /// song_key(artist, track) -> (artist_key, title_key)
    #[pyfunction]
    fn song_key(artist: &str, track: &str) -> (String, String) {
        let key = crate::canon::song_key(artist, track);
        (key.artist, key.title)
    }

    /// top_songs([(artist, track), ...], n) -> [(artist, track, plays), ...]
    #[pyfunction]
    fn top_songs(plays: Vec<(String, String)>, n: usize) -> Vec<(String, String, usize)> {
        crate::merge::top_songs(&plays, n)
            .into_iter()
            .map(|s| (s.artist, s.track, s.plays))
            .collect()
    }

    #[pymodule]
    fn _songmatch(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(song_key, m)?)?;
        m.add_function(wrap_pyfunction!(top_songs, m)?)?;
        Ok(())
    }
}
