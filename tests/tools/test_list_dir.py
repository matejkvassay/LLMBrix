import os
import tempfile

import pytest

from llmbrix.tools import ListDir


def test_list_dir_with_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        filenames = ["file1.txt", "file2.txt"]
        for name in filenames:
            open(os.path.join(tmpdir, name), "w").close()
        tool = ListDir()
        result = tool.exec(tmpdir).content
        assert result == str(sorted(filenames))


def test_list_dir_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = ListDir()
        result = tool.exec(tmpdir).content
        assert result == str([])


def test_list_dir_nonexistent_directory():
    tool = ListDir()
    with pytest.raises(FileNotFoundError):
        tool.exec("/path/that/does/not/exist")
