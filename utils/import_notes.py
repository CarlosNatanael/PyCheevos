import os
import sys
import json
import re
import requests
import getpass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

CACHE_PATH_FILE = os.path.join(ROOT_DIR, '.racache_path')
LOGIN_CACHE_FILE = os.path.join(ROOT_DIR, '.login_cache')

# --- CONFIGURATION FUNCTIONS ---

def get_racache_path():
    path = None
    if os.path.exists(CACHE_PATH_FILE):
        try:
            with open(CACHE_PATH_FILE, 'r') as f:
                path = f.read().strip()
        except: pass
    if path and os.path.exists(path):
        return path
    print("\n[CONFIG] Local Cache Folder not found.\n")
    
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        print("Opening folder selection window...")
        path = filedialog.askdirectory(title="Select Emulator Root Folder")
        root.destroy()
    except: pass

    if not path:
        print("Please enter the path manually:")
        path = input("Path: ").strip().strip('"').strip("'")

    if os.path.exists(path):
        with open(CACHE_PATH_FILE, 'w') as f: f.write(path)
        print(f"\n[INFO] Path saved to '{CACHE_PATH_FILE}'\n")
        return path
    else:
        print("[ERROR] Invalid path.")
        return None

def get_credentials():
    user, password = None, None
    if os.path.exists(LOGIN_CACHE_FILE):
        try:
            with open(LOGIN_CACHE_FILE, 'r') as f:
                data = json.load(f)
                user, password = data.get('user'), data.get('password')
        except: pass

    if user and password:
        return user, password

    print("\n[LOGIN] RetroAchievements Credentials Required")
    user = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

    if user and password:
        if input("Save credentials locally? (y/N): ").lower() == 'y':
            with open(LOGIN_CACHE_FILE, 'w') as f:
                json.dump({'user': user, 'password': password}, f)
            print(f"[INFO] Credentials saved to '{LOGIN_CACHE_FILE}'")
    
    return user, password

# --- SEARCH AND PARSE FUNCTIONS ---

def find_all_candidates(base_path, game_id):
    print(f"[DEBUG] Scanning {base_path} for ID {game_id}...")
    
    candidates = []
    target_files = [
        f"{game_id}-User.txt",
        f"{game_id}-Notes.json",
        f"{game_id}.json"
    ]
    targets_lower = [t.lower() for t in target_files]
    
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower() in targets_lower:
                full_path = os.path.join(root, file)
                priority = 3
                if file.lower().endswith("-user.txt"): priority = 1
                elif file.lower().endswith("-notes.json"): priority = 2
                
                candidates.append((priority, full_path, file))
                print(f"   Candidate found: {file}")
    candidates.sort(key=lambda x: x[0])
    return candidates

def parse_local_file(file_path):
    notes = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            if file_path.lower().endswith('.txt'):
                for line in f:
                    if line.startswith('N0:'):
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            notes.append({"Address": parts[1], "Note": parts[2].strip().strip('"')})
            else:
                data = json.load(f)
                if isinstance(data, list):
                    raw = data
                else:
                    raw = data.get('CodeNotes', []) or data.get('Notes', [])
                for n in raw:
                    notes.append({"Address": n.get('Address'), "Note": n.get('Note')})
    except Exception as e:
        print(f"[ERROR] Failed to read {os.path.basename(file_path)}: {e}")
    return notes

# --- SERVER FUNCTIONS ---

