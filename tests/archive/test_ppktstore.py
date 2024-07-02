import os
import tarfile
import typing
import zipfile
from pathlib import Path

import pytest

from ppktstore.archive import PPKtStore


class TestPPKtStore:

    @pytest.fixture
    def fpath_notebook_dir(
            self,
            fpath_test_data: str,
    ) -> str:
        return os.path.join(fpath_test_data, 'notebooks')

    @pytest.fixture
    def ppkt_store(
            self,
            fpath_notebook_dir: str,
    ) -> PPKtStore:
        return PPKtStore(fpath_notebook_dir)

    def test_get_store_zip(
            self,
            ppkt_store: PPKtStore,
            tmp_path: Path,
    ):
        outfilename = str(tmp_path)

        ppkt_store.get_store_zip(outfilename=outfilename)

        expected_archive_filename = f'{outfilename}.zip'
        assert os.path.isfile(expected_archive_filename)

        basename = os.path.basename(tmp_path)

        with zipfile.ZipFile(expected_archive_filename) as zf:
            filenames = tuple(file.filename for file in zf.filelist)

        TestPPKtStore.check_archive_spec(basename, filenames)

    def test_get_store_gzip(
            self,
            ppkt_store: PPKtStore,
            tmp_path: Path,
    ):
        outfilename = str(tmp_path)

        ppkt_store.get_store_gzip(outfilename)

        expected_archive_filename = f'{outfilename}.tgz'
        assert os.path.isfile(expected_archive_filename)

        basename = os.path.basename(tmp_path)
        with tarfile.open(expected_archive_filename) as fh:
            names = fh.getnames()
            filenames = tuple(name for name in names if name != '')

        TestPPKtStore.check_archive_spec(basename, filenames)

    @pytest.mark.parametrize(
        'suffix',
        [
            '.gz',
            '.tgz',
            '.tar.gz',
            '.zip',
            '.jar',
        ]
    )
    def test_suffix_in_outfilename_explodes(
            self,
            ppkt_store: PPKtStore,
            suffix: str,
    ):
        outname = f'whatever{suffix}'
        with pytest.raises(ValueError) as ctx:
            ppkt_store.get_store_gzip(outname)

        assert ctx.value.args[0] == f'The path must not include suffix but found {suffix} in {outname}'

    @staticmethod
    def check_archive_spec(
            basename: str,
            filenames: typing.Iterable[str],
    ):
        assert any(
            file == f'{basename}/{basename}.tsv' for file in filenames
        ), 'The archive should include the summary TSV file'

        json_files = tuple(file for file in filenames if file.endswith('.json'))
        assert len(json_files) == 10, 'The archive should include 10 JSON phenopackets'

        n_top_level = 0
        for file_name in filenames:
            n_seps = sum(1 for char in file_name if char == os.sep)
            if n_seps == 0 or (n_seps == 1 and file_name.endswith(os.sep)):
                n_top_level += 1
        assert n_top_level == 1, 'The archive should include only one top-level element'

        assert all(
            file.startswith(basename) for file in filenames
        ), 'All files should be located in the top-level directory'
