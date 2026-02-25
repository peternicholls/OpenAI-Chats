# Test Specifications

**Feature**: 002-web-ui Test Coverage  
**Date**: 2026-02-13  
**Purpose**: Detailed test case specifications for all layers

---

## Python Library Tests (chatgpt_archive/)

### tests/unit/test_exporters.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| EXP-001 | test_markdown_export_single_conversation | Export one conversation to markdown | Valid .md with title, messages formatted |
| EXP-002 | test_markdown_export_multipart_content | Export message with multiple parts | Parts joined with newlines |
| EXP-003 | test_json_export_structure | Export to JSON format | Valid JSON matching schema |
| EXP-004 | test_json_export_special_chars | Export with emoji/unicode | Characters preserved |
| EXP-005 | test_yaml_export_structure | Export to YAML format | Valid YAML, parseable |
| EXP-006 | test_html_export_structure | Export to HTML format | Valid HTML5, includes CSS |
| EXP-007 | test_html_export_xss_prevention | Export with HTML in content | Tags escaped |
| EXP-008 | test_xml_export_structure | Export to XML format | Valid XML, well-formed |
| EXP-009 | test_xml_export_special_chars | Export with <, >, & characters | Properly escaped |
| EXP-010 | test_csv_export_structure | Export to CSV format | Valid CSV, header row |
| EXP-011 | test_csv_export_commas_in_content | Export with commas in messages | Properly quoted |
| EXP-012 | test_excel_export_structure | Export to .xlsx format | Valid Excel file |
| EXP-013 | test_excel_export_binary | Export returns bytes | Returns bytes, not str |
| EXP-014 | test_export_empty_conversation | Export conversation with no messages | Valid output, empty messages section |

### tests/unit/test_search.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| SCH-001 | test_fts_search_basic | Search for single word | Returns matching conversations |
| SCH-002 | test_fts_search_phrase | Search for exact phrase | Phrase matches ranked higher |
| SCH-003 | test_fts_search_no_results | Search for nonexistent term | Empty results, no error |
| SCH-004 | test_fts_search_special_chars | Search with quotes, dashes | Handles gracefully |
| SCH-005 | test_search_with_date_filter | Search with from_date/to_date | Only returns in range |
| SCH-006 | test_search_result_preview | Search result contains preview | Preview has matching snippet |
| SCH-007 | test_search_match_count | Search shows match_count | Count reflects actual matches |
| SCH-008 | test_search_performance | Search 500 conversations | Returns in <500ms |

### tests/unit/test_embeddings.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| EMB-001 | test_estimate_tokens | Estimate token count | Returns positive integer |
| EMB-002 | test_estimate_cost | Estimate API cost | Returns cost in USD |
| EMB-003 | test_batch_messages | Batch messages for API | Batches respect size limit |
| EMB-004 | test_store_embedding | Store embedding vector | Vector stored in DB |
| EMB-005 | test_embedding_mock_api | Generate with mocked OpenAI | No real API call |

---

## API Integration Tests (api/)

### tests/integration/test_api_conversations.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| API-CONV-001 | test_list_conversations_empty | List with no data | 200, empty items |
| API-CONV-002 | test_list_conversations_paginated | List with pagination | 200, respects limit/offset |
| API-CONV-003 | test_list_conversations_sorted_date | Sort by date desc | Most recent first |
| API-CONV-004 | test_list_conversations_sorted_title | Sort by title asc | Alphabetical order |
| API-CONV-005 | test_get_conversation_exists | Get existing conversation | 200, full detail |
| API-CONV-006 | test_get_conversation_not_found | Get nonexistent ID | 404 error |
| API-CONV-007 | test_delete_conversation | Delete conversation | 204, actually deleted |
| API-CONV-008 | test_delete_conversation_not_found | Delete nonexistent | 404 error |

### tests/integration/test_api_search.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| API-SCH-001 | test_search_keyword | POST /api/search keyword | 200, results |
| API-SCH-002 | test_search_empty_query | POST with empty query | 422 validation error |
| API-SCH-003 | test_search_date_filter | POST with date range | Only filtered results |
| API-SCH-004 | test_search_limit | POST with limit=5 | Max 5 results |

