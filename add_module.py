import os
import shutil
import sys

def copytree_with_replace(src, dst, module_name):
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        target_dir = os.path.join(dst, rel_path.replace('module', module_name))
        os.makedirs(target_dir, exist_ok=True)
        for file in files:
            with open(os.path.join(root, file), "r", encoding="utf-8") as fin:
                content = fin.read().replace("{{module_name}}", module_name)
            target_file = os.path.join(target_dir, file.replace("module", module_name))
            with open(target_file, "w", encoding="utf-8") as fout:
                fout.write(content)
            print(f"[생성] {target_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python add_module.py [모듈명]")
        sys.exit(1)
    module_name = sys.argv[1]
    os.makedirs(f"{module_name}/backend/app", exist_ok=True)
    os.makedirs(f"{module_name}/frontend/src", exist_ok=True)
    os.makedirs(f"{module_name}/db", exist_ok=True)
    copytree_with_replace("templates/backend_module", f"{module_name}/backend", module_name)
    copytree_with_replace("templates/frontend_module", f"{module_name}/frontend", module_name)
    copytree_with_replace("templates/db_module", f"{module_name}/db", module_name)
    print(f"\n✅ '{module_name}' 모듈 자동 생성 완료!")
