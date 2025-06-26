#!/usr/bin/env python3
import uvicorn
import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    # 設置工作目錄
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 啟動應用
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."]
    )