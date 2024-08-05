# How to release

Follow this document to make new Phenopacket store release.

## Release checklist

1. Start on `main` branch
2. Ensure `main` branch is clean with no uncommitted changes
3. Update `src/ppktstore/__init__.py` to set `ppktstore.__version__` to the desired version (e.g. `0.1.16`)
4. Commit the change (e.g. with a commit message "Release 0.1.16")
5. If required, update the local installation to make sure we get the latest version
    ```shell
    python3 -m pip install -e .
    ```
6. Generate release archives with `ppktstore` CLI:
    ```shell
    python3 -m ppktstore package --notebook-dir notebooks --format zip --output all_phenopackets
    ```
  
    This will generate `all_phenopackets.zip` archive file in the current directory
7. Run the `PhenopacketStoreStats` notebook to update the stats
8. Commit the changes in the notebook
9. Push the commits to GitHub
10. Go to [Releases](https://github.com/monarch-initiative/phenopacket-store/releases) and click on *Draft a new release* button to start making a new release
11. Click on *Choose a tag* dropdown, type the release in (e.g. `0.1.16`), and click on *Create new tag on publish* (**IMPORTANT!**)
  ![Choose a tag](img/choose_a_tag.png)
12. Click on *Generate release notes* button to add what's changed into the release notes
13. Attach the release archive generated in the 6th step by dragging it into the area located below the release notes
14. Click *Publish release* to make the release
15. **IMPORTANT!** bump `ppktstore.__version__` (e.g. `0.1.17-dev0`), commit the change, and push the commit to GitHub to start the next development iteration

Done!
