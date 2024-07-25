import pytest

from ppktstore.stats import generate_phenopacket_store_report


class TestReport:

    @pytest.mark.skip("Run manually on demand")
    def test_generate_report(
        self,
        fpath_nb_dir: str,
    ):
        report = generate_phenopacket_store_report(
            fpath_nb_dir, 
            notebook_dir_url='https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks',
        )
        with open("report.md", "w") as fh:
            fh.write(report)
