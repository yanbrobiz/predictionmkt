# API 設定指南

本指南說明如何為每個預測市場平台設定 API 訪問。

## 平台 API 需求總覽

| 平台 | 需要 API Key | 狀態 | 備註 |
|------|-------------|------|------|
| Polymarket | ❌ 不需要 | ✅ 可用 | 公開 API，無需認證 |
| Limitless | ❌ 不需要 | ✅ 可用 | 公開 API，無需認證 |
| Opinion Labs | ✅ **需要** | ✅ 可用 | 需要 API key 認證 |
| Drift BET | ❌ 不需要 | ✅ 可用 | 公開 Data API，無需認證 |
| Kalshi | ❌ 不需要 | ✅ 可用 | 公開 API，無需認證 |
| Myriad | ❌ 無公開 API | ❌ 不可用 | 僅支援 SDK/智能合約整合 |

## 1. Polymarket API

**無需設定** - Polymarket 提供公開的 REST API。

- **API 文檔**: https://docs.polymarket.com/
- **Base URL**: https://gamma-api.polymarket.com
- **特點**: 流動性最高，市場數量最多

## 2. Limitless API

**無需設定** - Limitless 提供公開的 REST API。

- **API 文檔**: https://api.limitless.exchange/api-v1
- **Base URL**: https://api.limitless.exchange
- **特點**: Base 鏈生態，專注加密貨幣預測市場

## 3. Opinion Labs API ⚠️ 需要 API Key

### 如何獲取 API Key：

#### 步驟 1: 訪問 Opinion Trade
前往 [https://opinion.trade](https://opinion.trade)

#### 步驟 2: 連接錢包
- 點擊右上角的 "Connect Wallet"
- 選擇你的錢包（MetaMask、WalletConnect 等）
- 授權連接

#### 步驟 3: 生成 API Key
1. 登入後，點擊右上角的個人檔案/設定圖標
2. 尋找 "Developer" 或 "API" 選項
3. 點擊 "Generate API Key" 或 "Create New Key"
4. 複製生成的 API key（**只會顯示一次，請妥善保存**）

#### 步驟 4: 配置到 .env
在 `.env` 文件中添加：
```env
OPINION_LABS_API_KEY=你的_api_key_這裡
```

### API 資訊：
- **API 文檔**: https://docs.opinion.trade/developer-guide/opinion-open-api/overview
- **Base URL**: https://openapi.opinion.trade
- **認證方式**: API key 通過 HTTP header `apikey` 傳遞
- **特點**: 多鏈支持，專注宏觀經濟與金融數據

### 測試 Opinion Labs API：
```bash
python test_opinion.py
```

### 常見問題：

**Q: 沒有 Opinion Labs API key 可以運行監測系統嗎？**
A: 可以！系統會自動跳過 Opinion Labs，只監測其他平台（Polymarket、Limitless）。

**Q: API key 有使用限制嗎？**
A: 建議查看 Opinion Labs 官方文檔了解 rate limit 限制。

**Q: API key 安全嗎？**
A:
- ✅ **DO**: 將 API key 存放在 `.env` 文件中（已加入 .gitignore）
- ✅ **DO**: 定期輪換 API key
- ❌ **DON'T**: 將 API key 提交到 git 倉庫
- ❌ **DON'T**: 公開分享你的 API key

## 4. Drift BET API

**無需設定** - Drift BET 提供公開的 Data API。

- **Base URL**: https://data.api.drift.trade
- **API Playground**: https://data.api.drift.trade/playground/
- **端點**: `/contracts`（過濾 ticker 結尾為 `-BET` 的預測市場）
- **特點**: Solana 上首個資本效率預測市場，支持多種代幣

### 測試 Drift BET API：
```bash
python test_drift.py
```

## 5. Kalshi API

**無需設定** - Kalshi 提供公開的 REST API。

- **Base URL**: https://api.elections.kalshi.com
- **端點**: `/trade-api/v2/markets`
- **特點**: 美國 CFTC 監管的預測市場，涵蓋政治、經濟、體育等

### 測試 Kalshi API：
```bash
python test_kalshi.py
```

## 6. Myriad ❌

狀態：**無公開 API**

Myriad 是 Abstract/EVM 上的預測市場，但**不提供公開 REST API**。
它僅支援 SDK 和智能合約整合，需要直接與鏈上合約互動。

> ⚠️ 目前本系統無法整合 Myriad，已自動略過此平台。

## 快速開始（無需任何 API key）

如果你想立即開始，可以只使用 Polymarket 和 Limitless：

1. 配置 Telegram Bot（必需）
2. 不設定 Opinion Labs API key
3. 運行系統：
   ```bash
   python main.py
   ```

系統會自動監測 Polymarket 和 Limitless 兩個平台的套利機會！

## 支援

如有問題，請參考：
- [Polymarket 文檔](https://docs.polymarket.com/)
- [Limitless 文檔](https://api.limitless.exchange/api-v1)
- [Opinion Labs 文檔](https://docs.opinion.trade/)
