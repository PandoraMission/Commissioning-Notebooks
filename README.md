# Commissioning-Notebooks
Jupyter notebooks for simulating instrument commissioning tasks. To run each notebook, you will need to (1) clone this repository, and (2) install pandorasim.

# Folders are labeled by commissioning task number: 
- 3.10 VIS Focal Plane mapping
- 3.12/3.17 Update VIS Pointing Loop
- 3.15 VIS PSF Mapping
- 3.175 VIS PSF Full Frame Images
- ...etc...

# Within each folder:
- [].ipynp -- Jupyter Notebook for simulating the commissioning task. The task overview is documented at the top. 
- []_SOC.xml -- File with saved observation parameters for the Science Operations Center. This file is generated at the end of each Notebook. 
- []_ResultsSummary.md -- File where commissioning results for that task will eventually be documented.
- [].fits -- Simulated output file from PandoraSim. This file IS NOT saved on GitHub. They are too large. Instead, find them on Box: https://nasa-ext.box.com/s/xwmk1sjr0mrah45fxi301nz0vj61p4ea 
