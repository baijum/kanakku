#!/usr/bin/env python3
"""
Test script to check admin server imports and identify issues.
"""

import sys
import traceback


def test_import(module_name, description):
    """Test importing a module and report results."""
    try:
        __import__(module_name)
        print(f"✅ {description}: OK")
        return True
    except Exception as e:
        print(f"❌ {description}: FAILED - {e}")
        traceback.print_exc()
        return False


def main():
    """Test all critical imports for the admin server."""
    print("Testing admin server imports...")
    print("=" * 50)

    # Test basic Python modules
    test_import("asyncio", "asyncio")
    test_import("json", "json")
    test_import("logging", "logging")
    test_import("os", "os")
    test_import("subprocess", "subprocess")
    test_import("sys", "sys")
    test_import("datetime", "datetime")
    test_import("pathlib", "pathlib")
    test_import("typing", "typing")

    print("\nTesting MCP imports...")
    print("-" * 30)

    # Test MCP imports
    test_import("mcp", "mcp")
    test_import("mcp.server", "mcp.server")
    test_import("mcp.server.stdio", "mcp.server.stdio")
    test_import("mcp.types", "mcp.types")
    test_import("mcp.server.models", "mcp.server.models")

    print("\nTesting admin server specific imports...")
    print("-" * 40)

    # Test admin server modules
    try:
        import admin_server

        print("✅ admin_server: OK")
    except Exception as e:
        print(f"❌ admin_server: FAILED - {e}")
        traceback.print_exc()

    print("\nDone.")


if __name__ == "__main__":
    main()
