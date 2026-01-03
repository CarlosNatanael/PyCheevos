import os
import sys
import json
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

CACHE_PATH_FILE = os.path.join(ROOT_DIR, '.racache_path')

# --- CONFIGURATION AND SEARCH ---

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
        path = input("Paste the folder path: ").strip().strip('"').strip("'")

    if os.path.exists(path):
        with open(CACHE_PATH_FILE, 'w') as f: f.write(path)
        return path
    return None

def find_local_file(base_path, game_id):
    print(f"[SEARCH] Looking for game files for {game_id}...\n")
    candidates = [f"{game_id}-User.txt", f"{game_id}.json"]
    for root, _, files in os.walk(base_path):
        for file in files:
            if file in candidates:
                return os.path.join(root, file), file
    return None, None

# --- LOGIC PARSER ---
MEM_SIZES = {
    '0xH': 'byte', '0x': 'word', '0xX': 'dword',
    '0xL': 'low4', '0xU': 'high4',
    '0xM': 'bit0', '0xN': 'bit1', '0xO': 'bit2', '0xP': 'bit3',
    '0xQ': 'bit4', '0xR': 'bit5', '0xS': 'bit6', '0xT': 'bit7'
}

CMP_MAP = {'=': '==', '!=': '!=', '>': '>', '<': '<', '>=': '>=', '<=': '<='}

FLAG_MAP = {
    'R': 'reset_if', 'P': 'pause_if', 'T': 'trigger', 'M': 'measured',
    'Q': 'measured_if', 'A': 'add_source', 'B': 'sub_source',
    'N': 'and_next', 'O': 'or_next', 'I': 'add_address',
    'C': 'add_hits', 'Z': 'reset_next_if'
}

def parse_value(val_str):
    val_str = val_str.replace(' ', '')
    
    prefix = ""
    # Modificadores de valor
    if val_str.startswith('d'): prefix = ".delta()"; val_str = val_str[1:]
    elif val_str.startswith('p'): prefix = ".prior()"; val_str = val_str[1:]
    elif val_str.startswith('b'): prefix = ".bcd()"; val_str = val_str[1:]
    elif val_str.startswith('~'): prefix = ".invert()"; val_str = val_str[1:]

    # Memória
    for code, func in MEM_SIZES.items():
        if val_str.startswith(code):
            addr = val_str[len(code):]
            return f"{func}(0x{addr}){prefix}"
    if val_str.startswith('0x'):
        return f"word({val_str}){prefix}"

    if val_str.startswith('f'): return f"float({val_str[1:]})"
    return val_str

def parse_condition(cond_str):
    # 1. Extrai Hits
    hits = ""
    hit_match = re.search(r'\.(\d+)\.?$', cond_str)
    if hit_match:
        if 'f' not in cond_str[hit_match.start()-1:]:
            hits = f".with_hits({hit_match.group(1)})"
            cond_str = cond_str[:hit_match.start()]

    # 2. Extrai Flag
    flag = ""
    if ':' in cond_str:
        parts = cond_str.split(':')
        if len(parts[0]) == 1 and parts[0] in FLAG_MAP:
            flag_code = parts[0]
            cond_str = ':'.join(parts[1:])
            flag = f".with_flag({FLAG_MAP[flag_code]})"

    # 3. Separa Operador e Valores
    op = None
    for o in ['!=', '>=', '<=', '=', '>', '<']:
        if o in cond_str:
            op = o
            break
    
    if not op:
        val = parse_value(cond_str)
        return f"({val}){flag}{hits}"

    left_str, right_str = cond_str.split(op, 1)
    
    left = parse_value(left_str)
    right = parse_value(right_str)
    py_op = CMP_MAP[op]

    return f"({left} {py_op} {right}){flag}{hits}"

def parse_logic(mem_string):
    groups = mem_string.split('S')
    parsed_groups = []
    
    for i, group in enumerate(groups):
        conditions = []
        for cond_str in group.split('_'):
            if cond_str:
                conditions.append(parse_condition(cond_str))
        name = "logic" if i == 0 else f"alt{i}"
        parsed_groups.append((name, conditions))
        
    return parsed_groups

# --- READING AND GENERATION ---

def extract_data(file_path):
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            if file_path.endswith('.json'):
                content = json.load(f)
                achievements = []
                if 'Sets' in content:
                    for s in content['Sets']:
                        achievements.extend(s.get('Achievements', []))
                else:
                    achievements = content.get('Achievements', [])
                
                for a in achievements:
                    data.append({
                        'id': a.get('ID'),
                        'title': a.get('Title'),
                        'desc': a.get('Description'),
                        'points': a.get('Points'),
                        'mem': a.get('MemAddr')
                    })
            else:
                for line in f:
                    if re.match(r'^\d+:', line):
                        parts = line.split(':')
                        if len(parts) >= 4:
                            data.append({
                                'id': parts[0],
                                'mem': parts[1].strip('"'),
                                'title': parts[2].strip('"'),
                                'desc': parts[3].strip('"'),
                                'points': parts[5] if len(parts)>5 else "0"
                            })
    except Exception as e:
        print(f"[ERRO] Falha ao ler arquivo: {e}")
    return data

def generate_script(game_id, achievements):
    lines = []
    lines.append("from core.helpers import *")
    lines.append("from core.condition import Condition")
    lines.append("from models.achievement import Achievement")
    lines.append("from models.set import AchievementSet")
    lines.append("")
    lines.append(f'my_set = AchievementSet(game_id={game_id}, title="Imported Set")')
    lines.append("")

    for ach in achievements:
        title = ach['title']
        ach_id = ach['id']
        
        lines.append(f"# --- {title} ---")
        lines.append(f"# Original Logic: {ach['mem']}")
        
        logic_groups = parse_logic(ach['mem'])
        
        core_var = ""
        alt_vars = []
        
        for name, conds in logic_groups:
            var_name = f"logic_{ach_id}_{name}"
            if name == "logic": core_var = var_name
            else: alt_vars.append(var_name)
            
            lines.append(f"{var_name} = [")
            for c in conds:
                lines.append(f"    {c},")
            lines.append("]")
        
        lines.append(f"ach_{ach_id} = Achievement(")
        lines.append(f'    title="{title}",')
        lines.append(f'    description="{ach["desc"]}",')
        lines.append(f'    points={ach["points"]},')
        lines.append(f'    id={ach_id}')
        lines.append(")")
        
        if core_var:
            lines.append(f"ach_{ach_id}.add_core({core_var})")
        for alt in alt_vars:
            lines.append(f"ach_{ach_id}.add_alt({alt})")
            
        lines.append(f"my_set.add_achievement(ach_{ach_id})")
        lines.append("")

    # lines.append("# my_set.save()") 
    
    out_dir = os.path.join(ROOT_DIR, 'scripts')
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    out_file = os.path.join(out_dir, f"achievement_{game_id}.py")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        
    print(f"\nScript generated: {out_file}")
    print(f"   {len(achievements)} achievements processed.")

def main():
    print("--- PyCheevos Achievement Importer ---")
    
    racache = get_racache_path()
    if not racache: return

    game_id = input("Game ID: ").strip()
    if not game_id: return

    file_path, file_name = find_local_file(racache, game_id)
    if not file_path:
        print("File not found (User.txt or .json).")
        return

    print(f"Reading {file_name}...")
    data = extract_data(file_path)
    
    if not data:
        print("No achievements found.")
        return
        
    generate_script(game_id, data)

if __name__ == "__main__":
    main()