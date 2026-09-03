import os
import sys
import json
import re
import requests
import getpass
import hashlib
from pycheevos.utils import import_notes

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
    return import_notes.get_racache_path()

def get_credentials():
    return import_notes.get_credentials()

def calculate_checksum(data_list):
    standardized = []
    for item in data_list:
        id_str = str(item.get('id', ''))
        mem = str(item.get('mem') or '').strip()
        title = str(item.get('title') or '').strip()
        desc = str(item.get('desc') or '').strip()
        points = str(item.get('points', 0))
        badge = str(item.get('badge', ''))
        fmt = str(item.get('format', ''))
        
        entry = f"{id_str}|{mem}|{title}|{desc}|{points}|{badge}|{fmt}"
        standardized.append(entry)

    standardized.sort()
    data_str = "||".join(standardized)
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

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

ADDRESS_MAP = {}

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
            raw_addr = match.group(2).lstrip('0')
            if not raw_addr: raw_addr = "0"
            raw_addr = "0x" + raw_addr
            if raw_addr in ADDRESS_MAP:
                result = ADDRESS_MAP[raw_addr]
            else:
                prefix_type = match.group(1).strip() if match.group(1) else ""
                func = MEM_TYPES.get(prefix_type, "word") 
                result = f"{func}(0x{match.group(2)})"
        else:
            result = "value(0)"
    elif val_str.isdigit():
        val_int = int(val_str)
        hex_str = f"0x{val_int:02x}"
        result = hex_str if raw_hex else f"value({hex_str})"
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
        right_str, hits = parse_hits(right_str) # type: ignore
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
    groups = mem_string.split('S')
    parsed_groups = []
    for i, group in enumerate(groups):
        conditions = []
        for cond_str in group.split('_'):
            if cond_str: conditions.append(parse_condition(cond_str))
        name = "logic" if i == 0 else f"alt{i}"
        parsed_groups.append((name, conditions))
    return parsed_groups

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

def build_address_map(notes):
    global ADDRESS_MAP
    ADDRESS_MAP.clear()
    used_names = {}
    for note in notes:
        addr = note.get("Address")
        text = note.get("Note", "")
        if not text or not addr: continue
        try:
            int_addr = int(addr, 16) if str(addr).startswith("0x") else int(addr)
            norm_addr = hex(int_addr)
        except: continue
        note_lines = text.replace('\r', '').split('\n')
        clean_text = re.sub(r'^\s*\[[^\]]+\]\s*', '', note_lines[0])
        clean_text = clean_text.split('\n')[0].strip()
        var_name = import_notes.sanitize_name(clean_text)
        var_name = import_notes.prefix_region(var_name, text)
        if not var_name: var_name = f"unk_{norm_addr}"
        if var_name in used_names:
            used_names[var_name] += 1
            var_name = f"{var_name}_{used_names[var_name]}"
        else:
            used_names[var_name] = 1
        ADDRESS_MAP[norm_addr] = var_name
    print(f"[SMART IMPORT] Mapped {len(ADDRESS_MAP)} variables from Code Notes.")

# --- DATA EXTRACTION ---

def extract_from_json_obj(content):
    data_ach = []
    data_lb = []
    source_ach = []
    source_lb = []
    
    if "Sets" in content and isinstance(content["Sets"], list):
        for s in content["Sets"]: source_ach.extend(s.get("Achievements", []))
    
    if "PatchData" in content:
        if isinstance(content["PatchData"], list):
            for s in content["PatchData"]: source_ach.extend(s.get("Achievements", []))
        elif isinstance(content["PatchData"], dict):
            source_ach.extend(content["PatchData"].get("Achievements", []))
            
    if "Achievements" in content and isinstance(content["Achievements"], list):
        current_ids = {a.get('ID') for a in source_ach}
        for a in content["Achievements"]:
            if a.get('ID') not in current_ids:
                source_ach.append(a)

    if "Leaderboards" in content and isinstance(content["Leaderboards"], list):
        source_lb.extend(content["Leaderboards"])
        
    if "PatchData" in content and isinstance(content["PatchData"], dict):
        current_lb_ids = {lb.get('ID') for lb in source_lb}
        for lb in content["PatchData"].get("Leaderboards", []):
            if lb.get('ID') not in current_lb_ids:
                source_lb.append(lb)

    for a in source_ach:
        if a.get('ID') == 101000001: continue
        data_ach.append({
            'id': a.get('ID'),
            'title': a.get('Title', 'Sem Título') or '',
            'desc': a.get('Description', '') or '',
            'points': a.get('Points', 0),
            'mem': a.get('MemAddr', '') or '',
            'type': a.get('Type') or '',
            'badge': a.get('BadgeName', '00000')
        })
        
    for lb in source_lb:
        data_lb.append({
            'id': lb.get('ID'),
            'title': lb.get('Title', 'Sem Título') or '',
            'desc': lb.get('Description', '') or '',
            'mem': lb.get('Mem', '') or '',
            'format': lb.get('Format', 'VALUE'),
            'lower_is_better': lb.get('LowerIsBetter', False)
        })

    return data_ach, data_lb

