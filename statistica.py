#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess

def run_cli():
    # Append src_python path to find correct packages
    sys.path.append(os.path.join(os.path.dirname(__file__), "src_python"))
    
    # 1. Dependency check (skip slow bootstrap on fast diagnostics-only scans)
    if not any(a == "--diagnostics-only" for a in sys.argv[1:]):
        from bootstrap import check_and_install_dependencies
        print("Checking dependencies...")
        check_and_install_dependencies()
    
    # 2. Build parser matching required signature
    parser = argparse.ArgumentParser(description="STATISTICA Offline Analysis Tool - Command Line Interface")
    parser.add_argument("dataset", type=str, help="Absolute or relative path to .xlsx / .xls / .csv file to analyze.")
    parser.add_argument("--output", "-o", type=str, default="./output", help="Output directory to deposit files.")
    parser.add_argument("--sheet", "-s", type=str, default=None, help="Name of of specific Excel worksheet to analyze.")
    parser.add_argument("--config", "-c", type=str, default=None, help="Optional JSON parameters file configuration.")
    parser.add_argument("--open", action="store_true", help="Launch native system file explorer on completion.")
    parser.add_argument("--diagnostics-only", action="store_true", help="Schema scan only (fast); skip full analysis pipeline.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset):
        print(f"Error: Target file draft not found: '{args.dataset}'")
        sys.exit(1)

    if args.diagnostics_only:
        from diagnostics import emit_diagnostics_json
        print(f"STATISTICA diagnostics scan: {args.dataset}")
        try:
            emit_diagnostics_json(args.dataset, args.sheet)
        except Exception as e:
            print(f"Diagnostics Failure: {e}")
            sys.exit(1)
        sys.exit(0)
        
    print(f"Initiating STATISTICA deep offline engine metrics on: {args.dataset}")

    cfg = None
    if args.config:
        import json
        if os.path.isfile(args.config):
            with open(args.config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = json.loads(args.config)
    
    # Import and run inner execution methods
    try:
        from analyzer import execute_automated_analytics
    except (ImportError, ModuleNotFoundError) as e:
        print(f"Scientific libraries (pandas/numpy/scipy) are absent. Switching to high-performance Pure-Python Analytical Engine...")
        from pure_python_analyzer import execute_pure_python_analytics as execute_automated_analytics
        
    try:
        output_folder = execute_automated_analytics(
            input_path=args.dataset,
            sheet_name=args.sheet,
            custom_output=args.output,
            raw_config=cfg,
            open_folder=args.open,
        )
        print("\n========================================================")
        print("STATISTICA ANALYTICS COMPLETED SUCCESSFULLY!")
        print(f"Generated Package Folder: {os.path.abspath(output_folder)}")
        print(f"Interactive Document Report: {os.path.join(output_folder, 'report.html')}")
        print(f"Academic Dissertation Layout: {os.path.join(output_folder, 'report.docx')}")
        print("========================================================\n")
        print(f"SUCCESS|{os.path.abspath(output_folder)}")
    except Exception as e:
        print(f"Engine Process Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()
