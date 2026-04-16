# GradeInsight 成績管理系統

一個專業的成績管理平台，使用 FastAPI 作為後端、Streamlit 作為前端，支援成績匯入、分析、風險學生識別、成績編輯、報告匯出與備份功能。

## 專案目錄

```
GradeInsight_BDD/
├── backend/                    # FastAPI 後端服務
│   ├── main.py                # API 路由入口
│   ├── config.py              # 系統配置
│   ├── database.py            # SQLite 資料庫設定
│   ├── utils.py               # 共用工具函數
│   ├── models/                # Pydantic 與 ORM 模型
│   └── services/              # 核心業務邏輯服務
├── frontend/                   # Streamlit 前端
│   └── streamlit_app.py       # 單頁應用介面
├── data/                      # 本地資料庫與備份目錄
├── requirements.txt           # Python 依賴套件
└── README.md                  # 專案說明文檔
```

## 環境需求

- Python 3.10+（建議使用 Python 3.10 或 3.12）
- GitHub Codespaces 或類似開發環境
- 支援 `venv` 虛擬環境

## 安裝步驟

1. 克隆專案
   ```bash
   git clone <repository-url>
   cd GradeInsight_BDD
   ```

2. 建立並啟動虛擬環境
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. 安裝依賴套件
   ```bash
   pip install -r requirements.txt
   ```

4. 確認 Python 版本
   ```bash
   python --version
   ```

## 啟動方式

### 啟動後端 API

```bash
cd /workspaces/GradeInsight_BDD
source .venv/bin/activate
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

啟動後可瀏覽：http://localhost:8000/docs

啟動時若資料庫為空，系統會自動產生 30 筆模擬學生成績。

### 啟動前端介面

```bash
cd /workspaces/GradeInsight_BDD
source .venv/bin/activate
cd frontend
python -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

啟動後可瀏覽：http://localhost:8501

## 功能概述

- 📥 成績匯入（CSV/Excel）
- 📈 成績分佈與統計分析
- ⚠️ 風險學生識別
- ✏️ 單筆成績編輯與審計
- 📄 報告匯出（CSV/Excel）
- 💾 資料庫備份與狀態查詢
- 🧪 生成 30 筆模擬資料

## 常見問題排除

### 後端啟動失敗
- `uvicorn: command not found`：請先啟動虛擬環境 `source .venv/bin/activate`
- `ModuleNotFoundError`：請確認依賴已安裝 `pip install -r requirements.txt`
- 無法匯入 `backend.main`：請從專案根目錄執行啟動指令

### 前端啟動失敗
- `streamlit: command not found`：請啟動虛擬環境並安裝依賴
- 無法連線至後端：請先啟動後端 API，再啟動前端

### 匯入檔案失敗
- 檢查檔案是否為 CSV 或 Excel
- 檢查欄位是否包含 `name`, `student_id`, `usual`, `midterm`, `final`

### 其他
- 若資料庫未建立，可先啟動後端，系統會自動建立 `data/gradeinsight.db`

## 開發提示

- 後端模組位於 `backend/`
- 前端應用位於 `frontend/`
- 目前資料存放在 `data/`
- 如需重新生成模擬資料，可在前端「模擬資料」頁面執行
