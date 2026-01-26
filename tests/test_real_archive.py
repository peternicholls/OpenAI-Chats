"""Real-world integration test using actual ChatGPT export archive."""

import sqlite3
import tempfile
from pathlib import Path
from click.testing import CliRunner

from chatgpt_archive.cli import main


class TestRealArchive:
    """Test with actual ChatGPT export archive if available."""
    
    def test_import_real_archive(self):
        """Test importing the real archive in the workspace."""
        # Find the real archive directory
        archive_dir = Path(__file__).parent.parent / "6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875"
        
        if not archive_dir.exists():
            # Skip if archive not available
            import pytest
            pytest.skip("Real archive not found")
        
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_real.db"
            
            # Import the real archive
            result = runner.invoke(main, [
                '--json',
                '--db', str(db_path),
                'import',
                str(archive_dir)
            ])
            
            # Should succeed
            assert result.exit_code == 0, f"Import failed: {result.output}"
            
            # Parse JSON output
            import json
            output = json.loads(result.output)
            assert output["status"] == "success"
            assert output["conversations_imported"] > 0
            assert output["messages_imported"] > 0
            
            # Verify database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cursor.fetchone()[0]
            assert conv_count == output["conversations_imported"]
            
            # Check messages
            cursor.execute("SELECT COUNT(*) FROM messages")
            msg_count = cursor.fetchone()[0]
            assert msg_count == output["messages_imported"]
            
            # Test FTS5 search
            cursor.execute("""
                SELECT COUNT(*) FROM messages_fts 
                WHERE messages_fts MATCH 'machine learning'
            """)
            search_results = cursor.fetchone()[0]
            assert search_results > 0, "FTS5 search should find results"
            
            conn.close()
    
    def test_reimport_idempotency(self):
        """Test that re-importing same archive is idempotent."""
        archive_dir = Path(__file__).parent.parent / "6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875"
        
        if not archive_dir.exists():
            import pytest
            pytest.skip("Real archive not found")
        
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_idempotent.db"
            
            # First import
            result1 = runner.invoke(main, [
                '--json',
                '--db', str(db_path),
                'import',
                str(archive_dir)
            ])
            assert result1.exit_code == 0
            
            import json
            output1 = json.loads(result1.output)
            conv_count1 = output1["conversations_imported"]
            msg_count1 = output1["messages_imported"]
            
            # Second import
            result2 = runner.invoke(main, [
                '--json',
                '--db', str(db_path),
                'import',
                str(archive_dir)
            ])
            assert result2.exit_code == 0
            
            output2 = json.loads(result2.output)
            
            # Should have same counts
            assert output2["conversations_imported"] == conv_count1
            assert output2["messages_imported"] == msg_count1
            
            # Verify database has no duplicates
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM conversations")
            assert cursor.fetchone()[0] == conv_count1
            
            cursor.execute("SELECT COUNT(*) FROM messages")
            assert cursor.fetchone()[0] == msg_count1
            
            conn.close()
