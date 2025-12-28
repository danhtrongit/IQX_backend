"""Trading flow tests with mock price provider.

This module tests the full trading flow including:
- Market buy orders
- Market sell orders
- Limit buy orders
- Limit sell orders
- Order cancellation
- Position updates
- Balance updates
- Fee calculations
"""
import pytest
from decimal import Decimal
from typing import Optional
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient


# === Mock Price Provider ===

class MockPriceProvider:
    """Mock price provider for testing."""

    def __init__(self, prices: dict[str, Decimal] = None):
        self.prices = prices or {"VNM": Decimal("85000"), "FPT": Decimal("120000")}

    async def get_price(self, symbol: str) -> Optional[Decimal]:
        return self.prices.get(symbol.upper())


# === Helper Functions ===

async def register_and_get_token(client: AsyncClient, email: str = "trader@test.com") -> str:
    """Register a user and return access token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123", "fullname": "Test Trader"},
    )
    assert response.status_code == 200, f"Registration failed: {response.json()}"
    return response.json()["tokens"]["access_token"]


def auth_headers(token: str) -> dict:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {token}"}


async def setup_trader_with_cash(client: AsyncClient, email: str) -> str:
    """Register user and grant initial cash."""
    token = await register_and_get_token(client, email)
    await client.post(
        "/api/v1/trading/bootstrap/grant-initial-cash",
        headers=auth_headers(token),
    )
    return token


# =============================================================================
# FULL TRADING FLOW TESTS WITH MOCKED PRICE
# =============================================================================

class TestMarketBuyOrderFlow:
    """Test market buy order flow."""

    @pytest.mark.asyncio
    async def test_market_buy_order_success(self, client: AsyncClient):
        """Test successful market buy order."""
        token = await setup_trader_with_cash(client, "buy_market@test.com")

        # Mock the price provider
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            mock_provider = MockPriceProvider()
            MockProvider.return_value = mock_provider

            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={
                    "symbol": "VNM",
                    "side": "BUY",
                    "type": "MARKET",
                    "quantity": "100",
                },
            )

        assert response.status_code == 200
        data = response.json()

        # Verify order response
        order = data["order"]
        assert order["symbol"] == "VNM"
        assert order["side"] == "BUY"
        assert order["type"] == "MARKET"
        assert Decimal(str(order["quantity"])) == Decimal("100")
        assert order["status"] == "FILLED"  # Market orders fill immediately
        assert Decimal(str(order["filled_quantity"])) == Decimal("100")

        # Verify fee calculation (0.1%)
        price = Decimal("85000")
        expected_fee = Decimal("100") * price * Decimal("0.001")
        assert Decimal(str(order["fee_total"])) == expected_fee

        # Verify wallet update
        wallet = data["wallet"]
        initial_balance = Decimal("1000000000")
        total_cost = Decimal("100") * price + expected_fee
        expected_balance = initial_balance - total_cost
        assert Decimal(str(wallet["balance"])) == expected_balance

    @pytest.mark.asyncio
    async def test_market_buy_creates_position(self, client: AsyncClient):
        """Test that market buy creates a position."""
        token = await setup_trader_with_cash(client, "buy_pos@test.com")

        # Check positions before
        response = await client.get(
            "/api/v1/trading/positions",
            headers=auth_headers(token),
        )
        assert response.json()["data"] == []

        # Place buy order with mock
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={
                    "symbol": "VNM",
                    "side": "BUY",
                    "type": "MARKET",
                    "quantity": "100",
                },
            )

        # Check positions after
        response = await client.get(
            "/api/v1/trading/positions",
            headers=auth_headers(token),
        )
        positions = response.json()["data"]
        assert len(positions) == 1
        assert positions[0]["symbol"] == "VNM"
        assert Decimal(str(positions[0]["quantity"])) == Decimal("100")

    @pytest.mark.asyncio
    async def test_market_buy_creates_trade(self, client: AsyncClient):
        """Test that market buy creates a trade record."""
        token = await setup_trader_with_cash(client, "buy_trade@test.com")

        # Place buy order with mock
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={
                    "symbol": "VNM",
                    "side": "BUY",
                    "type": "MARKET",
                    "quantity": "100",
                },
            )

        # Check trades
        response = await client.get(
            "/api/v1/trading/trades",
            headers=auth_headers(token),
        )
        trades = response.json()["data"]
        assert len(trades) >= 1

        trade = trades[0]
        assert trade["symbol"] == "VNM"
        assert trade["side"] == "BUY"
        assert Decimal(str(trade["quantity"])) == Decimal("100")

    @pytest.mark.asyncio
    async def test_market_buy_creates_ledger_entries(self, client: AsyncClient):
        """Test that market buy creates ledger entries for audit trail."""
        token = await setup_trader_with_cash(client, "buy_ledger@test.com")

        # Place buy order with mock
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={
                    "symbol": "VNM",
                    "side": "BUY",
                    "type": "MARKET",
                    "quantity": "100",
                },
            )

        # Check ledger
        response = await client.get(
            "/api/v1/trading/ledger",
            headers=auth_headers(token),
        )
        entries = response.json()["data"]

        # Should have GRANT, LOCK, BUY, FEE entries (at least)
        entry_types = [e["entry_type"] for e in entries]
        assert "GRANT" in entry_types
        assert "BUY" in entry_types
        assert "FEE" in entry_types


class TestMarketSellOrderFlow:
    """Test market sell order flow."""

    @pytest.mark.asyncio
    async def test_market_sell_order_success(self, client: AsyncClient):
        """Test successful market sell order."""
        token = await setup_trader_with_cash(client, "sell_market@test.com")

        # First buy some shares
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        # Get balance after buy
        wallet_response = await client.get(
            "/api/v1/trading/wallet",
            headers=auth_headers(token),
        )
        balance_after_buy = Decimal(str(wallet_response.json()["balance"]))

        # Now sell
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "SELL", "type": "MARKET", "quantity": "50"},
            )

        assert response.status_code == 200
        data = response.json()

        # Verify order
        order = data["order"]
        assert order["side"] == "SELL"
        assert order["status"] == "FILLED"
        assert Decimal(str(order["filled_quantity"])) == Decimal("50")

        # Verify balance increased
        new_balance = Decimal(str(data["wallet"]["balance"]))
        assert new_balance > balance_after_buy

    @pytest.mark.asyncio
    async def test_market_sell_reduces_position(self, client: AsyncClient):
        """Test that market sell reduces position."""
        token = await setup_trader_with_cash(client, "sell_pos@test.com")

        # Buy first
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        # Sell partial
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "SELL", "type": "MARKET", "quantity": "30"},
            )

        # Check position
        response = await client.get(
            "/api/v1/trading/positions",
            headers=auth_headers(token),
        )
        positions = response.json()["data"]
        assert len(positions) == 1
        assert Decimal(str(positions[0]["quantity"])) == Decimal("70")


class TestLimitOrderFlow:
    """Test limit order flow."""

    @pytest.mark.asyncio
    async def test_limit_buy_order_fills_when_price_favorable(self, client: AsyncClient):
        """Test limit buy order fills when market price is at or below limit."""
        token = await setup_trader_with_cash(client, "limit_buy@test.com")

        # Limit price above market price - should fill immediately
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("80000")})
            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={
                    "symbol": "VNM",
                    "side": "BUY",
                    "type": "LIMIT",
                    "quantity": "100",
                    "limit_price": "85000",  # Above market price of 80000
                },
            )

        assert response.status_code == 200
        order = response.json()["order"]
        assert order["status"] == "FILLED"

    @pytest.mark.asyncio
    async def test_limit_buy_order_pending_when_price_unfavorable(self, client: AsyncClient):
        """Test limit buy order stays pending when market price is above limit."""
        token = await setup_trader_with_cash(client, "limit_pend@test.com")

        # Limit price below market price - should not fill
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("90000")})
            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={
                    "symbol": "VNM",
                    "side": "BUY",
                    "type": "LIMIT",
                    "quantity": "100",
                    "limit_price": "80000",  # Below market price of 90000
                },
            )

        assert response.status_code == 200
        order = response.json()["order"]
        assert order["status"] == "NEW"  # Not filled

    @pytest.mark.asyncio
    async def test_limit_sell_order_fills_when_price_favorable(self, client: AsyncClient):
        """Test limit sell order fills when market price is at or above limit."""
        token = await setup_trader_with_cash(client, "limit_sell@test.com")

        # Buy first
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        # Sell with limit at or below market - should fill
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("90000")})
            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={
                    "symbol": "VNM",
                    "side": "SELL",
                    "type": "LIMIT",
                    "quantity": "50",
                    "limit_price": "85000",  # Below market price of 90000
                },
            )

        assert response.status_code == 200
        order = response.json()["order"]
        assert order["status"] == "FILLED"


class TestOrderCancellation:
    """Test order cancellation."""

    @pytest.mark.asyncio
    async def test_cancel_pending_buy_order(self, client: AsyncClient):
        """Test canceling a pending buy order releases locked funds."""
        token = await setup_trader_with_cash(client, "cancel_buy@test.com")

        # Place limit order that won't fill
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("100000")})
            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={
                    "symbol": "VNM",
                    "side": "BUY",
                    "type": "LIMIT",
                    "quantity": "100",
                    "limit_price": "80000",  # Below market, won't fill
                },
            )

        order_id = response.json()["order"]["id"]
        locked_before = Decimal(str(response.json()["wallet"]["locked"]))
        assert locked_before > 0

        # Cancel the order
        cancel_response = await client.post(
            f"/api/v1/trading/orders/{order_id}/cancel",
            headers=auth_headers(token),
        )

        assert cancel_response.status_code == 200
        data = cancel_response.json()

        # Verify order is canceled
        assert data["order"]["status"] == "CANCELED"
        assert data["order"]["canceled_at"] is not None

        # Verify locked funds released
        assert Decimal(str(data["wallet"]["locked"])) < locked_before

    @pytest.mark.asyncio
    async def test_cancel_pending_sell_order(self, client: AsyncClient):
        """Test canceling a pending sell order releases locked shares."""
        token = await setup_trader_with_cash(client, "cancel_sell@test.com")

        # Buy shares first
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        # Place sell limit order that won't fill
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("80000")})
            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={
                    "symbol": "VNM",
                    "side": "SELL",
                    "type": "LIMIT",
                    "quantity": "50",
                    "limit_price": "100000",  # Above market, won't fill
                },
            )

        order_id = response.json()["order"]["id"]

        # Check locked quantity before cancel
        pos_response = await client.get(
            "/api/v1/trading/positions",
            headers=auth_headers(token),
        )
        locked_before = Decimal(str(pos_response.json()["data"][0]["locked_quantity"]))
        assert locked_before == Decimal("50")

        # Cancel the order
        await client.post(
            f"/api/v1/trading/orders/{order_id}/cancel",
            headers=auth_headers(token),
        )

        # Check locked quantity after cancel
        pos_response = await client.get(
            "/api/v1/trading/positions",
            headers=auth_headers(token),
        )
        locked_after = Decimal(str(pos_response.json()["data"][0]["locked_quantity"]))
        assert locked_after == Decimal("0")

    @pytest.mark.asyncio
    async def test_cannot_cancel_filled_order(self, client: AsyncClient):
        """Test that filled orders cannot be canceled."""
        token = await setup_trader_with_cash(client, "cancel_filled@test.com")

        # Place market order that fills immediately
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider()
            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        order_id = response.json()["order"]["id"]
        assert response.json()["order"]["status"] == "FILLED"

        # Try to cancel
        cancel_response = await client.post(
            f"/api/v1/trading/orders/{order_id}/cancel",
            headers=auth_headers(token),
        )

        assert cancel_response.status_code == 400
        assert cancel_response.json()["error"]["code"] == "ORDER_NOT_CANCELABLE"


class TestFeeCalculation:
    """Test fee calculations."""

    @pytest.mark.asyncio
    async def test_buy_fee_calculation(self, client: AsyncClient):
        """Test 0.1% fee on buy orders."""
        token = await setup_trader_with_cash(client, "fee_buy@test.com")

        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("100000")})
            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        order = response.json()["order"]
        # 100 shares * 100000 VND * 0.1% = 10000 VND
        expected_fee = Decimal("100") * Decimal("100000") * Decimal("0.001")
        assert Decimal(str(order["fee_total"])) == expected_fee

    @pytest.mark.asyncio
    async def test_sell_fee_calculation(self, client: AsyncClient):
        """Test 0.1% fee on sell orders."""
        token = await setup_trader_with_cash(client, "fee_sell@test.com")

        # Buy first
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("100000")})
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        # Sell
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("110000")})
            response = await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "SELL", "type": "MARKET", "quantity": "50"},
            )

        order = response.json()["order"]
        # 50 shares * 110000 VND * 0.1% = 5500 VND
        expected_fee = Decimal("50") * Decimal("110000") * Decimal("0.001")
        assert Decimal(str(order["fee_total"])) == expected_fee


class TestPositionAveragePriceCalculation:
    """Test position average price calculation."""

    @pytest.mark.asyncio
    async def test_multiple_buys_update_avg_price(self, client: AsyncClient):
        """Test that multiple buys correctly update average price."""
        token = await setup_trader_with_cash(client, "avg_price@test.com")

        # First buy at 80000
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("80000")})
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        # Second buy at 100000
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider({"VNM": Decimal("100000")})
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        # Check average price
        response = await client.get(
            "/api/v1/trading/positions",
            headers=auth_headers(token),
        )
        position = response.json()["data"][0]

        # (100 * 80000 + 100 * 100000) / 200 = 90000
        assert Decimal(str(position["quantity"])) == Decimal("200")
        assert Decimal(str(position["avg_price"])) == Decimal("90000")


class TestMultipleSymbolTrading:
    """Test trading multiple symbols."""

    @pytest.mark.asyncio
    async def test_trade_multiple_symbols(self, client: AsyncClient):
        """Test trading different symbols creates separate positions."""
        token = await setup_trader_with_cash(client, "multi_sym@test.com")

        prices = {"VNM": Decimal("85000"), "FPT": Decimal("120000")}

        # Buy VNM
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider(prices)
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "VNM", "side": "BUY", "type": "MARKET", "quantity": "100"},
            )

        # Buy FPT
        with patch(
            "app.presentation.api.v1.endpoints.trading.VnstockMarketPriceProvider"
        ) as MockProvider:
            MockProvider.return_value = MockPriceProvider(prices)
            await client.post(
                "/api/v1/trading/orders",
                headers=auth_headers(token),
                json={"symbol": "FPT", "side": "BUY", "type": "MARKET", "quantity": "50"},
            )

        # Check positions
        response = await client.get(
            "/api/v1/trading/positions",
            headers=auth_headers(token),
        )
        positions = response.json()["data"]
        assert len(positions) == 2

        symbols = [p["symbol"] for p in positions]
        assert "VNM" in symbols
        assert "FPT" in symbols
