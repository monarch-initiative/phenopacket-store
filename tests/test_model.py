
from ppktstore.model import PhenopacketStore


class TestPhenopacketStore:

    def test_from_notebook_dir(
        self,
        fpath_nb_dir: str,
    ):
        ps = PhenopacketStore.from_notebook_dir(fpath_nb_dir)
        
        assert set(ps.cohort_names()) == {'AAGAB', 'AXIN1'}
        
        aagab_cohort = ps.cohort_for_name('AAGAB')
        assert len(aagab_cohort) == 3

        axin1_cohort = ps.cohort_for_name('AXIN1')
        assert len(axin1_cohort) == 7