def extract_data(source_data, is_file=False):
    if is_file:
        file_path = source_data
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                if file_path.endswith('.json'):
                    content = json.load(f)
                    return extract_from_json_obj(content)
                else:
                    achievements = []
                    leaderboards = []
                    for line in f:
                        line = line.strip()
                        if re.match(r'^\d+:', line):
                            parts = line.split('":')
                            if len(parts) >= 4:
                                achievements.append({
                                    'id': parts[0].split(':')[0],
                                    'mem': parts[1].strip('"'),
                                    'title': parts[2].strip('"'),
                                    'desc': parts[3].strip('"'),
                                    'points': parts[5] if len(parts)>5 else "0",
                                    'type': "",
                                    'badge': parts[6].strip(':').strip() if len(parts)>6 else "00000"
                                })
                        elif re.match(r'^L\d+:', line):
                            match = re.match(r'^L(\d+):"([^"]*)":"([^"]*)":"([^"]*)":"([^"]*)":([^:]+):(.*):([01])$', line)
                            if match:
                                title_desc = match.group(7)
                                title = "Unknown"
                                desc = "Unknown"
                                td_match = re.match(r'^"(.+?)":"(.+?)"$', title_desc)
                                if td_match:
                                    title = td_match.group(1)
                                    desc = td_match.group(2)
                                else:
                                    title = title_desc.replace('"', '')

                                leaderboards.append({
                                    'id': match.group(1),
                                    'mem': f"STA:{match.group(2)}::CAN:{match.group(3)}::SUB:{match.group(4)}::VAL:{match.group(5)}",
                                    'title': title,
                                    'desc': desc,
                                    'format': match.group(6),
                                    'lower_is_better': match.group(8) == "1"
                                })
                    return achievements, leaderboards
        except Exception as e:
            print(f"[ERROR] Failed to read file: {e}")
            return [], []
    else:
        return extract_from_json_obj(source_data)

def generate_script(game_id, achievements, leaderboards, source_name):
    if not achievements and not leaderboards: return False
    
    out_dir = os.path.join(os.getcwd(), 'scripts')
    if not os.path.exists(out_dir): os.makedirs(out_dir)

    # --- 1. GENERATE ACHIEVEMENTS FILE ---
    if achievements:
        print(f"\n[GENERATING] Processing {len(achievements)} achievements from {source_name}...")
        
        lines = []
        lines.append("from pycheevos.core.helpers import *")
        lines.append("from pycheevos.core.constants import *")
        lines.append("from pycheevos.core.condition import Condition")
        lines.append("from pycheevos.models.achievement import Achievement")
        lines.append("from pycheevos.models.set import AchievementSet")
        lines.append(f"from notes_{game_id} import *") 
        lines.append("")
        lines.append(f'my_set = AchievementSet(game_id={game_id}, title="Imported Achievements")')
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
                for c in conds: lines.append(f"    {c},")
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
        
        ach_file = os.path.join(out_dir, f"achievement_{game_id}.py")
        with open(ach_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"SUCCESS! Achievements generated: {ach_file}")

    # --- 2. GENERATE LEADERBOARDS FILE ---
    if leaderboards:
        print(f"\n[GENERATING] Processing {len(leaderboards)} leaderboards from {source_name}...")
        
        lines = []
        lines.append("from pycheevos.core.helpers import *")
        lines.append("from pycheevos.core.constants import *")
        lines.append("from pycheevos.core.condition import Condition")
        lines.append("from pycheevos.models.leaderboard import Leaderboard")
        lines.append("from pycheevos.models.set import AchievementSet")
        lines.append(f"from notes_{game_id} import *") 
        lines.append("")
        lines.append(f'my_set = AchievementSet(game_id={game_id}, title="Imported Leaderboards")')
        lines.append("")

        for lb in leaderboards:
            lb_id = lb['id']
            title = lb['title'].replace('"', '\\"')
            desc = lb['desc'].replace('"', '\\"')
            fmt = lb['format']
            lower = "True" if lb['lower_is_better'] else "False"
            
            safe_fmt = FORMAT_MAPPING.get(fmt, 'VALUE')
            fmt_enum = f"LeaderboardFormat.{safe_fmt}"

            lines.append(f"# --- LB: {title} ---")
            sections = parse_lb_logic(lb['mem'])
            
            def write_groups(section_name, groups):
                arg_names = []
                for i, group in enumerate(groups):
                    suffix = "" if i == 0 else f"_alt{i}"
                    var_name = f"lb_{lb_id}_{section_name}{suffix}"
                    arg_names.append(var_name)
                    
                    lines.append(f"{var_name} = [")
                    for c in group: lines.append(f"    {c},")
                    lines.append("]")
                return ", ".join(arg_names)

            start_args = write_groups('start', sections['start'])
            cancel_args = write_groups('cancel', sections['cancel'])
            submit_args = write_groups('submit', sections['submit'])
            value_args = write_groups('value', sections['value'])

            lines.append(f"lb_{lb_id} = Leaderboard(")
            lines.append(f'    title="""{title}""",')
            lines.append(f'    description="""{desc}""",')
            lines.append(f'    id={lb_id},')
            lines.append(f'    format={fmt_enum},')
            lines.append(f'    lower_is_better={lower}')
            lines.append(")")
            
            if start_args: lines.append(f"lb_{lb_id}.set_start({start_args})")
            if cancel_args: lines.append(f"lb_{lb_id}.set_cancel({cancel_args})")
            if submit_args: lines.append(f"lb_{lb_id}.set_submit({submit_args})")
            if value_args: lines.append(f"lb_{lb_id}.set_value({value_args})")
            
            lines.append(f"my_set.add_leaderboard(lb_{lb_id})")
            lines.append("")

        lines.append("my_set.save()")
        
        lb_file = os.path.join(out_dir, f"leaderboard_{game_id}.py")
        with open(lb_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"SUCCESS! Leaderboards generated: {lb_file}")

    return True

