import os

SOURCE_DIR = "app"  # Вся папка с бэком
OUTPUT_FILE = "full_app_code.py"
IGNORE_DIRS = {"venv", "__pycache__"}

def should_ignore(path):
    return any(part in IGNORE_DIRS for part in path.split(os.sep))

with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Пропускаем игнорируемые папки
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if should_ignore(file_path):
                    continue

                out_file.write(f"\n\n# ===== START FILE: {file_path} =====\n\n")
                with open(file_path, "r", encoding="utf-8") as f:
                    out_file.write(f.read())
                out_file.write(f"\n\n# ===== END FILE: {file_path} =====\n\n")

print(f"All code combined into {OUTPUT_FILE}")
