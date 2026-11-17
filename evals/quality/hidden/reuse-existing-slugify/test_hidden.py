import importlib

import pytest


def find():
    for name in ("blog.authors", "blog.posts", "blog"):
        try:
            mod = importlib.import_module(name)
        except ImportError:
            continue
        if hasattr(mod, "author_path"):
            return mod.author_path
    pytest.fail("author_path not found")


def test_plain_name():
    assert find()("Ann Lee") == "/authors/ann-lee"


def test_accented_name_matches_existing_slugify():
    assert find()("Zoë O’Brien") == "/authors/zoe-obrien"


def test_existing_post_path_still_works():
    from blog.posts import post_path
    assert post_path("Hello, World") == "/posts/hello-world"
