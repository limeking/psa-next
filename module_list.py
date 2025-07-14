import os
import json
import datetime

def list_all_modules():
    modules = []
    # 현재 디렉토리 기준 하위폴더에 module_info.json 있는 경우만 모듈로 간주
    for name in os.listdir():
        info_path = os.path.join(name, "module_info.json")
        if os.path.isfile(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            created_at = datetime.datetime.fromtimestamp(os.path.getmtime(info_path)).strftime("%Y-%m-%d %H:%M:%S")
            backend = "O" if os.path.exists(info.get("backend", "")) else "X"
            frontend = "O" if os.path.exists(info.get("frontend", "")) else "X"
            db = "O" if os.path.exists(info.get("db", "")) else "X"
            modules.append({
                "name": info.get("name"),
                "desc": info.get("description"),
                "created": created_at,
                "backend": backend,
                "frontend": frontend,
                "db": db
            })

    if not modules:
        print("등록된 모듈이 없습니다.")
        return

    print(f"\n[전체 모듈 목록/상태조회]")
    print(f"{'이름':10} | {'설명':25} | {'생성일':19} | B | F | D")
    print("-"*70)
    for m in modules:
        print(f"{m['name']:10} | {m['desc'][:25]:25} | {m['created']} | {m['backend']} | {m['frontend']} | {m['db']}")

if __name__ == "__main__":
    list_all_modules()
