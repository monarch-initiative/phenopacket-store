import pytest
from ppktstore.registry import configure_phenopacket_registry


class TestPhenopacketStoreRegistry:

    @pytest.mark.skip("For now, just for manual debugging")
    def test_open_phenopacket_store(
        self,
    ):
        registry = configure_phenopacket_registry()

        with registry.open_phenopacket_store() as ps:
            pc = ps.phenopacket_count()
            print(pc)
