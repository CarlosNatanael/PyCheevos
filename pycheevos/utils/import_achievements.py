import os
import sys
import json
import re
import requests
import getpass
import hashlib

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

CACHE_PATH_FILE = os.path.join(ROOT_DIR, '.racache_path')
LOGIN_CACHE_FILE = os.path.join(ROOT_DIR, '.login_cache')

# --- CONFIGURATION AND CREDENTIALS ---

def get_racache_path():
    path = None
    if os.path.exists(CACHE_PATH_FILE):
        try:
            with open(CACHE_PATH_FILE, 'r') as f:
                path = f.read().strip()
        except: pass

    if path and os.path.exists(path):
        return path
    
    print("\n[CONFIG] Emulator folder not found.")
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        print("Opening selection window...")
        path = filedialog.askdirectory(title="Select the emulator's root folder.")
        root.destroy()
    except: pass

    if not path:
        print("Please enter the path manually:")
        path = input("Path: ").strip().strip('"').strip("'")

    if os.path.exists(path):
        with open(CACHE_PATH_FILE, 'w') as f: f.write(path)
        print(f"[INFO] Path saved in '{CACHE_PATH_FILE}'")
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
        if input("Save credentials locally? (y/n): ").lower() == 'y':
            with open(LOGIN_CACHE_FILE, 'w') as f:
                json.dump({'user': user, 'password': password}, f)
            print(f"[INFO] Credentials saved in '{LOGIN_CACHE_FILE}'")
    
    return user, password

# --- SYNC LOGIC (HASHING) ---

def calculate_checksum(achievements_list):
    """
    Gera um hash MD5 único baseado no conteúdo das conquistas para detecção de mudanças.
    """
    standardized = []
    for ach in achievements_list:
        id_str = str(ach.get('id', ''))
        
        mem = str(ach.get('mem') or '').strip()
        title = str(ach.get('title') or '').strip()
        desc = str(ach.get('desc') or '').strip()
        points = str(ach.get('points', 0))
        type_str = str(ach.get('type') or '').strip()
        badge = str(ach.get('badge', ''))
        
        entry = f"{id_str}|{mem}|{title}|{desc}|{points}|{type_str}|{badge}"
        standardized.append(entry)
    
    standardized.sort()
    
    data_str = "||".join(standardized)
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

# --- LOCAL SEARCH ---

def find_all_candidates(base_path, game_id):
    print(f"[DEBUG] Scanning {base_path} by ID {game_id}...")
    
    candidates = []
    target_files = [f"{game_id}-User.txt", f"{game_id}.json"]
    targets_lower = [t.lower() for t in target_files]
    
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower() in targets_lower:
                full_path = os.path.join(root, file)
                priority = 2
                if file.lower().endswith("-user.txt"): priority = 1
                
                candidates.append((priority, full_path, file))
                print(f"   File found: {file}")

    candidates.sort(key=lambda x: x[0])
    return candidates

# --- SERVER DOWNLOAD ---

def fetch_server_data(game_id):
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

        print(f"[SERVER] Downloading game data {game_id}...")
        payload = {'r': 'patch', 'g': game_id, 'u': user, 't': token}
        resp = sess.post(url, data=payload).json()
        
        if resp.get('Success'):
            return resp
        else:
            print(f"[ERROR] Server error: {resp.get('Error')}")
    
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
    
    return None

# --- LOGIC PARSER ---

FLAG_WRAPPER_MAP = {
    "R:": "reset_if", "P:": "pause_if", "M:": "measured", "Q:": "measured_if",
    "T:": "trigger", "I:": "add_address", "A:": "add_source", "B:": "sub_source",
    "C:": "add_hits", "D:": "sub_hits", "N:": "and_next", "O:": "or_next",
    "K:": "remember", "Z:": "reset_next_if", "G:": "measured_percent"
}

MEM_TYPES = {
    "M": "bit0", "N": "bit1", "O": "bit2", "P": "bit3", "Q": "bit4", "R": "bit5",
    "S": "bit6", "T": "bit7", "H": "byte", "": "word", "W": "tbyte", "X": "dword",
    "I": "word_be", "J": "tbyte_be", "G": "dword_be", "L": "low4", "U": "high4", "K": "bitcount",
    "fF": "float32", "fB": "float32_be", "fH": "double32", "fI": "double32_be", "fM": "mbf32", "fL": "mbf32_le",
}
PREFIXES = {"d": "delta", "p": "prior", "b": "bcd", "~": "invert"}
CMP_MAP = {"!=": "!=", ">=": ">=", "<=": "<=", "=": "==", ">": ">", "<": "<"}
CMP_KEYS = sorted(CMP_MAP.keys(), key=len, reverse=True)

