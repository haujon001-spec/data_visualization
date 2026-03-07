# -*- coding: utf-8 -*-
"""
Phase 1 Orchestrator - ETL Pipeline Executor

Orchestrates the complete ETL pipeline:
1. Fetch GDP (World Bank)
2. Fetch Population (World Bank)
3. Fetch Debt (World Bank IDS + IMF fallback)
4. Transform/Merge/Clean
5. Data QA Validation
6. Code/Output Verification

Emits heartbeat every 5 seconds to log file.
Returns structured JSON result with status, outputs, and verification results.

Output: reports/logs/orchestrator_log_<timestamp>.txt
        reports/etl_result_<timestamp>.json
"""

import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
import time
import sys
import os

# Configure logging (both console and file)
class DualLogger:
    """Logger that writes to both console and file."""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.console_logger = logging.getLogger('console')
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(
            logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
        )
        self.console_logger.addHandler(self.console_handler)
        self.console_logger.setLevel(logging.INFO)
    
    def info(self, msg):
        self.console_logger.info(msg)
        with open(self.log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - [INFO] {msg}\n")
    
    def error(self, msg):
        self.console_logger.error(msg)
        with open(self.log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - [ERROR] {msg}\n")
    
    def warning(self, msg):
        self.console_logger.warning(msg)
        with open(self.log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - [WARNING] {msg}\n")


class Phase1Orchestrator:
    """Orchestrates Phase 1 ETL pipeline."""
    
    def __init__(self, project_root: Path = None):
        """Initialize orchestrator."""
        self.project_root = project_root or Path(__file__).parent.parent
        self.start_time = datetime.now()
        self.orchestrator_pid = os.getpid()
        
        # Setup logging
        log_file = self.project_root / 'reports' / 'logs' / f'orchestrator_{self.start_time.strftime("%Y%m%d_%H%M%S")}.txt'
        self.logger = DualLogger(log_file)
        self.heartbeat_file = log_file
        
        # Results container
        self.results = {
            'timestamp': self.start_time.isoformat(),
            'orchestrator_pid': self.orchestrator_pid,
            'project_root': str(self.project_root),
            'steps': [],
            'overall_status': 'FAIL',
            'outputs': {},
            'verification': {}
        }
        
        # Define pipeline steps
        self.steps = [
            {'name': 'Fetch GDP', 'script': 'scripts/01_fetch_gdp.py'},
            {'name': 'Fetch Population', 'script': 'scripts/01_fetch_population.py'},
            {'name': 'Fetch Debt', 'script': 'scripts/03_fetch_debt.py'},
            {'name': 'Transform/Merge/Clean', 'script': 'scripts/04_transform_merge_clean.py'},
            {'name': 'Data QA', 'script': 'qa_agents/agent_data_qa.py'},
            {'name': 'Verification', 'script': 'verification/verify_all.py'}
        ]
    
    def emit_heartbeat(self, phase: str, step: int, status: str):
        """Emit heartbeat to log file."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        heartbeat = (
            f"[HEARTBEAT] orchestrator_pid={self.orchestrator_pid}, "
            f"timestamp={datetime.now().isoformat()}, "
            f"phase={phase}, "
            f"step={step}/{len(self.steps)}, "
            f"elapsed_seconds={elapsed:.1f}, "
            f"status={status}"
        )
        
        with open(self.heartbeat_file, 'a') as f:
            f.write(heartbeat + '\n')
    
    def run_script(self, script_name: str, step_num: int) -> bool:
        """Run a single pipeline step."""
        step_name = self.steps[step_num - 1]['name']
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"[STEP {step_num}/{len(self.steps)}] {step_name}")
        self.logger.info(f"{'='*70}")
        
        self.emit_heartbeat(
            phase='ETL',
            step=step_num,
            status=f'RUNNING_{step_name.replace(" ", "_").replace("/", "_")}'
        )
        
        script_path = self.project_root / script_name
        
        if not script_path.exists():
            self.logger.error(f"Script not found: {script_path}")
            self.emit_heartbeat(phase='ETL', step=step_num, status='FAILED')
            return False
        
        try:
            self.logger.info(f"[EXEC] {script_path}")
            
            # Run script with Python interpreter
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per step
            )
            
            # Log output
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.logger.info(f"[OUTPUT] {line}")
            
            if result.returncode != 0:
                self.logger.error(f"Step failed with return code: {result.returncode}")
                if result.stderr:
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            self.logger.error(f"[ERROR] {line}")
                
                self.emit_heartbeat(phase='ETL', step=step_num, status='FAILED')
                return False
            
            self.logger.info(f"[SUCCESS] {step_name} completed")
            self.emit_heartbeat(phase='ETL', step=step_num, status='COMPLETED')
            
            # Record step result
            self.results['steps'].append({
                'step_number': step_num,
                'step_name': step_name,
                'script': script_name,
                'status': 'PASS',
                'timestamp': datetime.now().isoformat()
            })
            
            return True
        
        except subprocess.TimeoutExpired:
            self.logger.error(f"Step timeout after 300 seconds")
            self.emit_heartbeat(phase='ETL', step=step_num, status='TIMEOUT')
            self.results['steps'].append({
                'step_number': step_num,
                'step_name': step_name,
                'script': script_name,
                'status': 'TIMEOUT',
                'timestamp': datetime.now().isoformat()
            })
            return False
        
        except Exception as e:
            self.logger.error(f"Step exception: {str(e)}")
            self.emit_heartbeat(phase='ETL', step=step_num, status='ERROR')
            self.results['steps'].append({
                'step_number': step_num,
                'step_name': step_name,
                'script': script_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def discover_outputs(self):
        """Discover and record output files."""
        self.logger.info("\n[DISCOVERY] Locating output files...")
        
        import glob
        
        output_patterns = [
            ('csv/raw', 'gdp_raw_*.csv'),
            ('csv/raw', 'population_raw_*.csv'),
            ('csv/raw', 'debt_raw_*.csv'),
            ('csv/processed', 'macro_*.csv'),
            ('reports/qa', 'data_qa_report_*.json'),
            ('reports/qa', 'data_qa_summary_*.md'),
        ]
        
        for subdir, pattern in output_patterns:
            full_pattern = str(self.project_root / subdir / pattern)
            matches = glob.glob(full_pattern)
            
            if matches:
                latest = max(matches, key=lambda p: Path(p).stat().st_mtime)
                self.results['outputs'][pattern] = {
                    'path': str(Path(latest).relative_to(self.project_root)),
                    'size_bytes': Path(latest).stat().st_size,
                    'modified': datetime.fromtimestamp(Path(latest).stat().st_mtime).isoformat()
                }
                self.logger.info(f"[FOUND] {Path(latest).relative_to(self.project_root)}")
            else:
                self.logger.warning(f"[MISSING] {subdir}/{pattern}")
    
    def run_pipeline(self) -> bool:
        """Run complete ETL pipeline."""
        self.logger.info("=" * 70)
        self.logger.info("PHASE 1 ETL ORCHESTRATOR")
        self.logger.info("=" * 70)
        self.logger.info(f"Start Time: {self.start_time.isoformat()}")
        self.logger.info(f"Project Root: {self.project_root}")
        self.logger.info(f"Orchestrator PID: {self.orchestrator_pid}")
        
        # Run each step
        all_passed = True
        
        for step_num in range(1, len(self.steps) + 1):
            script = self.steps[step_num - 1]['script']
            
            if not self.run_script(script, step_num):
                all_passed = False
                self.logger.error(f"Pipeline halted at step {step_num}")
                break
            
            # Brief heartbeat between steps
            time.sleep(0.5)
        
        # Discover outputs
        self.discover_outputs()
        
        # Final heartbeat
        if all_passed:
            self.emit_heartbeat(phase='ETL', step=len(self.steps), status='COMPLETED_ALL')
            self.results['overall_status'] = 'PASS'
        else:
            self.emit_heartbeat(phase='ETL', step=len(self.steps), status='FAILED')
            self.results['overall_status'] = 'FAIL'
        
        # Log summary
        self.logger.info("\n" + "=" * 70)
        self.logger.info("ORCHESTRATION SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"Overall Status: {self.results['overall_status']}")
        self.logger.info(f"Steps Completed: {sum(1 for s in self.results['steps'] if s['status'] == 'PASS')}/{len(self.steps)}")
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(f"Elapsed Time: {elapsed:.1f} seconds")
        self.logger.info("=" * 70)
        
        return all_passed
    
    def save_results(self) -> Path:
        """Save results JSON."""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        results_file = self.project_root / 'reports' / f'etl_result_{timestamp}.json'
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"\n[SAVE] Results saved to {results_file.relative_to(self.project_root)}")
        
        return results_file


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    
    orchestrator = Phase1Orchestrator(project_root)
    
    # Run pipeline
    success = orchestrator.run_pipeline()
    
    # Save results
    orchestrator.save_results()
    
    # Return appropriate exit code
    if success:
        orchestrator.logger.info("\n[SUCCESS] PHASE 1 ETL COMPLETED SUCCESSFULLY")
        return 0
    else:
        orchestrator.logger.error("\n[FAILED] PHASE 1 ETL FAILED")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
