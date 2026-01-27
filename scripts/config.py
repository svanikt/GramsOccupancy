"""
config.py
Author: Svanik Tandon
Date: 2025-01-22

Config for GramsOccupancy sim and analysis scripts.
"""

import os

# =============================================================================
# Directory and File Paths
# =============================================================================
BASE_DIR = "/nevis/tehanu/data/st3624/software/GRAMS/GramsOccupancy"
GS_DIR = "/nevis/tehanu/data/st3624/software/GRAMS/GramsSim-work"
PARMA_DIR = "/nevis/tehanu/data/st3624/software/GRAMS/parma/parma_cpp"
EXPACS_DIR = "/nevis/tehanu/data/st3624/software/GRAMS/parma/expacs_share"

# options file for GramsSim
OPTIONS_FILE = os.path.join(BASE_DIR, "occupancy_grams.xml")

# GramsSim data structures ROOT dictionary 
GRAMSSIM_DICTIONARY = os.path.join(GS_DIR, "libDictionary.so")

# =============================================================================
# Particle Dictionary
# =============================================================================
# Format: 'parma_name': [display name for plots, PDG code, mass in MeV, 
#                       name of particle in integrated flux files (generated in GramsSky/src/MapEnergyBands.cc)]
PARTICLE_DICT = {
    'neutro': ['Neutron', '2112', 939.565, 'neutron'],
    'proton': ['Proton', '2212', 938.272, 'proton'],
    'he---4': ['Helium-4', '1000020040', 3727.38, 'unknown'],  # helium uses 'unknown' bc PDG code not recognized in GramsSky
    'muplus': [r'$\mu^+$', '-13', 105.66, 'mu+'],
    'mumins': [r'$\mu^-$', '13', 105.66, 'mu-'],
    'electr': ['Electron', '11', 0.511, 'e-'],
    'positr': ['Positron', '-11', 0.511, 'e+'],
    'photon': ['Photon', '22', 0.0, 'gamma'],
}

# =============================================================================
# HEALPix Configuration
# =============================================================================
NSIDE = 32  # HEALPix resolution. NSIDE=32 corresponds to 2^32 = 12288 pixels

# =============================================================================
# TPC Geometry
# =============================================================================
# pGRAMS TPC dimensions
TPC_DIMENSIONS = {
    'x': 30,  # cm
    'y': 30,  # cm
    'z': 20,  # cm (drift direction)
}

# average cross-sectional area of TPC
TPC_SURFACE_AREA = 2 * (TPC_DIMENSIONS['x'] * TPC_DIMENSIONS['y']) + 4 * (TPC_DIMENSIONS['x'] * TPC_DIMENSIONS['z'])  # cm^2
TPC_AVG_CROSS_SECTION = TPC_SURFACE_AREA / 6  # cm^2

# =============================================================================
# Simulation Parameters
# =============================================================================
NUM_EVENTS = 10000

# =============================================================================
# Location Configuration
# =============================================================================
# pGRAMS flight location, date, and altitude
LOCATION = "tucson"
DATE = "2025_8_31"
ALTITUDE_M = 30000

# location name mappings for CSV filenames
LOCATION_NAMES = {
    'tucson': 'SpaceportTucson_Arizona',
    'esrange': 'Esrange_Sweden',
}

# path for flux CSV file
loc_name = LOCATION_NAMES.get(LOCATION, LOCATION)
FLUX_CSV = os.path.join(EXPACS_DIR, "parma_cpp_edit", "AngOutCsv", f"{loc_name}_{DATE}_alt{ALTITUDE_M}m.csv")

# output directory for maps and simulation data
MAPS_DIR = os.path.join(BASE_DIR, f"data/{LOCATION}_{DATE}_maps")

# =============================================================================
# Helper Functions
# =============================================================================
def ensure_dirs(maps_dir: str) -> None:
    """Create subdirectories for output."""
    subdirs = ['fits', 'sim', 'txt', 'gifs']
    for subdir in subdirs:
        os.makedirs(os.path.join(maps_dir, subdir), exist_ok=True)
