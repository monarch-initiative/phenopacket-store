# How to release

Follow this document to make new Phenopacket store release.

## Release checklist

1. Start on `main` branch
2. Ensure `main` branch is clean with no uncommitted changes
3. Update `src/ppktstore/__init__.py` to set `ppktstore.__version__` to the desired version (e.g. `0.1.16`)
4. Commit the change (e.g. with a commit message "Release 0.1.16")
5. Push the commit to GitHub
6. Generate release archives with `ppktstore` CLI:
    ```shell
    python3 -m ppktstore package --notebook-dir notebooks --format zip tgz --output all_phenopackets
    ```
  
    This will generate archives `all_phenopackets.zip` and `all_phenopackets.tgz` in the current directory

7. Go to [Releases](https://github.com/monarch-initiative/phenopacket-store/releases) and click on *Draft a new release* button to start making a new release
8. Click on *Choose a tag* dropdown, type the release in (e.g. `0.1.16`), and click on *Create new tag on publish* (**IMPORTANT!**)
  ![Choose a tag](img/choose_a_tag.png)
9. Click on *Generate release notes* button to add what's changed into the release notes
10. Attach the release archives generated in the 6th step by dragging them into area located below the release notes
11. Click *Publish release* to make the release
12. **IMPORTANT** update `src/ppktstore/__init__.py` to bump the release to the next development version (e.g. `0.1.17-dev0`), commit the change and push the commit to GitHub

Done!
