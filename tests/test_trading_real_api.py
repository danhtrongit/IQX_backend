"""Real API Trading Tests.

These tests run against the actual API with real market data.
They require a running server and real database connection.

Usage:
    # Start the server first
    uvicorn app.main:app --reload

    # Run these tests
    pytest tests/test_trading_real_api.py -v -s
"""
import pytest
import httpx
from decimal import Decimal
import time
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


def to_decimal(value) -> Decimal:
    """Convert value to Decimal safely."""
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def format_vnd(value) -> str:
    """Format value as VND."""
    return f"{to_decimal(value):,.0f}"


# === Fixtures ===

@pytest.fixture(scope="module")
def test_user_email():
    """Generate unique test user email."""
    return f"test_trader_{uuid.uuid4().hex[:8]}@test.com"


@pytest.fixture(scope="module")
def http_client():
    """Create HTTP client for API calls."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="module")
def auth_token(http_client, test_user_email):
    """Register user and get auth token."""
    response = http_client.post(
        f"{API_V1}/auth/register",
        json={
            "email": test_user_email,
            "password": "TestPassword123",
            "fullname": "Real API Tester",
        },
    )

    if response.status_code == 409:
        # User exists, login instead
        response = http_client.post(
            f"{API_V1}/auth/login",
            json={
                "email": test_user_email,
                "password": "TestPassword123",
            },
        )

    assert response.status_code == 200, f"Auth failed: {response.text}"
    return response.json()["tokens"]["access_token"]


@pytest.fixture(scope="module")
def headers(auth_token):
    """Auth headers."""
    return {"Authorization": f"Bearer {auth_token}"}


# =============================================================================
# WALLET TESTS
# =============================================================================

class TestRealWalletAPI:
    """Test wallet with real API."""

    def test_get_wallet(self, http_client, headers):
        """Test getting wallet."""
        response = http_client.get(f"{API_V1}/trading/wallet", headers=headers)

        assert response.status_code == 200
        data = response.json()

        print(f"\n=== Wallet ===")
        print(f"Balance: {format_vnd(data['balance'])} VND")
        print(f"Locked: {format_vnd(data['locked'])} VND")
        print(f"Available: {format_vnd(data['available'])} VND")
        print(f"Currency: {data['currency']}")

        assert "balance" in data
        assert "locked" in data
        assert "available" in data
        assert data["currency"] == "VND"

    def test_grant_initial_cash(self, http_client, headers):
        """Test granting initial cash."""
        response = http_client.post(
            f"{API_V1}/trading/bootstrap/grant-initial-cash",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()

        print(f"\n=== Grant Cash ===")
        print(f"Granted: {data['granted']}")
        print(f"Message: {data['message']}")
        print(f"Balance: {format_vnd(data['wallet']['balance'])} VND")

        # Either granted for first time or already granted
        assert "wallet" in data
        assert to_decimal(data["wallet"]["balance"]) >= Decimal("0")


# =============================================================================
# POSITIONS TESTS
# =============================================================================

class TestRealPositionsAPI:
    """Test positions with real API."""

    def test_get_positions(self, http_client, headers):
        """Test getting positions."""
        response = http_client.get(f"{API_V1}/trading/positions", headers=headers)

        assert response.status_code == 200
        data = response.json()

        print(f"\n=== Positions ===")
        print(f"Total positions: {len(data['data'])}")

        for pos in data["data"]:
            print(f"\n  Symbol: {pos['symbol']}")
            print(f"  Quantity: {pos['quantity']}")
            print(f"  Avg Price: {format_vnd(pos['avg_price'])}")
            print(f"  Market Price: {format_vnd(pos.get('market_price')) if pos.get('market_price') else 'N/A'}")
            print(f"  Unrealized P&L: {format_vnd(pos.get('unrealized_pnl')) if pos.get('unrealized_pnl') else 'N/A'}")

        if data["total_market_value"]:
            print(f"\nTotal Market Value: {format_vnd(data['total_market_value'])} VND")

        assert "data" in data


# =============================================================================
# ORDERS TESTS
# =============================================================================

class TestRealOrdersAPI:
    """Test orders with real API."""

    def test_get_orders(self, http_client, headers):
        """Test getting order history."""
        response = http_client.get(
            f"{API_V1}/trading/orders",
            headers=headers,
            params={"limit": 10},
        )

        assert response.status_code == 200
        data = response.json()

        print(f"\n=== Orders ===")
        print(f"Total orders: {data['count']}")

        for order in data["data"][:5]:  # Show first 5
            print(f"\n  ID: {order['id']}")
            print(f"  Symbol: {order['symbol']}")
            print(f"  Side: {order['side']}")
            print(f"  Type: {order['type']}")
            print(f"  Quantity: {order['quantity']}")
            print(f"  Status: {order['status']}")
            print(f"  Filled: {order['filled_quantity']}")

        assert "data" in data
        assert "count" in data

    def test_place_limit_buy_order_vnm(self, http_client, headers):
        """Test placing a limit buy order for VNM at low price (won't fill)."""
        # First check balance
        wallet_response = http_client.get(f"{API_V1}/trading/wallet", headers=headers)
        balance = Decimal(str(wallet_response.json()["available"]))

        if balance < Decimal("1000000"):
            pytest.skip("Insufficient balance for order test")

        # Place order at very low price so it won't fill
        response = http_client.post(
            f"{API_V1}/trading/orders",
            headers=headers,
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "10",
                "limit_price": "50000",  # Very low price
                "client_order_id": f"test-{uuid.uuid4().hex[:8]}",
            },
        )

        print(f"\n=== Place Limit Buy Order ===")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            order = data["order"]
            print(f"Order ID: {order['id']}")
            print(f"Symbol: {order['symbol']}")
            print(f"Status: {order['status']}")
            print(f"Limit Price: {format_vnd(order['limit_price'])}")
            print(f"Price Snapshot: {format_vnd(order['price_snapshot'])}")

            # Store order_id for cancel test
            pytest.order_id_to_cancel = order["id"]

            assert order["symbol"] == "VNM"
            assert order["side"] == "BUY"
            assert order["type"] == "LIMIT"
        else:
            print(f"Error: {response.text}")
            # Market price not found is expected outside trading hours
            error = response.json().get("error", {})
            if error.get("code") == "MARKET_PRICE_NOT_FOUND":
                pytest.skip("Market price not available (outside trading hours)")

    def test_cancel_pending_order(self, http_client, headers):
        """Test canceling a pending order."""
        order_id = getattr(pytest, "order_id_to_cancel", None)

        if not order_id:
            pytest.skip("No pending order to cancel")

        response = http_client.post(
            f"{API_V1}/trading/orders/{order_id}/cancel",
            headers=headers,
        )

        print(f"\n=== Cancel Order ===")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Order Status: {data['order']['status']}")
            print(f"Canceled At: {data['order']['canceled_at']}")
            assert data["order"]["status"] == "CANCELED"
        else:
            print(f"Response: {response.text}")

    def test_place_market_buy_order_fpt(self, http_client, headers):
        """Test placing a market buy order for FPT (will fill immediately)."""
        # Check balance
        wallet_response = http_client.get(f"{API_V1}/trading/wallet", headers=headers)
        balance = Decimal(str(wallet_response.json()["available"]))

        if balance < Decimal("50000000"):  # Need at least 50M for FPT
            pytest.skip("Insufficient balance for market order")

        response = http_client.post(
            f"{API_V1}/trading/orders",
            headers=headers,
            json={
                "symbol": "FPT",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "10",
            },
        )

        print(f"\n=== Place Market Buy Order FPT ===")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            order = data["order"]
            print(f"Order ID: {order['id']}")
            print(f"Symbol: {order['symbol']}")
            print(f"Status: {order['status']}")
            print(f"Filled Qty: {order['filled_quantity']}")
            print(f"Avg Price: {format_vnd(order['avg_filled_price'])}")
            print(f"Fee: {format_vnd(order['fee_total'])}")

            print(f"\nWallet After:")
            print(f"  Balance: {format_vnd(data['wallet']['balance'])}")
            print(f"  Available: {format_vnd(data['wallet']['available'])}")

            assert order["status"] == "FILLED"
            assert Decimal(str(order["filled_quantity"])) == Decimal("10")
        else:
            print(f"Error: {response.text}")
            error = response.json().get("error", {})
            if error.get("code") == "MARKET_PRICE_NOT_FOUND":
                pytest.skip("Market price not available")


