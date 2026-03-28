#!/usr/bin/env python3
"""Test script to debug .env file loading"""
from pathlib import Path
from dotenv import load_dotenv
import os

print("=" * 60)
print("Testing .env file loading")
print("=" * 60)

env_file = Path(".env")
print(f"✓ Looking for: {env_file.resolve()}")
print(f"✓ File exists: {env_file.exists()}")

if env_file.exists():
    with open(env_file, "r") as f:
        print(f"\n.env contents:")
        print(f.read())

# Load it
load_dotenv(env_file, override=True)

# Check variables
print("\n" + "=" * 60)
print("Environment variables after load_dotenv:")
print("=" * 60)
bot_token = os.getenv("BOT_TOKEN")
admin_ids = os.getenv("ADMIN_IDS")

print(f"BOT_TOKEN: {'SET ✓' if bot_token else 'NOT SET ✗'}")
if bot_token:
    print(f"  Value (first 30 chars): {bot_token[:30]}...")

print(f"ADMIN_IDS: {'SET ✓' if admin_ids else 'NOT SET ✗'}")
if admin_ids:
    print(f"  Value: {admin_ids}")

print("\nNow trying to import config...")
print("=" * 60)
try:
    from config import config
    print("✓ Config loaded successfully!")
    print(f"  BOT_TOKEN configured: {bool(config.BOT_TOKEN)}")
    print(f"  ADMIN_IDS configured: {bool(config.ADMIN_IDS)}")
except Exception as e:
    print(f"✗ Config loading failed:")
    print(f"  {type(e).__name__}: {e}")
