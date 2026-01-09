#!/usr/bin/env python3
"""
Demo script to test Chat API optimizations
"""
import asyncio
import time
import httpx


BASE_URL = "http://localhost:8000"


async def test_non_streaming():
    """Test non-streaming chat API"""
    print("=" * 60)
    print("TEST 1: Non-streaming Chat")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # First request - cache miss
        print("\n[Request 1] Asking about VNM (cache miss expected)...")
        start = time.time()

        response = await client.post(
            f"{BASE_URL}/api/v1/chat",
            json={
                "message": "Cho tôi biết về công ty Vinamilk (VNM)",
                "conversation_id": "demo-001",
                "stream": False
            },
            timeout=30.0
        )

        elapsed = time.time() - start
        print(f"⏱️  Response time: {elapsed:.2f}s")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"💬 Response preview: {data['message'][:200]}...")
            print(f"📁 Data used: {data.get('data_used', [])}")

        # Second request - cache hit
        print("\n[Request 2] Asking about VNM again (cache hit expected)...")
        start = time.time()

        response = await client.post(
            f"{BASE_URL}/api/v1/chat",
            json={
                "message": "Cổ đông của VNM là ai?",
                "conversation_id": "demo-001",
                "stream": False
            },
            timeout=30.0
        )

        elapsed = time.time() - start
        print(f"⏱️  Response time: {elapsed:.2f}s (should be faster!)")
        print(f"📊 Status: {response.status_code}")


async def test_streaming():
    """Test streaming chat API"""
    print("\n" + "=" * 60)
    print("TEST 2: Streaming Chat")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        print("\n[Streaming Request] Asking about FPT...")
        start = time.time()

        async with client.stream(
            "POST",
            f"{BASE_URL}/api/v1/chat",
            json={
                "message": "Giá FPT hiện tại là bao nhiêu?",
                "conversation_id": "demo-002",
                "stream": True
            },
            timeout=30.0
        ) as response:
            print(f"📊 Status: {response.status_code}")
            print("📡 Streaming response:")
            print("-" * 60)

            chunks_received = 0
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunks_received += 1
                    data_str = line[6:]  # Remove "data: " prefix
                    try:
                        import json
                        data = json.loads(data_str)
                        if "chunk" in data:
                            print(data["chunk"], end="", flush=True)
                        elif data.get("done"):
                            print("\n" + "-" * 60)
                            print(f"✅ Stream complete!")
                            print(f"📊 Chunks received: {chunks_received}")
                            print(f"📁 Data used: {data.get('data_used', [])}")
                    except:
                        pass

        elapsed = time.time() - start
        print(f"⏱️  Total time: {elapsed:.2f}s")


async def test_cache_stats():
    """Test cache statistics endpoint"""
    print("\n" + "=" * 60)
    print("TEST 3: Cache Statistics")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/cache/stats")

        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Cache Statistics:")
            print(f"  - Entries: {stats['entries']}")
            print(f"  - Hits: {stats['hits']}")
            print(f"  - Misses: {stats['misses']}")
            print(f"  - Hit Rate: {stats['hit_rate']}")
            print(f"  - Sets: {stats['sets']}")


async def test_rate_limiting():
    """Test rate limiting"""
    print("\n" + "=" * 60)
    print("TEST 4: Rate Limiting")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        print("\n[Rapid Fire] Sending 5 requests quickly...")

        for i in range(5):
            try:
                response = await client.post(
                    f"{BASE_URL}/api/v1/chat",
                    json={
                        "message": f"Test message {i+1}",
                        "stream": False
                    },
                    timeout=10.0
                )
                print(f"  Request {i+1}: {response.status_code}")
            except httpx.HTTPStatusError as e:
                print(f"  Request {i+1}: {e.response.status_code} (Rate limited)")


async def main():
    """Run all tests"""
    print("\n🚀 Chat API Optimization Tests")
    print("=" * 60)

    try:
        # Test non-streaming
        await test_non_streaming()

        # Test streaming
        await test_streaming()

        # Test cache stats
        await test_cache_stats()

        # Test rate limiting (optional - uncomment to test)
        # await test_rate_limiting()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)

    except httpx.ConnectError:
        print("\n❌ Error: Cannot connect to API server")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
