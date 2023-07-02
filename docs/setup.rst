.. _setup:

=====
Setup
=====

Users interested in the phenopackets do not need to install or setyup anything and can just download the phenopackets.


Users interested in contributing the Phenopacket Store should follow these instructions to set up the envuironment for 
running existing notebooks locally and for creating new notebooks (we welcome Pull Requests with new genes or new data for existing genes).


Python environment
^^^^^^^^^^^^^^^^^^

The following is one of several methods to setup the notebook environment.

.. code-block:: bash
   :caption: setup

       python3 -m venv psvenv
       source psvenv/bin/activate
       pip3 install pyphetools 
       # needed to create read-the-docs locally
       pip3 install sphinx sphinx-rtd-theme 
       # helpful to run the notebooks
       pip3 install jupyter
       pip3 install ipykernel
       python -m ipykernel install --name "psvenv" --user
       jupyter-notebook  # choose the "psvenv" kernel in the notebook


Using pyphetools
^^^^^^^^^^^^^^^^

Most of the phenopackets in this repository were created with the 
`pyphetools <https://github.com/monarch-initiative/pyphetools>`_ library.
Consult the pyphetools documentation and read through the notebooks in this 
repository to get a feeling for how to use pyphetools to create new phenopackets.


Creating read-the-docs documentation locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The documentation is available online. To test new documentation locally, run sphinx as follows

.. code-block:: bash
   :caption: creating documentation

       cd docs
       # if not done in the previous step
       pip3 install sphinx sphinx-rtd-theme 
       # helpful to run the notebooks
       make html

The documentation will be created in the build/html subfolder.
