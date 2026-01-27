"""
weights.py
Author: Svanik Tandon
Date: 2025-01-25

Calculation of weights for GramsOccupancy analysis. Computes weight factors for all particles based on integrated
flux maps, and saves to MAPS_DIR/pkl/weights.pkl.
"""
import numpy as np
from typing import Tuple, List, Dict, Optional
import os
import pickle
import argparse

from config import NSIDE, NUM_EVENTS, PARTICLE_DICT, MAPS_DIR, TPC_AVG_CROSS_SECTION

def read_integrated_flux_maps(path: str) -> Tuple[np.ndarray, List[np.ndarray], float]:
    """ 
    Read integrated flux maps from text file generated in GramsSky/MapEnergyBands.cc. Extracts sum
    of integrated flux over all pixels and energy bands.
    """
    data = np.loadtxt(path, comments="#")
    if data.ndim == 1:
        data = data[np.newaxis, :]

    pixel_idx = data[:, 0].astype(int)
    J_matrix = data[:, 1:]  # shape: (Npix, nBands)
    J_bands = [J_matrix[:, i].copy() for i in range(J_matrix.shape[1])]
    S = sum(float(np.sum(J)) for J in J_bands)

    return pixel_idx, J_bands, S

def calculate_weight_factor(S: float, nside: int, n_events: int) -> Tuple[float, float]:
    """Calculate the weight factor for converting event counts to rates."""
    omega = (4 * np.pi) / (12 * nside ** 2)  # HEALPix pixel solid angle
    T = n_events / (S * omega)  # effective time represented by simulation
    w = TPC_AVG_CROSS_SECTION / T # weighting factor to convert counts to rates (in Hz)

    return T, w

def main():
    parser = argparse.ArgumentParser(description="Calculate weights for GramsOccupancy analysis")
    parser.add_argument("--particles", type=str, nargs="+", help="Particles to calculate weights for (default: all)")
    args = parser.parse_args()

    particles_to_run = args.particles if args.particles else list(PARTICLE_DICT.keys())
    n_events = NUM_EVENTS

    weights: Dict[str, Dict[str, float]] = {}

    for particle in particles_to_run:
        if particle not in PARTICLE_DICT:
            print(f"[SKIP] Unknown particle: {particle}")
            continue

        flux_suffix = PARTICLE_DICT[particle][3] 
        integrated_flux_file = os.path.join(
            MAPS_DIR, "txt",
            f"int_flux_{flux_suffix}.txt"
        )

        if not os.path.exists(integrated_flux_file):
            print(f"[ERROR] Integrated flux file not found for {particle}: {integrated_flux_file}")
            continue

        _, _, S = read_integrated_flux_maps(integrated_flux_file)
        T, w = calculate_weight_factor(S, NSIDE, n_events)

        weights[particle] = {'S': S, 'T': T, 'w': w}

        print(f"[INFO] Particle: {particle}, S: {S:.3e} cm^-2 s^-1 sr^-1, T: {T:.3e} cm^2 s, w: {w:.3e} s^-1,")

    # save weights to pickle file
    pkl_dir = os.path.join(MAPS_DIR, "pkl")
    os.makedirs(pkl_dir, exist_ok=True)
    weights_file = os.path.join(pkl_dir, "weights.pkl")
    with open(weights_file, "wb") as f:
        pickle.dump(weights, f)

    print(f"[INFO] Weights saved to: {weights_file}")


if __name__ == "__main__":
    main()
