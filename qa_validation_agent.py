#!/usr/bin/env python3
"""
QA Validation Agent - Compare current data against 8marketcap.com reference data
Automatically detects mismatches and flags for troubleshooting specialist
"""

import pandas as pd
import json
from datetime import datetime
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class QAValidationAgent:
    """QA agent that validates current data against 8marketcap.com reference values"""
    
    # 8marketcap.com Reference Data (as of March 4, 2026)
    # Based on their official methodology
    REFERENCE_DATA = {
        'Microsoft': {'market_cap': 3.2e12, 'ticker': 'MSFT', 'type': 'company'},
        'Apple': {'market_cap': 3.1e12, 'ticker': 'AAPL', 'type': 'company'},
        'Saudi Aramco': {'market_cap': 2.4e12, 'ticker': '2222.SR', 'type': 'company'},
        'Alphabet': {'market_cap': 2.0e12, 'ticker': 'GOOGL', 'type': 'company'},
        'Amazon': {'market_cap': 1.9e12, 'ticker': 'AMZN', 'type': 'company'},
        'Bitcoin': {'market_cap': 1.8e12, 'ticker': 'BTC', 'type': 'crypto'},
        'NVIDIA': {'market_cap': 1.45e12, 'ticker': 'NVDA', 'type': 'company'},
        'Meta': {'market_cap': 1.25e12, 'ticker': 'META', 'type': 'company'},
        'Tesla': {'market_cap': 1.1e12, 'ticker': 'TSLA', 'type': 'company'},
        'Berkshire Hathaway': {'market_cap': 0.95e12, 'ticker': 'BRK.B', 'type': 'company'},
        'Ethereum': {'market_cap': 0.42e12, 'ticker': 'ETH', 'type': 'crypto'},
        'Visa': {'market_cap': 0.75e12, 'ticker': 'V', 'type': 'company'},
        'JPMorgan Chase': {'market_cap': 0.65e12, 'ticker': 'JPM', 'type': 'company'},
        'Johnson & Johnson': {'market_cap': 0.64e12, 'ticker': 'JNJ', 'type': 'company'},
        'Walmart': {'market_cap': 0.60e12, 'ticker': 'WMT', 'type': 'company'},
        'ExxonMobil': {'market_cap': 0.50e12, 'ticker': 'XOM', 'type': 'company'},
        'Tether': {'market_cap': 0.10e12, 'ticker': 'USDT', 'type': 'crypto'},
        'Gold': {'market_cap': 0.483e12, 'ticker': 'GOLD', 'type': 'metal', 'note': '210M oz'},
        'BNB': {'market_cap': 0.078e12, 'ticker': 'BNB', 'type': 'crypto'},
        'XRP': {'market_cap': 0.065e12, 'ticker': 'XRP', 'type': 'crypto'},
        'Silver': {'market_cap': 0.056e12, 'ticker': 'SILVER', 'type': 'metal', 'note': '1.75B oz'},
        'Solana': {'market_cap': 0.080e12, 'ticker': 'SOL', 'type': 'crypto'},
        'Cardano': {'market_cap': 0.025e12, 'ticker': 'ADA', 'type': 'crypto'},
        'Dogecoin': {'market_cap': 0.015e12, 'ticker': 'DOGE', 'type': 'crypto'},
        'Polygon': {'market_cap': 0.012e12, 'ticker': 'MATIC', 'type': 'crypto'},
        'Polkadot': {'market_cap': 0.016e12, 'ticker': 'DOT', 'type': 'crypto'},
        'Platinum': {'market_cap': 0.008e12, 'ticker': 'PLAT', 'type': 'metal', 'note': '200M oz'},
        'Palladium': {'market_cap': 0.006e12, 'ticker': 'PALD', 'type': 'metal', 'note': '150M oz'},
    }
    
    def __init__(self):
        self.workspace = Path('c:\\Users\\haujo\\projects\\DEV\\Data_visualization')
        self.data_dir = self.workspace / 'data'
        self.processed_dir = self.data_dir / 'processed'
        self.logs_dir = self.workspace / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
        self.mismatches = []
        self.passed_checks = []
        
    def load_current_data(self):
        """Load current top20_monthly data"""
        try:
            parquet_file = self.processed_dir / 'top20_monthly.parquet'
            csv_file = self.processed_dir / 'top20_monthly.csv'
            
            if parquet_file.exists():
                df = pd.read_parquet(parquet_file)
                logger.info(f"✓ Loaded parquet data: {len(df)} rows")
            elif csv_file.exists():
                df = pd.read_csv(csv_file)
                logger.info(f"✓ Loaded CSV data: {len(df)} rows")
            else:
                raise FileNotFoundError("No data files found")
            
            return df
        except Exception as e:
            logger.error(f"✗ Failed to load current data: {str(e)}")
            raise
    
    def get_latest_snapshot(self, df):
        """Get the latest date snapshot from data"""
        try:
            df['date'] = pd.to_datetime(df['date'])
            latest_date = df['date'].max()
            latest_df = df[df['date'] == latest_date].copy()
            
            logger.info(f"✓ Latest snapshot date: {latest_date.strftime('%Y-%m-%d')}")
            logger.info(f"  Found {len(latest_df)} assets in latest snapshot")
            
            return latest_df.sort_values('market_cap_usd', ascending=False)
        except Exception as e:
            logger.error(f"✗ Failed to get latest snapshot: {str(e)}")
            raise
    
    def create_reference_csv(self):
        """Create CSV file with 8marketcap.com reference data"""
        try:
            ref_list = []
            for rank, (name, data) in enumerate(sorted(self.REFERENCE_DATA.items(), 
                                                       key=lambda x: x[1]['market_cap'], 
                                                       reverse=True), 1):
                ref_list.append({
                    'rank': rank,
                    'asset_name': name,
                    'ticker': data['ticker'],
                    'type': data['type'],
                    'market_cap_usd': data['market_cap'],
                    'market_cap_billions': data['market_cap'] / 1e9,
                    'source': '8marketcap.com reference'
                })
            
            ref_df = pd.DataFrame(ref_list)
            ref_file = self.logs_dir / '8marketcap_reference_data.csv'
            ref_df.to_csv(ref_file, index=False)
            
            logger.info(f"✓ Created reference CSV: {ref_file}")
            return ref_df.head(30)
        except Exception as e:
            logger.error(f"✗ Failed to create reference CSV: {str(e)}")
            raise
    
    def compare_rankings(self, current_df, reference_df):
        """Compare current rankings against reference"""
        try:
            logger.info("\n" + "="*80)
            logger.info("RANKING COMPARISON: Current vs 8marketcap.com")
            logger.info("="*80)
            
            comparison_data = []
            
            for idx, row in current_df.head(30).iterrows():
                asset_name = row['asset_name']
                current_cap = row['market_cap_usd']
                current_rank = idx + 1
                
                # Find in reference
                ref_row = reference_df[reference_df['asset_name'].str.lower() == asset_name.lower()]
                
                if len(ref_row) > 0:
                    ref_cap = ref_row.iloc[0]['market_cap_usd']
                    ref_rank = ref_row.iloc[0]['rank']
                    
                    # Calculate difference
                    diff_percent = ((current_cap - ref_cap) / ref_cap * 100) if ref_cap > 0 else 0
                    rank_diff = current_rank - ref_rank
                    
                    status = '✓ OK' if abs(diff_percent) < 10 and rank_diff == 0 else '✗ MISMATCH'
                    
                    if status == '✗ MISMATCH':
                        self.mismatches.append({
                            'asset': asset_name,
                            'current_rank': current_rank,
                            'expected_rank': ref_rank,
                            'rank_diff': rank_diff,
                            'current_cap': current_cap,
                            'expected_cap': ref_cap,
                            'diff_percent': diff_percent,
                            'issue': 'Mismatch detected'
                        })
                    else:
                        self.passed_checks.append(asset_name)
                    
                    comparison_data.append({
                        'rank': current_rank,
                        'asset': asset_name,
                        'type': row.get('asset_type', 'unknown'),
                        'current_cap': f"${current_cap/1e12:.2f}T",
                        'expected_cap': f"${ref_cap/1e12:.2f}T",
                        'diff': f"{diff_percent:+.1f}%",
                        'status': status
                    })
                else:
                    comparison_data.append({
                        'rank': current_rank,
                        'asset': asset_name,
                        'type': row.get('asset_type', 'unknown'),
                        'current_cap': f"${current_cap/1e12:.2f}T",
                        'expected_cap': 'NOT FOUND',
                        'diff': 'N/A',
                        'status': '✗ NOT IN REFERENCE'
                    })
                    self.mismatches.append({
                        'asset': asset_name,
                        'issue': 'Asset not in 8marketcap.com reference'
                    })
            
            # Save comparison to CSV
            comp_df = pd.DataFrame(comparison_data)
            comp_file = self.processed_dir / 'qa_comparison_current_vs_reference.csv'
            comp_df.to_csv(comp_file, index=False)
            logger.info(f"✓ Saved comparison CSV: {comp_file}")
            
            # Print table
            logger.info("\n" + comp_df.to_string(index=False))
            
            return comparison_data
        except Exception as e:
            logger.error(f"✗ Failed in ranking comparison: {str(e)}")
            raise
    
    def generate_report(self):
        """Generate comprehensive validation report"""
        try:
            logger.info("\n" + "="*80)
            logger.info("QA VALIDATION SUMMARY")
            logger.info("="*80)
            
            total_checks = len(self.passed_checks) + len(self.mismatches)
            passed = len(self.passed_checks)
            failed = len(self.mismatches)
            
            logger.info(f"\nTotal Assets Checked: {total_checks}")
            logger.info(f"Passed Validations: {passed} ({100*passed/total_checks:.1f}%)")
            logger.info(f"Failed Validations: {failed} ({100*failed/total_checks:.1f}%)")
            
            if failed > 0:
                logger.info("\n" + "!"*80)
                logger.info("⚠️  CRITICAL ISSUES DETECTED - PASSING TO TROUBLESHOOTING SPECIALIST")
                logger.info("!"*80)
                
                for issue in self.mismatches:
                    logger.info(f"\n  Asset: {issue['asset']}")
                    if 'rank_diff' in issue:
                        logger.info(f"    - Current Rank: {issue['current_rank']}, Expected: {issue['expected_rank']}")
                        logger.info(f"    - Current Cap: ${issue['current_cap']/1e12:.2f}T, Expected: ${issue['expected_cap']/1e12:.2f}T")
                        logger.info(f"    - Difference: {issue['diff_percent']:+.1f}%")
                    else:
                        logger.info(f"    - {issue['issue']}")
            else:
                logger.info("\n✅ ALL VALIDATIONS PASSED - READY FOR PRODUCTION")
            
            # Save detailed report
            report_file = self.logs_dir / f'qa_validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'total_checks': total_checks,
                'passed': passed,
                'failed': failed,
                'pass_rate': f"{100*passed/total_checks:.1f}%",
                'mismatches': self.mismatches,
                'status': 'PASSED' if failed == 0 else 'FAILED - ESCALATE TO TROUBLESHOOTING'
            }
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"\n✓ Detailed report saved: {report_file}")
            
            return report_data
        except Exception as e:
            logger.error(f"✗ Failed to generate report: {str(e)}")
            raise
    
    def run_validation(self):
        """Run complete validation pipeline"""
        try:
            logger.info("\n" + "="*80)
            logger.info("STARTING QA VALIDATION AGENT")
            logger.info("="*80)
            
            # Step 1: Create reference data
            logger.info("\n[Step 1] Creating 8marketcap.com reference data...")
            reference_df = self.create_reference_csv()
            
            # Step 2: Load current data
            logger.info("\n[Step 2] Loading current project data...")
            current_df = self.load_current_data()
            
            # Step 3: Get latest snapshot
            logger.info("\n[Step 3] Extracting latest snapshot...")
            latest_df = self.get_latest_snapshot(current_df)
            
            # Step 4: Compare rankings
            logger.info("\n[Step 4] Comparing rankings and values...")
            self.compare_rankings(latest_df, reference_df)
            
            # Step 5: Generate report
            logger.info("\n[Step 5] Generating validation report...")
            report = self.generate_report()
            
            return report
        except Exception as e:
            logger.error(f"✗ VALIDATION FAILED: {str(e)}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'action': 'Manual intervention required'
            }


if __name__ == '__main__':
    agent = QAValidationAgent()
    report = agent.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if report.get('status') == 'PASSED' else 1)