### tests/integration/test_api_export.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| API-EXP-001 | test_export_markdown | Export as md | 200, text/markdown |
| API-EXP-002 | test_export_json | Export as json | 200, application/json |
| API-EXP-003 | test_export_yaml | Export as yaml | 200, application/x-yaml |
| API-EXP-004 | test_export_html | Export as html | 200, text/html |
| API-EXP-005 | test_export_xml | Export as xml | 200, application/xml |
| API-EXP-006 | test_export_csv | Export as csv | 200, text/csv |
| API-EXP-007 | test_export_excel | Export as xlsx | 200, application/vnd.openxmlformats |
| API-EXP-008 | test_export_invalid_format | Export as invalid | 422 error |
| API-EXP-009 | test_export_not_found | Export nonexistent | 404 error |

### tests/integration/test_api_tags.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| API-TAG-001 | test_list_tags_empty | List with no tags | 200, empty array |
| API-TAG-002 | test_list_tags_with_counts | List tags with usage | 200, includes count |
| API-TAG-003 | test_add_tag | POST tag to conversation | 204, tag visible |
| API-TAG-004 | test_add_tag_duplicate | Add same tag twice | 204, no duplicate |
| API-TAG-005 | test_remove_tag | DELETE tag | 204, tag removed |
| API-TAG-006 | test_remove_tag_not_found | DELETE nonexistent tag | 404 error |

### tests/integration/test_api_favorites.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| API-FAV-001 | test_toggle_favorite_on | Toggle favorite on | 200, is_favorite: true |
| API-FAV-002 | test_toggle_favorite_off | Toggle favorite off | 200, is_favorite: false |
| API-FAV-003 | test_list_favorites | List favorites only | 200, only favorited |
| API-FAV-004 | test_list_favorites_empty | No favorites | 200, empty |

### tests/integration/test_api_import.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| API-IMP-001 | test_import_valid_zip | POST valid archive | 202 accepted |
| API-IMP-002 | test_import_invalid_file | POST non-zip file | 400 error |
| API-IMP-003 | test_import_progress | GET progress | 200, progress object |
| API-IMP-004 | test_import_corrupted_zip | POST corrupted zip | Error in progress |

### tests/integration/test_api_settings.py

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| API-SET-001 | test_get_settings | GET /api/settings | 200, settings object |
| API-SET-002 | test_update_theme | PUT theme=dark | 200, theme updated |
| API-SET-003 | test_update_openai_key | PUT openai_api_key | 200, key stored |
| API-SET-004 | test_update_invalid | PUT invalid field | 422 error |

---

## Frontend Tests (web/)

### web/__tests__/services/api.test.ts

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| FE-API-001 | test_listConversations | Call listConversations() | Returns paginated data |
| FE-API-002 | test_listConversations_params | Call with sort/limit | Params in query string |
| FE-API-003 | test_getConversation | Call getConversation(id) | Returns detail |
| FE-API-004 | test_getConversation_error | Call with invalid id | Throws error |
| FE-API-005 | test_search | Call search() | Returns results |
| FE-API-006 | test_search_filters | Call with date filters | Filters in body |
| FE-API-007 | test_listTags | Call listTags() | Returns tag array |
| FE-API-008 | test_addTag | Call addTag() | Makes POST request |
| FE-API-009 | test_removeTag | Call removeTag() | Makes DELETE request |
| FE-API-010 | test_toggleFavorite | Call toggleFavorite() | Returns new status |
| FE-API-011 | test_uploadArchive | Call with File | FormData sent |
| FE-API-012 | test_getImportProgress | Poll progress | Returns progress |
| FE-API-013 | test_exportConversation | Get export blob | Returns Blob |
| FE-API-014 | test_healthCheck | Call healthCheck() | Returns status |
| FE-API-015 | test_error_handling | API returns 500 | Throws with message |

### web/__tests__/hooks/useConversations.test.ts

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| FE-HOOK-001 | test_useConversations_loading | Initial state | isLoading: true |
| FE-HOOK-002 | test_useConversations_success | After fetch | data populated |
| FE-HOOK-003 | test_useConversations_refetch | Call refetch | New request made |
| FE-HOOK-004 | test_useConversations_error | API error | error populated |
| FE-HOOK-005 | test_useConversation_detail | Fetch single | Returns detail |

### web/__tests__/hooks/useSearch.test.ts

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| FE-HOOK-006 | test_useSearch_idle | No query | No request made |
| FE-HOOK-007 | test_useSearch_debounce | Type query | Waits 500ms |
| FE-HOOK-008 | test_useSearch_results | After debounce | Results returned |
| FE-HOOK-009 | test_useSearch_error | API error | Error state |
| FE-HOOK-010 | test_useSearch_clear | Clear query | Results cleared |

