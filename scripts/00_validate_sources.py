#!/usr/bin/env python3
"""
Async validation script for production sources (yfinance, CoinGecko, VPS SSH connectivity).

This script validates:
1. yfinance data availability (fetches 1 day of AAPL data)
2. CoinGecko API accessibility (/simple/price endpoint)
3. VPS SSH connectivity for all enabled servers in config/vps_list.csv

Results are logged with timestamps and test data is saved to data/raw/.
Exit code: 0 on complete success, non-zero on any failure.
"""

import asyncio
import logging
import os
import sys
import csv
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path

import httpx
import yfinance as yf
import paramiko
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("validation_sources.log"),
    ],
)
logger = logging.getLogger(__name__)

# Load environment configuration
load_dotenv()
DATA_RAW_DIR = os.getenv("DATA_RAW_DIR", "./data/raw")
CONFIG_DIR = os.getenv("CONFIG_DIR", "./config")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
SSH_TIMEOUT = int(os.getenv("SSH_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Create output directory
Path(DATA_RAW_DIR).mkdir(parents=True, exist_ok=True)


@dataclass
class ValidationResult:
    """Container for validation test results."""

    source: str
    success: bool
    message: str
    timestamp: str = None
    error: Optional[str] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return {
            "source": self.source,
            "success": self.success,
            "message": self.message,
            "timestamp": self.timestamp,
            "error": self.error,
        }


class YFinanceValidator:
    """Validates yfinance connectivity and data availability."""

    @staticmethod
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def validate_yfinance() -> ValidationResult:
        """
        Test yfinance connectivity by fetching 1 day of AAPL data.

        Returns:
            ValidationResult: Test result with success status and message.
        """
        try:
            logger.info("Starting yfinance validation (fetching AAPL 1-day data)...")

            # Fetch 1 day of AAPL data
            ticker = yf.Ticker("AAPL")
            df = ticker.history(period="1d")

            if df is None or df.empty:
                msg = "yfinance returned empty dataframe for AAPL"
                logger.error(msg)
                return ValidationResult(
                    source="yfinance",
                    success=False,
                    message=msg,
                    error="Empty dataframe",
                )

            # Save test data
            output_file = os.path.join(
                DATA_RAW_DIR, f"yfinance_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            df.reset_index().to_json(output_file, orient="records", date_format="iso")

            msg = f"yfinance validation passed. Fetched {len(df)} AAPL records. Saved to {output_file}"
            logger.info(msg)

            return ValidationResult(
                source="yfinance",
                success=True,
                message=msg,
            )

        except Exception as e:
            msg = f"yfinance validation failed: {str(e)}"
            logger.error(msg)
            return ValidationResult(
                source="yfinance",
                success=False,
                message="yfinance connectivity test failed",
                error=str(e),
            )


class CoinGeckoValidator:
    """Validates CoinGecko API connectivity."""

    @staticmethod
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def validate_coingecko() -> ValidationResult:
        """
        Test CoinGecko API by querying /simple/price endpoint.

        Returns:
            ValidationResult: Test result with success status and message.
        """
        try:
            logger.info("Starting CoinGecko API validation...")

            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": "bitcoin,ethereum",
                "vs_currencies": "usd",
                "include_market_cap": "true",
            }

            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if not data:
                    msg = "CoinGecko returned empty response"
                    logger.error(msg)
                    return ValidationResult(
                        source="CoinGecko",
                        success=False,
                        message=msg,
                        error="Empty response",
                    )

                # Save test data
                output_file = os.path.join(
                    DATA_RAW_DIR,
                    f"coingecko_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                )
                with open(output_file, "w") as f:
                    json.dump(data, f, indent=2)

                msg = f"CoinGecko validation passed. Got prices for {len(data)} coins. Saved to {output_file}"
                logger.info(msg)

                return ValidationResult(
                    source="CoinGecko",
                    success=True,
                    message=msg,
                )

        except Exception as e:
            msg = f"CoinGecko API validation failed: {str(e)}"
            logger.error(msg)
            return ValidationResult(
                source="CoinGecko",
                success=False,
                message="CoinGecko API connectivity test failed",
                error=str(e),
            )


class VPSValidator:
    """Validates VPS SSH connectivity."""

    @staticmethod
    def _load_vps_config() -> List[Dict[str, str]]:
        """
        Load VPS configuration from CSV file.

        Returns:
            List[Dict]: List of VPS configurations for enabled servers.
        """
        vps_config_path = os.path.join(CONFIG_DIR, "vps_list.csv")

        if not os.path.exists(vps_config_path):
            logger.warning(f"VPS config file not found: {vps_config_path}")
            return []

        vps_list = []
        try:
            with open(vps_config_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Only include enabled VPS entries
                    if row.get("enabled", "").lower() == "true":
                        vps_list.append(row)
            logger.info(f"Loaded {len(vps_list)} enabled VPS entries from config")
        except Exception as e:
            logger.error(f"Failed to load VPS config: {str(e)}")

        return vps_list

    @staticmethod
    async def _test_ssh_connection(
        host: str, port: int, username: str, timeout: int = SSH_TIMEOUT
    ) -> Tuple[bool, str]:
        """
        Test SSH connectivity to a VPS.

        Args:
            host: IP address or hostname of VPS
            port: SSH port
            username: SSH username
            timeout: Connection timeout in seconds

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Try to connect (no authentication required for this test)
            client.connect(
                host,
                port=port,
                username=username,
                look_for_keys=False,
                allow_agent=False,
                timeout=timeout,
            )
            client.close()
            return True, f"SSH connection successful"

        except paramiko.ssh_exception.NoValidConnectionsError as e:
            return False, f"SSH connection refused: {str(e)}"
        except paramiko.ssh_exception.SSHException as e:
            # SSH connection established but auth failed (expected without key), so SSH is reachable
            if "Authentication failed" in str(e) or "not authenticated" in str(e):
                return True, f"SSH port reachable (auth required as expected)"
            return False, f"SSH error: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    @classmethod
    async def validate_vps_ssh(cls) -> ValidationResult:
        """
        Test SSH connectivity for all enabled VPS entries in config.

        Returns:
            ValidationResult: Aggregated test result for all VPS.
        """
        try:
            logger.info("Starting VPS SSH connectivity validation...")

            vps_list = cls._load_vps_config()

            if not vps_list:
                msg = "No enabled VPS entries found in config"
                logger.warning(msg)
                return ValidationResult(
                    source="VPS_SSH",
                    success=False,
                    message=msg,
                    error="No VPS config",
                )

            results = []
            all_success = True

            for vps in vps_list:
                host = vps.get("ip_address", "").strip()
                port_str = vps.get("ssh_port", "22").strip()
                user = vps.get("ssh_user", "ubuntu").strip()
                name = vps.get("name", "unknown").strip()

                try:
                    port = int(port_str)
                except ValueError:
                    logger.error(f"Invalid port for VPS {name}: {port_str}")
                    all_success = False
                    continue

                success, msg = await cls._test_ssh_connection(host, port, user)
                results.append(
                    {
                        "name": name,
                        "host": host,
                        "port": port,
                        "success": success,
                        "message": msg,
                    }
                )

                status = "✓" if success else "✗"
                logger.info(f"{status} VPS '{name}' ({host}:{port}): {msg}")

                if not success:
                    all_success = False

            # Save VPS test results
            output_file = os.path.join(
                DATA_RAW_DIR,
                f"vps_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            )
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)

            msg = (
                f"VPS validation complete. Tested {len(results)} servers. "
                f"Results saved to {output_file}"
            )
            logger.info(msg)

            return ValidationResult(
                source="VPS_SSH",
                success=all_success,
                message=msg,
            )

        except Exception as e:
            msg = f"VPS validation failed: {str(e)}"
            logger.error(msg)
            return ValidationResult(
                source="VPS_SSH",
                success=False,
                message="VPS SSH validation failed",
                error=str(e),
            )


async def run_all_validations() -> List[ValidationResult]:
    """
    Run all async validation tests in parallel.

    Returns:
        List[ValidationResult]: Results from all validators.
    """
    logger.info("=" * 60)
    logger.info("Starting all production source validations...")
    logger.info("=" * 60)

    results = await asyncio.gather(
        YFinanceValidator.validate_yfinance(),
        CoinGeckoValidator.validate_coingecko(),
        VPSValidator.validate_vps_ssh(),
    )

    return results


def save_validation_summary(results: List[ValidationResult]) -> None:
    """
    Save validation summary to JSON file.

    Args:
        results: List of validation results.
    """
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "passed": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "results": [r.to_dict() for r in results],
    }

    output_file = os.path.join(
        DATA_RAW_DIR,
        f"validation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )

    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Validation summary saved to {output_file}")


def main() -> int:
    """
    Main entry point for validation script.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    try:
        results = asyncio.run(run_all_validations())

        save_validation_summary(results)

        logger.info("=" * 60)
        logger.info("Validation Results Summary:")
        logger.info("=" * 60)

        for result in results:
            status = "✓ PASS" if result.success else "✗ FAIL"
            logger.info(f"{status}: {result.source} - {result.message}")

        # Determine exit code
        failed_count = sum(1 for r in results if not r.success)

        if failed_count == 0:
            logger.info("\n✓ All validation tests PASSED")
            return 0
        else:
            logger.error(f"\n✗ {failed_count} validation test(s) FAILED")
            return 1

    except Exception as e:
        logger.exception(f"Fatal error during validation: {str(e)}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
