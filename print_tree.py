import os

# 제외할 폴더/파일(원한다면 추가 가능)
EXCLUDE = {'.git', '__pycache__', '.venv', 'node_modules', '.idea', '.vscode', '.DS_Store', 'Thumbs.db'}

def print_tree(path, indent=""):
    entries = sorted([e for e in os.listdir(path) if e not in EXCLUDE and not e.startswith('.')])
    for idx, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        is_last = (idx == len(entries) - 1)
        branch = "└── " if is_last else "├── "
        print(indent + branch + entry)
        if os.path.isdir(full_path):
            next_indent = indent + ("    " if is_last else "│   ")
            print_tree(full_path, next_indent)

if __name__ == "__main__":
    print("📁 프로젝트 폴더 트리 구조\n")
    print_tree(".")