# =============================================================================
# TRADES TESTS
# =============================================================================

class TestRealTradesAPI:
    """Test trades with real API."""

    def test_get_trades(self, http_client, headers):
        """Test getting trade history."""
        response = http_client.get(
            f"{API_V1}/trading/trades",
            headers=headers,
            params={"limit": 10},
        )

        assert response.status_code == 200
        data = response.json()

        print(f"\n=== Trades ===")
        print(f"Total trades: {data['count']}")

        for trade in data["data"][:5]:
            print(f"\n  Trade ID: {trade['id']}")
            print(f"  Order ID: {trade['order_id']}")
            print(f"  Symbol: {trade['symbol']}")
            print(f"  Side: {trade['side']}")
            print(f"  Quantity: {trade['quantity']}")
            print(f"  Price: {format_vnd(trade['price'])}")
            print(f"  Fee: {format_vnd(trade['fee'])}")
            print(f"  Value: {format_vnd(trade['value'])}")

        assert "data" in data


# =============================================================================
# LEDGER TESTS
# =============================================================================

class TestRealLedgerAPI:
    """Test ledger with real API."""

    def test_get_ledger(self, http_client, headers):
        """Test getting ledger entries."""
        response = http_client.get(
            f"{API_V1}/trading/ledger",
            headers=headers,
            params={"limit": 20},
        )

        assert response.status_code == 200
        data = response.json()

        print(f"\n=== Ledger ===")
        print(f"Total entries: {data['count']}")

        for entry in data["data"][:10]:
            print(f"\n  ID: {entry['id']}")
            print(f"  Type: {entry['entry_type']}")
            print(f"  Amount: {format_vnd(entry['amount'])}")
            print(f"  Balance After: {format_vnd(entry['balance_after'])}")
            if entry.get("ref_type"):
                print(f"  Ref: {entry['ref_type']} #{entry.get('ref_id', 'N/A')}")

        assert "data" in data

    def test_get_ledger_by_type(self, http_client, headers):
        """Test filtering ledger by entry type."""
        for entry_type in ["GRANT", "BUY", "SELL", "FEE"]:
            response = http_client.get(
                f"{API_V1}/trading/ledger",
                headers=headers,
                params={"entry_type": entry_type, "limit": 5},
            )

            assert response.status_code == 200
            data = response.json()

            print(f"\n=== Ledger ({entry_type}) ===")
            print(f"Count: {data['count']}")

            for entry in data["data"]:
                assert entry["entry_type"] == entry_type


