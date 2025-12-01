"""File and Directory Operations Module.

A utility module to handle common file and directory operations
including creating, deleting, renaming, and moving files and directories.

Example:
    >>> from helpers.FaDO import create_directory, delete_directory
    >>> create_directory("/tmp/new_folder")
    True
    >>> delete_directory("/tmp/new_folder")
    True
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Union


def create_directory(path: Union[str, Path]) -> bool:
    """Create a new directory at the specified path.

    Creates a directory and all necessary parent directories.
    If the directory already exists, returns True without error.

    Args:
        path: The path of the new directory to create.

    Returns:
        True if the directory was created or already exists,
        False if creation failed.

    Example:
        >>> create_directory("/tmp/my_project/data")
        True
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory '{path}': {e}")
        return False


def delete_directory(path: Union[str, Path]) -> bool:
    """Delete a directory and all its contents.

    Recursively removes the directory and all files/subdirectories
    within it.

    Args:
        path: The path of the directory to delete.

    Returns:
        True if the directory was deleted successfully,
        False if deletion failed or directory doesn't exist.

    Example:
        >>> delete_directory("/tmp/old_project")
        True
    """
    try:
        if not os.path.exists(path):
            return False
        shutil.rmtree(path)
        return True
    except Exception as e:
        print(f"Error deleting directory '{path}': {e}")
        return False


def rename_directory(src: Union[str, Path], dest: Union[str, Path]) -> bool:
    """Rename a directory.

    Renames/moves a directory from the source path to the destination path.

    Args:
        src: The source path of the directory.
        dest: The destination path (new name/location).

    Returns:
        True if the directory was renamed successfully,
        False if the operation failed.

    Example:
        >>> rename_directory("/tmp/old_name", "/tmp/new_name")
        True
    """
    try:
        if not os.path.exists(src):
            return False
        shutil.move(src, dest)
        return True
    except Exception as e:
        print(f"Error renaming directory '{src}' to '{dest}': {e}")
        return False


def move_directory(src: Union[str, Path], dest: Union[str, Path]) -> bool:
    """Move a directory to a new location.

    Moves a directory from the source path to the destination path.

    Args:
        src: The source path of the directory.
        dest: The destination path for the directory.

    Returns:
        True if the directory was moved successfully,
        False if the operation failed.

    Example:
        >>> move_directory("/tmp/project", "/home/user/project")
        True
    """
    return rename_directory(src, dest)


def copy_directory(src: Union[str, Path], dest: Union[str, Path]) -> bool:
    """Copy a directory and its contents.

    Creates a copy of the source directory at the destination path.

    Args:
        src: The source path of the directory to copy.
        dest: The destination path for the copy.

    Returns:
        True if the directory was copied successfully,
        False if the operation failed.

    Example:
        >>> copy_directory("/tmp/project", "/tmp/project_backup")
        True
    """
    try:
        if not os.path.exists(src):
            return False
        shutil.copytree(src, dest)
        return True
    except Exception as e:
        print(f"Error copying directory '{src}' to '{dest}': {e}")
        return False


def list_directory(
    path: Union[str, Path],
    pattern: Optional[str] = None,
    recursive: bool = False,
) -> List[str]:
    """List contents of a directory.

    Returns a list of files and subdirectories in the specified path.

    Args:
        path: The directory path to list.
        pattern: Optional glob pattern to filter results (e.g., "*.py").
        recursive: If True, recursively list all nested contents.

    Returns:
        A list of file/directory paths within the specified directory.

    Example:
        >>> list_directory("/tmp/project", "*.py")
        ['main.py', 'utils.py']
        >>> list_directory("/tmp/project", recursive=True)
        ['main.py', 'src/app.py', 'tests/test_main.py']
    """
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return []

        if pattern:
            if recursive:
                return [str(p.relative_to(path)) for p in path_obj.rglob(pattern)]
            return [str(p.relative_to(path)) for p in path_obj.glob(pattern)]

        if recursive:
            return [
                str(p.relative_to(path))
                for p in path_obj.rglob("*")
                if p.is_file() or p.is_dir()
            ]
        return [p.name for p in path_obj.iterdir()]
    except Exception as e:
        print(f"Error listing directory '{path}': {e}")
        return []


def directory_exists(path: Union[str, Path]) -> bool:
    """Check if a directory exists.

    Args:
        path: The path to check.

    Returns:
        True if the path exists and is a directory, False otherwise.

    Example:
        >>> directory_exists("/tmp")
        True
        >>> directory_exists("/nonexistent")
        False
    """
    return os.path.isdir(path)


def file_exists(path: Union[str, Path]) -> bool:
    """Check if a file exists.

    Args:
        path: The path to check.

    Returns:
        True if the path exists and is a file, False otherwise.

    Example:
        >>> file_exists("/etc/passwd")
        True
        >>> file_exists("/nonexistent.txt")
        False
    """
    return os.path.isfile(path)


def get_file_size(path: Union[str, Path]) -> int:
    """Get the size of a file in bytes.

    Args:
        path: The path to the file.

    Returns:
        The file size in bytes, or -1 if the file doesn't exist.

    Example:
        >>> get_file_size("/tmp/test.txt")
        1024
    """
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


def ensure_directory(path: Union[str, Path]) -> bool:
    """Ensure a directory exists, creating it if necessary.

    This is an alias for create_directory with explicit semantics
    for ensuring a path exists.

    Args:
        path: The directory path to ensure exists.

    Returns:
        True if the directory exists (created or already present),
        False if creation failed.

    Example:
        >>> ensure_directory("/tmp/cache")
        True
    """
    return create_directory(path)