"""
Tests for File and Directory Operations (FaDO.py) module.

This module contains unit tests for the file and directory manipulation utilities.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from helpers.FaDO import (
    create_directory,
    delete_directory,
    rename_directory,
    move_directory,
    list_directory,
    file_exists,
    directory_exists
)


class TestCreateDirectory:
    """Test suite for create_directory function."""
    
    def test_create_new_directory(self, tmp_path):
        """Test creating a new directory."""
        test_dir = tmp_path / "test_new_dir"
        result = create_directory(str(test_dir))
        
        assert result is True
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    def test_create_nested_directory(self, tmp_path):
        """Test creating nested directories."""
        test_dir = tmp_path / "parent" / "child" / "grandchild"
        result = create_directory(str(test_dir))
        
        assert result is True
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    def test_create_existing_directory(self, tmp_path):
        """Test creating a directory that already exists."""
        test_dir = tmp_path / "existing_dir"
        test_dir.mkdir()
        
        result = create_directory(str(test_dir))
        
        assert result is True
        assert test_dir.exists()
    
    @patch('os.makedirs')
    def test_permission_error_handling(self, mock_makedirs, tmp_path):
        """Test that PermissionError is caught and logged."""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        test_dir = tmp_path / "no_permission"
        
        result = create_directory(str(test_dir))
        
        assert result is False
        mock_makedirs.assert_called_once_with(str(test_dir))
    
    @patch('os.makedirs')
    def test_os_error_handling(self, mock_makedirs, tmp_path):
        """Test that OSError is caught and logged."""
        mock_makedirs.side_effect = OSError("Disk full")
        test_dir = tmp_path / "disk_full"
        
        result = create_directory(str(test_dir))
        
        assert result is False
        mock_makedirs.assert_called_once_with(str(test_dir))
    
    @patch('os.makedirs')
    def test_unexpected_error_propagates(self, mock_makedirs, tmp_path):
        """Test that unexpected exceptions propagate."""
        mock_makedirs.side_effect = ValueError("Unexpected error")
        test_dir = tmp_path / "unexpected"
        
        with pytest.raises(ValueError, match="Unexpected error"):
            create_directory(str(test_dir))


class TestDeleteDirectory:
    """Test suite for delete_directory function."""
    
    def test_delete_existing_directory(self, tmp_path):
        """Test deleting an existing directory."""
        test_dir = tmp_path / "to_delete"
        test_dir.mkdir()
        
        result = delete_directory(str(test_dir))
        
        assert result is True
        assert not test_dir.exists()
    
    def test_delete_directory_with_contents(self, tmp_path):
        """Test deleting a directory with files."""
        test_dir = tmp_path / "with_files"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content")
        (test_dir / "file2.txt").write_text("content")
        
        result = delete_directory(str(test_dir))
        
        assert result is True
        assert not test_dir.exists()
    
    def test_delete_nonexistent_directory(self, tmp_path):
        """Test deleting a directory that doesn't exist."""
        test_dir = tmp_path / "nonexistent"
        
        result = delete_directory(str(test_dir))
        
        assert result is False
    
    @patch('shutil.rmtree')
    def test_permission_error_handling(self, mock_rmtree, tmp_path):
        """Test that PermissionError is caught and logged."""
        mock_rmtree.side_effect = PermissionError("Permission denied")
        test_dir = tmp_path / "no_permission"
        
        result = delete_directory(str(test_dir))
        
        assert result is False
        mock_rmtree.assert_called_once_with(str(test_dir))
    
    @patch('shutil.rmtree')
    def test_os_error_handling(self, mock_rmtree, tmp_path):
        """Test that OSError is caught and logged."""
        mock_rmtree.side_effect = OSError("Directory in use")
        test_dir = tmp_path / "in_use"
        
        result = delete_directory(str(test_dir))
        
        assert result is False
        mock_rmtree.assert_called_once_with(str(test_dir))
    
    @patch('shutil.rmtree')
    def test_unexpected_error_propagates(self, mock_rmtree, tmp_path):
        """Test that unexpected exceptions propagate."""
        mock_rmtree.side_effect = ValueError("Unexpected error")
        test_dir = tmp_path / "unexpected"
        
        with pytest.raises(ValueError, match="Unexpected error"):
            delete_directory(str(test_dir))


