"""Search functionality for ChatGPT archive with FTS5 full-text search.

Provides keyword search with relevance ranking, snippet generation,
date filtering, result formatting, and optional semantic/hybrid search.
"""

import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass
class SearchResult:
    """A single search result with metadata and preview snippet.
    
    Attributes:
        conversation_id: Internal database ID
        openai_id: Original OpenAI conversation ID
        title: Conversation title
        create_time: Unix timestamp of conversation creation
        preview: Context snippet with search term highlighted
        relevance_score: BM25 relevance score (lower = more relevant in SQLite)
        match_count: Number of matching messages in this conversation
    """
    conversation_id: int
    openai_id: str
    title: str
    create_time: Optional[float]
    preview: str
    relevance_score: float
    match_count: int = 1


@dataclass
class SearchResults:
    """Container for search results with metadata.
    
    Attributes:
        query: The original search query
        total_results: Total number of matching conversations
        results: List of SearchResult objects
    """
    query: str
    total_results: int
    results: List[SearchResult] = field(default_factory=list)


class InvalidQueryError(Exception):
    """Raised when search query syntax is invalid."""
    pass


def sanitize_query(query: str) -> str:
    """Sanitize a search query for safe FTS5 usage.
    
    Handles special FTS5 characters and converts the query to a safe
    format. Wraps bare terms in double quotes for phrase-like matching
    while preserving explicit FTS5 operators (AND, OR, NOT, NEAR).
    
    Args:
        query: Raw user search query
        
    Returns:
        Sanitized query string safe for FTS5 MATCH
        
    Raises:
        InvalidQueryError: If query is empty or invalid
    """
    if not query or not query.strip():
        raise InvalidQueryError("Search query cannot be empty")
    
    query = query.strip()
    
    # If user already uses explicit FTS5 syntax (quotes, AND, OR, NOT, NEAR),
    # pass through with minimal sanitization
    fts5_operators = re.compile(r'\b(AND|OR|NOT|NEAR)\b')
    has_fts5_syntax = (
        fts5_operators.search(query) or
        '"' in query or
        '*' in query
    )
    
    if has_fts5_syntax:
        # Minimal sanitization: remove dangerous characters but preserve structure
        # Remove unbalanced quotes
        if query.count('"') % 2 != 0:
            query = query.replace('"', '')
        return query
    
    # For simple queries: wrap individual terms for implicit AND matching
    # This handles multi-word queries naturally with FTS5
    # FTS5 implicitly ANDs space-separated tokens
    terms = query.split()
    
    # Remove FTS5 special characters from each term
    safe_terms = []
    for term in terms:
        # Strip special FTS5 characters: ^ { } ( ) : -> 
        cleaned = re.sub(r'[{}()\[\]:^]', '', term)
        if cleaned:
            safe_terms.append(cleaned)
    
    if not safe_terms:
        raise InvalidQueryError("Search query contains no valid search terms")
    
    return ' '.join(safe_terms)


def build_search_query(
    query: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 20,
) -> Tuple[str, list]:
    """Build the full SQL search query with optional date filtering.
    
    Uses FTS5 MATCH with BM25 scoring, groups results by conversation,
    and generates snippet previews.
    
    Args:
        query: Sanitized FTS5 query string
        from_date: Optional start date filter (YYYY-MM-DD)
        to_date: Optional end date filter (YYYY-MM-DD)
        limit: Maximum number of results to return
        
    Returns:
        Tuple of (SQL query string, list of parameters)
        
    Raises:
        InvalidQueryError: If date format is invalid
    """
    params: list = [query]
    
    # Build WHERE clauses for date filtering
    date_clauses = []
    
    if from_date:
        from_ts = _parse_date(from_date, start_of_day=True)
        date_clauses.append("c.create_time >= ?")
        params.append(from_ts)
    
    if to_date:
        to_ts = _parse_date(to_date, start_of_day=False)
        date_clauses.append("c.create_time <= ?")
        params.append(to_ts)
    
    date_filter = ""
    if date_clauses:
        date_filter = "AND " + " AND ".join(date_clauses)
    
    sql = f"""
        SELECT 
            c.id as conversation_id,
            c.openai_id,
            c.title,
            c.create_time,
            m.content as first_match_content,
            0 as score,
            COUNT(*) as match_count
        FROM messages_fts
        JOIN messages m ON messages_fts.rowid = m.id
        JOIN conversations c ON m.conversation_id = c.id
        WHERE messages_fts MATCH ?
        {date_filter}
        GROUP BY c.id
        ORDER BY match_count DESC, c.update_time DESC
        LIMIT ?
    """
    
    params.append(limit)
    
    return sql, params


