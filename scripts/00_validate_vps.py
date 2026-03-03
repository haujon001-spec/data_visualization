#!/usr/bin/env python3
"""
VPS validation script for SSH connectivity and HTTP port availability.

This script:
1. Reads config/vps_list.csv for VPS endpoints
2. For each enabled VPS, tests SSH connectivity
3. Tests HTTP port availability if defined
4. Logs results with timestamps
5. Returns exit code 0 if all enabled VPS are reachable, else non-zero

Production-ready with async operations, logging, type hints, and error handling.
"""

import asyncio
import csv
import logging
import os
import sys
import socket
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

import paramiko
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("vps_validation.log"),
    ],
)
logger = logging.getLogger(__name__)

# Load environment configuration
load_dotenv()
CONFIG_DIR = os.getenv("CONFIG_DIR", "./config")
SSH_TIMEOUT = int(os.getenv("SSH_TIMEOUT", "10"))
DATA_RAW_DIR = os.getenv("DATA_RAW_DIR", "./data/raw")

# Create output directory
Path(DATA_RAW_DIR).mkdir(parents=True, exist_ok=True)


@dataclass
class VPSCheckResult:
    """Container for individual VPS check results."""

    name: str
    ip_address: str
    ssh_port: int
    http_port: Optional[int]
    ssh_success: bool
    http_success: Optional[bool]
    ssh_message: str
    http_message: Optional[str] = None
    timestamp: str = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def overall_success(self) -> bool:
        """Determine if VPS check overall succeeded."""
        if self.http_port is not None:
            return self.ssh_success and self.http_success
        return self.ssh_success

    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return {
            "name": self.name,
            "ip_address": self.ip_address,
            "ssh_port": self.ssh_port,
            "http_port": self.http_port,
            "ssh_success": self.ssh_success,
            "ssh_message": self.ssh_message,
            "http_success": self.http_success,
            "http_message": self.http_message,
            "overall_success": self.overall_success(),
            "timestamp": self.timestamp,
        }


class VPSConnector:
    """Handles VPS SSH and HTTP connectivity testing."""

    @staticmethod
    async def test_ssh_connectivity(
        host: str, port: int, username: str, timeout: int = SSH_TIMEOUT
    ) -> Tuple[bool, str]:
        """
        Test SSH connectivity to a VPS (non-blocking, background check).

        Args:
            host: IP address or hostname
            port: SSH port
            username: SSH username
            timeout: Connection timeout in seconds

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Run SSH connection test in executor to avoid blocking
            loop = asyncio.get_event_loop()

            def ssh_connect() -> bool:
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(
                        hostname=host,
                        port=port,
                        username=username,
                        look_for_keys=False,
                        allow_agent=False,
                        timeout=timeout,
                    )
                    client.close()
                    return True
                except paramiko.ssh_exception.NoValidConnectionsError:
                    return False
                except paramiko.ssh_exception.SSHException as e:
                    # Connection reached but auth failed (expected), so port is reachable
                    if "Authentication failed" in str(e) or "not authenticated" in str(e):
                        return True
                    return False
                except Exception:
                    return False

            result = await loop.run_in_executor(None, ssh_connect)

            if result:
                message = f"SSH port {port} reachable"
                return True, message
            else:
                message = f"SSH port {port} not reachable"
                return False, message

        except asyncio.TimeoutError:
            message = f"SSH connection timeout after {timeout}s"
            return False, message
        except Exception as e:
            message = f"SSH error: {str(e)}"
            return False, message

    @staticmethod
    async def test_http_port(
        host: str, port: int, timeout: int = 5
    ) -> Tuple[bool, str]:
        """
        Test HTTP port availability via socket connection.

        Args:
            host: IP address or hostname
            port: HTTP port
            timeout: Connection timeout in seconds

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            loop = asyncio.get_event_loop()

            def check_port() -> bool:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    return result == 0
                except Exception:
                    return False

            result = await loop.run_in_executor(None, check_port)

            if result:
                message = f"HTTP port {port} is open"
                return True, message
            else:
                message = f"HTTP port {port} is closed"
                return False, message

        except Exception as e:
            message = f"HTTP port check error: {str(e)}"
            return False, message

    @classmethod
    async def check_vps(cls, vps_entry: Dict[str, str]) -> VPSCheckResult:
        """
        Perform comprehensive VPS connectivity checks.

        Args:
            vps_entry: Dictionary with VPS configuration

        Returns:
            VPSCheckResult: Complete check results for the VPS
        """
        name = vps_entry.get("name", "unknown").strip()
        ip_address = vps_entry.get("ip_address", "").strip()
        ssh_port_str = vps_entry.get("ssh_port", "22").strip()
        ssh_user = vps_entry.get("ssh_user", "ubuntu").strip()
        http_port_str = vps_entry.get("http_port", "").strip()

        try:
            ssh_port = int(ssh_port_str)
        except ValueError:
            logger.error(f"Invalid SSH port for {name}: {ssh_port_str}")
            return VPSCheckResult(
                name=name,
                ip_address=ip_address,
                ssh_port=22,
                http_port=None,
                ssh_success=False,
                http_success=None,
                ssh_message=f"Invalid SSH port: {ssh_port_str}",
            )

        http_port = None
        if http_port_str:
            try:
                http_port = int(http_port_str)
            except ValueError:
                logger.warning(f"Invalid HTTP port for {name}: {http_port_str}")

        logger.info(f"Starting VPS checks for '{name}' ({ip_address}:{ssh_port})...")

        # Test SSH (always required)
        ssh_success, ssh_message = await cls.test_ssh_connectivity(
            ip_address, ssh_port, ssh_user
        )
        logger.info(f"  SSH: {ssh_message}")

        # Test HTTP port (optional)
        http_success = None
        http_message = None
        if http_port:
            http_success, http_message = await cls.test_http_port(ip_address, http_port)
            logger.info(f"  HTTP: {http_message}")

        return VPSCheckResult(
            name=name,
            ip_address=ip_address,
            ssh_port=ssh_port,
            http_port=http_port,
            ssh_success=ssh_success,
            http_success=http_success,
            ssh_message=ssh_message,
            http_message=http_message,
        )


