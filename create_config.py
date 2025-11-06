#!/usr/bin/env python3
"""
Interactive script to create carconnectivity_config.json
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from getpass import getpass


def sanitize_config(config):
    """Create a copy of config with sensitive fields masked."""
    import copy
    sanitized = copy.deepcopy(config)

    # Fields to mask
    sensitive_fields = ['password', 'client_secret']

    def mask_sensitive(obj):
        """Recursively mask sensitive fields in nested structures."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in sensitive_fields:
                    obj[key] = '***REDACTED***'
                else:
                    mask_sensitive(value)
        elif isinstance(obj, list):
            for item in obj:
                mask_sensitive(item)

    mask_sensitive(sanitized)
    return sanitized


def get_connector_choice():
    """Ask user to select a connector type."""
    connectors = {
        "1": ("Audi", "audi"),
        "2": ("SeatCupra", "seatcupra"),
        "3": ("Skoda", "skoda"),
        "4": ("Tronity", "tronity"),
        "5": ("Volkswagen", "volkswagen"),
        "6": ("Volvo", "volvo"),
    }

    print("Available connectors:")
    for key, (display_name, _) in connectors.items():
        print(f"{key}. {display_name}")

    while True:
        choice = input(f"\nSelect connector (1-{len(connectors)}): ").strip()
        if choice in connectors:
            return connectors[choice][1]
        else:
            print(f"Invalid choice. Please select 1-{len(connectors)}.")


def get_vw_skoda_credentials():
    """Get username and password for VW/Skoda connectors."""
    username = input("Enter username/email: ").strip()
    password = getpass("Enter password: ")
    interval = input("Enter polling interval in seconds (default: 300): ").strip()
    interval = int(interval) if interval else 300

    return {
        "username": username,
        "password": password,
        "interval": interval
    }


def get_tronity_credentials():
    """Get client_id and client_secret for Tronity connector."""
    client_id = input("Enter client_id: ").strip()
    client_secret = getpass("Enter client_secret: ")
    interval = input("Enter polling interval in seconds (default: 60): ").strip()
    interval = int(interval) if interval else 60

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "interval": interval
    }


def get_webui_credentials():
    """Get username and password for webui plugin."""
    print("\n--- WebUI Plugin Configuration ---")
    username = input("Enter WebUI username: ").strip()
    password = getpass("Enter WebUI password: ")

    return {
        "username": username,
        "password": password
    }


def get_grafana_credentials():
    """Get admin username and password for Grafana container."""
    print("\n--- Grafana Container Configuration ---")
    admin_user = input("Enter Grafana admin username (default: admin): ").strip()
    admin_user = admin_user if admin_user else "admin"
    admin_password = getpass("Enter Grafana admin password (default: admin): ")
    admin_password = admin_password if admin_password else "admin"

    return {
        "admin_user": admin_user,
        "admin_password": admin_password
    }


def create_config():
    """Main function to create the configuration file."""
    print("=== Car Connectivity Configuration Setup ===\n")

    # Get connector type
    connector_type = get_connector_choice()
    print(f"\nConfiguring {connector_type} connector...")

    # Get connector credentials
    if connector_type in ["volkswagen", "skoda", "seatcupra", "volvo", "audi"]:
        connector_config = get_vw_skoda_credentials()
    else:  # tronity
        connector_config = get_tronity_credentials()

    # Get webui credentials
    webui_config = get_webui_credentials()

    # Get Grafana credentials
    grafana_config = get_grafana_credentials()

    # Build configuration structure
    config = {
        "carConnectivity": {
            "log_level": "error",
            "connectors": [
                {
                    "type": connector_type,
                    "config": connector_config
                }
            ],
            "plugins": [
                {
                    "type": "webui",
                    "disabled": False,
                    "config": webui_config
                },
                {
                    "type": "database",
                    "config": {
                        "db_url": "sqlite:///carconnectivity.db"
                    }
                }
            ]
        }
    }

    # Create config directory if it doesn't exist
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Check if config file exists and create backup
    config_file = config_dir / "carconnectivity_config.json"
    if config_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = config_dir / f"carconnectivity_config.json.backup_{timestamp}"
        shutil.copy2(config_file, backup_file)
        print(f"\n✓ Existing config backed up to {backup_file}")

    # Write configuration file
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    print(f"✓ Configuration saved to {config_file}")

    # Write Grafana credentials to .env file
    env_file = Path(".env")
    if env_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = Path(f".env.backup_{timestamp}")
        shutil.copy2(env_file, backup_file)
        print(f"✓ Existing .env file backed up to {backup_file}")

    with open(env_file, "w", encoding="utf-8") as f:
        f.write(f"GF_SECURITY_ADMIN_USER=\"{grafana_config['admin_user']}\"\n")
        f.write(f"GF_SECURITY_ADMIN_PASSWORD=\"{grafana_config['admin_password']}\"\n")

    print(f"✓ Grafana credentials saved to {env_file}")

    print("\nGenerated configuration:")
    print(json.dumps(sanitize_config(config), indent=4))


if __name__ == "__main__":
    try:
        create_config()
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled.")
        exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        exit(1)
