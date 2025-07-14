import os

def make_dockerfiles(frontend_path):
    dev = f"""\nFROM node:18\nWORKDIR /app\nCOPY package.json .\nCOPY package-lock.json .\nRUN npm install\nCOPY . .\nCMD ["npm", "start"]\n"""
    prod = f"""\nFROM node:18 AS build\nWORKDIR /app\nCOPY package.json .\nCOPY package-lock.json .\nRUN npm install\nCOPY . .\nRUN npm run build\n\nFROM nginx:alpine\nCOPY --from=build /app/build /usr/share/nginx/html\nEXPOSE 80\nCMD ["nginx", "-g", "daemon off;"]\n"""
    with open(os.path.join(frontend_path, "Dockerfile.dev"), "w", encoding="utf-8") as f:
        f.write(dev)
    with open(os.path.join(frontend_path, "Dockerfile.prod"), "w", encoding="utf-8") as f:
        f.write(prod)
    print(f"✅ Dockerfile.dev, Dockerfile.prod 자동 생성: {frontend_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("사용법: python add_frontend_dockerfiles.py [프론트엔드폴더경로]")
        exit(1)
    make_dockerfiles(sys.argv[1])
