from simple_sc import extract_info

SAMPLE_TEXT = (
    "The refinery reported a total throughput of 10 million tonnes. "
    "Safety incidents remained low this quarter. "
    "The THROUGHPUT figure was revised upward in the final report."
)


def test_extract_info_finds_matching_sentences():
    result = extract_info(SAMPLE_TEXT, "throughput")

    assert len(result) == 2
    assert "10 million tonnes" in result[0]
    assert "revised upward" in result[1]


def test_extract_info_is_case_insensitive():
    result = extract_info(SAMPLE_TEXT, "THROUGHPUT")

    assert len(result) == 2


def test_extract_info_no_match_returns_placeholder():
    result = extract_info(SAMPLE_TEXT, "nonexistent-keyword")

    assert result == [" "]
