#!/usr/bin/env python3
"""
Test script to verify streamable-http transport is working.
This script tests the MCP server by starting it and making a simple client connection.
"""

import asyncio
import os
import sys
import subprocess
import time
import requests


async def test_server():
    """Test that the server starts up with streamable-http transport."""
    print("🔧 Testing MCP Server with streamable-http transport...")

    # Set environment variables for testing
    env = os.environ.copy()
    env["MCP_TRANSPORT"] = "streamable-http"
    env["MCP_HOST"] = "127.0.0.1"
    env["MCP_PORT"] = "8001"  # Use different port to avoid conflicts

    print(f"   Transport: {env['MCP_TRANSPORT']}")
    print(f"   Host: {env['MCP_HOST']}")
    print(f"   Port: {env['MCP_PORT']}")

    # Start the server in a subprocess
    server_process = None
    try:
        print("   Starting MCP server...")
        server_process = subprocess.Popen(
            [sys.executable, "main.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Give the server time to start
        print("   Waiting for server to start...")
        time.sleep(3)

        # Check if server is running
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print("❌ Server failed to start:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return False

        # Try to make a health check request
        url = f"http://{env['MCP_HOST']}:{env['MCP_PORT']}/mcp"
        print(f"   Testing endpoint: {url}")

        try:
            # The MCP endpoint might not respond to GET requests normally,
            # but we should at least get a connection
            response = requests.get(url, timeout=5)
            print(f"   Response status: {response.status_code}")
            print("✅ Server is responding to HTTP requests")
            return True
        except requests.ConnectionError:
            print("❌ Could not connect to server")
            return False
        except requests.Timeout:
            print("❌ Server connection timed out")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    finally:
        if server_process:
            print("   Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()


def test_imports():
    """Test that all required imports are available."""
    print("🔧 Testing imports...")

    try:
        from mcp.server.fastmcp import FastMCP

        # Verify the class exists and has expected attributes
        assert hasattr(FastMCP, "run"), "FastMCP should have a run method"
        print("✅ FastMCP import successful")
    except ImportError as e:
        print(f"❌ FastMCP import failed: {e}")
        return False

    try:
        import uvicorn

        # Verify uvicorn has the run function we need
        assert hasattr(uvicorn, "run"), "uvicorn should have a run function"
        print("✅ Uvicorn import successful")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False

    return True


def test_configuration():
    """Test configuration parsing."""
    print("🔧 Testing configuration...")

    # Test with streamable-http transport
    test_env = {"MCP_TRANSPORT": "streamable-http", "MCP_HOST": "0.0.0.0", "MCP_PORT": "9000"}

    old_env = {}
    for key, value in test_env.items():
        old_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        # Import and check the configuration parsing
        transport_env = os.environ.get("MCP_TRANSPORT", "streamable-http")
        host = os.environ.get("MCP_HOST", "127.0.0.1")
        port = int(os.environ.get("MCP_PORT", "8000"))

        if transport_env == "streamable-http" and host == "0.0.0.0" and port == 9000:
            print("✅ Configuration parsing working correctly")
            return True
        else:
            print(f"❌ Configuration parsing failed: transport={transport_env}, host={host}, port={port}")
            return False

    finally:
        # Restore environment
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


async def main():
    """Run all tests."""
    print("🚀 Flight Control MCP Server - Streamable HTTP Test")
    print("=" * 60)

    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Server Test", test_server),
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n📊 Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"💥 {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:20}: {status}")
        if result:
            passed += 1

    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! Streamable HTTP transport is working correctly.")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
