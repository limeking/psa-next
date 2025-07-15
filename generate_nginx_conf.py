import os

# 개발모드(True): 로컬 프론트 프록시, False: 프론트 컨테이너 프록시
dev_mode = True  # 필요시 수동 변경

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
        f.write(f"    location /{m}/ " + "{\n")
        f.write(f"        proxy_pass http://backend:8000/{m}/;\n")
        f.write("        proxy_set_header Host $host;\n")
        f.write("        proxy_set_header X-Real-IP $remote_addr;\n")
        f.write("        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n")
        f.write("        proxy_set_header X-Forwarded-Proto $scheme;\n")
        f.write("    }\n")
    f.write("    location / {\n        " + frontend_proxy + "\n    }\n")
    f.write("}\n")
print(f"✅ {conf_path} 자동생성 완료! (dev_mode={dev_mode})")
