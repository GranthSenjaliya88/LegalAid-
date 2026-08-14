from app.db.database import get_connection


NEW_CURRENT_ACTS = {
    "Mediation Act 2023",
    "Sale of Goods Act 1930",
    "Partnership Act 1932",
    "Easements Act 1882",
    "MSMED Act 2006",
    "Legal Metrology Act 2009",
    "OSHWC Code 2020",
    "Bonded Labour Act 1976",
    "Child Labour Act 1986",
    "HIV AIDS Act 2017",
    "MTP Act 1971",
    "Disaster Management Act 2005",
    "Water Pollution Act 1974",
    "Air Pollution Act 1981",
    "Wild Life Act 1972",
    "NGT Act 2010",
    "Food Safety Act 2006",
    "Public Liability Insurance Act 1991",
    "Births and Deaths Act 1969",
    "Prevention of Corruption Act 1988",
    "NDPS Act 1985",
    "PMLA 2002",
    "Passports Act 1967",
    "Citizenship Act 1955",
}


def test_expanded_database_scale_and_fts_integrity():
    conn = get_connection()
    try:
        assert conn.execute("SELECT COUNT(*) FROM acts").fetchone()[0] >= 82
        sections = conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
        assert sections >= 6500
        assert conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0] == sections
        assert conn.execute("SELECT COUNT(*) FROM legal_concepts").fetchone()[0] == 65
    finally:
        conn.close()


def test_new_current_acts_have_verified_official_corpus_records():
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT a.short_name, a.status, COUNT(s.id) AS section_count,
                   SUM(CASE WHEN s.official_source_url LIKE '%indiacode.nic.in%'
                            AND s.verification_status = 'VERIFIED' THEN 1 ELSE 0 END) AS verified_count
            FROM acts a
            LEFT JOIN sections s ON s.act_id = a.id
            WHERE a.short_name IN ({})
            GROUP BY a.id
            """.format(",".join("?" for _ in NEW_CURRENT_ACTS)),
            tuple(sorted(NEW_CURRENT_ACTS)),
        ).fetchall()

        assert {row[0] for row in rows} == NEW_CURRENT_ACTS
        for short_name, status, section_count, verified_count in rows:
            assert status == "CURRENT", short_name
            assert section_count > 0, short_name
            assert verified_count == section_count, short_name
    finally:
        conn.close()


def test_superseded_labour_acts_are_historical():
    conn = get_connection()
    try:
        rows = dict(
            conn.execute(
                """
                SELECT short_name, status
                FROM acts
                WHERE short_name IN ('PGA 1972', 'MBA 1961', 'Factories Act 1948', 'Contract Labour Act 1970')
                """
            ).fetchall()
        )
        assert rows == {
            "PGA 1972": "HISTORICAL",
            "MBA 1961": "HISTORICAL",
            "Factories Act 1948": "HISTORICAL",
            "Contract Labour Act 1970": "HISTORICAL",
        }
    finally:
        conn.close()
