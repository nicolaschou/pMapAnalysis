from pathlib import Path
import numpy as np

def parse_pmap(
        pmap: np.ndarray,
        mask: np.ndarray,
        orig_pix_width: int,
        fov: float,
        depth: float,
    ):
    """
    Compute (normalized) pMap intensities at fixed pixel depths from the
    edge.

    For each edge pixel, the function propagates along four directions
    (up, down, left, right) until a fixed depth. Each pixel is assigned
    to the first edge that reaches it (its nearest edge in the
    four-directional sense). If the pixel lies within the mask and has
    not been visited by an edge yet, its normalized pmap value is
    recorded at the corresponding distance.

    Args:
        pmap (np.ndarray): Integer-valued pMap. Normalization assumes
            the values are scaled to the integer type's maximum.
        mask (np.ndarray): Binary (grayscale) mask defining the region
            of interest. Zero-valued pixels are considered to be masked
            and positive-valued pixels are considered to be unmasked.
        orig_pix_width (int):
            Pixel width of the original (uncropped) image.
        fov (float):
            Field of view of the original image in microns.
        depth (float):
            Sampling depth from the edge in microns.

    Returns:
        dict[float, list[float]]: Mapping from distance (microns) to
            lists of normalized pMap values.
    """
    H, W = pmap.shape

    bool_edge, bool_mask = parse_mask(mask)
    edge_list = np.argwhere(bool_edge)

    # normalize pmap to [0, 1]
    dtype = pmap.dtype
    pmap_f = pmap.astype(np.float32)
    if np.issubdtype(dtype, np.integer):
        pmap_norm = pmap_f / np.iinfo(dtype).max
    else:
        raise ValueError("pMap has non-integer values")

    # convert depth from micron to pixels
    pix_depth = int(np.ceil(depth * orig_pix_width / fov))
    distance_dict = {d: [] for d in range(1, pix_depth+1)}

    visited = np.zeros_like(pmap, dtype=bool)

    for d in range(1, pix_depth + 1):
        for e in edge_list:
            er, ec = e
            for r, c in [
                (er - d, ec),  # up
                (er + d, ec),  # down
                (er, ec - d),  # left
                (er, ec + d),  # right
            ]:
                if (
                    0 <= r < H and 0 <= c < W
                    and bool_mask[r, c]
                    and not visited[r, c]
                ):
                    distance_dict[d].append(pmap_norm[r, c])
                    visited[r, c] = True
    
    # convert back to micron
    pix_to_micron = fov / orig_pix_width
    distance_dict_micron = {
        d * pix_to_micron: values for d, values in distance_dict.items()
    }
    
    return distance_dict_micron


def parse_mask(mask: np.ndarray):
    """Return boolean masks for edge pixels and unmasked pixels."""
    bool_mask = mask > 0 # True where value is unmasked

    # adjacency boolean mask: True where at least one of the 4-adjacent
    # neighbors is unmasked
    bool_adj = np.zeros_like(bool_mask, dtype=bool)
    bool_adj[1:, :] |= bool_mask[:-1, :]    # up neighbor
    bool_adj[:-1, :] |= bool_mask[1:, :]    # down neighbor
    bool_adj[:, 1:] |= bool_mask[:, :-1]    # left neighbor
    bool_adj[:, :-1] |= bool_mask[:, 1:]    # right neighbor

    # edge boolean mask: True where masked and at least one of the
    # 4-adjacent neighbors is unmasked
    bool_edge = ~bool_mask & bool_adj
    
    return bool_edge, bool_mask


def mean_intensities(distance_dict: dict):
    """Compute the mean intensity for each distance key."""
    means = {}  

    for distance, values in distance_dict.items():
        if len(values) == 0:
            means[distance] = None
            continue

        mean_value = np.mean(values)
        means[distance] = mean_value       

    return means


def dist_csv(distance_dict: dict, csv_path: Path):
    """Write distance–intensity pairs to a CSV file."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="") as csvfile:
        csvfile.write("distance_micron,intensity\n")

        for d, values in distance_dict.items():
            for v in values:
                csvfile.write(f"{d},{v}\n")