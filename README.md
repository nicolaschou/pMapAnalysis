# pMap Analysis

Code for analyzing pMap images by computing precursor proportion as a function of distance from mask-defined edges.

## Overview

For each experiment, the pipeline:
- Loads mask and pMap images
- Optionally restricts analysis to a cropped region of interest
- Detects mask edges
- Groups proportion values by four-directional depth from the edge
- Averages the proportions at each depth
- Exports CSVs containing the (distance, proportion) pairs for every pixel
- Exports a CSV containing the mean proportion per distance across all pMaps

## Usage

To take advantage of multiprocessing, use `pmap_analysis.py`. If a Jupyter notebook is preferred, use `pmap_analysis.ipynb`.
1. Update the `experiments` dictionary to include experiment names and crop coordinates, if applicable
2. Add necessary files to the working directory, following the commented structure
3. Update the file paths and constants in the `get_pix_data` function as necessary
4. Run the program (if using `pmap_analysis.ipynb`, run the second cell)

## Key Notes

- pMaps must be integer-valued and normalized by the dtype maximum
  - E.g `int32` values are mapped to proportions via $\textbf{value} / 2^{32}-1$
- For masks, values are interpreted as follows: **>0 → unmasked, =0 → masked**
