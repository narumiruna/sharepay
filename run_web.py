#!/usr/bin/env python3
"""
從項目根目錄啟動旅行支出分帳網站
"""
import sys
import os

# 確保在項目根目錄
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# 添加web目錄到Python路徑
web_dir = os.path.join(project_root, 'web')
sys.path.insert(0, web_dir)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 啟動旅行支出分帳網站...")
    print("訪問 http://localhost:8000 查看網站")
    print("按 Ctrl+C 停止服務器")
    
    # 啟動uvicorn服務器
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[web_dir]
    )