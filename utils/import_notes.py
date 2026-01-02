import os
import sys
import json
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

CACHE_CONFIG_FILE = os.path.join(ROOT_DIR, '.racache_path')

def load_cache_path():
    if os.path.exists(CACHE_CONFIG_FILE):
        try:
            with open(CACHE_CONFIG_FILE, 'r') as f:
                path = f.read().strip()
                if os.path.exists(path):
                    return path
        except:
            return None
    return None

def save_cache_path(path):
    try:
        with open(CACHE_CONFIG_FILE, 'w') as f:
            f.write(path)
        print(f"\n[INFO] Path saved in '{CACHE_CONFIG_FILE}'.\n")
    except Exception as e:
        print(f"\n[WARN] Path could not be saved: {e}\n")

def find_file(base_path, filename_pattern):
    print(f"[LOG] Searching for '{filename_pattern}' in '{base_path}'...")
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower() == filename_pattern.lower():
                full_path = os.path.join(root, file)
                return full_path
                
    return None

def sanitize_name(note_text):
    clean = re.sub(r'\[.*?\]|\(.*?\)', '', note_text)
    clean = re.sub(r'[^a-zA-Z0-9_\s]', '', clean)
    clean = "_".join(clean.lower().split())
    if clean and clean[0].isdigit():
        clean = "var_" + clean
    return clean[:45]

def detect_type(note_text):
    lower = note_text.lower()
    if "32-bit" in lower or "32 bit" in lower: return "dword"
    if "24-bit" in lower or "24 bit" in lower: return "tbyte"
    if "16-bit" in lower or "16 bit" in lower: return "word"
    if "float" in lower: return "float32"
    return "byte"

def parse_user_txt(file_path):
    notes = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('N0:'):
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        addr_str = parts[1]
                        note_text = parts[2].strip().strip('"')
                        notes.append({"Address": addr_str, "Note": note_text})
    except Exception as e:
        print(f"[ERROR]: Error reading file: {e}\n")
    return notes

def parse_json_cache(file_path):
    notes = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            raw_notes = []
            if isinstance(data, list):
                raw_notes = data
            else:
                raw_notes = data.get('CodeNotes', []) or data.get('Notes', [])

            for n in raw_notes:
                notes.append({
                    "Address": n.get('Address'),
                    "Note": n.get('Note')
                })
    except Exception as e:
        pass
    return notes

def main():
    print("--- PyCheevos Note Importer (Smart Local) ---")
    racache_path = load_cache_path()
    
    if racache_path:
        print(f"Using saved folder: {racache_path}")
        if input("Change? (y/n): ").lower() == 'y':
            racache_path = None

    if not racache_path:
        print("\n[INFO]: Specify the emulator folder Root")
        print("[INFO]: The script will automatically search in subfolders.\n")
        
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            print("[INFO]: Opening folder selection window...")
            racache_path = filedialog.askdirectory(title="Select Emulator Folder")
            
            root.destroy()
        except:
            pass
        if not racache_path:
            racache_path = input("Path: ").strip().strip('"').strip("'")
        
        if os.path.exists(racache_path):
            save_cache_path(racache_path)
        else:
            print("\n[ERROR]: Folder not found.\n")
            return

    game_id = input("Game ID: ").strip()
    print("")
    if not game_id: return

    final_notes = []
    source_used = ""

    user_txt = find_file(racache_path, f"{game_id}-User.txt")
    if user_txt:
        print(f"User.txt found: {user_txt}\n")
        final_notes = parse_user_txt(user_txt)
        source_used = "User.txt (Local)"

    if not final_notes:
        notes_json = find_file(racache_path, f"{game_id}-Notes.json")
        if notes_json:
            print(f"Notes.json found: {notes_json}\n")
            final_notes = parse_json_cache(notes_json)
            source_used = "Notes.json"

    if not final_notes:
        official_json = find_file(racache_path, f"{game_id}.json")
        if official_json:
            print(f"Official Cache Found: {official_json}")
            final_notes = parse_json_cache(official_json)
            source_used = "Game Cache"

    if not final_notes:
        print(f"\nNo notes were found for ID {game_id} in the specified folder.")
        print("Make sure you load the game into the emulator at least once.\n")
        return

    print(f"Success! {len(final_notes)} notes extracted from {source_used}.")

    lines = []
    lines.append(f"# Code Notes for Game ID {game_id}")
    lines.append(f"# Source: {source_used}")
    lines.append("")
    lines.append("from core.helpers import byte, word, dword, tbyte, float32")
    lines.append("")

    count = 0
    used_names = {}

    for note in final_notes:
        addr = note["Address"]
        text = note.get("Note", "")
        if not text: continue

        if isinstance(addr, int): addr = hex(addr)
        elif isinstance(addr, str) and not addr.startswith("0x"):
            try: addr = hex(int(addr))
            except: 
                try: addr = "0x" + addr
                except: pass

        clean_text = re.sub(r'^\s*\[[^\]]+\]\s*', '', text)  # remove [bit] tags
        clean_text = re.split(r'[\n\r|]', clean_text, 1)[0]  # stop at newline or |
        clean_text = clean_text.replace('/', '_')            # turn / into _
        clean_text = clean_text.strip()                      # trim spaces

        mem_type = detect_type(text)
        var_name = sanitize_name(clean_text)
        if not var_name: var_name = f"unk_{addr}"
        
        if var_name in used_names:
            used_names[var_name] += 1
            var_name = f"{var_name}_{addr}"
        else:
            used_names[var_name] = 1

        comment = text.replace('\n', ' | ').replace('\r', '')
        lines.append(f"# {addr}: {comment}")
        lines.append(f"{var_name} = {mem_type}({addr})")
        lines.append("")
        count += 1

    output_dir = os.path.join(ROOT_DIR, 'scripts')
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    filename = os.path.join(output_dir, f"notes_{game_id}.py")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nSuccess! File generated in: {filename}")
    print(f"Total number of addresses mapped: {count}")

if __name__ == "__main__":
    main()