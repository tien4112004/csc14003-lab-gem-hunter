import os
import sys
from colorama import Fore, Style

from utils.io import clear_screen, get_map_files, load_map, save_solution
import map_generator
from solvers.sat_solver import SATSolver

def main_menu():
    """Display the main menu and return the selected option."""
    clear_screen()
    options = [
        "Generate New Map",
        "Select Map to Solve",
        "Exit"
    ]
    
    print("\n" + "="*50)
    print("               GEM HUNTER")
    print("="*50)
    print("Phan Thanh Tien - 22120368")
    print("\nSelect an option:")
    
    for i, option in enumerate(options):
        print(f"  {i+1}. {option}")
    
    print("\nEnter your choice (1-5):")
    
    while True:
        try:
            choice = input("> ")
            if choice.lower() in ('q', 'quit', 'exit'):
                return len(options) - 1 # Exit option
            
            choice = int(choice) - 1
            if 0 <= choice < len(options):
                return choice
            else:
                print(f"Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Please enter a valid number.")

def map_selection_menu():
    """Display a menu to select a map and return the selected map file."""
    map_files = get_map_files()
    if not map_files:
        print("No maps found in the maps/ directory!")
        input("Press Enter to continue...")
        return None
    
    clear_screen()
    print("\n" + "="*50)
    print("               MAP SELECTION")
    print("="*50)
    print("\nSelect a map:")
    
    for i, map_file in enumerate(map_files):
        print(f"  {i+1}. {map_file}")
    
    print("\n  0. Return to main menu")
    print("\nEnter your choice:")
    
    while True:
        try:
            choice = input("> ")
            if choice.lower() in ('q', 'quit', 'exit', '0'):
                return None
            
            choice = int(choice) - 1
            if 0 <= choice < len(map_files):
                return os.path.join("maps", map_files[choice])
            else:
                print(f"Please enter a number between 0 and {len(map_files)}.")
        except ValueError:
            print("Please enter a valid number.")

def generate_map_menu():
    """Display the map generation menu and handle the generation process."""
    clear_screen()
    print("\n" + "="*50)
    print("               GENERATE NEW MAP")
    print("="*50)
    
    try:
        map_generator.main()
    except Exception as e:
        print(f"\nError during map generation: {e}")
    finally:
        print("\nReturning to main menu...")
        input("Press Enter to continue...")