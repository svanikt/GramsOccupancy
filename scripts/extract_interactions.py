#!/usr/bin/env python3
"""
extract_interactions.py
Author: Svanik Tandon
Date: 2025-01-26

Extract daughter interaction processes by primary energy from GramsG4 ROOT trees.
Saves data to {MAPS_DIR}/pkl/processbyenergy.pkl

Output format:
    {particle: {process_label: [E0, E0, ...], ...}}

For each event, records the primary energy under each distinct daughter process
that produced at least one LArHit (direct daughters of primary only).

Usage:
    python extract_interactions.py
    python extract_interactions.py --particles photon proton
"""
import os
import pickle
import argparse
from collections import defaultdict

from config import PARTICLE_DICT, MAPS_DIR, GRAMSSIM_DICTIONARY, LOCATION


def load_root():
    """Import ROOT and load GramsSim dictionary."""
    import ROOT
    ROOT.gSystem.Load(GRAMSSIM_DICTIONARY)
    return ROOT


def extract_daughter_processes(tree, ROOT):
    """
    Extract direct daughter processes for events with LArHits.

    Returns dict: {process_label: [primary_energies]}

    For each event, only counts unique processes (one entry per process per event).
    """
    energies_by_process = defaultdict(list)

    for entry in tree:
        # find primary
        primary_id = None
        primary_E0 = None

        for trackID, track in tree.TrackList:
            if track.Process() == "Primary":
                primary_id = trackID
                traj = track.Trajectory()
                if len(traj) > 0:
                    primary_E0 = traj[0].momentum.E()
                break

        if primary_id is None or primary_E0 is None:
            continue

        # collect track IDs that produced hits
        hit_trackIDs = set()
        for key, _ in tree.LArHits:
            try:
                tid = ROOT.std.get[0](key)
            except TypeError:
                tid = ROOT.std.get(key, 0)
            hit_trackIDs.add(tid)

        # find direct daughters that produced hits
        counted_processes = set()

        for trackID, track in tree.TrackList:
            if trackID == primary_id:
                continue

            # check if direct daughter of primary
            try:
                parent_id = track.ParentID()
            except:
                parent_id = None

            if parent_id != primary_id:
                continue

            # check if this track produced a hit
            if trackID not in hit_trackIDs:
                continue

            # store process (only once per process per event)
            label = track.Process() or "UnknownCreation"
            if label not in counted_processes:
                energies_by_process[label].append(primary_E0)
                counted_processes.add(label)

    return dict(energies_by_process)


def main():
    parser = argparse.ArgumentParser(description="Extract interaction processes from ROOT trees")
    parser.add_argument("--particles", type=str, nargs="+",
                        help="Particles to process (default: all)")
    args = parser.parse_args()

    particles = args.particles if args.particles else list(PARTICLE_DICT.keys())

    ROOT = load_root()

    processed_data = {}

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
        processed_data[particle] = extract_daughter_processes(tree, ROOT)
        n_processes = len(processed_data[particle])
        total_entries = sum(len(v) for v in processed_data[particle].values())
        print(f"       -> {n_processes} processes, {total_entries} total entries")

        f.Close()

    # save to pickle
    pkl_dir = os.path.join(MAPS_DIR, "pkl")
    os.makedirs(pkl_dir, exist_ok=True)
    output_file = os.path.join(pkl_dir, "processbyenergy.pkl")

    with open(output_file, "wb") as f:
        pickle.dump(processed_data, f)

    print(f"[INFO] Saved to: {output_file}")


if __name__ == "__main__":
    main()
