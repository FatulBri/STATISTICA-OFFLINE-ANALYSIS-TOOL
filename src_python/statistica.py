#!/usr/bin/env python
"""
STATISTICA Offline Analysis Tool - Core Command Line Dispatcher
Supports fully customizable scientific statistical and financial modeling on local datasets.
"""

import os
import sys
import argparse
import json
import logging
from typing import Dict, List, Any

# Ensure parent directory is in python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bootstrap import check_and_install_dependencies
from data_manager import DataManager
from stat_engine import StatEngine
from psychometrics import PsychometricsEngine
from financial import FinancialEngine
from viz_engine import VisualEngine
from report_generator import ReportGenerator

# Setup master logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] STATISTICA: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("statistica_cli")

def run_pipeline(input_path: str, output_folder: str, open_folder: bool = False) -> None:
    """Run full automated analytical routing depending on spreadsheet features."""
    logger.info("Initializing STATISTICA offline analytics pipeline...")
    
    # 1. Dependency checklist
    check_and_install_dependencies()
    
    # 2. File Verification
    if not os.path.exists(input_path):
        logger.error(f"Target data file does not exist: {input_path}")
        sys.exit(1)
        
    # Prepare Output Directories
    os.makedirs(output_folder, exist_ok=True)
    
    # 3. Load input dataset
    dm = DataManager(input_path)
    df = dm.load_data()
    summary = dm.get_summary_stats()
    
    logger.info(f"Loaded successfully! {summary['rows']} row items indexed with {summary['columns']} active attributes.")
    logger.info(f"Auto-recommendation vectors: {summary['recommendations']}")
    
    # Setup visualization drawer
    viz = VisualEngine(output_folder)
    
    # Run stats
    results_compiled: Dict[str, Any] = {}
    results_compiled["fileName"] = summary["fileName"]
    results_compiled["rows"] = summary["rows"]
    results_compiled["columns"] = summary["columns"]
    results_compiled["duplicates"] = summary["duplicates"]
    
    # Run General Descriptive Statistics
    num_cols = summary["numericColumns"]
    if num_cols:
        logger.info(f"Generating continuous descriptors for: {num_cols[:5]}...")
        desc_res = StatEngine.descriptive_statistics(df, num_cols)
        results_compiled["descriptive"] = desc_res
        
        # Build first distribution histogram automatically as visual verification
        primary_num = num_cols[0]
        viz.generate_histogram(df, primary_num)
        viz.generate_boxplot(df, primary_num)
        viz.generate_qq_plot(df, primary_num)
        
    # Heatmap setup
    if len(num_cols) >= 2:
        logger.info("Computing Pearson multivariate correlation matrix...")
        corr_res = StatEngine.correlation_matrix(df, num_cols[:8])
        results_compiled["correlation"] = corr_res
        viz.generate_heatmap(corr_res)
        
        # Simple Linear regression of top two numeric columns
        reg_res = StatEngine.linear_regression(df, num_cols[0], [num_cols[1]])
        results_compiled["regression"] = reg_res
        viz.generate_scatter_trend(df, num_cols[1], num_cols[0])

    # Module Trigger logic: Psychometrics
    run_psych = False
    bin_cols = summary["binaryColumns"]
    if len(bin_cols) >= 5 or len(num_cols) >= 5:
        run_psych = True
        logger.info("Triggering Scientific Psychometrics Module...")
        target_psy_cols = bin_cols if len(bin_cols) >= 5 else num_cols[:8]
        results_compiled["kmo_bartlett"] = PsychometricsEngine.calculate_kmo_bartlett(df, target_psy_cols)
        results_compiled["efa"] = PsychometricsEngine.run_efa_scree(df, target_psy_cols)
        
        # Scree Plot visualization
        viz.generate_scree_plot(results_compiled["efa"]["eigenvalues"])
        
        if len(bin_cols) >= 5:
            # 2PL IRF
            logger.info("Fitting 2-Parameter Logistic (2PL) Item Response Function model...")
            results_compiled["irt_2pl"] = PsychometricsEngine.fit_irt_2pl(df, bin_cols[:8])
            
    # Module Trigger logic: Financial Analyst
    run_fin = False
    finance_keywords = ["price", "close", "open", "high", "low", "returns"]
    has_market_col = any(any(kw in c.lower() for kw in finance_keywords) for c in df.columns)
    
    if has_market_col:
        run_fin = True
        # Find close price matching key
        close_col = None
        for col in df.columns:
            if any(kw in col.lower() for kw in ["close", "price"]):
                close_col = col
                break
        if not close_col:
            close_col = num_cols[0] if num_cols else None
            
        if close_col:
            logger.info(f"Triggering Portfolio Finance Module. Target Stock Series: {close_col}")
            df_ind = FinancialEngine.calculate_indicators(df, close_col)
            results_compiled["risk_return"] = FinancialEngine.risk_return_metrics(df, close_col)
            results_compiled["arima_forecast"] = FinancialEngine.arima_forecast(df, close_col)
            results_compiled["garch_volatility"] = FinancialEngine.run_garch_volatility(df, close_col)
            
            # Save visual outputs
            viz.generate_financial_chart(df_ind, close_col)
            viz.generate_drawdown_plot(results_compiled["risk_return"]["drawdowns_series"])

    # Export compiled static formats
    logger.info("Initializing static templates composition...")
    report = ReportGenerator(output_folder)
    report.generate_html_report(results_compiled)
    report.generate_docx_report(results_compiled)
    
    # Write diagnostic summary dataset as standard JSON payload
    summary_path = os.path.join(output_folder, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results_compiled, f, indent=2, default=str)
        
    logger.info("✓ Complete analytical loop compiled flawlessly on disk!")
    logger.info(f"See outputs in targeted folder: {output_folder}")
    
    if open_folder:
        try:
            import subprocess
            if sys.platform == "win32":
                os.startfile(output_folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", output_folder])
            else:
                subprocess.Popen(["xdg-open", output_folder])
        except Exception as e:
            logger.warning(f"Failed to auto-open target directory: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="STATISTICA Offline Scientific Analytical Platform")
    parser.add_argument("dataset", help="Input spreadsheet path of format .xlsx/.xls/.csv")
    parser.add_argument("-o", "--output", default="./output/dataset_name", help="Specific output directory structure destination")
    parser.add_argument("--open", action="store_true", help="Launch native Explorer to reveal target compiled assets instantly")
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    dest_path = args.output
    if dest_path == "./output/dataset_name":
        # Extract direct name from filename to match requirements
        base_name = os.path.splitext(os.path.basename(args.dataset))[0]
        dest_path = f"./output/{base_name}"
        
    run_pipeline(args.dataset, dest_path, args.open)
