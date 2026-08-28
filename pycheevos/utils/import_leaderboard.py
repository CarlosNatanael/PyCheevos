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

FORMAT_MAPPING = {
    'SCORE': 'SCORE',
    'TIME': 'FRAMES',
    'FRAMES': 'FRAMES',
    'MILLISECS': 'MILLISECS',
    'TIMESECS': 'TIMESECS',
    'SECS': 'SECS',
    'VALUE': 'VALUE',
    'UNSIGNED': 'UNSIGNED',
    'MINUTES': 'MINUTES',
    'SECS_AS_MINS': 'SECS_AS_MINS',
    'FLOAT1': 'FLOAT1',
    'FLOAT2': 'FLOAT2',
    'FLOAT3': 'FLOAT3',
    'FLOAT4': 'FLOAT4',
    'FLOAT5': 'FLOAT5',
    'FLOAT6': 'FLOAT6',
    'FIXED1': 'FIXED1',
    'FIXED2': 'FIXED2',
    'FIXED3': 'FIXED3',
    'TENS': 'TENS',
    'HUNDREDS': 'HUNDREDS',
    'THOUSANDS': 'THOUSANDS'
}

def get_racache_path():
    path = None
    if os.path.exists(CACHE_PATH_FILE):
        try:
            with open(CACHE_PATH_FILE, 'r') as f: path = f.read().strip()
        except: pass
    if path and os.path.exists(path): return path
    
    return input("Emulator Path: ").strip().strip('"')

def get_credentials():
    user, password = None, None
    if os.path.exists(LOGIN_CACHE_FILE):
        try:
            with open(LOGIN_CACHE_FILE, 'r') as f:
                data = json.load(f)
                user, password = data.get('user'), data.get('password')
        except: pass
    if user and password: return user, password
    return input("User: "), getpass.getpass("Pass: ")

# --- HASHING ---

def calculate_checksum(data_list):
    standardized = []
    for item in data_list:
        id_str = str(item.get('id', ''))
        mem = str(item.get('mem') or '').strip()
        title = str(item.get('title') or '').strip()
        desc = str(item.get('desc') or '').strip()
        fmt = str(item.get('format', ''))
        lower = str(item.get('lower', ''))
        
        entry = f"{id_str}|{mem}|{title}|{desc}|{fmt}|{lower}"
        standardized.append(entry)
    
    standardized.sort()
    data_str = "||".join(standardized)
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

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

def parse_value(val_str: str) -> str:
    val_str = val_str.replace(" ", "")
    if not val_str: return "value(0)"
    
    wrap_func = ""
    if val_str[0] in PREFIXES:
        wrap_func = PREFIXES[val_str[0]]
        val_str = val_str[1:]

    if "{recall}" in val_str:
        return "recall()"

    if val_str.startswith("0x"):
        match = re.match(r"0x([a-zA-Z\s])?([a-fA-F0-9]+)", val_str)
        if match:
            prefix_type = match.group(1).strip() if match.group(1) else ""
            func = MEM_TYPES.get(prefix_type, "word") 
            result = f"{func}(0x{match.group(2)})"
        else:
            result = "value(0)"
    elif val_str.isdigit():
        result = f"value({int(val_str)})"
    else:
        result = "value(0)"

    return f"{result}.{wrap_func}()" if wrap_func else result

def parse_hits(right_str: str):
    if not right_str: return "0", ""
    right_str = right_str.strip('.')
    match = re.search(r'((?:0x)?[\da-fA-F]+)\.(\d+)', right_str)
    if match:
        return match.group(1), f".with_hits({int(match.group(2))})"
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
        right_str, hits = parse_hits(right_str) # type: ignore
        left = parse_value(left_str)
        right = parse_value(right_str)
        core_logic = f"({left} {py_op} {right})"
        if hits: core_logic += hits

    return f"{wrapper}({core_logic})" if wrapper else core_logic

def parse_lb_logic(mem_string):
    sections = {'start': [], 'cancel': [], 'submit': [], 'value': []}
    if not mem_string: return sections
    parts = mem_string.split("::")
    for part in parts:
        code = part[:4]
        logic_str = part[4:]
        target = None
        if code == "STA:": target = 'start'
        elif code == "CAN:": target = 'cancel'
        elif code == "SUB:": target = 'submit'
        elif code == "VAL:": target = 'value'
        
        if target:
            groups = logic_str.split('S')
            for group_str in groups:
                group_conds = []
                for cond in group_str.split('_'):
                    if cond:
                        group_conds.append(parse_condition(cond))
                if group_conds:
                    sections[target].append(group_conds)
    return sections

# --- DATA EXTRACTION ---

def extract_leaderboards(source_data, is_file=False):
    lbs = []
    if is_file:
        try:
            with open(source_data, 'r', encoding='utf-8', errors='ignore') as f:
                if source_data.endswith('.json'):
                    content = json.load(f)
                    return extract_from_json(content)
        except: return []
    else:
        return extract_from_json(source_data)
    return lbs