def parse_value(val_str: str, raw_hex: bool = False) -> str:
    val_str = val_str.replace(" ", "")
    if not val_str: return "value(0)"
    
    wrap_func = ""
    if val_str[0] in PREFIXES:
        wrap_func = PREFIXES[val_str[0]]
        val_str = val_str[1:]

    if "{recall}" in val_str:
        val_str = re.sub(r"0x[a-zA-Z]", "0x", val_str)
        op_match = re.search(r"(0x[a-fA-F0-9]+|[\d]+)\s*([\+\-\*\/])\s*\{recall\}", val_str)
        if op_match:
            numero = op_match.group(1)
            operador = op_match.group(2)
            val_obj = f"value({numero})" if numero.startswith("0x") else f"value({int(numero)})"
            result = f"recall() {operador} {val_obj}"
        else:
            result = val_str.replace("{recall}", "recall()")
        return f"({result}).{wrap_func}()" if wrap_func else result

    if val_str.startswith("0x"):
        match = re.match(r"0x([a-zA-Z\s])?([a-fA-F0-9]+)", val_str)
        if match:
            prefix_type = match.group(1).strip() if match.group(1) else ""
            addr = match.group(2)
            func = MEM_TYPES.get(prefix_type, "word") 
            result = f"{func}(0x{addr})"
        else:
            result = "value(0)"
    elif val_str.isdigit():
        val_int = int(val_str)
        hex_str = f"0x{val_int:02x}"
        if raw_hex:
            result = hex_str
        else:
            result = f"value({hex_str})"
            
    elif val_str.replace('.', '', 1).isdigit():
        result = f"float({val_str})"
    else:
        result = "value(0)"

    return f"{result}.{wrap_func}()" if wrap_func else result

def parse_hits(right_str: str):
    if not right_str: return "0", ""
    right_str = right_str.strip('.')
    match = re.search(r'((?:0x)?[\da-fA-F]+)\.(\d+)', right_str)
    if match:
        hits_val = int(match.group(2))
        return match.group(1), f".with_hits({hits_val})"
    return str(int(right_str)) if right_str.isdigit() else right_str, ""

def parse_comparison(cond_str: str):
    for op in CMP_KEYS:
        if op in cond_str:
            left, right = cond_str.split(op, 1)
            return left, CMP_MAP[op], right
    return cond_str, None, None

def parse_condition(cond_str: str):
    wrapper = None
    for flag_code, func_name in FLAG_WRAPPER_MAP.items():
        if cond_str.startswith(flag_code):
            wrapper = func_name
            cond_str = cond_str[len(flag_code):]
            break
    
    left_str, py_op, right_str = parse_comparison(cond_str)

    if py_op is None:
        val = parse_value(left_str)
        core_logic = f"{val}" if val and val != "0" else "value(0)"
    else:
        right_str, hits = parse_hits(right_str)
        if right_str.startswith("f"): right_str = right_str[1:]
        
        left = parse_value(left_str)
        use_raw_right = not left.startswith("float(")
        right = parse_value(right_str, raw_hex=use_raw_right)
        
        if not left: left = "value(0)"
        if not right: right = "value(0)"

        core_logic = f"({left} {py_op} {right})"
        
        if hits: core_logic += hits

    return f"{wrapper}({core_logic})" if wrapper else core_logic

def parse_logic(mem_string):
    if not mem_string: return []
    groups = re.split(r'(?:S.:)', mem_string)
    parsed_groups = []
    for i, group in enumerate(groups):
        conditions = []
        for cond_str in group.split('_'):
            if cond_str: conditions.append(parse_condition(cond_str))
        name = "logic" if i == 0 else f"alt{i}"
        parsed_groups.append((name, conditions))
    return parsed_groups

# --- DATA PROCESSING ---

def extract_achievements(source_data, is_file=False):
    achievements = []
    
    if is_file:
        file_path = source_data
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                if file_path.endswith('.json'):
                    content = json.load(f)
                    return extract_from_json_obj(content)
                else:
                    for line in f:
                        if re.match(r'^\d+:', line):
                            parts = line.split('":')
                            if len(parts) >= 4:
                                achievements.append({
                                    'id': parts[0],
                                    'mem': parts[1].strip('"'),
                                    'title': parts[2].strip('"'),
                                    'desc': parts[3].strip('"'),
                                    'points': parts[5] if len(parts)>5 else "0",
                                    'type': "",
                                    'badge': parts[6].strip(':').strip() if len(parts)>6 else "00000"
                                })
        except Exception as e:
            print(f"[ERROR] Failed to read file: {e}")
            return []
    else:
        return extract_from_json_obj(source_data)

    return achievements

def extract_from_json_obj(content):
    data = []
    source_list = []
    
    if "Sets" in content and isinstance(content["Sets"], list):
        for s in content["Sets"]: source_list.extend(s.get("Achievements", []))
    elif "PatchData" in content and isinstance(content["PatchData"], list):
        for s in content["PatchData"]: source_list.extend(s.get("Achievements", []))
    
    if not source_list and "Achievements" in content:
        source_list = content["Achievements"]

    if "PatchData" in content and isinstance(content["PatchData"], dict):
        patch = content["PatchData"]
        achievements = patch.get("Achievements", [])
        source_list.extend(achievements)

    for a in source_list:
        if a.get('ID') == 101000001: continue
        data.append({
            'id': a.get('ID'),
            'title': a.get('Title', 'Sem Título') or '',
            'desc': a.get('Description', '') or '',
            'points': a.get('Points', 0),
            'mem': a.get('MemAddr', '') or '',
            'type': a.get('Type') or '',
            'badge': a.get('BadgeName', '00000')
        })
    return data