def process_game(game_id):
    if not game_id: return
    racache = get_racache_path()
    
    print("\n--- STEP 1: Loading Notes for Variable Mapping ---")
    local_notes = []
    if racache:
        candidates = import_notes.find_all_candidates(racache, game_id)
        for _, file_path, file_name in candidates:
            parsed = import_notes.parse_local_file(file_path)
            if parsed:
                local_notes = parsed
                break
    server_notes = import_notes.fetch_server_notes(game_id)
    final_notes = local_notes if local_notes else server_notes
    
    if final_notes:
        build_address_map(final_notes)
        print("\n[SMART IMPORTER] Auto-generating notes script...")
        import_notes.generate_script(game_id, final_notes, "Smart Importer Sync")
    else:
        print("[WARNING] No notes found. Script will use raw byte(0x...) addresses.")

    print("\n--- STEP 2: Loading Achievements & Leaderboards ---")
    local_achs, local_lbs = [], []
    local_source = "None"
    
    if racache:
        candidates = find_all_candidates(racache, game_id)
        for _, file_path, file_name in candidates:
            parsed_achs, parsed_lbs = extract_data(file_path, is_file=True)
            if parsed_achs or parsed_lbs:
                local_achs, local_lbs = parsed_achs, parsed_lbs
                local_source = file_name
                break

    print(f"[SYNC] Checking server for updates on ID {game_id}...")
    server_data = fetch_server_data(game_id)
    server_achs, server_lbs = [], []
    if server_data:
        server_achs, server_lbs = extract_data(server_data, is_file=False)

    final_achs, final_lbs = [], []
    final_source = ""
    status_msg = ""

    if not local_achs and not server_achs and not local_lbs and not server_lbs:
        print("[ERROR] No data found.")
        return

    local_hash = calculate_checksum(local_achs + local_lbs)
    server_hash = calculate_checksum(server_achs + server_lbs)

    if local_hash == server_hash:
        final_achs, final_lbs = server_achs, server_lbs
        final_source = "RA Server (Synced)"
        status_msg = "Synced with Local"
    elif not local_achs and not local_lbs:
        final_achs, final_lbs = server_achs, server_lbs
        final_source = "RA Server"
        status_msg = "Server Only (New Import)"
    elif not server_achs and not server_lbs:
        final_achs, final_lbs = local_achs, local_lbs
        final_source = local_source
        status_msg = "Local Only (Offline)"
    else:
        if local_achs:
            final_achs = local_achs
            src_a = "Local"
        else:
            final_achs = server_achs
            src_a = "Server"
        if local_lbs:
            final_lbs = local_lbs
            src_l = "Local"
        else:
            final_lbs = server_lbs
            src_l = "Server"

        final_source = local_source
        status_msg = f"Merged: Achievements ({src_a}) + Leaderboards ({src_l})"

    print(f"\n[RESULT] Using: {final_source}")
    print(f"[STATUS] {status_msg}")
    generate_script(game_id, final_achs, final_lbs, final_source)

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

def fetch_server_data(game_id):
    user, password = get_credentials()
    if not user or not password: return None
    sess = requests.Session()
    sess.headers.update({'User-Agent': f'PyCheevos_Importer/1.0 ({user})'})
    url = "https://retroachievements.org/dorequest.php"
    try:
        login = sess.post(url, data={'r': 'login', 'u': user, 'p': password}).json()
        if not login.get('Success'): return None
        token = login.get('Token')
        payload = {'r': 'patch', 'g': game_id, 'u': user, 't': token}
        resp = sess.post(url, data=payload).json()
        if resp.get('Success'): return resp
    except: pass
    return None

def main():
    print("--- PyCheevos Smart Importer ---")
    while True:
        game_id = input("\nEnter the Game ID (or 'q' to exit): ").strip()
        if game_id.lower() == 'q': break
        process_game(game_id)

if __name__ == "__main__":
    main()