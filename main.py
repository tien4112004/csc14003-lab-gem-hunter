import os
import sys
from colorama import init

import consts
from ui.menu import (
    main_menu, generate_map_menu, map_selection_menu
)
from ui.cli import parse_args, process_args
from utils.io import clear_screen
from ui.solve import solve_map

# init colorama for cross-platform colored output
init()

def main():
    """Main function to run the Gem Hunter program."""
    print("Gem Hunter Solver started")
    
    while True:
        option = main_menu()
        
        if option == consts.MENU_OPTIONS_GENERATE_MAP:
            generate_map_menu()
        elif option == consts.MENU_OPTIONS_SOLVE_MAP:
            map_file = map_selection_menu()
            if map_file:
                clear_screen()
                print("\n" + "="*50)
                print("               SOLVE MAP")
                print("="*50)
                solve_map(map_file)
                input("\nPress Enter to continue...")        
        else:
            clear_screen()
            print("\nExiting Gem Hunter. Goodbye!")
            break

if __name__ == "__main__":
    args = parse_args()   
    if process_args(args):
        sys.exit(0)
    
    # no args -> fallback to interactive mode
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        input("Press Enter to exit...")