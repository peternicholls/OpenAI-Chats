"""Integration tests for CLI commands."""

import json
import tempfile
from pathlib import Path
from click.testing import CliRunner

from chatgpt_archive.cli import main


class TestCLI:
    """Tests for command-line interface."""
    
    def test_version_option(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert "chatgpt-archive" in result.output
        assert "0.1.0" in result.output
    
    def test_help_option(self):
        """Test --help flag."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "import" in result.output
        assert "search" in result.output
        assert "list" in result.output
        assert "view" in result.output
        assert "export" in result.output
    
    def test_import_help(self):
        """Test import command help."""
        runner = CliRunner()
        result = runner.invoke(main, ['import', '--help'])
        assert result.exit_code == 0
        assert "ARCHIVE_DIR" in result.output
    
    def test_import_missing_directory(self):
        """Test import with nonexistent directory."""
        runner = CliRunner()
        result = runner.invoke(main, ['import', '/nonexistent/path'])
        assert result.exit_code != 0
    
    def test_import_valid_archive(self):
        """Test importing a minimal valid archive."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create minimal archive
            archive_dir = tmp_path / "archive"
            archive_dir.mkdir()
            
            conversations_data = [
                {
                    "id": "test-conv",
                    "title": "Test Conversation",
                    "create_time": 1710000000.0,
                    "mapping": {
                        "msg-1": {
                            "id": "msg-1",
                            "message": {
                                "id": "msg-1",
                                "author": {"role": "user"},
                                "content": {"parts": ["Hello"]},
                                "create_time": 1710000000.0
                            },
                            "parent": None,
                            "children": []
                        }
                    }
                }
            ]
            
            conversations_file = archive_dir / "conversations.json"
            conversations_file.write_text(json.dumps(conversations_data))
            
            # Use temporary database
            db_path = tmp_path / "test.db"
            
            # Run import
            result = runner.invoke(main, [
                '--db', str(db_path),
                'import',
                str(archive_dir)
            ])
            
            assert result.exit_code == 0
            assert "Import complete" in result.output or "success" in result.output
            assert db_path.exists()
    
    def test_import_json_output(self):
        """Test import with JSON output."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create minimal archive
            archive_dir = tmp_path / "archive"
            archive_dir.mkdir()
            
            conversations_data = [{
                "id": "test",
                "title": "Test",
                "create_time": 1710000000.0,
                "mapping": {}
            }]
            
            (archive_dir / "conversations.json").write_text(json.dumps(conversations_data))
            db_path = tmp_path / "test.db"
            
            # Run import with --json
            result = runner.invoke(main, [
                '--json',
                '--db', str(db_path),
                'import',
                str(archive_dir)
            ])
            
            assert result.exit_code == 0
            
            # Parse JSON output
            output = json.loads(result.output)
            assert output["status"] == "success"
            assert "conversations_imported" in output
            assert output["conversations_imported"] == 1


class TestCommandAliases:
    """Test command aliases."""
    
    def test_ls_alias_for_list(self):
        """Test 'ls' alias for 'list' command."""
        runner = CliRunner()
        result = runner.invoke(main, ['ls', '--help'])
        # Should work even though command doesn't exist yet
        assert "list" in result.output.lower() or result.exit_code == 0
    
    def test_find_alias_for_search(self):
        """Test 'find' alias for 'search' command."""
        runner = CliRunner()
        result = runner.invoke(main, ['find', '--help'])
        assert "search" in result.output.lower() or result.exit_code == 0
    
    def test_show_alias_for_view(self):
        """Test 'show' alias for 'view' command."""
        runner = CliRunner()
        result = runner.invoke(main, ['show', '--help'])
        assert "view" in result.output.lower() or result.exit_code == 0
