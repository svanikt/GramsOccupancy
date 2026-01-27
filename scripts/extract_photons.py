#!/usr/bin/env python3
"""
extract_photons.py
Author: Svanik Tandon
Date: 2025-01-26

Extract scintillation and Cherenkov photon yields from GramsG4 ROOT trees.
Saves data to {MAPS_DIR}/pkl/photon_yield.pkl

Output format:
    {particle: {'energy': [E0, ...], 'scint': [n_scint, ...], 'cer': [n_cer, ...]}} 

Usage:
    python extract_photons.py
    python extract_photons.py --particles photon proton
"""
import os
import pickle
import argparse

from config import PARTICLE_DICT, MAPS_DIR, GRAMSSIM_DICTIONARY, LOCATION


def load_root():
    """Import ROOT and load GramsSim dictionary."""
    import ROOT
    ROOT.gSystem.Load(GRAMSSIM_DICTIONARY)
    return ROOT


def extract_photon_yields(tree):
    """
    Extract photon yield data from a single particle tree.

    Returns dict with 'energy', 'scint', 'cer' lists.
    Only includes events with at least one LArHit.
    """
    energies = []
    scint_photons = []
    cer_photons = []

    for entry in tree:
        # find primary energy
        primary_E = None
        for trackID, track in tree.TrackList:
            if track.Process() == "Primary":
                traj = track.Trajectory()
                if len(traj) > 0:
                    primary_E = traj[0].momentum.E()
                break

        if primary_E is None:
            continue

        # skip events without hits
        if tree.LArHits.size() == 0:
            continue

        # sum photons from all hits
        cer_sum = 0
        scint_sum = 0
        for key, hit in tree.LArHits:
            cer_sum += hit.cerPhotons
            scint_sum += hit.numPhotons

        energies.append(primary_E)
        scint_photons.append(scint_sum)
        cer_photons.append(cer_sum)

    return {
        'energy': energies,
        'scint': scint_photons,
        'cer': cer_photons,
    }


def main():
    parser = argparse.ArgumentParser(description="Extract photon yields from ROOT trees")
    parser.add_argument("--particles", type=str, nargs="+",
                        help="Particles to process (default: all)")
    args = parser.parse_args()

    particles = args.particles if args.particles else list(PARTICLE_DICT.keys())

    ROOT = load_root()

    photon_data = {}

    for particle in particles:
        if particle not in PARTICLE_DICT:
            print(f"[SKIP] Unknown particle: {particle}")
            continue

        root_file = os.path.join(MAPS_DIR, "sim", f"{LOCATION}_{particle}_g4.root")

        if not os.path.exists(root_file):
            print(f"[SKIP] File not found: {root_file}")
            continue

        f = ROOT.TFile.Open(root_file)
        if not f or f.IsZombie():
            print(f"[ERROR] Failed to open: {root_file}")
            continue

        tree = f.Get("gramsg4")
        if not tree:
            print(f"[ERROR] Tree 'gramsg4' not found in: {root_file}")
            f.Close()
            continue

        print(f"[INFO] Extracting {particle} ({tree.GetEntries()} events)...")
        photon_data[particle] = extract_photon_yields(tree)
        n_events = len(photon_data[particle]['energy'])
        print(f"       -> {n_events} events with LArHits")

        f.Close()

    # save to pickle
    pkl_dir = os.path.join(MAPS_DIR, "pkl")
    os.makedirs(pkl_dir, exist_ok=True)
    output_file = os.path.join(pkl_dir, "photon_yield.pkl")

    with open(output_file, "wb") as f:
        pickle.dump(photon_data, f)

    print(f"[INFO] Saved to: {output_file}")


if __name__ == "__main__":
    main()
