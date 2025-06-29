#!/usr/bin/env python3
"""
Live Integration Test Script for Flight Control MCP Server

This script tests the MCP server against your actual Flight Control instance.
It requires that you have already run 'flightctl login'.
"""

import sys
import traceback
from resource_queries import Configuration, FlightControlClient, setup_logging


def test_live_connection():
    """Test basic connectivity to Flight Control API."""
    print("🔧 Testing Flight Control API connectivity...")

    try:
        # Set up logging
        setup_logging()

        # Load configuration
        config = Configuration()

        if not config.api_base_url:
            print("❌ No Flight Control configuration found.")
            print("   Please run 'flightctl login' first.")
            return False

        print(f"   API URL: {config.api_base_url}")
        print(f"   Skip SSL: {config.insecure_skip_verify}")

        # Create client
        FlightControlClient(config)
        print("✅ Client initialized successfully")

        return True

    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False


def test_api_queries(client):
    """Test various API queries."""
    print("\n🔍 Testing API queries...")

    results = {}

    # Test device query
    try:
        print("   Testing device query...")
        devices = client.query_devices(limit=3)
        results["devices"] = len(devices)
        print(f"   ✅ Found {len(devices)} devices")
        if devices:
            print(f"      Example device: {devices[0].get('metadata', {}).get('name', 'unnamed')}")
    except Exception as e:
        print(f"   ❌ Device query failed: {e}")
        results["devices"] = "error"

    # Test fleet query
    try:
        print("   Testing fleet query...")
        fleets = client.query_fleets(limit=3)
        results["fleets"] = len(fleets)
        print(f"   ✅ Found {len(fleets)} fleets")
        if fleets:
            print(f"      Example fleet: {fleets[0].get('metadata', {}).get('name', 'unnamed')}")
    except Exception as e:
        print(f"   ❌ Fleet query failed: {e}")
        results["fleets"] = "error"

    # Test event query
    try:
        print("   Testing event query...")
        events = client.query_events(limit=3)
        results["events"] = len(events)
        print(f"   ✅ Found {len(events)} events")
    except Exception as e:
        print(f"   ❌ Event query failed: {e}")
        results["events"] = "error"

    # Test enrollment requests
    try:
        print("   Testing enrollment request query...")
        enrollment_requests = client.query_enrollment_requests(limit=3)
        results["enrollment_requests"] = len(enrollment_requests)
        print(f"   ✅ Found {len(enrollment_requests)} enrollment requests")
    except Exception as e:
        print(f"   ❌ Enrollment request query failed: {e}")
        results["enrollment_requests"] = "error"

    # Test repositories
    try:
        print("   Testing repository query...")
        repositories = client.query_repositories(limit=3)
        results["repositories"] = len(repositories)
        print(f"   ✅ Found {len(repositories)} repositories")
    except Exception as e:
        print(f"   ❌ Repository query failed: {e}")
        results["repositories"] = "error"

    # Test resource syncs
    try:
        print("   Testing resource sync query...")
        resource_syncs = client.query_resource_syncs(limit=3)
        results["resource_syncs"] = len(resource_syncs)
        print(f"   ✅ Found {len(resource_syncs)} resource syncs")
    except Exception as e:
        print(f"   ❌ Resource sync query failed: {e}")
        results["resource_syncs"] = "error"

    return results


def test_console_command(client):
    """Test console command execution (if devices are available)."""
    print("\n💻 Testing console command execution...")

    try:
        # First, get a device to test with
        devices = client.query_devices(limit=1)
        if not devices:
            print("   ⚠️  No devices available for console testing")
            return False

        device_name = devices[0].get("metadata", {}).get("name")
        if not device_name:
            print("   ❌ Device has no name")
            return False

        print(f"   Testing console command on device: {device_name}")

        # Test a simple, safe command
        result = client.run_console_command("/usr/local/bin/flightctl", device_name, 'echo "test"')
        print(f"   ✅ Console command successful: {result.strip()}")
        return True

    except Exception as e:
        print(f"   ❌ Console command failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return False


def main():
    """Run all live tests."""
    print("🚀 Flight Control MCP Server - Live Integration Test")
    print("=" * 60)

    # Test connection
    if not test_live_connection():
        sys.exit(1)

    try:
        # Create client for testing
        config = Configuration()
        client = FlightControlClient(config)

        # Test API queries
        api_results = test_api_queries(client)

        # Test console commands
        console_success = test_console_command(client)

        # Summary
        print("\n📊 Test Summary:")
        print("=" * 30)
        for resource, count in api_results.items():
            if count == "error":
                print(f"   {resource:20}: ❌ ERROR")
            else:
                print(f"   {resource:20}: ✅ {count} items")

        if console_success:
            print(f"   {'console_commands':20}: ✅ Working")
        else:
            print(f"   {'console_commands':20}: ❌ Failed")

        # Overall status
        errors = sum(1 for result in api_results.values() if result == "error")
        if errors == 0 and console_success:
            print("\n🎉 All tests passed! Your Flight Control MCP server is working correctly.")
            sys.exit(0)
        elif errors < len(api_results) // 2:
            print(f"\n⚠️  Most tests passed, but {errors} API endpoints had issues.")
            sys.exit(0)
        else:
            print("\n❌ Multiple failures detected. Check your Flight Control setup.")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        print(f"Error details: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
