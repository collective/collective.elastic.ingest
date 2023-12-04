from . import plone


def test_full_url_keep(monkeypatch):
    monkeypatch.setenv("PLONE_SERVICE", "http://plone:8080")
    monkeypatch.setenv("PLONE_SITE_PREFIX", "Plone")
    assert plone._full_url("Plone/foo/bar") == "http://plone:8080/Plone/foo/bar"
    assert plone._full_url("Plone") == "http://plone:8080/Plone"

    monkeypatch.setenv("PLONE_SITE_PREFIX", "zopefolder/Plone")
    assert (
        plone._full_url("zopefolder/Plone/foo/bar")
        == "http://plone:8080/zopefolder/Plone/foo/bar"
    )
    assert plone._full_url("zopefolder/Plone") == "http://plone:8080/zopefolder/Plone"


def test_full_url_strip_simple_prefix(monkeypatch):
    monkeypatch.setenv("PLONE_SITE_PREFIX_METHOD", "strip")
    monkeypatch.setenv("PLONE_SERVICE", "http://www.plone.example")
    monkeypatch.setenv("PLONE_SITE_PREFIX_PATH", "Plone")
    assert plone._full_url("Plone/foo/bar") == "http://www.plone.example/foo/bar"
    assert plone._full_url("Plone") == "http://www.plone.example"


def test_full_url_strip_double_prefix(monkeypatch):
    monkeypatch.setenv("PLONE_SITE_PREFIX_METHOD", "strip")
    monkeypatch.setenv("PLONE_SERVICE", "http://www.plone.example")
    monkeypatch.setenv("PLONE_SITE_PREFIX_PATH", "zopefolder/Plone")
    assert (
        plone._full_url("zopefolder/Plone/foo/bar")
        == "http://www.plone.example/foo/bar"
    )
    assert plone._full_url("zopefolder/Plone") == "http://www.plone.example"


def test_full_url_strip_simple_prefix_with_subpath(monkeypatch):
    monkeypatch.setenv("PLONE_SITE_PREFIX_METHOD", "strip")
    monkeypatch.setenv("PLONE_SERVICE", "http://www.plone.example/folder/subfolder")
    monkeypatch.setenv("PLONE_SITE_PREFIX_PATH", "Plone")
    assert (
        plone._full_url("Plone/foo/bar")
        == "http://www.plone.example/folder/subfolder/foo/bar"
    )
    assert plone._full_url("Plone") == "http://www.plone.example/folder/subfolder"


def test_full_url_strip_double_prefix_with_subpath(monkeypatch):
    monkeypatch.setenv("PLONE_SITE_PREFIX_METHOD", "strip")
    monkeypatch.setenv("PLONE_SERVICE", "http://www.plone.example/folder/subfolder")
    monkeypatch.setenv("PLONE_SITE_PREFIX_PATH", "zopefolder/Plone")
    assert (
        plone._full_url("zopefolder/Plone/foo/bar")
        == "http://www.plone.example/folder/subfolder/foo/bar"
    )
    assert (
        plone._full_url("zopefolder/Plone")
        == "http://www.plone.example/folder/subfolder"
    )


def test_schema_url_keep_prefix_simple(monkeypatch):
    monkeypatch.setenv("PLONE_SERVICE", "http://www.plone.example")
    monkeypatch.setenv("PLONE_SITE_PREFIX_PATH", "Plone")
    assert plone._schema_url() == "http://www.plone.example/Plone/@cesp-schema"


def test_schema_url_keep_double_prefix(monkeypatch):
    monkeypatch.setenv("PLONE_SERVICE", "http://www.plone.example")
    monkeypatch.setenv("PLONE_SITE_PREFIX_PATH", "zopefolder/Plone")
    assert (
        plone._schema_url() == "http://www.plone.example/zopefolder/Plone/@cesp-schema"
    )


def test_schema_url_strip_simple_prefix(monkeypatch):
    monkeypatch.setenv("PLONE_SITE_PREFIX_METHOD", "strip")
    monkeypatch.setenv("PLONE_SERVICE", "http://www.plone.example")
    monkeypatch.setenv("PLONE_SITE_PREFIX_PATH", "Plone")
    assert plone._schema_url() == "http://www.plone.example/@cesp-schema"


def test_schema_url_strip_double_prefix(monkeypatch):
    monkeypatch.setenv("PLONE_SITE_PREFIX_METHOD", "strip")
    monkeypatch.setenv("PLONE_SERVICE", "http://www.plone.example")
    monkeypatch.setenv("PLONE_SITE_PREFIX_PATH", "zopefolder/Plone")
    assert plone._schema_url() == "http://www.plone.example/@cesp-schema"
