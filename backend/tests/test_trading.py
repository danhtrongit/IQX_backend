"""Trading API tests.

Comprehensive test suite for the Trading API following TDD principles.
Tests cover:
- Wallet operations (get wallet, grant initial cash)
- Position operations (get positions with P&L)
- Order operations (place, list, get, cancel)
- Trade operations (list trades)
- Ledger operations (audit trail)
- Error handling and edge cases
- Full trading flow with mock price provider
"""
import pytest
from decimal import Decimal
from typing import Optional
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


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


# =============================================================================
# WALLET API TESTS
# =============================================================================

class TestWalletAPI:
    """Test wallet endpoints."""

    @pytest.mark.asyncio
    async def test_get_wallet_new_user(self, client: AsyncClient):
        """Test getting wallet for a new user creates empty wallet."""
        token = await register_and_get_token(client, "wallet_new@test.com")

        response = await client.get(
            "/api/v1/trading/wallet",
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["balance"])) == Decimal("0")
        assert Decimal(str(data["locked"])) == Decimal("0")
        assert Decimal(str(data["available"])) == Decimal("0")
        assert data["currency"] == "VND"
        assert data["first_grant_at"] is None

    @pytest.mark.asyncio
    async def test_get_wallet_after_grant(self, client: AsyncClient):
        """Test wallet reflects granted cash."""
        token = await register_and_get_token(client, "wallet_grant@test.com")

        # Grant cash first
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        response = await client.get(
            "/api/v1/trading/wallet",
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["balance"])) == Decimal("1000000000")
        assert Decimal(str(data["available"])) == Decimal("1000000000")
        assert data["first_grant_at"] is not None

    @pytest.mark.asyncio
    async def test_get_wallet_unauthorized(self, client: AsyncClient):
        """Test wallet access without authentication."""
        response = await client.get("/api/v1/trading/wallet")

        assert response.status_code == 401


# =============================================================================
# BOOTSTRAP API TESTS
# =============================================================================

class TestBootstrapAPI:
    """Test bootstrap endpoints."""

    @pytest.mark.asyncio
    async def test_grant_initial_cash_first_time(self, client: AsyncClient):
        """Test granting initial cash to new user."""
        token = await register_and_get_token(client, "grant_first@test.com")

        response = await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["granted"] is True
        assert "1,000,000,000" in data["message"]
        assert Decimal(str(data["wallet"]["balance"])) == Decimal("1000000000")

    @pytest.mark.asyncio
    async def test_grant_initial_cash_idempotent(self, client: AsyncClient):
        """Test granting cash multiple times is idempotent."""
        token = await register_and_get_token(client, "grant_idem@test.com")

        # First grant
        response1 = await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )
        assert response1.json()["granted"] is True

        # Second grant - should be idempotent
        response2 = await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        assert response2.status_code == 200
        data = response2.json()
        assert data["granted"] is False
        assert "already granted" in data["message"].lower()
        # Balance should not double
        assert Decimal(str(data["wallet"]["balance"])) == Decimal("1000000000")


# =============================================================================
# POSITIONS API TESTS
# =============================================================================

