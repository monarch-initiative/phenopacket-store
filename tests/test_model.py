import zipfile

from ppktstore.model import PhenopacketStore, CohortInfo


class TestPhenopacketStore:

    def test_from_notebook_dir(
        self,
        fpath_nb_dir: str,
    ):
        ps = PhenopacketStore.from_notebook_dir(fpath_nb_dir)
        assert ps.name == "notebooks"

        check_ps_specs(ps)

    def test_from_release_zip(
        self,
        fpath_ps_release_zip: str,
    ):
        with zipfile.ZipFile(fpath_ps_release_zip) as zf:
            ps = PhenopacketStore.from_release_zip(zf)
            assert ps.name == "test_get_store_zip0"

            check_ps_specs(ps)


def check_ps_specs(
    ps: PhenopacketStore,
):
    assert isinstance(ps, PhenopacketStore)

    assert set(ps.cohort_names()) == {"AAGAB", "AXIN1"}

    aagab_cohort = ps.cohort_for_name("AAGAB")
    check_aagab_cohort_specs(aagab_cohort)

    axin1_cohort = ps.cohort_for_name("AXIN1")
    check_axin1_cohort_specs(axin1_cohort)


def check_aagab_cohort_specs(
    cohort: CohortInfo,
):
    assert cohort.name == "AAGAB"
    # assert cohort.path == ?  # Not checking cohort path because it is different depending
    # on whether Phenopacket store is loaded from a notebook folder or from a release ZIP.
    assert len(cohort) == 3

    pp_ids = set(pp_info.phenopacket.id for pp_info in cohort.phenopackets)
    assert pp_ids == {
        "PMID_28239884_Family_1_proband",
        "PMID_28239884_Family_2_proband",
        "PMID_28239884_Family_3_proband",
    }


def check_axin1_cohort_specs(
    cohort: CohortInfo,
):
    assert cohort.name == "AXIN1"
    # Not checking cohort and phenopacket paths because they are different depending
    # on whether Phenopacket store is loaded from a notebook folder or from a release ZIP.
    assert len(cohort) == 7

    pp_ids = set(pp_info.phenopacket.id for pp_info in cohort.phenopackets)
    assert pp_ids == {
        "PMID_37582359_F1-II-4",
        "PMID_37582359_F2-III-2",
        "PMID_37582359_F4-III-3",
        "PMID_37582359_F4-III-4",
        "PMID_37582359_F1-II-1",
        "PMID_37582359_F3-III-1",
        "PMID_37582359_F4-III-1",
    }