def fetch_server_notes(game_id):
    user, password = get_credentials()
    if not user or not password: return None

    print(f"[SERVER] Connecting as {user}...")
    sess = requests.Session()
    sess.headers.update({'User-Agent': f'PyCheevos_Importer/1.0 ({user})'})
    url = "https://retroachievements.org/dorequest.php"

    try:
        login = sess.post(url, data={'r': 'login', 'u': user, 'p': password}).json()
        if not login.get('Success'):
            print(f"[ERROR] Login failed: {login.get('Error')}")
            if os.path.exists(LOGIN_CACHE_FILE): os.remove(LOGIN_CACHE_FILE)
            return None
        token = login.get('Token')

        print(f"[SERVER] Downloading notes for ID {game_id}...")
        payload = {'r': 'codenotes2', 'g': game_id, 'u': user, 't': token}
        resp = sess.post(url, data=payload).json()

        if not resp.get('Success'):
            payload['r'] = 'codenotes'
            resp = sess.post(url, data=payload).json()
        
        if resp.get('Success'):
            return resp.get('CodeNotes', [])
        else:
            print(f"[ERROR] Server error: {resp.get('Error')}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
    
    return None

# --- FILE GENERATION ---

def sanitize_name(note_text):

    clean = re.sub(r'\[.*?\]|\(.*?\)', '', note_text)
    clean = re.sub(r'^[:\-\s_]+', '', clean)

    separators = ['\n', '.', ',', '=']
    for sep in separators:
        if sep in clean:
            clean = clean.split(sep)[0]
            break
    clean = re.sub(r"[:/-]", "_", clean)
    clean = re.sub(r'[^a-zA-Z0-9_\s]', '', clean)
    words = clean.lower().split()
    clean = "_".join(words)
    
    if clean and clean[0].isdigit(): 
        clean = "var_" + clean
    print(clean)
    return clean[:65]

def detect_type(note_text, default="byte"):
    note_lower = note_text.lower()
    
    type_candidates = [
        # Big-Endian
        ("dword_be", ["32-bit be", "32 bit be", "be 32 bit", "be 32-bit"]),
        ("tbyte_be", ["24-bit be", "24 bit be", "be 24 bit", "be 24-bit"]),
        ("word_be", ["16-bit be", "16 bit be", "be 16 bit", "be 16-bit"]),
        ("float32_be", ["float be", "be float"]),
        # Little-Endian / default
        ("dword", ["32-bit", "32 bit"]),
        ("tbyte", ["24-bit", "24 bit"]),
        ("word", ["16-bit", "16 bit"]),
        ("byte", ["8-bit", "8 bit"]),
        ("float32", ["float", "32-bit float", "32 bit float"]),
        # Uncommon
        ("mfb32_be", ["mbf be", "be mbf", "microsoft binary format"]),
        ("mfb32", ["mbf", "microsoft binary format"]),
        ("double32_be", ["double be", "double32 be", "be double", "be double32"]),
        ("double", ["double32", "double"]),
        ("bitcount", ["bitcount", "bit count", "bit-count"])
    ]
    
    # --- Step 1: check [Type] at start of line ---
    match_start = re.match(r'^\s*\[([^\]]+)\]', note_text)
    if match_start:
        type_hint = match_start.group(1).lower()
        # Only accept it if it contains a known type keyword
        if any(kw in type_hint for _, kws in type_candidates for kw in kws):
            note_lower = type_hint
    
    # --- Step 2: check [Type] at end of line ---
    match_end = re.search(r'\[([^\]]+)\]\s*$', note_text)
    if match_end:
        type_hint = match_end.group(1).lower()
        if any(kw in type_hint for _, kws in type_candidates for kw in kws):
            note_lower = type_hint
    
    # --- Step 3: first occurrence of a size/type keyword ---
    for type_name, keywords in type_candidates:
        for keyword in keywords:
            if keyword in note_lower:
                return type_name

    # fallback
    return default

def prefix_region(var_name, note_text):
    # List of known regions (case-insensitive)
    regions = ["us", "eu", "jp", "pal", "ntsc"]
    
    match = re.search(r'^\s*\[([a-zA-Z]+)\]', note_text)
    if match:
        region = match.group(1).lower()
        if region in regions:
            # prefix variable name
            var_name = f"{region}_{var_name}"
    
    return var_name

def parse_pointers_in_note(root_var, note_text):
    pointer_lines = []
    lines = note_text.split('\n')
    chain = {0: root_var} 
    
    for line in lines:

        stripped = line.strip()
        if not stripped.startswith('+'):
            continue
        depth = 0
        while depth < len(stripped) and stripped[depth] == '+':
            depth += 1
            
        content = stripped[depth:].strip()
        match = re.match(r'^(0x[\da-fA-F]+|\d+)', content)
        if not match: continue
        
        offset_str = match.group(1)
        rest_of_line = content[len(offset_str):].strip()
        
        if (depth - 1) not in chain: continue
        
        parent_expr = chain[depth - 1]
    
        link_type = detect_type(rest_of_line, default="dword")
        
        offset_expr = f"{link_type}({offset_str})"
        full_expr = f"{parent_expr} >> {offset_expr}"
        
        var_name = None
        if len(rest_of_line) > 2:
            potential_name = sanitize_name(rest_of_line)
            if potential_name and not potential_name.startswith("unk_"):
                var_name = potential_name
        
        if var_name:
            pointer_lines.append(f"{var_name} = ({full_expr})")
        chain[depth] = full_expr
        
    return pointer_lines

def generate_script(game_id, notes, source):
    if not notes: return False

    print(f"\n[GEN] Processing {len(notes)} notes from {source}...")

    lines = []
    lines.append(f"# Code Notes for Game ID {game_id}")
    lines.append(f"# Source: {source}")
    lines.append("")
    lines.append("from core.helpers import *")
    lines.append("")

    used_names = {}
    count = 0

    for note in notes:
        addr = note.get("Address")
        text = note.get("Note", "")
        if not text or not addr: 
            continue

        if isinstance(addr, int): addr = hex(addr)
        elif not str(addr).startswith("0x"):
            try: addr = hex(int(str(addr)))
            except: pass

        note_lines = text.replace('\r', '').split('\n')

        clean_text = re.sub(r'^\s*\[[^\]]+\]\s*', '', note_lines[0])  # remove [bit] tags
        clean_text = clean_text.split('\n')[0].strip()

        mem_type = detect_type(note_lines[0])
        var_name = sanitize_name(clean_text)
        var_name = prefix_region(var_name, text)
        if not var_name: var_name = f"unk_{addr}"

        if var_name in used_names:
            used_names[var_name] += 1
            var_name = f"{var_name}_{addr}"
        else:
            used_names[var_name] = 1

        # Top-level note header + variable
        lines.append(f"# {addr}: {note_lines[0]}")
        lines.append(f"{var_name} = {mem_type}({addr})")

        # --- Nested + / ++ lines ---
        chain = {0: var_name}
        current_var = None
        value_comments = []

        for line in note_lines[1:]:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith('+'):
                if current_var:
                    lines.append(f"{current_var} = {current_expr}")
                    if value_comments:
                        lines.extend(value_comments)
                    lines.append("")  # blank line after variable + comments
                    value_comments = []

                # Determine depth
                depth = 0
                while depth < len(stripped) and stripped[depth] == '+':
                    depth += 1

                content = stripped[depth:].strip()
                match = re.match(r'^(0x[\da-fA-F]+|\d+)\s*[:=]?\s*(.*)', content)
                if not match:
                    continue

                offset_str = match.group(1)
                rest_of_line = match.group(2) or ""

                # Get parent expression from chain
                parent_expr = chain.get(depth - 1, var_name)
                link_type = detect_type(rest_of_line, default="dword")
                current_expr = f"{parent_expr} >> {link_type}({offset_str})"

                # Store in chain for children to use
                chain[depth] = current_expr

                current_var = None
                potential_name = sanitize_name(rest_of_line)
                if potential_name:
                    potential_name = prefix_region(potential_name, text)
                    if potential_name in used_names:
                        used_names[potential_name] += 1
                        current_var = f"{potential_name}_{used_names[potential_name]}_{offset_str}"
                    else:
                        used_names[potential_name] = 1
                        current_var = potential_name
            
            if current_var:
                value_comments.append(f"#{stripped}")
            else:
                lines.append(f"#{stripped}")

        if current_var:
            lines.append(f"{current_var} = {current_expr}")
            if value_comments:
                lines.extend(value_comments)
            lines.append("")  # one blank line before next note

        lines.append("")
        count += 1

    # Write to file
    output_dir = os.path.join(ROOT_DIR, 'scripts')
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)
    filename = os.path.join(output_dir, f"notes_{game_id}.py")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nSuccess! File generated in: {filename}")
    print(f"Total number of addresses mapped: {count}")
    return True

