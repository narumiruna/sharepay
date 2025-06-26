# 旅行支出分帳系統

基於SharePay核心功能開發的網頁版旅行支出分帳系統，讓您輕鬆與朋友記錄和分攤旅行費用。

## 功能特色

- 🔐 用戶註冊和登入系統
- 🏝️ 創建和管理旅行群組
- 💰 記錄多幣別支出
- 👥 智能費用分攤
- 📊 自動結算計算
- 📱 響應式設計，支援手機和電腦

## 技術架構

- **後端**: FastAPI + SQLAlchemy + SQLite
- **前端**: HTML5 + Bootstrap 5 + JavaScript
- **認證**: JWT Token
- **核心邏輯**: SharePay 函式庫

## 安裝和運行

### 1. 安裝依賴

```bash
# 回到項目根目錄並使用uv安裝依賴
cd ../
uv sync
```

### 2. 運行應用

```bash
# 方法1: 在項目根目錄使用Makefile
make web

# 方法2: 使用啟動腳本
python start_web.py

# 方法3: 手動運行
cd web
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 訪問應用

打開瀏覽器訪問: http://localhost:8000

## 使用方法

### 1. 註冊和登入
- 訪問首頁，點擊「開始使用」進行註冊
- 填寫用戶名、Email和密碼完成註冊
- 使用註冊的帳號登入系統

### 2. 創建旅行
- 登入後在控制台點擊「創建新旅行」
- 填寫旅行名稱、描述和主要幣別
- 創建成功後可以看到旅行卡片

### 3. 添加支出
- 進入旅行詳情頁面
- 點擊「添加支出」按鈕
- 填寫金額、幣別、描述和日期
- 選擇要分攤費用的成員
- 提交後支出會自動記錄

### 4. 查看結算
- 在旅行詳情頁面點擊「查看結算」
- 系統會自動計算每個人應付或應收的金額
- 顯示最優化的轉帳建議，減少交易次數

## 支援的幣別

- TWD - 新台幣
- USD - 美元  
- EUR - 歐元
- JPY - 日圓
- GBP - 英鎊
- CAD - 加拿大元

## 資料庫結構

應用使用SQLite資料庫，包含以下主要表格：

- `users`: 用戶資訊
- `trips`: 旅行資訊
- `trip_members`: 旅行成員關聯
- `payments`: 支出記錄
- `payment_splits`: 支出分攤詳情

## 開發說明

### 項目結構

```
web/
├── app/
│   ├── main.py          # FastAPI應用主文件
│   ├── database.py      # 資料庫模型和配置
│   ├── auth.py          # 認證相關功能
│   └── schemas.py       # Pydantic數據模型
├── static/
│   ├── css/style.css    # 自定義樣式
│   └── js/app.js        # 前端JavaScript
├── templates/           # Jinja2模板
├── requirements.txt     # Python依賴
└── run.py              # 應用啟動腳本
```

### 核心集成

本應用整合了SharePay核心庫的以下功能：
- 多幣別支付處理
- 債務計算和追蹤
- 智能結算算法
- 匯率自動轉換

## 注意事項

- 首次運行時會自動創建SQLite資料庫
- 應用使用JWT進行身份認證，請在生產環境中更改SECRET_KEY
- 匯率數據來自SharePay核心庫的匯率查詢功能
- 建議在生產環境中使用PostgreSQL或MySQL替換SQLite