class TestRenameDirectory:
    """Test suite for rename_directory function."""
    
    def test_rename_directory(self, tmp_path):
        """Test renaming a directory."""
        old_dir = tmp_path / "old_name"
        new_dir = tmp_path / "new_name"
        old_dir.mkdir()
        
        result = rename_directory(str(old_dir), str(new_dir))
        
        assert result is True
        assert not old_dir.exists()
        assert new_dir.exists()
    
    def test_rename_nonexistent_directory(self, tmp_path):
        """Test renaming a directory that doesn't exist."""
        old_dir = tmp_path / "nonexistent"
        new_dir = tmp_path / "new_name"
        
        result = rename_directory(str(old_dir), str(new_dir))
        
        assert result is False
    
    @patch('shutil.move')
    def test_permission_error_handling(self, mock_move, tmp_path):
        """Test that PermissionError is caught and logged."""
        mock_move.side_effect = PermissionError("Permission denied")
        old_dir = tmp_path / "old"
        new_dir = tmp_path / "new"
        
        result = rename_directory(str(old_dir), str(new_dir))
        
        assert result is False
        mock_move.assert_called_once_with(str(old_dir), str(new_dir))
    
    @patch('shutil.move')
    def test_os_error_handling(self, mock_move, tmp_path):
        """Test that OSError is caught and logged."""
        mock_move.side_effect = OSError("Cross-device link")
        old_dir = tmp_path / "old"
        new_dir = tmp_path / "new"
        
        result = rename_directory(str(old_dir), str(new_dir))
        
        assert result is False
        mock_move.assert_called_once_with(str(old_dir), str(new_dir))
    
    @patch('shutil.move')
    def test_unexpected_error_propagates(self, mock_move, tmp_path):
        """Test that unexpected exceptions propagate."""
        mock_move.side_effect = ValueError("Unexpected error")
        old_dir = tmp_path / "old"
        new_dir = tmp_path / "new"
        
        with pytest.raises(ValueError, match="Unexpected error"):
            rename_directory(str(old_dir), str(new_dir))


class TestMoveDirectory:
    """Test suite for move_directory function."""
    
    def test_move_directory(self, tmp_path):
        """Test moving a directory."""
        src_dir = tmp_path / "source"
        dest_dir = tmp_path / "destination"
        src_dir.mkdir()
        
        result = move_directory(str(src_dir), str(dest_dir))
        
        assert result is True
        assert not src_dir.exists()
        assert dest_dir.exists()
    
    def test_move_nonexistent_directory(self, tmp_path):
        """Test moving a directory that doesn't exist."""
        src_dir = tmp_path / "nonexistent"
        dest_dir = tmp_path / "destination"
        
        result = move_directory(str(src_dir), str(dest_dir))
        
        assert result is False
    
    @patch('shutil.move')
    def test_permission_error_handling(self, mock_move, tmp_path):
        """Test that PermissionError is caught and logged."""
        mock_move.side_effect = PermissionError("Permission denied")
        src_dir = tmp_path / "src"
        dest_dir = tmp_path / "dest"
        
        result = move_directory(str(src_dir), str(dest_dir))
        
        assert result is False
        mock_move.assert_called_once_with(str(src_dir), str(dest_dir))
    
    @patch('shutil.move')
    def test_os_error_handling(self, mock_move, tmp_path):
        """Test that OSError is caught and logged."""
        mock_move.side_effect = OSError("Destination exists")
        src_dir = tmp_path / "src"
        dest_dir = tmp_path / "dest"
        
        result = move_directory(str(src_dir), str(dest_dir))
        
        assert result is False
        mock_move.assert_called_once_with(str(src_dir), str(dest_dir))
    
    @patch('shutil.move')
    def test_unexpected_error_propagates(self, mock_move, tmp_path):
        """Test that unexpected exceptions propagate."""
        mock_move.side_effect = ValueError("Unexpected error")
        src_dir = tmp_path / "src"
        dest_dir = tmp_path / "dest"
        
        with pytest.raises(ValueError, match="Unexpected error"):
            move_directory(str(src_dir), str(dest_dir))


