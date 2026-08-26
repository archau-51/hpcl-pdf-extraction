import pytest

# `transformers` (and the model it downloads) is a heavy, network-dependent
# dependency we don't want to require just to run the test suite - skip
# these tests entirely if it isn't installed/available.
pytest.importorskip("transformers")

import advanced_sc


class _DummyPipeline:
    """Stands in for the real HuggingFace QA pipeline in tests."""

    def __init__(self):
        self.call_count = 0

    def __call__(self, payload):
        self.call_count += 1
        return {"answer": f"dummy answer for {payload['question']}"}


@pytest.fixture(autouse=True)
def reset_pipeline_cache(monkeypatch):
    # Make sure no real pipeline gets built and the module-level cache
    # starts empty for every test.
    monkeypatch.setattr(advanced_sc, "_qa_pipeline", None)
    yield
    monkeypatch.setattr(advanced_sc, "_qa_pipeline", None)


def test_adv_extract_returns_pipeline_result(monkeypatch):
    dummy = _DummyPipeline()
    monkeypatch.setattr(advanced_sc, "pipeline", lambda *a, **kw: dummy)

    result = advanced_sc.adv_extract("some context text", "throughput")

    assert "answer" in result
    assert dummy.call_count == 1


def test_adv_extract_reuses_cached_pipeline(monkeypatch):
    build_calls = []

    def fake_pipeline(*args, **kwargs):
        build_calls.append((args, kwargs))
        return _DummyPipeline()

    monkeypatch.setattr(advanced_sc, "pipeline", fake_pipeline)

    advanced_sc.adv_extract("context one", "keyword-one")
    advanced_sc.adv_extract("context two", "keyword-two")

    # The pipeline constructor should only ever be called once, no matter
    # how many keywords/requests use adv_extract afterwards.
    assert len(build_calls) == 1
