//! The thin Python-facing layer: just forwards to the real code in lib.rs.

use pyo3::prelude::*;

/// song_key(title, artist) -> str: equal keys mean "same song".
#[pyfunction]
fn song_key(title: &str, artist: &str) -> String {
    crate::song_key(title, artist)
}

#[pymodule]
fn _songkey(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(song_key, m)?)
}
