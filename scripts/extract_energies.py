#!/usr/bin/env python3
"""
extract_energies.py
Author: Svanik Tandon
Date: 2025-01-26

Extract primary particle energies from GramsG4 ROOT trees.
Saves data to {MAPS_DIR}/pkl/primary_energies.pkl

Output format:
    {particle: {'all': [E0, ...], 'with_hits': [E0, ...]}}

'all' contains energies for all events.
'with_hits' contains energies only for events with at least one LArHit.

Usage:
    python extract_energies.py
    python extract_energies.py --particles photon proton
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


def extract_primary_energies(tree):
    """
    Extract primary energies from a single particle tree.

    Returns dict with:
        'all': energies for all events
        'with_hits': energies for events with LArHits
    """
    all_energies = []
    energies_with_hits = []

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

        all_energies.append(primary_E)

        # check if event has hits
        if tree.LArHits.size() > 0:
            energies_with_hits.append(primary_E)

    return {
        'all': all_energies,
        'with_hits': energies_with_hits,
    }


def main():
    parser = argparse.ArgumentParser(description="Extract primary energies from ROOT trees")
    parser.add_argument("--particles", type=str, nargs="+",
                        help="Particles to process (default: all)")
    args = parser.parse_args()

    particles = args.particles if args.particles else list(PARTICLE_DICT.keys())

    ROOT = load_root()

    energy_data = {}

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
        energy_data[particle] = extract_primary_energies(tree)
        n_all = len(energy_data[particle]['all'])
        n_hits = len(energy_data[particle]['with_hits'])
        print(f"       -> {n_all} total, {n_hits} with hits")

        f.Close()

    # save to pickle
    pkl_dir = os.path.join(MAPS_DIR, "pkl")
    os.makedirs(pkl_dir, exist_ok=True)
    output_file = os.path.join(pkl_dir, "primary_energies.pkl")

    with open(output_file, "wb") as f:
        pickle.dump(energy_data, f)

    print(f"[INFO] Saved to: {output_file}")


if __name__ == "__main__":
    main()
