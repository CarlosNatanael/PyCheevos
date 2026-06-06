import os
import sys
import importlib.util
from pycheevos.utils.markdown import export_set_to_markdown

def process_game(game_id):
    script_path = os.path.join(os.getcwd(), 'scripts', f"achievement_{game_id}.py")
    
    if not os.path.exists(script_path):
        print(f"[ERROR] Script {script_path} not found. Generate the Python script first using option [2] or [4].")
        return
    
    print(f"\n[GENERATING] Loading logic from {script_path}...")
    
    # Dynamic import of user-generated script
    spec = importlib.util.spec_from_file_location(f"ach_{game_id}", script_path)
    ach_module = importlib.util.module_from_spec(spec)
    sys.modules[f"ach_{game_id}"] = ach_module
    spec.loader.exec_module(ach_module)
    
    # Extracts the compiled AchievementSet
    if not hasattr(ach_module, 'my_set'):
        print("[ERROR] 'my_set' object not found in the target script.")
        return
        
    my_set = ach_module.my_set
    out_path = os.path.join(os.getcwd(), 'scripts', f"README_{game_id}.md")
    
    # Export to Markdown
    export_set_to_markdown(my_set, out_path)
    print(f"[SUCCESS] Markdown documentation generated at: {out_path}")