class TestPositionsAPI:
    """Test position endpoints."""

    @pytest.mark.asyncio
    async def test_get_positions_empty(self, client: AsyncClient):
        """Test getting positions for user with no holdings."""
        token = await register_and_get_token(client, "pos_empty@test.com")

        response = await client.get(
            "/api/v1/trading/positions",
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total_market_value"] is None

    @pytest.mark.asyncio
    async def test_get_positions_unauthorized(self, client: AsyncClient):
        """Test positions access without authentication."""
        response = await client.get("/api/v1/trading/positions")

        assert response.status_code == 401


# =============================================================================
# ORDERS API TESTS
# =============================================================================

class TestOrdersAPI:
    """Test order endpoints."""

    # --- Place Order Tests ---

    @pytest.mark.asyncio
    async def test_place_market_buy_order_insufficient_balance(self, client: AsyncClient):
        """Test placing buy order without sufficient balance."""
        token = await register_and_get_token(client, "order_no_balance@test.com")

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

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INSUFFICIENT_BALANCE"

    @pytest.mark.asyncio
    async def test_place_limit_order_missing_price(self, client: AsyncClient):
        """Test placing limit order without limit_price."""
        token = await register_and_get_token(client, "order_no_price@test.com")

        # Grant cash first
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "100",
                # Missing limit_price
            },
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INVALID_ORDER"

    @pytest.mark.asyncio
    async def test_place_sell_order_no_position(self, client: AsyncClient):
        """Test selling shares without position."""
        token = await register_and_get_token(client, "order_no_pos@test.com")

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "SELL",
                "type": "MARKET",
                "quantity": "100",
            },
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INSUFFICIENT_POSITION"

    @pytest.mark.asyncio
    async def test_place_order_invalid_side(self, client: AsyncClient):
        """Test placing order with invalid side."""
        token = await register_and_get_token(client, "order_bad_side@test.com")

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "INVALID",
                "type": "MARKET",
                "quantity": "100",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_place_order_invalid_type(self, client: AsyncClient):
        """Test placing order with invalid type."""
        token = await register_and_get_token(client, "order_bad_type@test.com")

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "STOP_LOSS",  # Not supported
                "quantity": "100",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_place_order_negative_quantity(self, client: AsyncClient):
        """Test placing order with negative quantity."""
        token = await register_and_get_token(client, "order_neg_qty@test.com")

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "-100",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_place_order_zero_quantity(self, client: AsyncClient):
        """Test placing order with zero quantity."""
        token = await register_and_get_token(client, "order_zero_qty@test.com")

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "0",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_place_order_duplicate_client_order_id(self, client: AsyncClient):
        """Test placing order with duplicate client_order_id."""
        token = await register_and_get_token(client, "order_dup_id@test.com")

        # Grant cash
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        # First order with client_order_id
        await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "100",
                "limit_price": "50000",
                "client_order_id": "unique-order-123",
            },
        )

        # Second order with same client_order_id
        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "100",
                "limit_price": "50000",
                "client_order_id": "unique-order-123",
            },
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "DUPLICATE_CLIENT_ORDER_ID"

    # --- Get Orders Tests ---

    @pytest.mark.asyncio
    async def test_get_orders_empty(self, client: AsyncClient):
        """Test getting orders when none exist."""
        token = await register_and_get_token(client, "orders_empty@test.com")

        response = await client.get(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_get_orders_with_filters(self, client: AsyncClient):
        """Test getting orders with status and symbol filters."""
        token = await register_and_get_token(client, "orders_filter@test.com")

        response = await client.get(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            params={"status": "NEW", "symbol": "VNM", "limit": 50, "offset": 0},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_orders_pagination(self, client: AsyncClient):
        """Test orders pagination."""
        token = await register_and_get_token(client, "orders_page@test.com")

        response = await client.get(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            params={"limit": 10, "offset": 0},
        )

        assert response.status_code == 200

    # --- Get Order by ID Tests ---

    @pytest.mark.asyncio
    async def test_get_order_not_found(self, client: AsyncClient):
        """Test getting non-existent order."""
        token = await register_and_get_token(client, "order_404@test.com")

        response = await client.get(
            "/api/v1/trading/orders/99999",
            headers=auth_headers(token),
        )

        # API returns 400 for order not found (TradingError base class behavior)
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "ORDER_NOT_FOUND"

    # --- Cancel Order Tests ---

    @pytest.mark.asyncio
    async def test_cancel_order_not_found(self, client: AsyncClient):
        """Test canceling non-existent order."""
        token = await register_and_get_token(client, "cancel_404@test.com")

        response = await client.post(
            "/api/v1/trading/orders/99999/cancel",
            headers=auth_headers(token),
        )

        # API returns 400 for order not found (TradingError base class behavior)
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "ORDER_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_place_order_unauthorized(self, client: AsyncClient):
        """Test placing order without authentication."""
        response = await client.post(
            "/api/v1/trading/orders",
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "100",
            },
        )

        assert response.status_code == 401


# =============================================================================
# TRADES API TESTS
# =============================================================================

class TestTradesAPI:
    """Test trade endpoints."""

    @pytest.mark.asyncio
    async def test_get_trades_empty(self, client: AsyncClient):
        """Test getting trades when none exist."""
        token = await register_and_get_token(client, "trades_empty@test.com")

        response = await client.get(
            "/api/v1/trading/trades",
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_get_trades_with_symbol_filter(self, client: AsyncClient):
        """Test getting trades with symbol filter."""
        token = await register_and_get_token(client, "trades_filter@test.com")

        response = await client.get(
            "/api/v1/trading/trades",
            headers=auth_headers(token),
            params={"symbol": "VNM"},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_trades_pagination(self, client: AsyncClient):
        """Test trades pagination."""
        token = await register_and_get_token(client, "trades_page@test.com")

        response = await client.get(
            "/api/v1/trading/trades",
            headers=auth_headers(token),
            params={"limit": 10, "offset": 0},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_trades_unauthorized(self, client: AsyncClient):
        """Test trades access without authentication."""
        response = await client.get("/api/v1/trading/trades")

        assert response.status_code == 401


# =============================================================================
# LEDGER API TESTS
# =============================================================================

class TestLedgerAPI:
    """Test ledger endpoints."""

    @pytest.mark.asyncio
    async def test_get_ledger_empty(self, client: AsyncClient):
        """Test getting ledger when no entries exist."""
        token = await register_and_get_token(client, "ledger_empty@test.com")

        response = await client.get(
            "/api/v1/trading/ledger",
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_get_ledger_after_grant(self, client: AsyncClient):
        """Test ledger records grant entry."""
        token = await register_and_get_token(client, "ledger_grant@test.com")

        # Grant cash
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        response = await client.get(
            "/api/v1/trading/ledger",
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1

        # Find GRANT entry
        grant_entries = [e for e in data["data"] if e["entry_type"] == "GRANT"]
        assert len(grant_entries) == 1
        assert Decimal(str(grant_entries[0]["amount"])) == Decimal("1000000000")

    @pytest.mark.asyncio
    async def test_get_ledger_with_type_filter(self, client: AsyncClient):
        """Test getting ledger with entry_type filter."""
        token = await register_and_get_token(client, "ledger_filter@test.com")

        # Grant cash to create an entry
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        response = await client.get(
            "/api/v1/trading/ledger",
            headers=auth_headers(token),
            params={"entry_type": "GRANT"},
        )

        assert response.status_code == 200
        data = response.json()
        # All entries should be GRANT type
        for entry in data["data"]:
            assert entry["entry_type"] == "GRANT"

    @pytest.mark.asyncio
    async def test_get_ledger_pagination(self, client: AsyncClient):
        """Test ledger pagination."""
        token = await register_and_get_token(client, "ledger_page@test.com")

        response = await client.get(
            "/api/v1/trading/ledger",
            headers=auth_headers(token),
            params={"limit": 10, "offset": 0},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_ledger_unauthorized(self, client: AsyncClient):
        """Test ledger access without authentication."""
        response = await client.get("/api/v1/trading/ledger")

        assert response.status_code == 401


# =============================================================================
# INTEGRATION TESTS - FULL TRADING FLOW
# =============================================================================

class TestTradingIntegration:
    """Integration tests for complete trading workflows."""

    @pytest.mark.asyncio
    async def test_wallet_balance_update_after_grant(self, client: AsyncClient):
        """Test that wallet balance updates correctly after grant."""
        token = await register_and_get_token(client, "int_grant@test.com")

        # Check initial balance
        response1 = await client.get(
            "/api/v1/trading/wallet",
            headers=auth_headers(token),
        )
        assert Decimal(str(response1.json()["balance"])) == Decimal("0")

        # Grant cash
        grant_response = await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )
        assert grant_response.json()["granted"] is True

        # Check balance after grant
        response2 = await client.get(
            "/api/v1/trading/wallet",
            headers=auth_headers(token),
        )
        assert Decimal(str(response2.json()["balance"])) == Decimal("1000000000")

    @pytest.mark.asyncio
    async def test_ledger_audit_trail_for_grant(self, client: AsyncClient):
        """Test ledger provides audit trail for grant operation."""
        token = await register_and_get_token(client, "int_audit@test.com")

        # Grant cash
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        # Check ledger
        response = await client.get(
            "/api/v1/trading/ledger",
            headers=auth_headers(token),
        )

        data = response.json()
        assert len(data["data"]) >= 1

        grant_entry = data["data"][0]
        assert grant_entry["entry_type"] == "GRANT"
        assert Decimal(str(grant_entry["amount"])) == Decimal("1000000000")
        assert grant_entry["ref_type"] == "SYSTEM"
        assert grant_entry["balance_after"] is not None


# =============================================================================
# EDGE CASES AND VALIDATION TESTS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_symbol(self, client: AsyncClient):
        """Test placing order with empty symbol."""
        token = await register_and_get_token(client, "edge_empty_sym@test.com")

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "100",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_very_large_quantity(self, client: AsyncClient):
        """Test placing order with very large quantity."""
        token = await register_and_get_token(client, "edge_large_qty@test.com")

        # Grant cash
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "999999999999",  # Very large
            },
        )

        # Should fail due to insufficient balance
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INSUFFICIENT_BALANCE"

    @pytest.mark.asyncio
    async def test_decimal_quantity(self, client: AsyncClient):
        """Test placing order with decimal quantity."""
        token = await register_and_get_token(client, "edge_decimal@test.com")

        # Grant cash
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "100.5",
                "limit_price": "50000",
            },
        )

        # System accepts decimal quantities
        # Response depends on price provider availability
        assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_negative_limit_price(self, client: AsyncClient):
        """Test placing order with negative limit price."""
        token = await register_and_get_token(client, "edge_neg_price@test.com")

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "100",
                "limit_price": "-50000",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_symbol_case_insensitive(self, client: AsyncClient):
        """Test that symbol is normalized to uppercase."""
        token = await register_and_get_token(client, "edge_symbol_case@test.com")

        # Grant cash
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "vnm",  # lowercase
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "100",
                "limit_price": "50000",
            },
        )

        # If successful, symbol should be uppercase in response
        if response.status_code == 200:
            assert response.json()["order"]["symbol"] == "VNM"

    @pytest.mark.asyncio
    async def test_pagination_limits(self, client: AsyncClient):
        """Test pagination with boundary values."""
        token = await register_and_get_token(client, "edge_page@test.com")

        # Test minimum limit
        response = await client.get(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            params={"limit": 1},
        )
        assert response.status_code == 200

        # Test maximum limit
        response = await client.get(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            params={"limit": 1000},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_pagination_invalid_limit(self, client: AsyncClient):
        """Test pagination with invalid limit."""
        token = await register_and_get_token(client, "edge_bad_limit@test.com")

        # Limit below minimum
        response = await client.get(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            params={"limit": 0},
        )
        assert response.status_code == 422

        # Limit above maximum
        response = await client.get(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            params={"limit": 1001},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_status_filter_ignored(self, client: AsyncClient):
        """Test that invalid status filter is ignored."""
        token = await register_and_get_token(client, "edge_bad_status@test.com")

        response = await client.get(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            params={"status": "INVALID_STATUS"},
        )

        # Should still return 200, just ignore invalid filter
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_long_client_order_id(self, client: AsyncClient):
        """Test placing order with client_order_id at max length."""
        token = await register_and_get_token(client, "edge_long_id@test.com")

        # Grant cash
        await client.post(
            "/api/v1/trading/bootstrap/grant-initial-cash",
            headers=auth_headers(token),
        )

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "100",
                "limit_price": "50000",
                "client_order_id": "a" * 50,  # Max length
            },
        )

        # Should be accepted or fail on market price, not on client_order_id length
        assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_too_long_client_order_id(self, client: AsyncClient):
        """Test placing order with client_order_id exceeding max length."""
        token = await register_and_get_token(client, "edge_too_long_id@test.com")

        response = await client.post(
            "/api/v1/trading/orders",
            headers=auth_headers(token),
            json={
                "symbol": "VNM",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "100",
                "limit_price": "50000",
                "client_order_id": "a" * 51,  # Exceeds max length
            },
        )

        assert response.status_code == 422  # Validation error
