# GradeInsight 成績管理系統

一個完整的成績管理系統，基於 FastAPI 後端和 Streamlit 前端，提供成績匯入、統計分析、風險學生識別等功能。

## 專案簡介

GradeInsight 是一個智慧成績管理平台，幫助教師和助教高效管理學生成績。系統支援成績數據的匯入、分析、可視化、編輯和匯出，提供完整的成績管理解決方案。

### 主要功能
- 📊 成績統計分析與視覺化
- 👥 學生成績管理與編輯
- ⚠️ 風險學生自動識別
- 📈 成績分佈圖表展示
- 📥 批量成績數據匯入
- 📄 自訂報告匯出
- 💾 自動備份策略
- 🔧 自訂評分方案與調整規則

## 目錄結構

```
GradeInsight_BDD/
├── backend/                    # FastAPI 後端
│   ├── main.py                # API 路由定義
│   ├── models.py              # Pydantic 數據模型
│   └── services.py            # 業務邏輯服務
├── frontend/                   # Streamlit 前端
│   └── streamlit_app.py       # 網頁介面應用
├── requirements/               # 需求文件
├── requirements.txt            # Python 依賴套件
└── README.md                   # 專案說明文檔
```

## 環境需求

- **Python**: 3.10+
- **作業系統**: Linux/macOS/Windows
- **環境**: GitHub Codespaces（已預配置）

## 安裝步驟

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd GradeInsight_BDD
   ```

2. **建立與啟動 Python 虛擬環境**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

4. **確認安裝**
   ```bash
   python --version  # 應為 3.10+
   ```

## 啟動方式

系統包含後端 API 和前端介面，需要分開啟動。

### 啟動後端 API

請從專案根目錄執行：
```bash
cd /workspaces/GradeInsight_BDD
source .venv/bin/activate
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

請勿直接在 `backend/` 目錄下執行 `uvicorn main:app`，這會導致相對匯入失敗。

如果出現 `uvicorn: command not found`，請確認已先執行 `source .venv/bin/activate`，或執行 `pip install -r requirements.txt`。

啟動成功後，訪問：http://localhost:8000/docs 查看 API 文檔。

### 啟動前端介面

開啟新的終端機視窗，執行：
```bash
cd /workspaces/GradeInsight_BDD
source .venv/bin/activate
cd frontend
python -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

如果出現 `streamlit: command not found`，請確認已啟動虛擬環境並安裝依賴。

啟動成功後，訪問：http://localhost:8501 使用系統。

## 使用說明

1. **首次使用**: 系統會自動生成 30 筆模擬學生數據
2. **功能導航**: 使用左側選單切換不同功能模組
3. **數據操作**: 支持成績匯入、編輯、統計分析等操作
4. **視覺化**: 提供多種圖表展示成績分佈和統計信息

## 常見問題排除 (Troubleshooting)

### 後端啟動失敗
- **問題**: `ModuleNotFoundError`
- **解決**: 確保已安裝所有依賴套件 `pip install -r requirements.txt`

- **問題**: 端口 8000 被佔用
- **解決**: 更換端口 `uvicorn main:app --port 8001`

### 前端啟動失敗
- **問題**: 無法連接到後端
- **解決**: 確保後端已啟動並運行在 http://localhost:8000

- **問題**: Streamlit 版本衝突
- **解決**: 更新 Streamlit `pip install --upgrade streamlit`

### 數據相關問題
- **問題**: 匯入檔案失敗
- **解決**: 檢查 CSV/Excel 檔案格式，確保包含必要欄位：name, student_id, usual, midterm, final

- **問題**: 圖表顯示異常
- **解決**: 重新生成模擬數據或檢查數據完整性

### 其他問題
- **問題**: 記憶體不足
- **解決**: 減少模擬數據量或重啟 Codespaces 環境

- **問題**: 中文顯示亂碼
- **解決**: 確保系統編碼為 UTF-8，檔案以 UTF-8 格式保存

## 開發者資訊

- **架構**: 職責分離設計，後端處理業務邏輯，前端負責介面展示
- **API**: RESTful 設計，完整 OpenAPI 文檔
- **數據**: 內存存儲（開發環境），生產環境建議使用資料庫
- **安全性**: 基本錯誤處理，生產環境需增加認證和加密

## 授權

本專案僅供學習和演示使用。

---

如有問題或建議，請聯繫開發團隊。