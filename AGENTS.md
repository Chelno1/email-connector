# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Build/Dependency Management

### uv Package Manager
- Project uses `uv` instead of pip/venv for faster package management
- Virtual environment created with `uv venv` (not `python -m venv`)
- Dependencies installed via `uv pip sync requirements.txt` or `uv pip install -r requirements.txt`
- `uv pip sync` removes unlisted packages - ensures exact match with requirements.txt
- Virtual environment location: `.venv/` (standard uv convention)

## Project-Specific Patterns

### ConfigManager Singleton Pattern
- [`ConfigManager`](src/utils/config_manager.py:23) uses singleton pattern - only initializes once even with multiple instantiations
- Must pass `cli_args` dict during construction for CLI parameter priority to work
- Config priority: CLI args > env vars > defaults (implemented via `_convert_type()` internal method)

### Logger Initialization
- [`setup_logging()`](src/utils/logger.py:39) must be called BEFORE any logger usage
- Auto-initializes with defaults if [`get_logger()`](src/utils/logger.py:218) called first
- Console uses simplified format; file uses full format with line numbers
- File handler creates 10MB rotating logs (not configurable via env)

### CSV Encoding
- [`CSVWriter`](src/core/csv_writer.py:27) uses `utf-8-sig` (with BOM) for Excel compatibility
- Must call [`open()`](src/core/csv_writer.py:119) before [`write_message()`](src/core/csv_writer.py:185)
- Auto-flushes every 100 emails during batch writes

### Email Parsing Character Encoding
- [`EmailParser._decode_bytes()`](src/core/email_parser.py:264) tries multiple encodings in order: utf-8, gbk, gb2312, gb18030, iso-8859-1, windows-1252
- Final fallback uses utf-8 with `errors='replace'` - prevents crashes but may show replacement characters

### IMAP UID vs Sequence Numbers
- All IMAP operations use UID (not sequence numbers) via [`client.uid()`](src/core/imap_client.py:563)
- [`fetch_messages_batch()`](src/core/imap_client.py:582) yields `(uid, raw_email)` tuples - UID is first element

### Attachment File Conflicts
- [`Attachment.save()`](src/models/attachment.py:95) auto-renames on conflict: `file.pdf` → `file_1.pdf` → `file_2.pdf`
- Sets file permissions to 0o600 (owner read/write only) after save

### EmailMessage Validation
- [`EmailMessage.__post_init__()`](src/models/email_message.py:74) validates email formats and date types
- Automatically updates `has_attachment` flag when attachments list changes
- `to_csv_row()` returns semicolon-separated lists (not commas) for multi-value fields

## Testing Patterns

### CLI Testing
- [`src/cli.py`](src/cli.py:283) has standalone `main()` for testing argument parsing
- Run `python -m src.cli` to test CLI without executing email operations

### Running Single Components
- Each core module has usage examples in `examples/` directory
- Examples show module initialization order and required dependencies

## Critical Gotchas

- IMAP search criteria strings must NOT use 'ALL' as prefix when other criteria present (line 444 in imap_client.py shows the pattern)
- Date format for IMAP search is DD-Mon-YYYY (e.g., "01-Jan-2024"), NOT YYYY-MM-DD
- Logger's `@log_performance` decorator measures execution time - avoid on frequently called small functions
- EmailParser limits text to 50000 chars by default - not configurable via env vars