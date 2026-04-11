# Troubleshooting Guide

Common issues and solutions for ChatGPT Archive Search & Export.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Import Problems](#import-problems)
- [Search Issues](#search-issues)
- [Export Errors](#export-errors)
- [Database Issues](#database-issues)
- [Semantic Search Problems](#semantic-search-problems)
- [Performance Issues](#performance-issues)
- [Web UI Issues](#web-ui-issues)
- [General Debugging](#general-debugging)

---

## Installation Issues

### "Command not found: chatgpt-archive"

**Problem**: After installing with `pip install -e .`, the command is not found.

**Solutions**:
1. Ensure the installation completed successfully:
   ```bash
   pip install -e .
   ```

2. Check if the command is in your PATH:
   ```bash
   which chatgpt-archive
   ```

3. Try running with Python module syntax:
   ```bash
   python -m chatgpt_archive --help
   ```

4. If using a virtual environment, make sure it's activated:
   ```bash
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

5. Reinstall in editable mode:
   ```bash
   pip uninstall chatgpt-archive
   pip install -e .
   ```

### "ModuleNotFoundError: No module named 'click'"

**Problem**: Missing dependencies.

**Solution**:
```bash
pip install click pyyaml
# or reinstall the package
pip install -e .
```

### "ImportError: cannot import name 'something'"

**Problem**: Outdated installation or corrupted cache.

**Solution**:
```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Reinstall
pip install -e . --force-reinstall
```

---

## Import Problems

### "Error: conversations.json not found"

**Problem**: The archive directory doesn't contain `conversations.json`.

**Solutions**:
1. Verify you're pointing to the correct directory:
   ```bash
   ls -la /path/to/export/
   # Should show conversations.json
   ```

2. Make sure you've extracted the ChatGPT export archive:
   ```bash
   # The export comes as a .zip file, extract it first
   unzip chatgpt-export-2024-01-15.zip
   cd chatgpt-export-2024-01-15/
   chatgpt-archive import .
   ```

3. Check if the export format has changed. ChatGPT exports should contain:
   - `conversations.json` (required)
   - Various subdirectories with attachments (optional)

### "Error: Invalid JSON in conversations.json"

**Problem**: The `conversations.json` file is malformed or corrupted.

**Solutions**:
1. Validate the JSON file:
   ```bash
   python -m json.tool conversations.json > /dev/null
   # If this errors, the file is malformed
   ```

2. Re-download your ChatGPT export from OpenAI and try again.

3. Check file size - if it's unexpectedly small, the download may have been interrupted:
   ```bash
   ls -lh conversations.json
   ```

### "Import succeeds but shows 0 conversations"

**Problem**: The file format may have changed or is incompatible.

**Solutions**:
1. Check the JSON structure:
   ```bash
   head -n 50 conversations.json | python -m json.tool
   ```

2. Verify it's actually a ChatGPT export (should be an array of conversation objects).

3. File a bug report with a sample of the JSON structure (redact personal content).

### Import is very slow

**Problem**: Large archives take time to import.

**Expected Performance**:
- ~60 seconds for 64,000 messages on SSD
- Progress updates every 100 conversations

**Solutions**:
1. Ensure you're using an SSD, not HDD
2. Close other applications using the disk
3. Run with `--json` flag to reduce output overhead:
   ```bash
   chatgpt-archive import ./archive --json
   ```

---

## Search Issues

### "Error: Database not found"

**Problem**: Database doesn't exist yet or is in an unexpected location.

**Solutions**:
1. Run import first:
   ```bash
   chatgpt-archive import ./archive
   ```

2. Check if database exists:
   ```bash
   ls -la ~/.chatgpt-archive/chats.db
   ```

3. If using custom database location, specify it:
   ```bash
   chatgpt-archive --db /path/to/chats.db search "query"
   ```

4. Check environment variable:
   ```bash
   echo $CHATGPT_ARCHIVE_DB
   # If set, make sure it points to valid database
   ```

### "Error: Invalid query syntax"

**Problem**: FTS5 query syntax error.

**Common Syntax Errors**:
- Unbalanced quotes: `"machine learning`
- Invalid operators: `machine learning & python` (use `AND` not `&`)
- Special characters: `C++` (escape as `"C++"`)

**Solutions**:
1. Use quotes for phrases:
   ```bash
   chatgpt-archive search '"machine learning"'
   ```

2. Proper boolean operators:
   ```bash
   # Correct
   chatgpt-archive search "python AND flask"
   chatgpt-archive search "python OR javascript"
   
   # Incorrect
   chatgpt-archive search "python && flask"  # Wrong operator
   ```

3. Escape special characters:
   ```bash
   chatgpt-archive search '"C++"'
   chatgpt-archive search "node.js"
   ```

### Search returns no results for known content

**Problem**: Content exists but isn't found.

**Solutions**:
1. Try simpler search terms:
   ```bash
   # Instead of exact phrase
   chatgpt-archive search "neural network"
   # Try individual words
   chatgpt-archive search "neural OR network"
   ```

2. Check if message was actually imported:
   ```bash
   # View the conversation directly
   chatgpt-archive view <conversation-id>
   ```

3. Try semantic search (if embeddings exist):
   ```bash
   chatgpt-archive search "neural networks" --semantic
   ```

4. Query database directly to verify content:
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db \
     "SELECT content FROM messages WHERE content LIKE '%neural%' LIMIT 5;"
   ```

### Search is too slow

**Expected Performance**: <500ms for keyword search on 64K messages

**Solutions**:
1. Verify FTS5 index exists:
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db \
     "SELECT name FROM sqlite_master WHERE type='table' AND name='messages_fts';"
   ```

2. Reduce result limit:
   ```bash
   chatgpt-archive search "python" --limit 10
   ```

3. Use more specific search terms to reduce result set.

---

## Export Errors

### "Error: Conversation not found"

**Problem**: Invalid conversation ID or conversation doesn't exist in database.

**Solutions**:
1. Verify the conversation ID is correct:
   ```bash
   # Search for the conversation first
   chatgpt-archive search "keyword"
   # Copy the ID from results
   ```

2. List all conversations to confirm ID exists:
   ```bash
   chatgpt-archive list --json | jq '.conversations[].id'
   ```

3. Make sure you're using the correct database:
   ```bash
   chatgpt-archive --db ~/.chatgpt-archive/chats.db list
   ```

### "Error: Failed to write file"

**Problem**: Permission denied or invalid path.

**Solutions**:
1. Check directory exists and is writable:
   ```bash
   mkdir -p exports
   chatgpt-archive export <id> -f md -o exports/chat.md
   ```

2. Verify permissions:
   ```bash
   ls -ld exports/
   # Should show write permissions
   ```

3. Use absolute path:
   ```bash
   chatgpt-archive export <id> -f md -o ~/Documents/chat.md
   ```

4. Write to stdout instead:
   ```bash
   chatgpt-archive export <id> -f md > chat.md
   ```

### Export output is garbled or unreadable

**Problem**: Encoding issues or binary data in content.

**Solutions**:
1. Ensure terminal supports UTF-8:
   ```bash
   echo $LANG
   # Should include UTF-8
   ```

2. Export to file instead of viewing in terminal:
   ```bash
   chatgpt-archive export <id> -f md -o chat.md
   ```

3. Open exported file in text editor that supports UTF-8.

---

## Database Issues

### "Error: database is locked"

**Problem**: Another process is using the database.

**Solutions**:
1. Close other `chatgpt-archive` processes:
   ```bash
   ps aux | grep chatgpt-archive
   kill <pid>
   ```

2. Wait a moment and retry.

3. Check for `.db-wal` and `.db-shm` files:
   ```bash
   ls -la ~/.chatgpt-archive/
   # If stuck, can delete .db-wal and .db-shm (NOT .db file)
   ```

### Database is corrupted

**Symptoms**: "database disk image is malformed" or similar errors

**Solutions**:
1. Try SQLite recovery:
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db "PRAGMA integrity_check;"
   ```

2. Export and reimport:
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db .dump > backup.sql
   rm ~/.chatgpt-archive/chats.db
   sqlite3 ~/.chatgpt-archive/chats.db < backup.sql
   ```

3. Re-import from original ChatGPT export:
   ```bash
   rm ~/.chatgpt-archive/chats.db
   chatgpt-archive import ./original-export/
   ```

### Database is too large / disk space issues

**Expected Size**: 1.5-2x the original `conversations.json` size

**Solutions**:
1. Check database size:
   ```bash
   du -h ~/.chatgpt-archive/chats.db
   ```

2. Vacuum database to reclaim space:
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db "VACUUM;"
   ```

3. If you have embeddings, they add significant size:
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db \
     "SELECT COUNT(*) FROM message_embeddings;"
   ```

4. Move database to location with more space:
   ```bash
   mv ~/.chatgpt-archive/chats.db /path/to/large/disk/chats.db
   export CHATGPT_ARCHIVE_DB=/path/to/large/disk/chats.db
   ```

---

## Semantic Search Problems

### "Error: Semantic search requires additional packages"

**Problem**: Semantic search dependencies not installed.

**Solution**:
```bash
pip install 'chatgpt-archive[semantic]'
```

### "Error: OPENAI_API_KEY not found"

**Problem**: API key not set in environment.

**Solutions**:
1. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="sk-..."
   # Make it permanent by adding to ~/.bashrc or ~/.zshrc
   ```

2. Verify it's set:
   ```bash
   echo $OPENAI_API_KEY
   ```

### "Error: No embeddings found"

**Problem**: Embeddings haven't been generated yet.

**Solution**:
```bash
# Generate embeddings first
chatgpt-archive embed

# Then use semantic search
chatgpt-archive search "query" --semantic
```

### Embedding generation is too expensive

**Problem**: Cost estimate is higher than expected.

**Solutions**:
1. Use smaller/cheaper model:
   ```bash
   # Default: text-embedding-3-small ($0.02/1M tokens)
   chatgpt-archive embed --estimate
   ```

2. Only embed specific conversations (not yet implemented - would need custom query):
   - Consider if semantic search is necessary for your use case
   - Keyword search (FTS5) is free and fast

3. Check for duplicate embeddings:
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db \
     "SELECT COUNT(*) FROM message_embeddings;"
   ```

### Embedding fails midway

**Problem**: API rate limits or network issues.

**Solution**:
Embedding is resumable - just run the command again:
```bash
chatgpt-archive embed
# Will skip already-embedded messages and continue
```

---

## Performance Issues

### Import is slower than expected

**Expected**: ~60 seconds for 64,000 messages on SSD

**Benchmarks**:
- HDD: 2-5x slower
- Network drive: 10x+ slower

**Solutions**:
1. Use local SSD
2. Close disk-intensive applications
3. Import to local disk first, then move database if needed

### Search is slow (>1 second for keywords)

**Expected**: <500ms for keyword search

**Solutions**:
1. Verify FTS5 index exists (see "Search is too slow" above)
2. Use more specific search terms
3. Add `--limit` to reduce results:
   ```bash
   chatgpt-archive search "python" --limit 10
   ```

### Semantic search is very slow

**Expected**: 2-5 seconds for semantic search

**This is normal** - vector similarity search is computationally expensive. Use hybrid search for best balance:
```bash
chatgpt-archive search "query" --hybrid
```

---

## Web UI Issues

### Raw markdown markers or dict-like payloads still appear in the transcript

**Problem**: The conversation page shows raw markdown syntax, `asset_pointer` dictionaries, or unformatted mixed-content blocks.

**Solutions**:
1. Inspect the conversation API response and confirm messages include `segments`.
2. Confirm the frontend is rendering `segments` before falling back to legacy `content` parsing.
3. Run the focused validation suites:
   ```bash
   cd /Users/peternicholls/Dev/OpenAI-Chats
   PYTHONPATH=/Users/peternicholls/Dev/OpenAI-Chats uv run --with pytest --with pytest-asyncio --with httpx --with fastapi --with pydantic --with python-multipart --with cryptography python -m pytest api/tests/test_conversations.py api/tests/test_formatting_service.py

   cd /Users/peternicholls/Dev/OpenAI-Chats/web
   npm run test -- __tests__/services/api.test.ts __tests__/components/MessageBubble.test.tsx __tests__/components/MarkdownRenderer.test.tsx __tests__/components/FallbackBlock.test.tsx
   npm run test:e2e -- --project=chrome __tests__/e2e/conversation.spec.ts
   ```

### Unsafe HTML appears to execute in the transcript

**Problem**: HTML-like content appears to render as live DOM instead of inert text.

**Solutions**:
1. Verify `MarkdownRenderer` does not use `rehype-raw` or any equivalent raw HTML plugin.
2. Run the markdown renderer tests to confirm script-like content stays inert text.
3. If you changed the markdown pipeline, re-audit the renderer before shipping.

### Port 80, 3000, or 8000 already in use

**Problem**: When starting the web UI, you get "address already in use" error.

**Solutions**:
1. Find and kill the process using the port:
   ```bash
   # Docker/nginx default
   lsof -i :80

   # Find process on port 3000
   lsof -i :3000
   # Kill it
   kill -9 <PID>
   
   # Same for port 8000
   lsof -i :8000
   kill -9 <PID>
   ```

2. Or change the nginx host port in `docker-compose.yml`:
   ```yaml
   services:
     nginx:
       ports:
         - "8080:80"  # Use 8080 instead
     api:
       environment:
         - CORS_ORIGINS=["http://localhost:8080"]
     web:
       build:
         args:
           - NEXT_PUBLIC_API_URL=http://localhost:8080
   ```

### CORS errors in browser console

**Problem**: Browser shows "Cross-Origin Request Blocked" or similar CORS errors.

**Solutions**:
1. Ensure CORS_ORIGINS environment variable includes your frontend URL:
   ```bash
   # In .env or docker-compose.yml
   CORS_ORIGINS='["http://localhost:3000"]'
   ```

2. For production, include all allowed origins:
   ```bash
   CORS_ORIGINS='["http://localhost:3000", "https://your-domain.com"]'
   ```

3. Verify the API is running and accessible:
   ```bash
   curl http://localhost:8000/api/health
   ```

### Permission denied on volume mount

**Problem**: Docker container can't access `~/.chatgpt-archive/` directory.

**Solutions**:
1. Ensure the directory exists and has correct permissions:
   ```bash
   mkdir -p ~/.chatgpt-archive
   chmod 755 ~/.chatgpt-archive
   ```

2. On Linux, you may need to run with your user ID:
   ```yaml
   # In docker-compose.yml
   services:
     api:
       user: "${UID}:${GID}"
   ```

3. Check SELinux (on Fedora/RHEL):
   ```bash
   # Allow Docker to access home directory
   chcon -Rt svirt_sandbox_file_t ~/.chatgpt-archive
   ```

### API returns 500 errors

**Problem**: API endpoints return internal server errors.

**Solutions**:
1. Check API logs for detailed error:
   ```bash
   docker-compose logs api
   ```

2. Verify environment variables are set correctly:
   ```bash
   # Required variables
   DB_PATH=/data/archive.db
   CORS_ORIGINS='["http://localhost:3000"]'
   ```

3. Check database file exists and has correct schema:
   ```bash
   sqlite3 ~/.chatgpt-archive/archive.db "PRAGMA integrity_check;"
   ```

### Security warning: "API exposed on all interfaces"

**Problem**: Startup shows "Security: API exposed on all interfaces (0.0.0.0)"

**Explanation**: This warning appears when the API binds to `0.0.0.0`, making it accessible from any network interface. This is expected for Docker deployments but may be a security concern.

**Solutions**:
1. For local-only access, set the host:
   ```bash
   API_HOST=127.0.0.1
   ```

2. In Docker, use network isolation:
   ```yaml
   # In docker-compose.yml
   services:
     api:
       networks:
         - internal
       # Don't expose port directly
   ```

3. Use a reverse proxy (nginx) to control access.

### Content Security Policy blocking resources

**Problem**: Browser blocks scripts or styles due to CSP headers.

**Solutions**:
1. Check browser console for specific CSP violations.

2. The API includes CSP headers that allow:
   - Scripts from 'self' and inline (for Next.js hydration)
   - Styles from 'self' and inline (for Tailwind)
   - Images from 'self', data:, and blob:
   - Connections to 'self' only

3. If you need additional sources, modify `api/middleware/cors.py`.

---

## Test Issues

### API tests fail with "OPENAI_API_KEY not set"

**Problem**: Some tests require mocked API credentials.

**Solution**: Tests use mocked clients and shouldn't require real API keys. If tests are failing:
```bash
# Ensure you're in the virtual environment
source .venv/bin/activate

# Run with verbose output to see the actual error
pytest api/tests/ -v --tb=long
```

### Frontend tests fail with "Cannot find module"

**Problem**: Dependencies not installed or path aliases not configured.

**Solution**:
```bash
cd web
npm install
npm test
```

### E2E tests fail to start server

**Problem**: Port 3030 already in use or server startup timeout.

**Solutions**:
1. Check if port is in use:
   ```bash
   lsof -i :3030
   kill -9 <PID>
   ```

2. Increase timeout in playwright.config.ts if needed.

3. Run the dev server manually first:
   ```bash
   npm run dev -- -p 3030
   # In another terminal
   npx playwright test
   ```

### Tests pass locally but fail in CI

**Problem**: Environment differences between local and CI.

**Solutions**:
1. Ensure all dependencies are in package.json/pyproject.toml
2. Check Node.js and Python versions match CI
3. Run tests with `--no-cache` to avoid stale test results

---

## General Debugging

### Enable verbose output

Run commands with `--json` to see machine-readable output:
```bash
chatgpt-archive import ./archive --json
chatgpt-archive search "python" --json
```

### Check database schema

Verify tables exist:
```bash
sqlite3 ~/.chatgpt-archive/chats.db << EOF
.tables
.schema conversations
.schema messages
.schema messages_fts
EOF
```

### Verify data integrity

Count records:
```bash
sqlite3 ~/.chatgpt-archive/chats.db << EOF
SELECT COUNT(*) as conversations FROM conversations;
SELECT COUNT(*) as messages FROM messages;
SELECT COUNT(*) as fts_entries FROM messages_fts;
EOF
```

### Get version info

```bash
chatgpt-archive --version
python --version
pip show chatgpt-archive
```

### Run with Python directly

Bypass potential PATH issues:
```bash
python -m chatgpt_archive --help
python -m chatgpt_archive import ./archive
```

### Check file permissions

```bash
# Database directory
ls -la ~/.chatgpt-archive/

# Database file
ls -la ~/.chatgpt-archive/chats.db
```

---

## Still Having Issues?

### Collect Debug Information

When filing a bug report, include:

1. Version information:
   ```bash
   chatgpt-archive --version
   python --version
   uname -a  # OS info
   ```

2. Database stats:
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db << EOF
   SELECT COUNT(*) FROM conversations;
   SELECT COUNT(*) FROM messages;
   .dbinfo
   EOF
   ```

3. Error output with `--json`:
   ```bash
   chatgpt-archive search "test" --json
   ```

4. Relevant logs/error messages (full text)

### File a Bug Report

- GitHub Issues: [https://github.com/peternicholls/OpenAI-Chats/issues](https://github.com/peternicholls/OpenAI-Chats/issues)
- Include debug information above
- Redact any personal/sensitive content from logs

### Community Support

- Check existing GitHub issues for similar problems
- Search discussions for solutions
- Ask in project discussions (if enabled)

---

## See Also

- [User Guide Index](README.md) - User documentation home
- [Root README](../../README.md) - Quick start and developer overview
- [CLI Reference](usage.md) - Complete command reference
- [Contributing](../../CONTRIBUTING.md) - Development guide
- [Python API](../API.md) - Programmatic usage
