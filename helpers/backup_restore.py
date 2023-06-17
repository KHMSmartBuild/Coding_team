# backup_restore.py - Backup and Restore
# A script that creates backups of important files or directories, compresses them,
# and allows restoring them when needed.
# Typical uses include backing up project files, configuration files, or other critical data.
# Save this script in the project's "utilities" or "helpers" folder.

import os
import zipfile
import shutil
from datetime import datetime

def create_backup(src: str, dest: str, compress: bool = True) -> str:
    """
    Create a backup of the specified source directory or file.

    :param src: The path to the source directory or file to back up.
    :param dest: The destination directory where the backup should be saved.
    :param compress: Whether to compress the backup as a zip file.
    :return: The path of the created backup.
    """
    backup_name = os.path.basename(src) + '_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(dest, backup_name)

    if compress:
        backup_path += '.zip'
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isdir(src):
                for root, _, files in os.walk(src):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, src))
            else:
                zipf.write(src, os.path.basename(src))
    else:
        if os.path.isdir(src):
            shutil.copytree(src, backup_path)
        else:
            shutil.copy2(src, backup_path)

    return backup_path

def restore_backup(src: str, dest: str) -> None:
    """
    Restore a backup from the specified source file or directory.

    :param src: The path to the backup file or directory to restore.
    :param dest: The destination directory where the backup should be restored.
    """
    if src.endswith('.zip'):
        with zipfile.ZipFile(src, 'r') as zipf:
            zipf.extractall(dest)
    else:
        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)

# TODO: Add more backup and restore options, such as incremental backups or encryption.

"""

Script name: Backup and Restore
Filename: backup_restore.py
Description: A script that creates backups of important files or directories, 
compresses them, and allows restoring them when needed.

Typical uses: This script can be used for tasks such as backing up project files, 
configuration files, or other critical data.

Typical locations: This script can be saved in the project's "utilities" or "helpers" folder.
Purpose and functions: The purpose of this script is to provide an easy way 
to create and restore backups of important files or directories.


"""