# =============================================================================
# FULL TRADING FLOW TEST
# =============================================================================

class TestRealTradingFlow:
    """Test complete trading flow with real API."""

    def test_complete_buy_sell_flow(self, http_client, headers):
        """Test complete buy and sell flow."""
        print("\n" + "=" * 60)
        print("COMPLETE TRADING FLOW TEST")
        print("=" * 60)

        # 1. Check initial wallet
        response = http_client.get(f"{API_V1}/trading/wallet", headers=headers)
        initial_balance = to_decimal(response.json()["available"])
        print(f"\n1. Initial Balance: {format_vnd(initial_balance)} VND")

        if initial_balance < Decimal("10000000"):
            pytest.skip("Insufficient balance for trading flow test")

        # 2. Check initial positions for VNM
        response = http_client.get(f"{API_V1}/trading/positions", headers=headers)
        positions = {p["symbol"]: p for p in response.json()["data"]}
        initial_vnm_qty = to_decimal(positions.get("VNM", {}).get("quantity", "0"))
        print(f"2. Initial VNM Position: {initial_vnm_qty}")

        # 3. Place market buy order
        print("\n3. Placing MARKET BUY order for VNM...")
        buy_response = http_client.post(
            f"{API_V1}/trading/orders",
            headers=headers,
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "100",
            },
        )

        if buy_response.status_code != 200:
            error = buy_response.json().get("error", {})
            if error.get("code") == "MARKET_PRICE_NOT_FOUND":
                pytest.skip("Market price not available (outside trading hours)")
            else:
                pytest.fail(f"Buy order failed: {buy_response.text}")

        buy_data = buy_response.json()
        buy_order = buy_data["order"]
        print(f"   Order ID: {buy_order['id']}")
        print(f"   Status: {buy_order['status']}")
        print(f"   Filled: {buy_order['filled_quantity']} @ {format_vnd(buy_order['avg_filled_price'])}")
        print(f"   Fee: {format_vnd(buy_order['fee_total'])}")

        balance_after_buy = to_decimal(buy_data["wallet"]["balance"])
        print(f"   Balance After: {format_vnd(balance_after_buy)} VND")

        assert buy_order["status"] == "FILLED"

        # 4. Check position updated
        response = http_client.get(f"{API_V1}/trading/positions", headers=headers)
        positions = {p["symbol"]: p for p in response.json()["data"]}
        vnm_position = positions.get("VNM", {})
        print(f"\n4. VNM Position After Buy:")
        print(f"   Quantity: {vnm_position.get('quantity')}")
        print(f"   Avg Price: {format_vnd(vnm_position.get('avg_price'))}")

        # 5. Place market sell order
        print("\n5. Placing MARKET SELL order for VNM...")
        sell_response = http_client.post(
            f"{API_V1}/trading/orders",
            headers=headers,
            json={
                "symbol": "VNM",
                "side": "SELL",
                "type": "MARKET",
                "quantity": "50",  # Sell half
            },
        )

        assert sell_response.status_code == 200
        sell_data = sell_response.json()
        sell_order = sell_data["order"]
        print(f"   Order ID: {sell_order['id']}")
        print(f"   Status: {sell_order['status']}")
        print(f"   Filled: {sell_order['filled_quantity']} @ {format_vnd(sell_order['avg_filled_price'])}")
        print(f"   Fee: {format_vnd(sell_order['fee_total'])}")

        balance_after_sell = to_decimal(sell_data["wallet"]["balance"])
        print(f"   Balance After: {format_vnd(balance_after_sell)} VND")

        assert sell_order["status"] == "FILLED"

        # 6. Check final position
        response = http_client.get(f"{API_V1}/trading/positions", headers=headers)
        positions = {p["symbol"]: p for p in response.json()["data"]}
        vnm_position = positions.get("VNM", {})
        print(f"\n6. VNM Position After Sell:")
        print(f"   Quantity: {vnm_position.get('quantity')}")

        # 7. Check trades
        response = http_client.get(
            f"{API_V1}/trading/trades",
            headers=headers,
            params={"symbol": "VNM", "limit": 5},
        )
        trades = response.json()["data"]
        print(f"\n7. Recent VNM Trades: {len(trades)}")

        # 8. Check ledger
        response = http_client.get(
            f"{API_V1}/trading/ledger",
            headers=headers,
            params={"limit": 10},
        )
        entries = response.json()["data"]
        print(f"\n8. Recent Ledger Entries: {len(entries)}")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Initial Balance: {format_vnd(initial_balance)} VND")
        print(f"After Buy: {format_vnd(balance_after_buy)} VND")
        print(f"After Sell: {format_vnd(balance_after_sell)} VND")
        net_change = balance_after_sell - initial_balance
        print(f"Net Change: {format_vnd(net_change)} VND")
        print("=" * 60)


