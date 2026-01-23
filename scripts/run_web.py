#!/usr/bin/env python3
"""
啟動 SharePay Web 應用程式
整合了原本的三個啟動腳本功能
"""

import os
import subprocess
from pathlib import Path


class UvNotFoundError(FileNotFoundError):
    def __init__(self) -> None:
        super().__init__("uv not found")


def ensure_uv_available() -> None:
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise UvNotFoundError from exc
    if result.returncode != 0:
        raise UvNotFoundError


def main() -> None:
    print("🚀 啟動 SharePay Web 應用程式...")

    # Ensure we are in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check whether uv is available
    try:
        ensure_uv_available()
        print("✅ uv 可用")
    except UvNotFoundError:
        print("❌ 未找到 uv, 請先安裝 uv")
        print("安裝方法: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return

    # Install dependencies
    print("📦 安裝依賴...")
    result = subprocess.run(["uv", "sync"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 依賴安裝失敗: {result.stderr}")
        return

    print("✅ 依賴安裝完成")

    # Start the server
    print("🌐 啟動服務器...")
    print("訪問 http://localhost:8000 查看網站")
    print("按 Ctrl+C 停止服務器")

    # Run uvicorn via uv
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
