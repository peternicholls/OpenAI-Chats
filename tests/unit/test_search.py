"""Unit tests for full-text search functionality (SCH-001 through SCH-008).

Tests keyword search, phrase matching, date filtering, result previews,
and performance characteristics.
"""

import sqlite3
import time
from pathlib import Path

import pytest

from chatgpt_archive import db
from chatgpt_archive.search import (
    InvalidQueryError,
    SearchResults,
    execute_search,
    sanitize_query,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def search_db(tmp_path: Path) -> sqlite3.Connection:
    """Create a populated in-memory database for search tests."""
    db_path = tmp_path / "search_test.db"
    conn = db.init_db(db_path)

    # Insert test conversations
    conversations = [
        ("conv-search-001", "Python Programming Discussion", 1700000000.0, 1700001000.0),
        ("conv-search-002", "Machine Learning Basics", 1700100000.0, 1700101000.0),
        ("conv-search-003", "JavaScript and TypeScript", 1700200000.0, 1700201000.0),
    ]

    for openai_id, title, create_time, update_time in conversations:
        cursor = conn.execute(
            "INSERT INTO conversations (openai_id, title, create_time, update_time) VALUES (?, ?, ?, ?)",
            (openai_id, title, create_time, update_time),
        )
        conv_db_id = cursor.lastrowid

        # Insert messages
        if "Python" in title:
            messages = [
                ("user", "How do I use Python decorators?", create_time),
                ("assistant", "Python decorators are functions that modify other functions.", create_time + 60),
                ("user", "Can you show me an example decorator?", create_time + 120),
                ("assistant", "Sure! Here is a simple timer decorator.", create_time + 180),
            ]
        elif "Machine Learning" in title:
            messages = [
                ("user", "What is machine learning?", create_time),
                ("assistant", "Machine learning is a subset of artificial intelligence.", create_time + 60),
                ("user", "What are neural networks?", create_time + 120),
                ("assistant", "Neural networks are computational models inspired by brain structure.", create_time + 180),
            ]
        else:
            messages = [
                ("user", "What is TypeScript?", create_time),
                ("assistant", "TypeScript is a typed superset of JavaScript.", create_time + 60),
            ]

        for role, content, msg_time in messages:
            conn.execute(
                """
                INSERT INTO messages (conversation_id, openai_id, author_role, content, create_time)
                VALUES (?, ?, ?, ?, ?)
                """,
                (conv_db_id, f"msg-{openai_id}-{role}", role, content, msg_time),
            )

    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# SCH-001: Basic FTS search
# ---------------------------------------------------------------------------


class TestBasicSearch:
    """Tests for basic full-text search functionality (SCH-001)."""

    def test_fts_search_basic(self, search_db: sqlite3.Connection):
        """SCH-001: Basic keyword search returns relevant results."""
        results = execute_search(search_db, "Python")

        assert isinstance(results, SearchResults)
        assert results.total_results >= 1
        found_ids = {r.openai_id for r in results.results}
        assert "conv-search-001" in found_ids

    def test_fts_search_returns_search_results_type(self, search_db: sqlite3.Connection):
        """SCH-001: Search returns SearchResults instance."""
        results = execute_search(search_db, "machine learning")

        assert isinstance(results, SearchResults)
        assert results.query == "machine learning"

    def test_fts_search_case_insensitive(self, search_db: sqlite3.Connection):
        """SCH-001: Search is case-insensitive."""
        results_lower = execute_search(search_db, "python")
        results_upper = execute_search(search_db, "PYTHON")

        assert results_lower.total_results == results_upper.total_results


# ---------------------------------------------------------------------------
# SCH-002: Phrase search
# ---------------------------------------------------------------------------


class TestPhraseSearch:
    """Tests for phrase search functionality (SCH-002)."""

    def test_fts_search_phrase(self, search_db: sqlite3.Connection):
        """SCH-002: Phrase search returns conversations with matching phrases."""
        results = execute_search(search_db, "machine learning")

        assert results.total_results >= 1
        found_ids = {r.openai_id for r in results.results}
        assert "conv-search-002" in found_ids

    def test_fts_search_multi_word(self, search_db: sqlite3.Connection):
        """SCH-002: Multi-word search returns relevant results."""
        results = execute_search(search_db, "neural networks")

        assert results.total_results >= 1


# ---------------------------------------------------------------------------
# SCH-003: No results
# ---------------------------------------------------------------------------


class TestNoResultsSearch:
    """Tests for search returning no results (SCH-003)."""

    def test_fts_search_no_results(self, search_db: sqlite3.Connection):
        """SCH-003: Search for non-existent term returns empty results."""
        results = execute_search(search_db, "xyznonexistentterm12345")

        assert results.total_results == 0
        assert results.results == []

    def test_fts_search_no_results_preserves_query(self, search_db: sqlite3.Connection):
        """SCH-003: Even empty results preserve the query string."""
        results = execute_search(search_db, "xyznonexistentterm12345")

        assert results.query == "xyznonexistentterm12345"


# ---------------------------------------------------------------------------
# SCH-004: Special characters in search
# ---------------------------------------------------------------------------


class TestSpecialCharsSearch:
    """Tests for special character handling in search (SCH-004)."""

    def test_fts_search_special_chars(self, search_db: sqlite3.Connection):
        """SCH-004: Search handles special characters without error."""
        # These should not raise exceptions
        special_queries = [
            "python (decorator)",
            "machine:learning",
            "neural+networks",
        ]

        for query in special_queries:
            results = execute_search(search_db, query)
            assert isinstance(results, SearchResults)

    def test_sanitize_query_strips_fts5_specials(self):
        """SCH-004: Query sanitizer handles FTS5 special characters."""
        sanitized = sanitize_query("python (test)")
        assert "(" not in sanitized
        assert ")" not in sanitized

    def test_sanitize_query_rejects_empty(self):
        """SCH-004: Empty queries raise InvalidQueryError."""
        with pytest.raises(InvalidQueryError):
            sanitize_query("")

    def test_sanitize_query_rejects_whitespace_only(self):
        """SCH-004: Whitespace-only queries raise InvalidQueryError."""
        with pytest.raises(InvalidQueryError):
            sanitize_query("   ")


# ---------------------------------------------------------------------------
# SCH-005: Date range filtering
# ---------------------------------------------------------------------------


class TestDateFilterSearch:
    """Tests for date-filtered search (SCH-005)."""

    def test_search_with_date_filter_from(self, search_db: sqlite3.Connection):
        """SCH-005: from_date filter excludes older conversations."""
        # conv-search-001 is at 2023-11-14, conv-search-003 is at 2023-11-16
        # Filter from 2023-11-15 should exclude conv-search-001
        results = execute_search(search_db, "Python OR machine OR TypeScript", from_date="2023-11-15")

        found_ids = {r.openai_id for r in results.results}
        # Conv-001 (2023-11-14) should be filtered out
        assert "conv-search-001" not in found_ids

    def test_search_with_date_filter_to(self, search_db: sqlite3.Connection):
        """SCH-005: to_date filter excludes newer conversations."""
        results = execute_search(search_db, "Python OR machine OR TypeScript", to_date="2023-11-15")

        found_ids = {r.openai_id for r in results.results}
        # Conv-003 (2023-11-16) should be filtered out
        assert "conv-search-003" not in found_ids

    def test_search_with_invalid_date_raises(self, search_db: sqlite3.Connection):
        """SCH-005: Invalid date format raises InvalidQueryError."""
        with pytest.raises((InvalidQueryError, ValueError)):
            execute_search(search_db, "Python", from_date="not-a-date")


# ---------------------------------------------------------------------------
# SCH-006: Result preview/snippet
# ---------------------------------------------------------------------------


class TestSearchResultPreview:
    """Tests for result preview snippet generation (SCH-006)."""

    def test_search_result_preview(self, search_db: sqlite3.Connection):
        """SCH-006: Search results include a non-empty preview snippet."""
        results = execute_search(search_db, "Python")

        for result in results.results:
            assert isinstance(result.preview, str)
            assert len(result.preview) > 0

    def test_search_result_preview_contains_context(self, search_db: sqlite3.Connection):
        """SCH-006: Preview snippet includes content related to the search term."""
        results = execute_search(search_db, "decorators")

        assert results.total_results >= 1
        # At least one preview should contain related content
        previews = " ".join(r.preview for r in results.results)
        assert "decorator" in previews.lower() or "python" in previews.lower()


# ---------------------------------------------------------------------------
# SCH-007: Match count
# ---------------------------------------------------------------------------


class TestMatchCount:
    """Tests for per-conversation match count (SCH-007)."""

    def test_search_match_count(self, search_db: sqlite3.Connection):
        """SCH-007: Each result reports the number of matching messages."""
        results = execute_search(search_db, "Python")

        for result in results.results:
            assert isinstance(result.match_count, int)
            assert result.match_count >= 1

    def test_search_match_count_positive(self, search_db: sqlite3.Connection):
        """SCH-007: Match count is always positive for returned results."""
        results = execute_search(search_db, "machine learning")

        for result in results.results:
            assert result.match_count > 0


# ---------------------------------------------------------------------------
# SCH-008: Search performance
# ---------------------------------------------------------------------------


class TestSearchPerformance:
    """Tests for search performance (SCH-008)."""

    def test_search_performance(self, search_db: sqlite3.Connection):
        """SCH-008: Search completes within 500ms."""
        start = time.perf_counter()
        results = execute_search(search_db, "Python")
        duration = time.perf_counter() - start

        assert duration < 0.5, f"Search took {duration:.3f}s, expected <0.5s"
        assert isinstance(results, SearchResults)

    def test_search_with_limit(self, search_db: sqlite3.Connection):
        """SCH-008: Search limit parameter controls result count."""
        results = execute_search(search_db, "Python OR machine OR TypeScript", limit=1)

        assert len(results.results) <= 1