### web/__tests__/hooks/useFavorites.test.ts

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| FE-HOOK-011 | test_useFavorites_list | Fetch favorites | Returns favorites |
| FE-HOOK-012 | test_useFavorites_toggle | Toggle mutation | Optimistic update |
| FE-HOOK-013 | test_useFavorites_invalidate | After toggle | List refetched |

### web/__tests__/hooks/useTags.test.ts

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| FE-HOOK-014 | test_useTags_list | Fetch all tags | Returns tags |
| FE-HOOK-015 | test_useTags_add | Add mutation | Tag added |
| FE-HOOK-016 | test_useTags_remove | Remove mutation | Tag removed |
| FE-HOOK-017 | test_useTags_invalidate | After mutation | List refetched |

### web/__tests__/components/ConversationCard.test.tsx

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| FE-COMP-001 | test_renders_title | Render with title | Title visible |
| FE-COMP-002 | test_renders_untitled | Render null title | Shows "[Untitled]" |
| FE-COMP-003 | test_renders_date | Render with date | Formatted date visible |
| FE-COMP-004 | test_renders_message_count | Render with count | Count badge visible |
| FE-COMP-005 | test_click_navigates | Click card | onClick called |
| FE-COMP-006 | test_favorite_icon | Favorited card | Star icon filled |
| FE-COMP-007 | test_tags_displayed | Card with tags | Tag chips visible |

### web/__tests__/components/MessageBubble.test.tsx

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| FE-COMP-008 | test_user_message_style | User role | Right-aligned, blue |
| FE-COMP-009 | test_assistant_message_style | Assistant role | Left-aligned, gray |
| FE-COMP-010 | test_content_rendered | Message content | Content visible |
| FE-COMP-011 | test_markdown_rendered | Content with markdown | Markdown formatted |
| FE-COMP-012 | test_code_highlighted | Code blocks | Syntax highlighting |
| FE-COMP-013 | test_empty_content | Null content | Handles gracefully |

### web/__tests__/components/SearchBar.test.tsx

| Test ID | Test Name | Description | Expected |
|---------|-----------|-------------|----------|
| FE-COMP-014 | test_renders_input | Render component | Input visible |
| FE-COMP-015 | test_typing_calls_onChange | Type text | onChange with value |
| FE-COMP-016 | test_clear_button | Click clear | Input cleared |
| FE-COMP-017 | test_loading_spinner | isLoading prop | Spinner visible |
| FE-COMP-018 | test_placeholder | Default state | Placeholder text |

---

## Test Fixtures

### tests/fixtures/sample_conversation.json

```json
{
  "id": "test-conv-001",
  "title": "Test Conversation",
  "create_time": 1710000000.0,
  "update_time": 1710000100.0,
  "mapping": {
    "msg-1": {
      "id": "msg-1",
      "message": {
        "id": "msg-1",
        "author": {"role": "user"},
        "content": {"parts": ["Hello, how are you?"]},
        "create_time": 1710000000.0
      },
      "parent": null,
      "children": ["msg-2"]
    },
    "msg-2": {
      "id": "msg-2",
      "message": {
        "id": "msg-2",
        "author": {"role": "assistant"},
        "content": {"parts": ["I'm doing well, thank you! How can I help you today?"]},
        "create_time": 1710000050.0
      },
      "parent": "msg-1",
      "children": []
    }
  }
}
```

### tests/fixtures/sample_archive/

```
sample_archive/
├── conversations.json   # Array of 3 sample conversations
├── user.json           # User profile
├── message_feedback.json
└── shared_conversations.json
```

---

## Coverage Targets

| Layer | Target | Measurement |
|-------|--------|-------------|
| Python unit tests | 80%+ | pytest-cov |
| Python integration | 100% endpoints | All routes tested |
| Frontend services | 100% methods | All API client methods |
| Frontend hooks | 80%+ | All query hooks |
| Frontend components | 70%+ | Key user-facing components |

---

## Running Tests

### Python
```bash
# Unit tests only
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# All tests with coverage
pytest --cov=chatgpt_archive --cov=api --cov-report=term-missing

# Specific test file
pytest tests/integration/test_api_conversations.py -v
```

### TypeScript
```bash
cd web

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch

# Specific file
npm test -- api.test.ts
```

### CI Pipeline
```yaml
test:
  script:
    - pip install -e ".[dev]"
    - cd api && pip install -e ".[dev]"
    - pytest --cov --cov-fail-under=70
    - cd ../web && npm ci && npm test
```
