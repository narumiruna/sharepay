#!/usr/bin/env python3
"""
啟動旅行支出分帳網站
"""
import os
import sys
import subprocess

def main():
    print("🚀 啟動旅行支出分帳網站...")
    
    # 確保在項目根目錄
    project_root = os.path.dirname(__file__)
    os.chdir(project_root)
    
    # 檢查uv是否可用
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError("uv not found")
        print("✅ uv 可用")
    except FileNotFoundError:
        print("❌ 未找到uv，請先安裝uv")
        print("安裝方法: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return
    
    # 安裝依賴
    print("📦 安裝依賴...")
    result = subprocess.run(["uv", "sync"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 依賴安裝失敗: {result.stderr}")
        return
    
    print("✅ 依賴安裝完成")
    
    # 啟動服務器
    print("🌐 啟動服務器...")
    print("訪問 http://localhost:8000 查看網站")
    print("按 Ctrl+C 停止服務器")
    
    # 使用uv運行uvicorn
    os.chdir('web')
    subprocess.run([
        "uv", "run", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

if __name__ == "__main__":
    main()