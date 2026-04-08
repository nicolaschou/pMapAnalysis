from pathlib import Path
import multiprocessing as mp
import time

from export import means_csv
from format_pmaps import apply_crop, get_grayscale
from parse_pmaps import dist_csv, mean_proportions, parse_pmap

# ----------------------------------------------------------------------
# EDIT EXPERIMENT INFO
#
# "experiment_name": ((y1, x1), (y2, x2))
#
# (y1, x1) = top-left corner
# (y2, x2) = bottom-right corner
# ----------------------------------------------------------------------
experiments = {

}
# ----------------------------------------------------------------------


def get_pix_data(
        exp_name: str,
        crop: tuple | None = None,
        export_raw_proportions: bool = True,
        export_mean_proportions: bool = True
    ):
    # ------------------------------------------------------------------
    # EDIT PATHS / FILE PATTERNS
    #
    # Default file structure:
    # <data_root>/
    #   <exp_name>/
    #       <mask_path>     # mask image
    #       <pmap_path>     # pMap images (indexed)
    #       <raw_path>      # raw (depth, proportion) data
    #   <means_path>        # output data
    # ------------------------------------------------------------------
    data_root = Path("data")
    exp_dir = data_root / exp_name

    mask_path = exp_dir / f"{exp_name}_mask.tif"
    pmap_path_tmp = exp_dir / f"{exp_name}_pMap_{{idx}}.tif"
    raw_path_tmp = exp_dir / f"{exp_name}_{{idx}}.csv"
    means_path = data_root / f"{exp_name}.csv"
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # EDIT ANALYSIS CONSTANTS
    #
    # pmap_indices      : list of pMap indices to consider
    # orig_pix_width    : uncropped image width in pixels
    # fov               : uncropped image field of view in micron
    # depth             : analysis depth in micron
    # ------------------------------------------------------------------
    pmap_indices = ["0", "1", "2", "3", "5"]
    orig_pix_width = 1030
    fov = 45
    depth = 4
    # ------------------------------------------------------------------


    mask = apply_crop(get_grayscale(mask_path), crop)
    mean_dicts = {}

    for pmap_ind in pmap_indices:
        pmap_path = Path(str(pmap_path_tmp).format(idx=pmap_ind))
        pmap = apply_crop(get_grayscale(pmap_path), crop)

        distance_dict = parse_pmap(
            pmap,
            mask,
            orig_pix_width=orig_pix_width,
            fov=fov,
            depth=depth,
        )  

        if export_raw_proportions:
            raw_path = Path(str(raw_path_tmp).format(idx=pmap_ind))
            dist_csv(distance_dict, raw_path)

        mean_dicts[pmap_ind] = mean_proportions(distance_dict)
    
    if export_mean_proportions:
        means_csv(mean_dicts, pmap_indices, means_path)
        
    return mean_dicts


def run_one(item):
    key, coords = item
    return get_pix_data(key, coords)


if __name__ == "__main__":
    print("Running pMap analysis...")
    start = time.time()

    with mp.Pool(processes=8) as pool:
        results = pool.map(run_one, experiments.items())

    end = time.time()
    print("Runtime:", end - start, "seconds")