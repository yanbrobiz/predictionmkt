# Prediction Market Arbitrage Monitor

自動監測多個預測市場平台的套利機會，當利潤超過設定門檻時透過 Telegram 發送通知。

## 支援平台

1. **Polymarket** (Polygon) - 流動性最高、全球知名度最強
2. **Drift BET** (Solana) - 高頻交易、低延遲、支持多種資產
3. **Limitless** (Base) - Base 生態龍頭、擅長加密貨幣相關預測
4. **Kalshi** (Centralized) - CFTC 監管的美國預測市場
5. **Opinion Labs** (多鏈) - 專注宏觀經濟與金融數據
6. **Myriad** (Abstract/EVM) - ⚠️ 無公開 API，暫無法整合

## 功能特點

- 🔄 每 30 秒自動掃描所有平台
- 📊 智能匹配相似的預測市場
- 💰 自動計算套利利潤
-  **智慧類別過濾** (Sports & Crypto)
- 📱 Telegram 即時通知
- ⚡ 異步並發處理，高效快速
- 🎯 可自訂利潤門檻（預設 0.1%）

## 智慧類別過濾

為了讓監測更精準，系統內建智慧過濾器，僅關注以下兩大類別市場：

- **🏀 Sports (運動)**：NBA, NFL, F1, 足球, 網球, UFC 等賽事
- **💎 Crypto (加密貨幣)**：Bitcoin, Ethereum, Solana, DeFi, Token 價格預測

*如需修改過濾設定，請調整 `config.py` 中的 `ALLOWED_CATEGORIES`。*

## 安裝步驟

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定 Telegram Bot

1. 在 Telegram 中搜尋 [@BotFather](https://t.me/botfather)
2. 發送 `/newbot` 建立新機器人
3. 按照指示設定機器人名稱
4. 複製獲得的 Bot Token

### 3. 獲取 Chat ID

1. 在 Telegram 中搜尋 [@userinfobot](https://t.me/userinfobot)
2. 點擊 Start
3. 複製顯示的 Chat ID

或者：

1. 先啟動你的 bot，發送任意訊息給它
2. 訪問：`https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. 在返回的 JSON 中找到 `chat.id`

### 4. 獲取 Opinion Labs API Key（可選）

Opinion Labs 需要 API key 才能訪問數據：

1. 訪問 [https://opinion.trade](https://opinion.trade)
2. 連接你的錢包
3. 在設定或開發者選項中生成 API key
4. 複製 API key

**注意**：沒有 Opinion Labs API key 不影響其他平台的監控。

### 5. 配置環境變數

複製 `.env.example` 為 `.env`：

```bash
cp .env.example .env
```

編輯 `.env` 文件，填入你的配置：

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
CHECK_INTERVAL_SECONDS=30
MIN_PROFIT_THRESHOLD=2.0

# 可選：Opinion Labs API Key
OPINION_LABS_API_KEY=your_opinion_api_key_here
```

## 使用方法

### 啟動監控

```bash
python main.py
```

### 運行測試

```bash
# 測試 Limitless API
python test_limitless.py

# 測試 Opinion Labs API（需要 API key）
python test_opinion.py

# 單次掃描測試（所有平台）
python -c "import asyncio; from main import ArbitrageMonitor; asyncio.run(ArbitrageMonitor().run_once())"
```

## 通知格式

當發現套利機會時，你會收到類似以下格式的 Telegram 通知：

```
📊 套利機會 (1/1)

TRUMP-WIN-2024?

🔥 此對沖策略必勝 (Yes+No < 1)
星等：⭐⭐⭐⭐⭐
💰 利潤：5.2632%

 操作指南：
1. 在 Polymarket 買入 Yes
   價格: $0.400
2. 在 Kalshi 買入 No
   價格: $0.550

💵總成本: $0.950

💹 交易量24H：
  • Polymarket: $5.26M
  • Kalshi: $2.69M
```

## 專案結構

```
prediction-market/
├── main.py                  # 主程式入口
├── config.py               # 配置管理
├── category_filter.py      # 類別過濾邏輯 (Sports/Crypto)
├── arbitrage_detector.py   # 套利檢測邏輯
├── telegram_notifier.py    # Telegram 通知
├── requirements.txt        # Python 依賴
├── .env.example           # 環境變數範例
├── .env                   # 環境變數（不提交到 git）
└── markets/               # 市場平台整合
    ├── __init__.py
    ├── base.py           # 基礎類別
    ├── polymarket.py     # Polymarket 整合
    ├── drift_bet.py      # Drift BET 整合
    ├── limitless.py      # Limitless 整合
    ├── kalshi.py         # Kalshi 整合
    ├── myriad.py         # Myriad 整合
    └── opinion_labs.py   # Opinion Labs 整合
```

## 套利原理

系統會：

1. 同時獲取所有平台的市場數據
2. 使用文字相似度算法匹配相同的預測問題
3. 比較相同結果在不同平台的賠率
4. 計算是否存在**無風險對沖機會**（即：平台 A 買 Yes + 平台 B 買 No，總成本 < 1）
5. 過濾出利潤超過門檻的機會
6. 透過 Telegram 發送詳細操作指南

## 注意事項

⚠️ **重要提醒**

- **API Keys**: Opinion Labs 需要 API key，其他平台無需 key（詳見 `API_SETUP_GUIDE.md`）
- 套利機會可能稍縱即逝，收到通知後需快速行動
- 請考慮交易手續費、網路延遲、滑點等因素
- 建議先用小額測試
- 注意各平台的 API 請求限制
- 目前 Drift BET 和 Myriad 的 API 端點待確認

## API 狀態

| 平台 | API 狀態 | 說明 |
|-----|---------|------|
| Polymarket | ✅ 可用 | 官方公開 API（無需 API key）|
| Drift BET | ✅ 可用 | Data API（無需 API key）|
| Limitless | ✅ 可用 | 官方 API（無需 API key）|
| Kalshi | ✅ 可用 | 公開 API（無需 API key）|
| Opinion Labs | ✅ 可用 | 官方 API（**需要 API key**）|
| Myriad | ❌ 不可用 | 無公開 REST API |

## 後續優化

- [ ] 加入更多市場平台
- [ ] 實作交易執行功能
- [ ] 添加歷史數據記錄
- [ ] Web 界面監控儀表板
- [ ] 多帳號管理
- [ ] 風險評估模型

## 授權

MIT License

## 免責聲明

本工具僅供學習和研究使用。使用本工具進行交易的所有風險由使用者自行承擔。