# =============================================================================
# PERFORMANCE TEST
# =============================================================================

class TestAPIPerformance:
    """Test API response times."""

    def test_wallet_response_time(self, http_client, headers):
        """Test wallet API response time."""
        start = time.time()
        response = http_client.get(f"{API_V1}/trading/wallet", headers=headers)
        elapsed = (time.time() - start) * 1000

        print(f"\nWallet API: {elapsed:.0f}ms")
        assert response.status_code == 200
        assert elapsed < 1000  # Should be under 1 second

    def test_positions_response_time(self, http_client, headers):
        """Test positions API response time (includes price fetching)."""
        start = time.time()
        response = http_client.get(f"{API_V1}/trading/positions", headers=headers)
        elapsed = (time.time() - start) * 1000

        print(f"Positions API: {elapsed:.0f}ms")
        assert response.status_code == 200
        # Positions can be slower due to price fetching
        assert elapsed < 10000  # Should be under 10 seconds

    def test_orders_response_time(self, http_client, headers):
        """Test orders API response time."""
        start = time.time()
        response = http_client.get(
            f"{API_V1}/trading/orders",
            headers=headers,
            params={"limit": 100},
        )
        elapsed = (time.time() - start) * 1000

        print(f"Orders API: {elapsed:.0f}ms")
        assert response.status_code == 200
        assert elapsed < 2000  # Should be under 2 seconds
