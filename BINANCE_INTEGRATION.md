# 🚀 Binance Integration Guide

## 📋 **OVERVIEW**

Bot trading ini sekarang mendukung **Binance Futures** sebagai exchange alternatif selain Bybit. Integrasi Binance mencakup:

- ✅ **Trading API** - Place orders, manage positions
- ✅ **Market Data** - Klines, ticker, orderbook
- ✅ **WebSocket** - Real-time data streaming
- ✅ **Health Checks** - Connection monitoring
- ✅ **Configuration** - Exchange switching

## 🔧 **SETUP BINANCE**

### **1. API Credentials**

Tambahkan ke file `.env`:

```bash
# Binance API Keys
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
BINANCE_TESTNET=true  # Set to false for mainnet

# Exchange Selection
EXCHANGE=binance  # or "bybit"
```

### **2. Install Dependencies**

```bash
pip install ccxt
```

### **3. Exchange Switching**

#### **Via Telegram Bot:**
```
/exchange binance
```

#### **Via Dashboard:**
- Navigate to Controls page
- Select "binance" from Exchange dropdown
- Save settings

#### **Via Config:**
```python
from core.config_manager import set_exchange
set_exchange("binance")
```

## 📊 **BINANCE FEATURES**

### **Trading Operations**
- ✅ Market orders
- ✅ Leverage setting
- ✅ Position management
- ✅ Balance checking
- ✅ Order cancellation

### **Market Data**
- ✅ Klines/candlesticks (1m, 3m, 5m, 15m, 30m, 1h, 4h)
- ✅ Real-time ticker
- ✅ Order book depth
- ✅ WebSocket streaming

### **Health Monitoring**
- ✅ API connectivity
- ✅ Account balance
- ✅ Open positions
- ✅ Market data availability

## 🔄 **EXCHANGE COMPARISON**

| Feature | Bybit | Binance |
|---------|-------|---------|
| **Trading** | ✅ Full | ✅ Full |
| **WebSocket** | ✅ Full | ✅ Full |
| **TP/SL** | ✅ Native | ⚠️ Manual |
| **Testnet** | ✅ Full | ✅ Full |
| **Leverage** | ✅ Up to 100x | ✅ Up to 125x |
| **Fees** | 0.01% | 0.02% |

## ⚠️ **BINANCE LIMITATIONS**

### **1. TP/SL Handling**
Binance tidak mendukung TP/SL dalam single order seperti Bybit. Bot akan:
- Place market order
- Set TP/SL sebagai separate orders (manual implementation needed)

### **2. Order Types**
- ✅ Market orders
- ✅ Limit orders
- ❌ Stop orders (need manual implementation)

### **3. Position Management**
- ✅ Get positions
- ✅ Close positions
- ⚠️ Partial TP/SL (manual implementation)

## 🛠️ **USAGE EXAMPLES**

### **Switch to Binance**
```python
from core.config_manager import set_exchange, set_binance_testnet

# Switch to Binance testnet
set_exchange("binance")
set_binance_testnet(True)

# Switch to Binance mainnet
set_exchange("binance")
set_binance_testnet(False)
```

### **Check Binance Health**
```python
from core.binance_health import get_binance_health_summary

# Check Binance health
health = get_binance_health_summary(testnet=True)
print(f"Status: {health['overall_status']}")
```

### **Place Order on Binance**
```python
from core.trade_executor import place_order

# Place order (will use current exchange setting)
result = place_order(
    symbol="BTCUSDT",
    side="BUY",
    qty=0.001,
    tp_frac=0.02,
    sl_frac=0.01,
    leverage=10,
    trailing=0.0,
    testnet=True
)
```

## 📈 **DASHBOARD INTEGRATION**

### **Live Chart**
- Select "binance" from Exchange dropdown
- Real-time data via Binance WebSocket
- Support for multiple symbols

### **Monitoring**
- Binance-specific health checks
- Connection status monitoring
- Balance and position tracking

### **Controls**
- Exchange switching
- Testnet/mainnet toggle
- API credential validation

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **1. API Connection Failed**
```
Error: Binance client not initialized - missing API credentials
```
**Solution:** Check `BINANCE_API_KEY` and `BINANCE_API_SECRET` in `.env`

#### **2. Testnet vs Mainnet**
```
Error: Binance testnet connection failed
```
**Solution:** 
- Set `BINANCE_TESTNET=true` for testnet
- Set `BINANCE_TESTNET=false` for mainnet
- Ensure API keys match the environment

#### **3. Order Placement Failed**
```
Error: Binance order placement failed
```
**Solution:**
- Check account balance
- Verify symbol format (e.g., "BTCUSDT")
- Ensure sufficient margin

### **Debug Commands**

#### **Test Connection**
```python
from core.binance_client import get_binance_client

client = get_binance_client(testnet=True)
print(f"Connection test: {client.test_connection()}")
```

#### **Check Balance**
```python
from core.binance_client import get_binance_client

client = get_binance_client(testnet=True)
balance = client.get_account_balance()
print(f"USDT Balance: {balance.get('total', {}).get('USDT', 0)}")
```

#### **Get Positions**
```python
from core.binance_client import get_binance_client

client = get_binance_client(testnet=True)
positions = client.get_positions()
print(f"Open positions: {len(positions)}")
```

## 📚 **API REFERENCE**

### **BinanceClient Methods**

```python
# Market Data
get_klines(symbol, timeframe, limit)
get_ticker(symbol)
get_orderbook(symbol, limit)

# Trading
place_order(symbol, side, amount, price, order_type)
cancel_order(order_id, symbol)
get_open_orders(symbol)

# Account
get_account_balance()
get_positions(symbol)
set_leverage(symbol, leverage)

# Utility
test_connection()
get_market_info(symbol)
```

### **Configuration Functions**

```python
# Exchange Management
get_exchange() -> str
set_exchange(name: str)
get_exchange_config() -> dict

# Binance Specific
get_binance_testnet() -> bool
set_binance_testnet(testnet: bool)
```

## 🚀 **NEXT STEPS**

### **Planned Enhancements**
- [ ] Advanced order types (stop, trailing stop)
- [ ] Binance-specific TP/SL implementation
- [ ] Multi-exchange arbitrage
- [ ] Binance-specific risk management
- [ ] Advanced position management

### **Performance Optimization**
- [ ] Connection pooling
- [ ] Rate limiting
- [ ] Error handling improvements
- [ ] Caching mechanisms

## 📞 **SUPPORT**

Jika mengalami masalah dengan integrasi Binance:

1. **Check logs** di `logs/bot.log`
2. **Verify credentials** di `.env`
3. **Test connection** menggunakan debug commands
4. **Check health status** via dashboard

---

**Note:** Binance integration menggunakan library `ccxt` untuk kompatibilitas maksimal dengan berbagai exchange di masa depan.
