//! Python binding: converts types only; the logic is in `merge`.

mod merge;

use pyo3::prelude::*;

/// Key under which plays of the same song are counted together.
#[pymodule]
mod _core {
    use pyo3::pyfunction;

    #[pyfunction]
    fn song_key(track: &str, artist: &str) -> (String, String) {
        crate::merge::song_key(track, artist)
    }
}
