
import os

# 개발모드(True)면 로컬 프론트(npm start), False면 운영(컨테이너) 프론트
dev_mode = True  # 필요시 직접 True/False 바꿔서 실행

modules = []
for name in os.listdir('.'):
    if os.path.isdir(name) and os.path.exists(f"{name}/backend/app"):
        modules.append(name)

if dev_mode:
    conf_path = "nginx/nginx.dev.conf"
    frontend_proxy = "proxy_pass http://host.docker.internal:3000;"
else:
    conf_path = "nginx/nginx.prod.conf"
    frontend_proxy = "proxy_pass http://frontend:80;"

with open(conf_path, "w", encoding="utf-8") as f:
    f.write("server {\n    listen 80;\n")
    for m in modules:
        f.write(f"    location /{m}/api/ " + "{\n")
        f.write(f"        proxy_pass http://{m}-backend:8000/;\n")
        f.write("    }\n")
    f.write("    location / {\n        " + frontend_proxy + "\n    }\n")
    f.write("}\n")
print(f"✅ {conf_path} 자동생성 완료! (dev_mode={dev_mode})")