# --- MAIN LOOP ---

def main():
    print("--- PyCheevos Note Importer (Hybrid v3) ---")
    
    while True:
        print("")
        game_id = input("Enter Game ID (or 'q' to quit): ").strip()
        if game_id.lower() == 'q': break
        if not game_id: continue

        racache = get_racache_path()
        candidates = []
        if racache:
            candidates = find_all_candidates(racache, game_id)
        
        notes_found = False
        
        for prio, file_path, file_name in candidates:
            notes = parse_local_file(file_path)
            
            if notes:
                print(f"[LOCAL] Successfully read {len(notes)} notes from {file_name}")
                if generate_script(game_id, notes, file_name):
                    notes_found = True
                    break
            else:
                print(f"\n[LOCAL] File found but empty/invalid: {file_name}")

        if notes_found:
            break

        # Fallback to Server
        print(f"\n[INFO] No usable local notes found for ID {game_id}.")
        print("Options:")
        print("  [1] Try another Game ID")
        print("  [2] Download from RetroAchievements (Login required)")
        print("  [3] Quit")
        
        choice = input("Choice: ").strip()
        
        if choice == '3' or choice.lower() == 'q': break
        if choice == '1': continue
        
        if choice == '2':
            server_notes = fetch_server_notes(game_id)
            if server_notes:
                if generate_script(game_id, server_notes, "RA Server"):
                    break
            else:
                print("\n[WARN] Could not fetch notes from server.")
                input("Press Enter to try again...")

if __name__ == "__main__":
    main()