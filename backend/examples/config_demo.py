#!/usr/bin/env python3
"""
Global Configuration System Demo

This script demonstrates how to use Kanakku's global configuration system
to manage API tokens and other application-wide settings.

Usage:
    python config_demo.py

Requirements:
    - Flask application context
    - Admin privileges (for setting configurations)
    - Proper database setup
"""

import os
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.utils.config_manager import (
    configuration_exists,
    delete_configuration,
    get_all_configurations,
    get_configuration,
    get_gemini_api_token,
    is_gemini_api_configured,
    set_configuration,
    set_gemini_api_token,
    validate_gemini_api_token,
)


def demo_basic_operations():
    """Demonstrate basic configuration operations."""
    print("=== Basic Configuration Operations ===")

    # Set a simple configuration
    print("1. Setting a simple configuration...")
    success = set_configuration(
        key="DEMO_SETTING",
        value="Hello, World!",
        description="A demo configuration setting",
        is_encrypted=False,
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Get the configuration
    print("2. Retrieving the configuration...")
    value = get_configuration("DEMO_SETTING")
    print(f"   Value: {value}")

    # Check if configuration exists
    print("3. Checking if configuration exists...")
    exists = configuration_exists("DEMO_SETTING")
    print(f"   Exists: {'✅ Yes' if exists else '❌ No'}")

    # Update the configuration
    print("4. Updating the configuration...")
    success = set_configuration(
        key="DEMO_SETTING",
        value="Updated value!",
        description="Updated demo configuration",
        is_encrypted=False,
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Get updated value
    updated_value = get_configuration("DEMO_SETTING")
    print(f"   Updated value: {updated_value}")

    # Clean up
    print("5. Cleaning up...")
    success = delete_configuration("DEMO_SETTING")
    print(f"   Deletion result: {'✅ Success' if success else '❌ Failed'}")


def demo_encrypted_operations():
    """Demonstrate encrypted configuration operations."""
    print("\n=== Encrypted Configuration Operations ===")

    # Set an encrypted configuration
    print("1. Setting an encrypted configuration...")
    success = set_configuration(
        key="SECRET_API_KEY",
        value="sk-1234567890abcdef",
        description="A secret API key",
        is_encrypted=True,
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Retrieve the encrypted configuration (it will be automatically decrypted)
    print("2. Retrieving the encrypted configuration...")
    value = get_configuration("SECRET_API_KEY")
    print(f"   Decrypted value: {value}")

    # Clean up
    print("3. Cleaning up...")
    success = delete_configuration("SECRET_API_KEY")
    print(f"   Deletion result: {'✅ Success' if success else '❌ Failed'}")


def demo_gemini_api_operations():
    """Demonstrate Gemini API token operations."""
    print("\n=== Gemini API Token Operations ===")

    # Check current status
    print("1. Checking current Gemini API configuration...")
    is_configured = is_gemini_api_configured()
    print(f"   Currently configured: {'✅ Yes' if is_configured else '❌ No'}")

    if is_configured:
        current_token = get_gemini_api_token()
        print(
            f"   Current token (first 10 chars): {current_token[:10] if current_token else 'None'}..."
        )

    # Validate a sample token
    print("2. Validating sample Gemini API tokens...")
    test_tokens = [
        "AIzaSyDummyTokenForTesting123456789",  # Valid format
        "invalid_token",  # Invalid format
        "AIzaSy123",  # Too short
        "",  # Empty
    ]

    for token in test_tokens:
        is_valid, error = validate_gemini_api_token(token)
        status = "✅ Valid" if is_valid else f"❌ Invalid: {error}"
        print(f"   Token '{token[:20]}...': {status}")

    # Set a demo Gemini API token
    print("3. Setting a demo Gemini API token...")
    demo_token = "AIzaSyDemoTokenForTestingPurposes123"
    success, error = set_gemini_api_token(demo_token, "Demo Gemini API token")

    if success:
        print("   ✅ Demo token set successfully")

        # Verify it was set
        print("4. Verifying the demo token...")
        is_configured = is_gemini_api_configured()
        retrieved_token = get_gemini_api_token()

        print(f"   Is configured: {'✅ Yes' if is_configured else '❌ No'}")
        print(
            f"   Retrieved token matches: {'✅ Yes' if retrieved_token == demo_token else '❌ No'}"
        )

        # Clean up
        print("5. Cleaning up demo token...")
        cleanup_success = delete_configuration("GEMINI_API_TOKEN")
        print(f"   Cleanup result: {'✅ Success' if cleanup_success else '❌ Failed'}")
    else:
        print(f"   ❌ Failed to set demo token: {error}")


def demo_list_all_configurations():
    """Demonstrate listing all configurations."""
    print("\n=== List All Configurations ===")

    # Set a few demo configurations
    demo_configs = [
        ("APP_NAME", "Kanakku Demo", "Application name", False),
        ("MAX_USERS", "100", "Maximum number of users", False),
        ("SECRET_KEY", "super-secret-key-123", "Application secret key", True),
    ]

    print("1. Setting up demo configurations...")
    for key, value, desc, encrypted in demo_configs:
        success = set_configuration(key, value, desc, encrypted)
        print(f"   {key}: {'✅' if success else '❌'}")

    # List all configurations
    print("2. Listing all configurations...")
    all_configs = get_all_configurations()

    if all_configs:
        print(f"   Found {len(all_configs)} configurations:")
        for config in all_configs:
            encrypted_indicator = "🔒" if config.get("is_encrypted") else "🔓"
            print(
                f"   {encrypted_indicator} {config['key']}: {config['value']} ({config.get('description', 'No description')})"
            )
    else:
        print("   No configurations found")

    # Clean up
    print("3. Cleaning up demo configurations...")
    for key, _, _, _ in demo_configs:
        success = delete_configuration(key)
        print(f"   Deleted {key}: {'✅' if success else '❌'}")


def demo_error_handling():
    """Demonstrate error handling scenarios."""
    print("\n=== Error Handling Scenarios ===")

    # Try to get a non-existent configuration
    print("1. Getting non-existent configuration...")
    value = get_configuration("NON_EXISTENT_KEY")
    print(f"   Result: {value} (should be None)")

    # Try to get a non-existent configuration with default
    print("2. Getting non-existent configuration with default...")
    value = get_configuration("NON_EXISTENT_KEY", "default_value")
    print(f"   Result: {value} (should be 'default_value')")

    # Try to delete a non-existent configuration
    print("3. Deleting non-existent configuration...")
    success = delete_configuration("NON_EXISTENT_KEY")
    print(f"   Result: {'✅ Success' if success else '❌ Failed'} (should be False)")

    # Try to set an invalid Gemini API token
    print("4. Setting invalid Gemini API token...")
    success, error = set_gemini_api_token("invalid_token")
    print(f"   Result: {'✅ Success' if success else f'❌ Failed: {error}'}")


def main():
    """Main demonstration function."""
    print("🚀 Kanakku Global Configuration System Demo")
    print("=" * 50)

    # Create Flask application context
    app = create_app()

    with app.app_context():
        try:
            # Run all demonstrations
            demo_basic_operations()
            demo_encrypted_operations()
            demo_gemini_api_operations()
            demo_list_all_configurations()
            demo_error_handling()

            print("\n" + "=" * 50)
            print("✅ Demo completed successfully!")
            print("\nKey takeaways:")
            print("- Use set_configuration() to store any key-value pair")
            print("- Use get_configuration() to retrieve values")
            print(
                "- Sensitive values are automatically encrypted when is_encrypted=True"
            )
            print(
                "- Use specialized functions like set_gemini_api_token() for validated settings"
            )
            print("- All operations include proper error handling and validation")

        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