def generate_script(game_id, achievements, source_name):
    if not achievements: return False
    print(f"\n[GENERATING] Processing {len(achievements)} achievements from {source_name}...\n")
    
    lines = []
    lines.append("from pycheevos.core.helpers import *")
    lines.append("from pycheevos.core.constants import *")
    lines.append("from pycheevos.core.condition import Condition")
    lines.append("from pycheevos.models.achievement import Achievement")
    lines.append("from pycheevos.models.set import AchievementSet")
    lines.append("")
    lines.append(f'my_set = AchievementSet(game_id={game_id}, title="Imported Set")')
    lines.append("")

    for ach in achievements:
        title = ach['title'].replace('"', '\\"')
        desc = ach['desc'].replace('"', '\\"')
        ach_id = ach['id']
        ach_type = ach.get('type', '')
        badge = ach.get('badge', '00000')

        type_str = ""
        if ach_type == "progression": type_str = ", type=AchievementType.PROGRESSION"
        elif ach_type == "win_condition": type_str = ", type=AchievementType.WIN_CONDITION"
        elif ach_type == "missable": type_str = ", type=AchievementType.MISSABLE"
        
        lines.append(f"# --- {title} ---")
        lines.append(f"# Logic: {ach['mem']}")
        
        logic_groups = parse_logic(ach['mem'])
        
        core_var = ""
        alt_vars = []
        
        for name, conds in logic_groups:
            var_name = f"ach_{ach_id}_{name}"
            if name == "logic": core_var = var_name
            else: alt_vars.append(var_name)
            
            lines.append(f"{var_name} = [")
            for c in conds:
                lines.append(f"    {c},")
            lines.append("]")
        
        lines.append(f"ach_{ach_id} = Achievement(")
        lines.append(f'    title="""{title}""",')
        lines.append(f'    description="""{desc}""",')
        lines.append(f'    points={ach["points"]}{type_str},')
        lines.append(f'    id={ach_id}, badge="{badge}"')
        lines.append(")")
        
        if core_var: lines.append(f"ach_{ach_id}.add_core({core_var})")
        for alt in alt_vars: lines.append(f"ach_{ach_id}.add_alt({alt})")
        lines.append(f"my_set.add_achievement(ach_{ach_id})")
        lines.append("")

    lines.append("my_set.save()")

    out_dir = os.path.join(os.getcwd(), 'scripts')
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    out_file = os.path.join(out_dir, f"achievement_{game_id}.py")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"SUCCESS! Script generated: {out_file}")
    return True

# --- MAIN LOOP (SYNC ENABLED) ---

def process_game(game_id):
    if not game_id: return

    racache = get_racache_path()
    local_achs = []
    local_source = "None"
    
    if racache:
        candidates = find_all_candidates(racache, game_id)
        for _, file_path, file_name in candidates:
            parsed = extract_achievements(file_path, is_file=True)
            if parsed:
                local_achs = parsed
                local_source = file_name
                break

    print(f"[SYNC] Checking server for updates on ID {game_id}...")
    server_data = fetch_server_data(game_id)
    server_achs = []
    if server_data:
        server_achs = extract_achievements(server_data, is_file=False)

    final_achs = []
    final_source = ""
    status_msg = ""

    if not local_achs and not server_achs:
        print("[ERROR] No achievements found locally or on server.")
        return

    if local_achs and not server_achs:
        final_achs = local_achs
        final_source = local_source
        status_msg = "Local Only (Offline)"
    
    elif server_achs and not local_achs:
        final_achs = server_achs
        final_source = "RA Server"
        status_msg = "Server Only (New Import)"

    else:
        local_hash = calculate_checksum(local_achs)
        server_hash = calculate_checksum(server_achs)

        if local_hash == server_hash:
            final_achs = server_achs
            final_source = "RA Server (Synced)"
            status_msg = "Synced with Local"
        else:
            final_achs = local_achs
            final_source = local_source
            status_msg = "Local Modifications Detected (Unsynced)"
            
            diff = len(local_achs) - len(server_achs)
            if diff != 0: status_msg += f" [Count Diff: {diff:+d}]"

    # 4. Gera o Script
    print(f"\n[RESULT] Using: {final_source}")
    print(f"[STATUS] {status_msg}")
    
    generate_script(game_id, final_achs, final_source)

def main():
    print("--- PyCheevos Achievement Importer ---")
    while True:
        game_id = input("\nEnter the Game ID (or 'q' to exit): ").strip()
        if game_id.lower() == 'q': break
        process_game(game_id)

if __name__ == "__main__":
    main()