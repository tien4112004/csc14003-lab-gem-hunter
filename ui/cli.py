import os
import sys
import argparse
import map_generator
from utils.io import load_map
from ui.solve import solve_map

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Gem Hunter Solver')
    parser.add_argument('--map', help='Path to map file to solve')
    parser.add_argument('--solver', choices=['sat', 'bf', 'bt'], default='sat',
                      help='Solver to use (sat=SAT, bf=Brute Force, bt=Backtracking)')
    parser.add_argument('--generate', action='store_true', help='Generate a new map')
    parser.add_argument('--size', type=int, default=8, help='Size of generated map')
    parser.add_argument('--probability', type=float, default=0.25, help='Trap probability for generated map')
    parser.add_argument('--output-dir', default='testcase', help='Output directory for generated maps')
    
    return parser.parse_args()

def process_args(args):
    """Process command line arguments."""
    if args.generate:
        result = map_generator.generate_and_save_map(
            args.size, args.size, 
            trap_probability=args.probability,
            map_dir=args.output_dir,
            name_suffix=""
        )
        return True
    
    if args.map:
        if not os.path.exists(args.map):
            print(f"Map file '{args.map}' does not exist!")
            return True
        
        # if args.benchmark:
        #     run_benchmark(args.map, verbose=True)
        # else:
        solve_map(args.map, args.solver)
        return True
    
    return False