#!/usr/bin/env python3
"""CLI script for OHLC sync operations.

Usage:
    # Full sync (all symbols, 200 days)
    python -m scripts.ohlc_sync full

    # Daily sync (only today's data)
    python -m scripts.ohlc_sync daily

    # Sync specific symbols
    python -m scripts.ohlc_sync symbols VNM VIC FPT --days 100

    # Check for gaps
    python -m scripts.ohlc_sync gaps

    # Fill gaps automatically
    python -m scripts.ohlc_sync fill-gaps

    # Get sync status
    python -m scripts.ohlc_sync status
"""
import asyncio
import argparse
import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.sync.ohlc_sync import ohlc_sync_service


async def cmd_full_sync(args):
    """Run full sync."""
    print(f"Starting full OHLC sync ({args.days} days)...")
    stats = await ohlc_sync_service.full_sync(days=args.days)
    print(f"\nSync completed:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def cmd_daily_sync(args):
    """Run daily sync."""
    print("Starting daily OHLC sync...")
    stats = await ohlc_sync_service.daily_sync()
    print(f"\nSync completed:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def cmd_sync_symbols(args):
    """Sync specific symbols."""
    print(f"Syncing {len(args.symbols)} symbols for {args.days} days...")
    stats = await ohlc_sync_service.sync_symbols(args.symbols, days=args.days)
    print(f"\nSync completed:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def cmd_detect_gaps(args):
    """Detect gaps in data."""
    print(f"Checking for gaps in last {args.days} days...")
    gaps = await ohlc_sync_service.detect_gaps(days_back=args.days)
    print(f"\n{json.dumps(gaps, indent=2)}")


async def cmd_fill_gaps(args):
    """Fill gaps in data."""
    print(f"Checking and filling gaps in last {args.days} days...")
    result = await ohlc_sync_service.fill_gaps(days_back=args.days)
    print(f"\nResult:")
    print(json.dumps(result, indent=2))


async def cmd_status(args):
    """Get sync status."""
    print("Getting sync status...")
    status = await ohlc_sync_service.get_sync_status()
    print(f"\nSync Status:")
    print(json.dumps(status, indent=2))


async def cmd_calculate_ma(args):
    """Calculate Moving Averages."""
    if args.date:
        from datetime import datetime as dt
        target_date = dt.strptime(args.date, "%Y-%m-%d").date()
        print(f"Calculating MA for date: {target_date}")
        stats = await ohlc_sync_service.calculate_ma(target_date=target_date)
    else:
        print("Calculating MA for all records with NULL values...")
        stats = await ohlc_sync_service.calculate_ma_batch(batch_size=args.batch_size)

    print(f"\nMA Calculation completed:")
    print(json.dumps(stats, indent=2))


def main():
    parser = argparse.ArgumentParser(description="OHLC Sync CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Full sync
    full_parser = subparsers.add_parser("full", help="Full sync all symbols")
    full_parser.add_argument("--days", type=int, default=200, help="Number of days to sync")

    # Daily sync
    subparsers.add_parser("daily", help="Daily sync (today only)")

    # Sync specific symbols
    symbols_parser = subparsers.add_parser("symbols", help="Sync specific symbols")
    symbols_parser.add_argument("symbols", nargs="+", help="Symbols to sync")
    symbols_parser.add_argument("--days", type=int, default=200, help="Number of days to sync")

    # Detect gaps
    gaps_parser = subparsers.add_parser("gaps", help="Detect gaps in data")
    gaps_parser.add_argument("--days", type=int, default=30, help="Days to check")

    # Fill gaps
    fill_parser = subparsers.add_parser("fill-gaps", help="Fill gaps in data")
    fill_parser.add_argument("--days", type=int, default=30, help="Days to check and fill")

    # Status
    subparsers.add_parser("status", help="Get sync status")

    # Calculate MA
    ma_parser = subparsers.add_parser("calculate-ma", help="Calculate Moving Averages")
    ma_parser.add_argument("--date", type=str, help="Specific date (YYYY-MM-DD), default: all NULL records")
    ma_parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing")

    args = parser.parse_args()

    if args.command == "full":
        asyncio.run(cmd_full_sync(args))
    elif args.command == "daily":
        asyncio.run(cmd_daily_sync(args))
    elif args.command == "symbols":
        asyncio.run(cmd_sync_symbols(args))
    elif args.command == "gaps":
        asyncio.run(cmd_detect_gaps(args))
    elif args.command == "fill-gaps":
        asyncio.run(cmd_fill_gaps(args))
    elif args.command == "status":
        asyncio.run(cmd_status(args))
    elif args.command == "calculate-ma":
        asyncio.run(cmd_calculate_ma(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
