from corpus.official_importer import (
    _page_title,
    _title_similarity,
    _merge_curated_metadata,
    _derive_curated_subsections,
    extract_numbered_subsection,
    html_to_text,
    parse_section_links,
)


def test_parse_indiacode_unescaped_section_parameters():
    html = """
    <a href=/show-data?abv=CEN&actid=ACT_1&sectionId=50026&sectionno=1&orderno=1>
      <span>Section 1.</span> Short title and commencement.
    </a>
    """
    links = parse_section_links(html, "https://www.indiacode.nic.in/handle/example")
    assert len(links) == 1
    assert links[0].section_id == "50026"
    assert links[0].section_number == "1"
    assert links[0].title == "Short title and commencement."


def test_html_to_text_removes_markup_and_preserves_paragraphs():
    value = "<p>(1) First clause.</p><br><p>(2) Second <b>clause</b>.</p>"
    assert html_to_text(value) == "(1) First clause.\n(2) Second clause."


def test_page_title_mismatch_can_be_rejected_before_import():
    html = "<html><title>India Code: Indian Easements (Extension) Act, 1961</title></html>"
    actual = _page_title(html)

    assert actual == "Indian Easements (Extension) Act, 1961"
    assert _title_similarity("Code on Wages, 2019", actual) < 0.65
    assert _title_similarity("The Code on Wages, 2019", "Code on Wages, 2019") >= 0.65


def test_official_title_conflict_drops_incompatible_curated_summary():
    official = {
        "section_number": "82",
        "title": "Application of Chapter",
        "text": "This Chapter shall apply to every claim for compensation under a product liability action.",
        "footnotes": "",
    }
    curated = {
        "title": "Product Liability Action",
        "plain_language_summary": "Incorrectly describes a different provision.",
        "keywords": ["manufacturer"],
    }
    act = {"domain": "consumer", "status": "CURRENT", "jurisdiction": "India"}
    merged = _merge_curated_metadata(official, curated, act, "2026-08-14T00:00:00+00:00")
    assert not merged.get("plain_language_summary")
    assert "curated_metadata_conflict" in merged
    assert merged["verification_status"] == "VERIFIED"
    assert len(merged["content_hash"]) == 64


def test_act_state_is_applied_to_official_sections():
    official = {"section_number": "15", "title": "Tenant protection", "text": "Official text"}
    act = {
        "domain": "tenant",
        "jurisdiction": "State",
        "state": "Maharashtra",
        "status": "CURRENT",
    }

    merged = _merge_curated_metadata(official, {}, act, "2026-08-14T00:00:00+00:00")

    assert merged["state"] == "Maharashtra"


def test_curated_definition_uses_exact_official_subsection_text():
    text = "Intro\n(9) previous definition;\n(10) defect means a fault;\n(11) deficiency means a shortcoming;"
    assert extract_numbered_subsection(text, "10") == "(10) defect means a fault;"

    derived = _derive_curated_subsections(
        [{"section_number": "2", "title": "Definitions", "text": text, "source_url": "https://www.indiacode.nic.in/show-data"}],
        {"2(10)": {"section_number": "2(10)", "title": "Defect in Goods"}},
    )
    assert derived[0]["section_number"] == "2(10)"
    assert derived[0]["text"] == "(10) defect means a fault;"
