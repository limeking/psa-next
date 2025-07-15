import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

import json

dev_mode = True  # 필요시 수동으로 변경

modules = []
modules_base = "backend/app/modules"
if os.path.exists(modules_base):
    for module_name in os.listdir(modules_base):
        info_path = os.path.join(modules_base, module_name, "module_info.json")
        if os.path.isfile(info_path):
            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                if info.get("enabled", True):
                    modules.append(info["name"])
            except Exception as e:
                print(f"[경고] {info_path} 파싱 실패: {e}")
else:
    print("[경고] backend/app/modules 폴더를 찾을 수 없습니다.")

if dev_mode:
    conf_path = "nginx/nginx.dev.conf"
    frontend_proxy = "proxy_pass http://host.docker.internal:3000;"
else:
    conf_path = "nginx/nginx.prod.conf"
    frontend_proxy = "proxy_pass http://frontend:80;"

with open(conf_path, "w", encoding="utf-8") as f:
    f.write("server {\n    listen 80;\n")
    for m in modules:
        f.write(f"    location /api/{m}/ {{\n")
        f.write(f"        proxy_pass http://backend:8000/{m}/;\n")
        f.write("        proxy_set_header Host $host;\n")
        f.write("        proxy_set_header X-Real-IP $remote_addr;\n")
        f.write("        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n")
        f.write("        proxy_set_header X-Forwarded-Proto $scheme;\n")
        f.write("    }\n")
    f.write("    location / {\n")
    f.write(f"        {frontend_proxy}\n")
    f.write("    }\n")
    f.write("}\n")

print(f"✅ {conf_path} 자동생성 완료! (dev_mode={dev_mode})")