def extract_from_json(content):
    data = []
    source = []
    if "Leaderboards" in content: source = content["Leaderboards"]
    elif "PatchData" in content: source = content["PatchData"].get("Leaderboards", [])
    
    for lb in source:
        data.append({
            'id': lb.get('ID'),
            'title': lb.get('Title', 'Untitled'),
            'desc': lb.get('Description', ''),
            'mem': lb.get('Mem', ''),
            'format': lb.get('Format', 'VALUE'),
            'lower': lb.get('LowerIsBetter', False)
        })
    return data

def generate_script(game_id, leaderboards, source_name):
    if not leaderboards: return
    print(f"\n[GENERATING] Processing {len(leaderboards)} leaderboards from {source_name}...\n")
    
    lines = []
    lines.append("from pycheevos.core.helpers import *")
    lines.append("from pycheevos.core.constants import *")
    lines.append("from pycheevos.core.condition import Condition")
    lines.append("from pycheevos.models.leaderboard import Leaderboard")
    lines.append("from pycheevos.models.set import AchievementSet")
    lines.append("")
    lines.append(f'my_set = AchievementSet(game_id={game_id}, title="Imported Leaderboards")')
    lines.append("")

    for lb in leaderboards:
        raw_fmt = lb['format']
        safe_fmt = FORMAT_MAPPING.get(raw_fmt, 'VALUE')
        fmt_enum = f"LeaderboardFormat.{safe_fmt}"
        
        lower = "True" if lb['lower'] else "False"
        
        lines.append(f"# --- LB: {lb['title']} ---")
        sections = parse_lb_logic(lb['mem'])
        
        def write_groups(section_name, groups):
            arg_names = []
            for i, group in enumerate(groups):
                suffix = "" if i == 0 else f"_alt{i}"
                var_name = f"lb_{lb['id']}_{section_name}{suffix}"
                arg_names.append(var_name)
                
                lines.append(f"{var_name} = [")
                for c in group: lines.append(f"    {c},")
                lines.append("]")
            return ", ".join(arg_names)

        start_args = write_groups('start', sections['start'])
        cancel_args = write_groups('cancel', sections['cancel'])
        submit_args = write_groups('submit', sections['submit'])
        value_args = write_groups('value', sections['value'])

        lines.append(f"lb_{lb['id']} = Leaderboard(")
        lines.append(f'    title="""{lb["title"]}""",')
        lines.append(f'    description="""{lb["desc"]}""",')
        lines.append(f'    id={lb["id"]},')
        lines.append(f'    format={fmt_enum},')
        lines.append(f'    lower_is_better={lower}')
        lines.append(")")
        
        if start_args: lines.append(f"lb_{lb['id']}.set_start({start_args})")
        if cancel_args: lines.append(f"lb_{lb['id']}.set_cancel({cancel_args})")
        if submit_args: lines.append(f"lb_{lb['id']}.set_submit({submit_args})")
        if value_args: lines.append(f"lb_{lb['id']}.set_value({value_args})")
        
        lines.append(f"my_set.add_leaderboard(lb_{lb['id']})")
        lines.append("")

    lines.append("my_set.save()")

    out_dir = os.path.join(os.getcwd(), 'scripts')
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    out_file = os.path.join(out_dir, f"leaderboard_{game_id}.py")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"SUCCESS! Script generated: {out_file}")

def process_game(game_id):
    racache = get_racache_path()
    local_lbs = []
    local_source = "None"
    
    if racache:
        target = os.path.join(racache, "Data", f"{game_id}.json")
        if os.path.exists(target):
            local_lbs = extract_leaderboards(target, is_file=True)
            local_source = "Local File"

    print(f"[SYNC] Checking server for updates on ID {game_id}...")
    server_data = fetch_server_data(game_id)
    server_lbs = []
    if server_data:
        server_lbs = extract_leaderboards(server_data, is_file=False)

    final_lbs = []
    final_source = ""
    status_msg = ""

    if not local_lbs and not server_lbs:
        print("[ERROR] No leaderboards found locally or on server.")
        return

    if local_lbs and not server_lbs:
        final_lbs = local_lbs
        final_source = local_source
        status_msg = "Local Only (Offline)"
    
    elif server_lbs and not local_lbs:
        final_lbs = server_lbs
        final_source = "RA Server"
        status_msg = "Server Only"

    else:
        local_hash = calculate_checksum(local_lbs)
        server_hash = calculate_checksum(server_lbs)

        if local_hash == server_hash:
            final_lbs = server_lbs
            final_source = "RA Server (Synced)"
            status_msg = "Synced with Local"
        else:
            final_lbs = local_lbs
            final_source = local_source
            status_msg = "Local Modifications Detected (Unsynced)"
            
            diff = len(local_lbs) - len(server_lbs)
            if diff != 0: status_msg += f" [Count Diff: {diff:+d}]"

    # 4. Gera o Script
    print(f"\n[RESULT] Using: {final_source}")
    print(f"[STATUS] {status_msg}")
    
    generate_script(game_id, final_lbs, final_source)

def main():
    print("--- PyCheevos Leaderboard Importer ---")
    while True:
        game_id = input("\nEnter the Game ID (or 'q' to exit): ").strip()
        if game_id.lower() == 'q': break
        process_game(game_id)

if __name__ == "__main__":
    main()