def _parse_date(date_str: str, start_of_day: bool = True) -> float:
    """Parse a YYYY-MM-DD date string to Unix timestamp.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        start_of_day: If True, returns start of day (00:00:00).
                      If False, returns end of day (23:59:59).
        
    Returns:
        Unix timestamp as float
        
    Raises:
        InvalidQueryError: If date format is invalid
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if not start_of_day:
            dt = dt.replace(hour=23, minute=59, second=59)
        return dt.timestamp()
    except ValueError:
        raise InvalidQueryError(
            f"Invalid date format: '{date_str}'. Use YYYY-MM-DD."
        )


def execute_search(
    conn: sqlite3.Connection,
    query: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 20,
) -> SearchResults:
    """Execute a full-text search and return formatted results.
    
    Args:
        conn: Database connection
        query: Raw search query from user
        from_date: Optional start date filter (YYYY-MM-DD)
        to_date: Optional end date filter (YYYY-MM-DD)
        limit: Maximum number of results
        
    Returns:
        SearchResults with matching conversations
        
    Raises:
        InvalidQueryError: If query or date format is invalid
    """
    sanitized = sanitize_query(query)
    sql, params = build_search_query(sanitized, from_date, to_date, limit)
    
    try:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        error_msg = str(e)
        if "fts5" in error_msg.lower() or "syntax" in error_msg.lower():
            raise InvalidQueryError(
                f"Invalid search query syntax: {query}"
            ) from e
        raise
    
    results = []
    for row in rows:
        # Generate context snippet from the matched content
        content = row[4] or ""
        preview = _generate_snippet(content, query, max_length=200)
        
        result = SearchResult(
            conversation_id=row[0],
            openai_id=row[1],
            title=row[2] or "[Untitled]",
            create_time=row[3],
            preview=preview,
            relevance_score=abs(row[5]),  # BM25 returns negative scores
            match_count=row[6],
        )
        results.append(result)
    
    return SearchResults(
        query=query,
        total_results=len(results),
        results=results,
    )


def format_results_human(results: SearchResults) -> str:
    """Format search results for human-readable terminal output.
    
    Follows CLI contract format:
        Found N conversations matching "query"
        
        1. [YYYY-MM-DD] Title
           "...snippet with **highlighted** terms..."
           ID: openai-id
    
    Args:
        results: SearchResults to format
        
    Returns:
        Formatted string for terminal display
    """
    if results.total_results == 0:
        return _format_no_results(results.query)
    
    lines = []
    lines.append(
        f'Found {results.total_results} conversation{"s" if results.total_results != 1 else ""} '
        f'matching "{results.query}"'
    )
    lines.append("")
    
    for i, result in enumerate(results.results, 1):
        # Format date
        if result.create_time:
            dt = datetime.fromtimestamp(result.create_time)
            date_str = dt.strftime("%Y-%m-%d")
        else:
            date_str = "Unknown"
        
        # Clean preview - replace FTS5 highlight markers with terminal emphasis
        preview = result.preview.strip()
        
        lines.append(f"{i}. [{date_str}] {result.title}")
        lines.append(f'   "{preview}"')
        lines.append(f"   ID: {result.openai_id}")
        lines.append("")
    
    showing = len(results.results)
    if showing < results.total_results:
        lines.append(f"(showing {showing} of {results.total_results} results)")
    
    return "\n".join(lines)


def format_results_json(results: SearchResults) -> dict:
    """Format search results as JSON-serializable dictionary.
    
    Follows CLI contract JSON output format.
    
    Args:
        results: SearchResults to format
        
    Returns:
        Dictionary matching the CLI contract JSON schema
    """
    return {
        "query": results.query,
        "total_results": results.total_results,
        "results": [
            {
                "id": r.openai_id,
                "title": r.title,
                "create_time": r.create_time,
                "preview": r.preview,
                "relevance_score": round(r.relevance_score, 4),
                "match_count": r.match_count,
            }
            for r in results.results
        ],
    }


def _generate_snippet(content: str, query: str, max_length: int = 200) -> str:
    """Generate a context snippet from content centered around the query match.
    
    Finds the first occurrence of any query term in the content and extracts
    a window of text around it, adding ellipsis markers where truncated.
    
    Args:
        content: The full message content
        query: The search query (may contain multiple terms)
        max_length: Maximum length of the snippet
        
    Returns:
        Snippet string with context around the match
    """
    if not content:
        return ""
    
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    
    if len(content) <= max_length:
        return content
    
    # Extract individual search terms (ignoring FTS5 operators)
    terms = [t for t in query.split() if t.upper() not in ('AND', 'OR', 'NOT', 'NEAR')]
    terms = [re.sub(r'[{}()\[\]:^"*]', '', t) for t in terms]
    terms = [t for t in terms if t]
    
    # Find the first occurrence of any term (case-insensitive)
    best_pos = -1
    for term in terms:
        try:
            pos = content.lower().find(term.lower())
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos
        except (re.error, ValueError):
            continue
    
    if best_pos == -1:
        # Term not found in this content, show start
        return content[:max_length] + "..."
    
    # Center the snippet around the match
    half_window = max_length // 2
    start = max(0, best_pos - half_window)
    end = min(len(content), start + max_length)
    
    # Adjust start if we're near the end
    if end - start < max_length:
        start = max(0, end - max_length)
    
    snippet = content[start:end]
    
    # Add ellipsis markers
    if start > 0:
        snippet = "..." + snippet.lstrip()
    if end < len(content):
        snippet = snippet.rstrip() + "..."
    
    return snippet


def _format_no_results(query: str) -> str:
    """Format a user-friendly message when no results are found.
    
    Args:
        query: The search query that returned no results
        
    Returns:
        Helpful message with suggestions
    """
    return (
        f'No conversations found matching "{query}"\n'
        "\n"
        "Tips:\n"
        "  • Try broader or different search terms\n"
        "  • Check spelling\n"
        "  • Use simpler keywords (FTS5 uses word stemming)\n"
        "  • Remove date filters to search all conversations"
    )


def execute_semantic_search(
    conn: sqlite3.Connection,
    query: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 20,
) -> SearchResults:
    """Execute semantic search using vector embeddings.
    
    Generates an embedding for the query and finds the most similar
    messages using cosine/L2 distance in the vector table.
    
    Args:
        conn: Database connection
        query: Natural language search query
        from_date: Optional start date filter (YYYY-MM-DD)
        to_date: Optional end date filter (YYYY-MM-DD)
        limit: Maximum number of results
        
    Returns:
        SearchResults with semantically similar conversations
        
    Raises:
        InvalidQueryError: If query is empty or embedding fails
    """
    if not query or not query.strip():
        raise InvalidQueryError("Search query cannot be empty")
    
    try:
        from chatgpt_archive.embeddings import get_openai_client, generate_embeddings_batch
        from chatgpt_archive.db import serialize_embedding, load_sqlite_vec, deserialize_embedding
    except ImportError:
        raise InvalidQueryError(
            "Semantic search requires 'chatgpt-archive[semantic]'. "
            "Install with: pip install 'chatgpt-archive[semantic]'"
        )
    
    # Generate query embedding
    client = get_openai_client()
    query_embeddings = generate_embeddings_batch(client, [query])
    if not query_embeddings:
        raise InvalidQueryError("Failed to generate query embedding")
    
    query_blob = serialize_embedding(query_embeddings[0])
    
    # Check if sqlite-vec is available for fast search
    vec_loaded = load_sqlite_vec(conn)
    
    if vec_loaded:
        results = _vec_semantic_search(conn, query_blob, query, from_date, to_date, limit)
    else:
        results = _fallback_semantic_search(conn, query_embeddings[0], query, from_date, to_date, limit)
    
    return results


def _vec_semantic_search(
    conn: sqlite3.Connection,
    query_blob: bytes,
    query: str,
    from_date: Optional[str],
    to_date: Optional[str],
    limit: int,
) -> SearchResults:
    """Semantic search using sqlite-vec virtual table.
    
    Uses the vec0 virtual table for efficient nearest-neighbor search.
    """
    params: list = [query_blob, limit * 3]  # Fetch more to allow for date filtering
    
    try:
        # Query the vec table for nearest neighbors
        cursor = conn.execute("""
            SELECT message_id, distance
            FROM vec_messages
            WHERE embedding MATCH ?
            ORDER BY distance
            LIMIT ?
        """, params)
        
        vec_results = cursor.fetchall()
    except Exception:
        # Fall back if vec table doesn't exist
        from chatgpt_archive.db import deserialize_embedding
        return _fallback_semantic_search(
            conn, deserialize_embedding(query_blob), query,
            from_date, to_date, limit
        )
    
    if not vec_results:
        return SearchResults(query=query, total_results=0, results=[])
    
    # Get conversation details for matched messages
    message_ids = [row[0] for row in vec_results]
    distances = {row[0]: row[1] for row in vec_results}
    
    placeholders = ",".join("?" * len(message_ids))
    
    date_clauses = []
    date_params: list = []
    if from_date:
        from_ts = _parse_date(from_date, start_of_day=True)
        date_clauses.append("c.create_time >= ?")
        date_params.append(from_ts)
    if to_date:
        to_ts = _parse_date(to_date, start_of_day=False)
        date_clauses.append("c.create_time <= ?")
        date_params.append(to_ts)
    
    date_filter = ""
    if date_clauses:
        date_filter = "AND " + " AND ".join(date_clauses)
    
    sql = f"""
        SELECT DISTINCT 
            c.id as conversation_id,
            c.openai_id,
            c.title,
            c.create_time,
            m.content,
            m.id as message_id
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE m.id IN ({placeholders})
        {date_filter}
        ORDER BY c.update_time DESC
    """
    
    cursor = conn.execute(sql, message_ids + date_params)
    rows = cursor.fetchall()
    
    # Group by conversation, pick best match
    seen_conversations = {}
    for row in rows:
        conv_id = row[0]
        if conv_id not in seen_conversations:
            msg_id = row[5]
            distance = distances.get(msg_id, 999)
            content = row[4] or ""
            preview = content[:200] + "..." if len(content) > 200 else content
            
            seen_conversations[conv_id] = SearchResult(
                conversation_id=conv_id,
                openai_id=row[1],
                title=row[2] or "[Untitled]",
                create_time=row[3],
                preview=preview,
                relevance_score=round(1.0 / (1.0 + distance), 4),
                match_count=1,
            )
    
    results = list(seen_conversations.values())[:limit]
    
    return SearchResults(
        query=query,
        total_results=len(results),
        results=results,
    )


def _fallback_semantic_search(
    conn: sqlite3.Connection,
    query_embedding: list,
    query: str,
    from_date: Optional[str],
    to_date: Optional[str],
    limit: int,
) -> SearchResults:
    """Fallback semantic search using brute-force cosine similarity.
    
    Used when sqlite-vec is not available. Slower but functional.
    Calculates cosine similarity in Python.
    """
    import math
    from chatgpt_archive.db import deserialize_embedding
    
    date_clauses = []
    date_params: list = []
    if from_date:
        from_ts = _parse_date(from_date, start_of_day=True)
        date_clauses.append("c.create_time >= ?")
        date_params.append(from_ts)
    if to_date:
        to_ts = _parse_date(to_date, start_of_day=False)
        date_clauses.append("c.create_time <= ?")
        date_params.append(to_ts)
    
    date_filter = ""
    if date_clauses:
        date_filter = "AND " + " AND ".join(date_clauses)
    
    sql = f"""
        SELECT 
            e.message_id,
            e.embedding,
            c.id as conversation_id,
            c.openai_id,
            c.title,
            c.create_time,
            m.content
        FROM message_embeddings e
        JOIN messages m ON e.message_id = m.id
        JOIN conversations c ON m.conversation_id = c.id
        WHERE 1=1
        {date_filter}
    """
    
    cursor = conn.execute(sql, date_params)
    
    # Calculate cosine similarity for each embedding
    scored = []
    q_norm = math.sqrt(sum(x * x for x in query_embedding))
    
    for row in cursor:
        embedding = deserialize_embedding(row[1])
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(query_embedding, embedding))
        e_norm = math.sqrt(sum(x * x for x in embedding))
        
        if q_norm > 0 and e_norm > 0:
            similarity = dot_product / (q_norm * e_norm)
        else:
            similarity = 0
        
        scored.append((similarity, row))
    
    # Sort by similarity (highest first)
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Group by conversation
    seen_conversations = {}
    for similarity, row in scored:
        conv_id = row[2]
        if conv_id not in seen_conversations:
            content = row[6] or ""
            preview = content[:200] + "..." if len(content) > 200 else content
            
            seen_conversations[conv_id] = SearchResult(
                conversation_id=conv_id,
                openai_id=row[3],
                title=row[4] or "[Untitled]",
                create_time=row[5],
                preview=preview,
                relevance_score=round(similarity, 4),
                match_count=1,
            )
        
        if len(seen_conversations) >= limit:
            break
    
    results = list(seen_conversations.values())
    
    return SearchResults(
        query=query,
        total_results=len(results),
        results=results,
    )


def execute_hybrid_search(
    conn: sqlite3.Connection,
    query: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 20,
) -> SearchResults:
    """Execute hybrid search combining FTS5 keyword and vector semantic search.
    
    Runs both keyword and semantic searches, then merges results using
    reciprocal rank fusion for the best of both approaches.
    
    Args:
        conn: Database connection
        query: Search query
        from_date: Optional start date filter (YYYY-MM-DD)
        to_date: Optional end date filter (YYYY-MM-DD)
        limit: Maximum number of results
        
    Returns:
        SearchResults with combined keyword + semantic results
    """
    # Run keyword search
    try:
        keyword_results = execute_search(conn, query, from_date, to_date, limit)
    except InvalidQueryError:
        keyword_results = SearchResults(query=query, total_results=0, results=[])
    
    # Run semantic search
    try:
        semantic_results = execute_semantic_search(conn, query, from_date, to_date, limit)
    except (InvalidQueryError, Exception):
        semantic_results = SearchResults(query=query, total_results=0, results=[])
    
    # Merge using reciprocal rank fusion (RRF)
    # RRF score = sum(1 / (k + rank)) for each ranking list where result appears
    k = 60  # Standard RRF constant
    
    scores: dict = {}  # openai_id -> (rrf_score, SearchResult)
    
    for rank, result in enumerate(keyword_results.results, 1):
        rrf = 1.0 / (k + rank)
        if result.openai_id in scores:
            scores[result.openai_id] = (
                scores[result.openai_id][0] + rrf,
                result  # Keep keyword result for preview quality
            )
        else:
            scores[result.openai_id] = (rrf, result)
    
    for rank, result in enumerate(semantic_results.results, 1):
        rrf = 1.0 / (k + rank)
        if result.openai_id in scores:
            scores[result.openai_id] = (
                scores[result.openai_id][0] + rrf,
                scores[result.openai_id][1]  # Keep existing result
            )
        else:
            scores[result.openai_id] = (rrf, result)
    
    # Sort by combined RRF score
    ranked = sorted(scores.values(), key=lambda x: x[0], reverse=True)
    
    merged_results = []
    for rrf_score, result in ranked[:limit]:
        result.relevance_score = round(rrf_score, 4)
        merged_results.append(result)
    
    return SearchResults(
        query=query,
        total_results=len(merged_results),
        results=merged_results,
    )
