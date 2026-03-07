#!/usr/bin/env python3
"""
Complete Execution Pipeline - Steps 1-5
Orchestrates: Data fix → Verification → Visualization → Validation → Enhancement
"""

import subprocess
import sys
import logging
from datetime import datetime
from pathlib import Path
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExecutionOrchestrator:
    """Orchestrates complete pipeline execution"""
    
    def __init__(self):
        self.workspace = Path('c:\\Users\\haujo\\projects\\DEV\\Data_visualization')
        self.start_time = datetime.now()
        self.results = {}
    
    def run_python_script(self, script_name: str, description: str, args: list = None) -> bool:
        """Execute a Python script and track results"""
        try:
            logger.info("\n" + "="*80)
            logger.info(f"[STEP] {description}")
            logger.info("="*80)
            
            cmd = [sys.executable, str(self.workspace / script_name)]
            if args:
                cmd.extend(args)
            
            logger.info(f"Executing: {' '.join(cmd)}\n")
            
            result = subprocess.run(cmd, capture_output=False, text=True, timeout=600)  # 10 minute timeout
            
            if result.returncode == 0:
                logger.info(f"✅ {description} - PASSED")
                self.results[description] = 'PASSED'
                return True
            else:
                logger.error(f"❌ {description} - FAILED (exit code: {result.returncode})")
                self.results[description] = 'FAILED'
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {description} - TIMEOUT (exceeded 10 minutes)")
            self.results[description] = 'TIMEOUT'
            return False
        except Exception as e:
            logger.error(f"❌ {description} - ERROR: {str(e)}")
            self.results[description] = f'ERROR: {str(e)}'
            return False
    
    def print_separator(self, title: str):
        """Print decorative separator"""
        logger.info("\n" + "#"*80)
        logger.info(f"# {title.center(76)} #")
        logger.info("#"*80 + "\n")
    
    def execute_pipeline(self):
        """Execute complete pipeline"""
        self.print_separator("DATA VISUALIZATION PIPELINE - COMPLETE EXECUTION")
        
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Workspace: {self.workspace}")
        
        # STEP 1: Fix Precious Metals Data
        step1_pass = self.run_python_script(
            'precious_metals_supply_correction.py',
            'STEP 1: Fix Precious Metals Data (Critical)',
            []
        )
        
        if not step1_pass:
            logger.error("\n⚠️  STEP 1 FAILED - Cannot proceed without fixing data")
            logger.info("Manual intervention required. Check precious_metals_supply_correction.py")
            return False
        
        time.sleep(2)  # Brief pause between steps
        
        # STEP 2: Verify the Fix
        step2_pass = self.run_python_script(
            'data_integrity_audit.py',
            'STEP 2: Verify Data Fix (Audit)',
            []
        )
        
        if not step2_pass:
            logger.error("\n⚠️  STEP 2 FAILED - Data still has issues")
            logger.info("Review data_integrity_audit.py output for specifics")
            # Don't fail - continue to see what's wrong
        
        time.sleep(2)
        
        # STEP 3: Regenerate Rankings and Visualization
        logger.info("\n" + "="*80)
        logger.info("[STEP] STEP 3A: Rebuild Rankings from Fixed Data")
        logger.info("="*80)
        step3a_pass = self.run_python_script(
            'scripts/02_build_rankings.py',
            'STEP 3A: Rebuild Rankings',
            []
        )
        
        time.sleep(2)
        
        logger.info("\n" + "="*80)
        logger.info("[STEP] STEP 3B: Generate Visualization")
        logger.info("="*80)
        step3b_pass = self.run_python_script(
            'scripts/03_build_visualizations.py',
            'STEP 3B: Generate Visualization',
            [
                '--input_path', 'data/processed/top20_monthly.parquet',
                '--output_path', 'data/processed/bar_race_top20.html'
            ]
        )
        
        step3_pass = step3a_pass and step3b_pass
        
        time.sleep(2)
        
        # STEP 4: Validate Against 8marketcap Reference
        step4_pass = self.run_python_script(
            'qa_validation_agent.py',
            'STEP 4: QA Validation - Compare Against 8marketcap.com Reference',
            []
        )
        
        if not step4_pass:
            logger.error("\n⚠️  STEP 4 FAILED - Data doesn't match 8marketcap.com reference")
            logger.info("\n📋 ESCALATING TO TROUBLESHOOTING SPECIALIST AGENT")
            logger.info("   Reason: Ranking/value mismatches detected")
            self.results['STEP 4: QA Validation'] = 'FAILED - ESCALATE TO TROUBLESHOOTING'
            # Don't fail - still try to enhance visualization
        
        time.sleep(2)
        
        # STEP 5: Enhance Visualization with Logos & Full-Page Layout
        step5_pass = self.run_python_script(
            'enhanced_visualization_builder_phase5.py',
            'STEP 5: Enhance Visualization - Add Logos & Full-Page Layout',
            []
        )
        
        # Print Summary
        self.print_separator("PIPELINE EXECUTION SUMMARY")
        
        logger.info("Step Results:")
        logger.info(f"  1. Fix Precious Metals Data:        {self.results.get('STEP 1: Fix Precious Metals Data (Critical)', 'SKIPPED')}")
        logger.info(f"  2. Verify Data Fix:                 {self.results.get('STEP 2: Verify Data Fix (Audit)', 'SKIPPED')}")
        logger.info(f"  3. Regenerate Visualization:        {self.results.get('STEP 3A: Rebuild Rankings', 'SKIPPED')} / {self.results.get('STEP 3B: Generate Visualization', 'SKIPPED')}")
        logger.info(f"  4. QA Validation:                   {self.results.get('STEP 4: QA Validation - Compare Against 8marketcap.com Reference', 'SKIPPED')}")
        logger.info(f"  5. Enhancement (Logos & Layout):    {self.results.get('STEP 5: Enhance Visualization - Add Logos & Full-Page Layout', 'SKIPPED')}")
        
        # Overall result
        critical_steps_passed = step1_pass and step3_pass
        
        if critical_steps_passed:
            logger.info("\n" + "="*80)
            logger.info("✅ CORE PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            
            if not step4_pass:
                logger.info("\n⚠️  QA VALIDATION CONCERNS:")
                logger.info("   - Review logs for ranking/value mismatches")
                logger.info("   - Check: logs/qa_validation_report_*.json")
                logger.info("   - Check: data/processed/qa_comparison_current_vs_reference.csv")
            
            if step5_pass:
                logger.info("\n✨ ENHANCED VISUALIZATION READY:")
                logger.info("   Open: data/processed/bar_race_top20_enhanced.html")
            else:
                logger.info("\nOriginal visualization available:")
                logger.info("   Open: data/processed/bar_race_top20.html")
            
            return True
        else:
            logger.error("\n" + "="*80)
            logger.error("❌ PIPELINE FAILED - CRITICAL STEPS DID NOT PASS")
            logger.error("="*80)
            return False
    
    def print_next_steps(self):
        """Print recommended next steps"""
        logger.info("\n" + "="*80)
        logger.info("NEXT STEPS")
        logger.info("="*80)
        
        if self.results.get('STEP 4: QA Validation - Compare Against 8marketcap.com Reference') == 'FAILED - ESCALATE TO TROUBLESHOOTING':
            logger.info("\n1. REVIEW QA VALIDATION REPORT")
            logger.info("   File: logs/qa_validation_report_*.json")
            logger.info("   File: data/processed/qa_comparison_current_vs_reference.csv")
            logger.info("")
            logger.info("2. IDENTIFY MISMATCHES")
            logger.info("   Compare your data against 8marketcap.com reference")
            logger.info("")
            logger.info("3. APPLY FIXES")
            logger.info("   Update source data or configuration as needed")
            logger.info("")
            logger.info("4. RE-RUN PIPELINE")
            logger.info("   python complete_execution_pipeline.py")
        
        logger.info("\n5. VIEW FINAL VISUALIZATION")
        logger.info("   Open in browser: data/processed/bar_race_top20_enhanced.html")
        logger.info("")
        logger.info("6. DEPLOY")
        logger.info("   Share the HTML file - it's standalone, no dependencies needed")


if __name__ == '__main__':
    orchestrator = ExecutionOrchestrator()
    
    try:
        success = orchestrator.execute_pipeline()
        orchestrator.print_next_steps()
        
        end_time = datetime.now()
        duration = (end_time - orchestrator.start_time).total_seconds()
        
        logger.info("\n" + "="*80)
        logger.info(f"Execution completed in {duration:.1f} seconds ({duration/60:.1f} minutes)")
        logger.info("="*80)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"\n❌ PIPELINE ERRORR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