class TestListDirectory:
    """Test suite for list_directory function."""
    
    def test_list_directory_contents(self, tmp_path):
        """Test listing directory contents."""
        test_dir = tmp_path / "list_test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content")
        (test_dir / "file2.txt").write_text("content")
        (test_dir / "subdir").mkdir()
        
        result = list_directory(str(test_dir))
        
        assert result is not None
        assert len(result) == 3
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir" in result
    
    def test_list_directory_recursive(self, tmp_path):
        """Test listing directory contents recursively."""
        test_dir = tmp_path / "recursive_test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content")
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("content")
        
        result = list_directory(str(test_dir), recursive=True)
        
        assert result is not None
        assert len(result) == 2
        assert "file1.txt" in result
        assert str(Path("subdir") / "file2.txt") in result
    
    def test_list_nonexistent_directory(self, tmp_path):
        """Test listing a directory that doesn't exist."""
        test_dir = tmp_path / "nonexistent"
        
        result = list_directory(str(test_dir))
        
        assert result is None
    
    @patch('pathlib.Path.iterdir')
    def test_permission_error_handling(self, mock_iterdir, tmp_path):
        """Test that PermissionError is caught and logged."""
        mock_iterdir.side_effect = PermissionError("Permission denied")
        test_dir = tmp_path / "no_permission"
        test_dir.mkdir()
        
        result = list_directory(str(test_dir))
        
        assert result is None
    
    @patch('pathlib.Path.iterdir')
    def test_os_error_handling(self, mock_iterdir, tmp_path):
        """Test that OSError is caught and logged."""
        mock_iterdir.side_effect = OSError("I/O error")
        test_dir = tmp_path / "io_error"
        test_dir.mkdir()
        
        result = list_directory(str(test_dir))
        
        assert result is None
    
    @patch('pathlib.Path.iterdir')
    def test_unexpected_error_propagates(self, mock_iterdir, tmp_path):
        """Test that unexpected exceptions propagate."""
        mock_iterdir.side_effect = ValueError("Unexpected error")
        test_dir = tmp_path / "unexpected"
        test_dir.mkdir()
        
        with pytest.raises(ValueError, match="Unexpected error"):
            list_directory(str(test_dir))


class TestFileExists:
    """Test suite for file_exists function."""
    
    def test_file_exists_true(self, tmp_path):
        """Test checking if a file exists (true case)."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        result = file_exists(str(test_file))
        
        assert result is True
    
    def test_file_exists_false(self, tmp_path):
        """Test checking if a file exists (false case)."""
        test_file = tmp_path / "nonexistent.txt"
        
        result = file_exists(str(test_file))
        
        assert result is False
    
    def test_directory_not_file(self, tmp_path):
        """Test that directory is not considered a file."""
        test_dir = tmp_path / "dir"
        test_dir.mkdir()
        
        result = file_exists(str(test_dir))
        
        assert result is False


class TestDirectoryExists:
    """Test suite for directory_exists function."""
    
    def test_directory_exists_true(self, tmp_path):
        """Test checking if a directory exists (true case)."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        
        result = directory_exists(str(test_dir))
        
        assert result is True
    
    def test_directory_exists_false(self, tmp_path):
        """Test checking if a directory exists (false case)."""
        test_dir = tmp_path / "nonexistent"
        
        result = directory_exists(str(test_dir))
        
        assert result is False
    
    def test_file_not_directory(self, tmp_path):
        """Test that file is not considered a directory."""
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")
        
        result = directory_exists(str(test_file))
        
        assert result is False


class TestIntegration:
    """Integration tests for file and directory operations."""
    
    def test_create_move_delete_workflow(self, tmp_path):
        """Test a complete workflow of creating, moving, and deleting."""
        # Create
        original = tmp_path / "original"
        result = create_directory(str(original))
        assert result is True
        assert original.exists()
        
        # Move
        moved = tmp_path / "moved"
        result = move_directory(str(original), str(moved))
        assert result is True
        assert not original.exists()
        assert moved.exists()
        
        # Delete
        result = delete_directory(str(moved))
        assert result is True
        assert not moved.exists()
    
    def test_create_rename_list_workflow(self, tmp_path):
        """Test creating, renaming, and listing directory."""
        # Create with contents
        original = tmp_path / "test_project"
        create_directory(str(original))
        (original / "file1.py").write_text("print('hello')")
        (original / "file2.py").write_text("print('world')")
        
        # List contents
        contents = list_directory(str(original))
        assert contents is not None
        assert len(contents) == 2
        
        # Rename
        renamed = tmp_path / "renamed_project"
        result = rename_directory(str(original), str(renamed))
        assert result is True
        
        # List renamed directory
        contents = list_directory(str(renamed))
        assert contents is not None
        assert len(contents) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
