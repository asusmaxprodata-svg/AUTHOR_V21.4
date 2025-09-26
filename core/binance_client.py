# core/binance_client.py
"""
Binance Futures Trading Client
Menggunakan ccxt untuk trading dan REST API untuk data
"""
import os
import time
import ccxt
import pandas as pd
from typing import Any, Dict, List
from core.logger import get_logger

log = get_logger("binance_client")


class BinanceClient:
    """Binance Futures trading client menggunakan ccxt"""

    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.exchange = self._create_exchange()

    def _create_exchange(self) -> ccxt.binance:
        """Create Binance exchange instance"""
        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_API_SECRET", "")

        if not api_key or not api_secret:
            log.warning("Binance API credentials not found in environment")
            return None

        config = {
            "apiKey": api_key,
            "secret": api_secret,
            "sandbox": self.testnet,
            "enableRateLimit": True,
            "options": {
                "defaultType": "future",  # Use futures market
            },
        }

        if self.testnet:
            config["urls"] = {
                "api": {
                    "public": "https://testnet.binancefuture.com/fapi/v1",
                    "private": "https://testnet.binancefuture.com/fapi/v1",
                }
            }

        return ccxt.binance(config)

    def get_klines(
        self, symbol: str, timeframe: str = "5m", limit: int = 300
    ) -> pd.DataFrame:
        """Fetch klines/candlestick data"""
        if not self.exchange:
            log.error("Binance exchange not initialized")
            return pd.DataFrame()

        try:
            # Convert timeframe to ccxt format
            tf_map = {
                "1m": "1m",
                "3m": "3m",
                "5m": "5m",
                "15m": "15m",
                "30m": "30m",
                "1h": "1h",
                "4h": "4h",
                "1d": "1d",
            }
            tf = tf_map.get(timeframe, "5m")

            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, tf, limit=limit)

            if not ohlcv:
                return pd.DataFrame()

            df = pd.DataFrame(
                ohlcv,
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["start"] = df["timestamp"]
            df = df.drop("timestamp", axis=1)

            return df

        except Exception as e:
            log.error(f"Error fetching klines for {symbol}: {e}")
            return pd.DataFrame()

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker information"""
        if not self.exchange:
            return {}

        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                "symbol": symbol,
                "last": ticker.get("last", 0),
                "bid": ticker.get("bid", 0),
                "ask": ticker.get("ask", 0),
                "high": ticker.get("high", 0),
                "low": ticker.get("low", 0),
                "volume": ticker.get("baseVolume", 0),
                "change": ticker.get("change", 0),
                "percentage": ticker.get("percentage", 0),
            }
        except Exception as e:
            log.error(f"Error fetching ticker for {symbol}: {e}")
            return {}

    def get_orderbook(self, symbol: str, limit: int = 50) -> Dict[str, Any]:
        """Get order book"""
        if not self.exchange:
            return {}

        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return {
                "bids": orderbook.get("bids", []),
                "asks": orderbook.get("asks", []),
                "timestamp": orderbook.get(
                    "timestamp", int(time.time() * 1000)
                ),
            }
        except Exception as e:
            log.error(f"Error fetching orderbook for {symbol}: {e}")
            return {}

    def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        if not self.exchange:
            return {}

        try:
            balance = self.exchange.fetch_balance()
            return {
                "total": balance.get("total", {}),
                "free": balance.get("free", {}),
                "used": balance.get("used", {}),
                "info": balance.get("info", {}),
            }
        except Exception as e:
            log.error(f"Error fetching balance: {e}")
            return {}

    def get_positions(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get open positions"""
        if not self.exchange:
            return []

        try:
            positions = self.exchange.fetch_positions(
                symbols=[symbol] if symbol else None
            )
            return [
                {
                    "symbol": pos.get("symbol", ""),
                    "side": pos.get("side", ""),
                    "size": pos.get("size", 0),
                    "entryPrice": pos.get("entryPrice", 0),
                    "markPrice": pos.get("markPrice", 0),
                    "pnl": pos.get("unrealizedPnl", 0),
                    "percentage": pos.get("percentage", 0),
                    "contracts": pos.get("contracts", 0),
                    "notional": pos.get("notional", 0),
                }
                for pos in positions
                if pos.get("contracts", 0) != 0
            ]
        except Exception as e:
            log.error(f"Error fetching positions: {e}")
            return []

    def place_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float = None,
        order_type: str = "market",
        params: Dict = None,
    ) -> Dict[str, Any]:
        """Place order"""
        if not self.exchange:
            return {"error": "Exchange not initialized"}

        try:
            # Convert side to ccxt format
            side = "buy" if side.lower() == "buy" else "sell"

            # Set order type
            if order_type == "market":
                order_type = "market"
            elif order_type == "limit":
                order_type = "limit"
            else:
                order_type = "market"

            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price,
                params=params or {},
            )

            return {
                "id": order.get("id", ""),
                "symbol": order.get("symbol", ""),
                "side": order.get("side", ""),
                "amount": order.get("amount", 0),
                "price": order.get("price", 0),
                "status": order.get("status", ""),
                "filled": order.get("filled", 0),
                "remaining": order.get("remaining", 0),
                "info": order.get("info", {}),
            }

        except Exception as e:
            log.error(f"Error placing order: {e}")
            return {"error": str(e)}

    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel order"""
        if not self.exchange:
            return {"error": "Exchange not initialized"}

        try:
            result = self.exchange.cancel_order(order_id, symbol)
            return {
                "id": result.get("id", ""),
                "status": result.get("status", ""),
                "info": result.get("info", {}),
            }
        except Exception as e:
            log.error(f"Error canceling order {order_id}: {e}")
            return {"error": str(e)}

    def get_open_orders(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get open orders"""
        if not self.exchange:
            return []

        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return [
                {
                    "id": order.get("id", ""),
                    "symbol": order.get("symbol", ""),
                    "side": order.get("side", ""),
                    "amount": order.get("amount", 0),
                    "price": order.get("price", 0),
                    "status": order.get("status", ""),
                    "filled": order.get("filled", 0),
                    "remaining": order.get("remaining", 0),
                    "timestamp": order.get("timestamp", 0),
                }
                for order in orders
            ]
        except Exception as e:
            log.error(f"Error fetching open orders: {e}")
            return []

    def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """Set leverage for symbol"""
        if not self.exchange:
            return {"error": "Exchange not initialized"}

        try:
            result = self.exchange.set_leverage(leverage, symbol)
            return {"symbol": symbol, "leverage": leverage, "info": result}
        except Exception as e:
            log.error(f"Error setting leverage for {symbol}: {e}")
            return {"error": str(e)}

    def get_market_info(self, symbol: str) -> Dict[str, Any]:
        """Get market information"""
        if not self.exchange:
            return {}

        try:
            market = self.exchange.market(symbol)
            return {
                "symbol": market.get("symbol", ""),
                "base": market.get("base", ""),
                "quote": market.get("quote", ""),
                "active": market.get("active", False),
                "precision": market.get("precision", {}),
                "limits": market.get("limits", {}),
                "info": market.get("info", {}),
            }
        except Exception as e:
            log.error(f"Error fetching market info for {symbol}: {e}")
            return {}

    def test_connection(self) -> bool:
        """Test connection to Binance"""
        if not self.exchange:
            return False

        try:
            # Try to fetch server time
            self.exchange.fetch_time()
            return True
        except Exception as e:
            log.error(f"Binance connection test failed: {e}")
            return False


def get_binance_client(testnet: bool = True) -> BinanceClient:
    """Get Binance client instance"""
    return BinanceClient(testnet=testnet)
