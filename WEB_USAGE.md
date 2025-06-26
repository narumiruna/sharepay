# 旅行支出分帳網站使用指南

## 🚀 快速啟動

### 方法1: 使用 Makefile (推薦)
```bash
make web
```

### 方法2: 使用啟動腳本
```bash
uv run python run_web.py
```

### 方法3: 手動啟動
```bash
cd web
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

啟動後訪問: http://localhost:8000

## 📖 使用流程

### 1. 用戶註冊
- 訪問首頁，點擊「開始使用」
- 填寫用戶名、Email 和密碼
- 點擊「註冊」完成帳號創建

### 2. 登入系統
- 在首頁點擊「登入」
- 輸入用戶名和密碼
- 成功登入後會進入控制台

### 3. 創建旅行
- 在控制台點擊「創建新旅行」
- 填寫旅行名稱、描述
- 選擇主要幣別 (TWD, USD, EUR, JPY, GBP, CAD)
- 創建成功後可在控制台看到旅行卡片

### 4. 管理旅行成員
- 目前版本中，旅行創建者會自動成為成員
- 其他成員可以通過註冊帳號並被邀請加入

### 5. 記錄支出
- 進入旅行詳情頁面
- 點擊「添加支出」按鈕
- 填寫支出資訊:
  - 金額 (支援小數)
  - 幣別 (可選擇不同於旅行主幣別)
  - 描述 (例: "晚餐", "計程車費")
  - 日期 (默認為今天)
  - 分攤成員 (勾選要分攤的成員)

### 6. 查看結算
- 在旅行詳情頁面點擊「查看結算」
- 系統會自動計算:
  - 每個人的總支出
  - 每個人應付的金額
  - 最優化的轉帳建議
- 支援多幣別自動匯率轉換

## 🌟 功能特色

### 智能分帳
- 使用 SharePay 核心算法
- 自動計算最少轉帳次數
- 支援複雜的分攤場景

### 多幣別支援
- 支援 6 種主要幣別
- 自動匯率轉換
- 統一結算幣別

### 響應式設計
- 支援電腦和手機瀏覽
- Bootstrap 5 現代化界面
- 直觀的操作流程

### 安全認證
- JWT Token 身份驗證
- 密碼加密存儲
- 安全的API端點

## 🔧 技術架構

### 後端
- **框架**: FastAPI 
- **資料庫**: SQLite (支援升級至 PostgreSQL/MySQL)
- **認證**: JWT + bcrypt
- **ORM**: SQLAlchemy

### 前端
- **框架**: HTML5 + Bootstrap 5
- **JavaScript**: 原生 ES6+
- **樣式**: 自定義 CSS + Bootstrap

### 核心邏輯
- **分帳算法**: SharePay 核心庫
- **匯率轉換**: 實時匯率查詢
- **結算優化**: 最小化轉帳次數

## 📁 項目結構

```
sharepay/
├── web/                     # 網站應用
│   ├── app/                 # 後端應用
│   │   ├── main.py          # FastAPI 主應用
│   │   ├── database.py      # 資料庫模型
│   │   ├── auth.py          # 認證系統
│   │   └── schemas.py       # API 數據模型
│   ├── static/              # 靜態文件
│   │   ├── css/style.css    # 自定義樣式
│   │   └── js/app.js        # 前端 JavaScript
│   ├── templates/           # HTML 模板
│   └── README.md            # 詳細文檔
├── src/sharepay/            # 核心邏輯庫
├── run_web.py               # 啟動腳本
├── start_web.py             # 備用啟動腳本
└── Makefile                 # 構建工具
```

## 🐛 故障排除

### 啟動問題
```bash
# 確保依賴已安裝
uv sync

# 檢查 Python 路徑
python -c "import sys; print(sys.path)"

# 檢查 SharePay 模塊
python -c "from src.sharepay import SharePay; print('OK')"
```

### 資料庫問題
- 資料庫文件自動創建在 `web/travel_expenses.db`
- 如果遇到問題，可以刪除資料庫文件重新開始

### 匯率問題
- 匯率數據來自 SharePay 核心庫
- 需要網絡連接獲取實時匯率

## 🔮 未來改進

- [ ] 成員邀請功能
- [ ] 支出分類和標籤
- [ ] 數據導出功能
- [ ] 移動端 App
- [ ] 多語言支援
- [ ] 支出圖表分析

## 📞 支援

如有問題請查看:
1. `web/README.md` - 詳細技術文檔
2. `CLAUDE.md` - 開發指南
3. SharePay 核心庫文檔