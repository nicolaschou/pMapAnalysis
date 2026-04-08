from pathlib import Path

def means_csv(mean_dicts: dict, pmap_indices: list, csv_path: Path):
    """
    Write mean proportion values to a CSV file.

    Each column corresponds to a pMap, and each row corresponds to a
    distance/depth value. Entries are taken from `mean_dicts`,
    which maps pMap indices to dictionaries of
    {distance: mean_proportion}. Missing or None values are written as
    empty fields.

    Args:
        mean_dicts (dict): {pmap_index: dict} where dict is
            {distance: mean_proportion}.
        pmap_indices (list): List of pmap_index keys for mean_dicts.
        csv_path (Path): Path to export CSV to.
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="") as f:
        f.write("distance," + ",".join(pmap_indices) + "\n")

        distances = mean_dicts[pmap_indices[0]].keys()
        for d in distances:
            row = [str(d)]
            for ind in pmap_indices:
                val = mean_dicts[ind].get(d, "")
                row.append("" if val is None else str(val))

            f.write(",".join(row) + "\n")