def load_vps_config(config_path: str) -> List[Dict[str, str]]:
    """
    Load VPS configuration from CSV file.

    Args:
        config_path: Path to vps_list.csv

    Returns:
        List[Dict]: List of enabled VPS entries
    """
    if not os.path.exists(config_path):
        logger.error(f"VPS config file not found: {config_path}")
        return []

    vps_list = []
    try:
        with open(config_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Only include enabled entries
                if row.get("enabled", "").lower() == "true":
                    vps_list.append(row)

        logger.info(
            f"Loaded {len(vps_list)} enabled VPS entries from {config_path}"
        )

    except Exception as e:
        logger.error(f"Failed to load VPS config: {str(e)}")

    return vps_list


async def validate_all_vps(vps_list: List[Dict[str, str]]) -> List[VPSCheckResult]:
    """
    Run all VPS checks concurrently.

    Args:
        vps_list: List of VPS configurations

    Returns:
        List[VPSCheckResult]: Results from all checks
    """
    logger.info("=" * 60)
    logger.info(f"Starting VPS validation for {len(vps_list)} server(s)...")
    logger.info("=" * 60)

    # Run all checks concurrently
    results = await asyncio.gather(
        *[VPSConnector.check_vps(vps) for vps in vps_list]
    )

    return results


def save_results(results: List[VPSCheckResult]) -> None:
    """
    Save VPS check results to JSON file.

    Args:
        results: List of VPS check results
    """
    import json

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_vps": len(results),
        "successful": sum(1 for r in results if r.overall_success()),
        "failed": sum(1 for r in results if not r.overall_success()),
        "results": [r.to_dict() for r in results],
    }

    output_file = os.path.join(
        DATA_RAW_DIR,
        f"vps_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )

    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Validation results saved to {output_file}")


def main() -> int:
    """
    Main entry point for VPS validation.

    Returns:
        int: Exit code (0 for all passed, non-zero for failures)
    """
    try:
        config_path = os.path.join(CONFIG_DIR, "vps_list.csv")
        vps_list = load_vps_config(config_path)

        if not vps_list:
            logger.error("No enabled VPS entries to validate")
            return 1

        # Run async validation
        results = asyncio.run(validate_all_vps(vps_list))

        save_results(results)

        logger.info("=" * 60)
        logger.info("VPS Validation Summary:")
        logger.info("=" * 60)

        for result in results:
            status = "✓" if result.overall_success() else "✗"
            logger.info(
                f"{status} {result.name} ({result.ip_address}): "
                f"SSH={'OK' if result.ssh_success else 'FAIL'}"
                + (
                    f", HTTP={'OK' if result.http_success else 'FAIL'}"
                    if result.http_port
                    else ""
                )
            )

        # Determine exit code
        failed_count = sum(1 for r in results if not r.overall_success())

        if failed_count == 0:
            logger.info("\n✓ All VPS checks PASSED")
            return 0
        else:
            logger.error(f"\n✗ {failed_count} VPS check(s) FAILED")
            return 1

    except Exception as e:
        logger.exception(f"Fatal error during VPS validation: {str(e)}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
