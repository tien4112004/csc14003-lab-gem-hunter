import os
import curses
from curses import wrapper

def get_map_files():
    map_dir = "maps"
    if not os.path.exists(map_dir):
        return []
    
    map_files = [f for f in os.listdir(map_dir) if os.path.isfile(os.path.join(map_dir, f))]
    return map_files

def display_menu(stdscr, map_files, selected_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    title = "GEM HUNTER - MAP SELECTION"
    x = w//2 - len(title)//2
    stdscr.addstr(2, x, title, curses.A_BOLD)
    
    instructions = "Use [UP/DOWN] arrows to navigate, [ENTER] to select, [Q] to quit"
    x = w//2 - len(instructions)//2
    stdscr.addstr(4, x, instructions)
    
    start_y = 6
    if map_files:
        for i, map_file in enumerate(map_files):
            x = w//2 - len(map_file)//2
            if i == selected_idx:
                stdscr.addstr(start_y + i, x, map_file, curses.A_REVERSE)
            else:
                stdscr.addstr(start_y + i, x, map_file)
    else:
        no_maps = "No maps found in the maps/ directory!"
        x = w//2 - len(no_maps)//2
        stdscr.addstr(start_y, x, no_maps)
    
    stdscr.refresh()

def map_selection_menu():
    map_files = get_map_files()
    if not map_files:
        print("No maps found in the maps/ directory!")
        return None
    
    def _menu(stdscr):
        curses.curs_set(0)  # Hide cursor
        selected_idx = 0
                
        while True:
            display_menu(stdscr, map_files, selected_idx)
            
            # Get key press
            key = stdscr.getch()
            
            if key == curses.KEY_UP and selected_idx > 0:
                selected_idx -= 1
            elif key == curses.KEY_DOWN and selected_idx < len(map_files) - 1:
                selected_idx += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
                return map_files[selected_idx]
            elif key == ord('q') or key == ord('Q'):
                return None
    
    try:
        selected_map = wrapper(_menu)
        return selected_map
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def main():
    print("Welcome to Gem Hunter!")
    
    selected_map = map_selection_menu()
    
    if selected_map:
        map_path = os.path.join("maps", selected_map)
        print(f"Selected map: {map_path}")
        # load_and_run_game(map_path)
    else:
        print("No map selected. Exiting...")

if __name__ == "__main__":
    main()