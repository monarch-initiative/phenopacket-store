import os
import typing

from mdutils import MdUtils

from ppktstore.model import PhenopacketStore, CohortInfo


def generate_phenopacket_store_report(
    notebook_dir: str,
    notebook_dir_url: str,
) -> str:
    """
    Generate report in Markdown format.

    :returns: a `str` with Markdown text.
    """
    store = PhenopacketStore.from_notebook_dir(notebook_dir)

    md_file = MdUtils(
        file_name="whatever.md"
    )  # whatever because we do not write into the file, we just get the `str` at the end.
    md_file.new_header(level=1, title="Collections")
    md_file.new_paragraph(
        'Phenopacket store is a repository of [GA4GH phenopackets](https://pubmed.ncbi.nlm.nih.gov/35705716){:target="_blank"}. '
        'that were mainly created using the Python library [pyphetools](https://github.com/monarch-initiative/pyphetools/){:target="_blank"}. '
        "All of the phenopackets were derived from publised case or cohort reports. We have created one page for each of the collections of "
        "phenopackets offered by this repository."
    )

    table_data = ["Cohort", "Comments"]
    row_count = 1  # due to header

    cohort_names = sorted(store.cohort_names())
    for cohort_name in cohort_names:
        cohort = store.cohort_for_name(cohort_name)
        dx_data = _summarize_cohort_diseases(cohort)
        if len(dx_data) == 0:
            continue

        cohort_count = len(cohort.phenopackets)

        notebook_link = _prepare_cohort_link(notebook_dir_url, notebook_dir, cohort.name)
        cohort_text = "[" + cohort.name + "](" + notebook_link + '){:target="_blank"}'
        table_data.append(cohort_text)
        
        
        # Show details on diseases in a cohort except for very large cohorts (up to 20 distinct diseases)
        comments_text = "1 Phenopacket;" if cohort_count == 1 else f"{cohort_count} Phenopackets;"
        if len(dx_data) < 21:
            for dx_id, dx_label in dx_data.items():
                dx_link = _prepare_dx_link(dx_id)
                comments_text += "[" + dx_label + "](" + dx_link + '){:target="_blank"}'
        table_data.append(comments_text)

        row_count += 1

    md_file.new_line()
    md_file.new_table(columns=2, rows=row_count, text=table_data, text_align="left")

    return md_file.get_md_text()


def _summarize_cohort_diseases(
    cohort: CohortInfo,
) -> typing.Mapping[str, str]:
    dxs = {}
    for pp_info in cohort.phenopackets:
        pp = pp_info.phenopacket
        if not pp.interpretations:
            continue

        for interpretation in pp.interpretations:
            if not interpretation.diagnosis:
                continue
            dx = interpretation.diagnosis
            dxs[dx.disease.id] = dx.disease.label

    return dxs


def _prepare_dx_link(
    dx_id: str,
) -> str:
    parts = dx_id.split(":")
    if len(parts) != 2:
        return ""
    prefix, identifier = parts
    if prefix.lower() == "omim":
        return "https://omim.org/entry/" + identifier
    else:
        return "http://purl.obolibrary.org/obo/" + dx_id.replace(":", "_")


def _prepare_cohort_link(
    notebook_dir_url: str, 
    notebook_dir: str,
    cohort_name: str,
) -> str:
    cohort_dir = os.path.join(notebook_dir, cohort_name)
    cohort_url = os.path.join(notebook_dir_url, cohort_name)
    notebook_links = [
        os.path.join(cohort_url, fname)
        for fname in os.listdir(cohort_dir)
        if fname.endswith(".ipynb")
    ]

    if len(notebook_dir) == 0:
        return cohort_url
    if len(notebook_links) == 1:
        # just take the notebook
        return notebook_links[0]
    else:
        # try to find the summary notebook
        for nb_link in notebook_links:
            if "summary" in nb_link.lower():
                return nb_link
        # or use link to the folder itself in the absence of the summary notebook
        return cohort_url
