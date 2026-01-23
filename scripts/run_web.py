#!/usr/bin/env python3
"""
啟動 SharePay Web 應用程式
整合了原本的三個啟動腳本功能
"""

import os
import subprocess
from pathlib import Path


def main() -> None:
    print("🚀 啟動 SharePay Web 應用程式...")

    # 確保在項目根目錄
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # 檢查 uv 是否可用
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError("uv not found")
        print("✅ uv 可用")
    except FileNotFoundError:
        print("❌ 未找到 uv，請先安裝 uv")
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

    # 使用 uv 運行 uvicorn
    subprocess.run(
        [
            "uv",
            "run",
            "uvicorn",
            "src.sharepay_web.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload",
            "--reload-dir",
            "src",
        ]
    )


if __name__ == "__main__":
    main()
