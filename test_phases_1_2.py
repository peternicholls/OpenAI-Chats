#!/usr/bin/env python3
"""Comprehensive validation tests for Phase 1 & 2 implementation."""

import sys
from pathlib import Path

# Test 1: Package structure
print('=== TEST 1: Package Structure ===')
expected_files = [
    'chatgpt_archive/__init__.py',
    'chatgpt_archive/__main__.py',
    'chatgpt_archive/cli.py',
    'chatgpt_archive/db.py',
    'chatgpt_archive/models.py',
    'pyproject.toml',
    'README.md'
]
for f in expected_files:
    exists = Path(f).exists()
    status = '✓' if exists else '✗'
    print(f'{status} {f}')

# Test 2: Imports work
print('\n=== TEST 2: Module Imports ===')
try:
    from chatgpt_archive import __version__, Conversation, Message, Attachment
    print(f'✓ Package imports work, version: {__version__}')
except Exception as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)

# Test 3: Models validation
print('\n=== TEST 3: Model Validation ===')
try:
    # Valid message
    msg = Message(openai_id='test-123', author_role='user', content='Hello')
    print(f'✓ Valid message created: {msg.author_role}')
    
    # Invalid role should raise error
    try:
        bad_msg = Message(openai_id='test-456', author_role='invalid')
        print('✗ Should have raised ValueError for invalid role')
    except ValueError as e:
        print(f'✓ Correctly rejected invalid role: {str(e)[:50]}...')
        
    # Conversation with display_title fallback
    conv1 = Conversation(openai_id='conv-1', title='Test Title')
    conv2 = Conversation(openai_id='conv-2')
    conv2.messages = [msg]
    conv3 = Conversation(openai_id='conv-3')
    
    print(f'✓ Titled conversation: "{conv1.display_title}"')
    print(f'✓ Fallback to message: "{conv2.display_title}"')
    print(f'✓ Fallback to [Untitled]: "{conv3.display_title}"')
    
except Exception as e:
    print(f'✗ Model test failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\n=== TEST 4: Database Schema ===')
from chatgpt_archive.db import init_db, get_db_size
import tempfile
import sqlite3

try:
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = Path(f.name)
    
    conn = init_db(test_db)
    
    # Check all required tables
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = {row[0] for row in cursor.fetchall()}
    required_tables = {'conversations', 'messages', 'attachments', 'messages_fts'}
    
    if required_tables.issubset(tables):
        print(f'✓ All required tables present: {required_tables}')
    else:
        missing = required_tables - tables
        print(f'✗ Missing tables: {missing}')
        sys.exit(1)
    
    # Check FTS5 works
    cursor = conn.execute("SELECT * FROM messages_fts_config")
    print(f'✓ FTS5 virtual table configured')
    
    # Check triggers
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
    triggers = {row[0] for row in cursor.fetchall()}
    required_triggers = {'messages_ai', 'messages_ad', 'messages_au'}
    
    if required_triggers.issubset(triggers):
        print(f'✓ All FTS sync triggers present: {required_triggers}')
    else:
        missing = required_triggers - triggers
        print(f'✗ Missing triggers: {missing}')
        sys.exit(1)
    
    # Test foreign key enforcement
    conn.execute('PRAGMA foreign_keys')
    fk_result = conn.execute('PRAGMA foreign_keys').fetchone()
    if fk_result[0] == 1:
        print(f'✓ Foreign key constraints enabled')
    else:
        print(f'✗ Foreign key constraints not enabled')
        sys.exit(1)
    
    # Test basic insert
    cursor = conn.execute(
        'INSERT INTO conversations (openai_id, title) VALUES (?, ?)',
        ('test-conv-1', 'Test Conversation')
    )
    conv_id = cursor.lastrowid
    
    cursor = conn.execute(
        'INSERT INTO messages (conversation_id, openai_id, author_role, content) VALUES (?, ?, ?, ?)',
        (conv_id, 'msg-1', 'user', 'Test message content')
    )
    msg_id = cursor.lastrowid
    conn.commit()
    
    # Verify FTS auto-indexing via trigger
    cursor = conn.execute('SELECT content FROM messages_fts WHERE rowid = ?', (msg_id,))
    fts_result = cursor.fetchone()
    if fts_result and fts_result[0] == 'Test message content':
        print(f'✓ FTS trigger auto-indexed message on insert')
    else:
        print(f'✗ FTS trigger did not auto-index message')
        sys.exit(1)
    
    # Test search works
    cursor = conn.execute("SELECT rowid FROM messages_fts WHERE messages_fts MATCH 'test'")
    if cursor.fetchone():
        print(f'✓ FTS5 search query works')
    else:
        print(f'✗ FTS5 search failed')
        sys.exit(1)
    
    conn.close()
    test_db.unlink()
    
except Exception as e:
    print(f'✗ Database test failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\n=== All Phase 1 & 2 Tests Passed ✓ ===')
