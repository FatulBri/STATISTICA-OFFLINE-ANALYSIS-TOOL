import os
import sys
import json
import argparse
import logging
import math
import pandas as pd
import numpy as np

# Configure standard logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] STATISTICA ANALYZER: %(message)s'
)
logger = logging.getLogger("analyzer")


def make_json_safe(value):
    """Recursively convert numpy/pandas values and non-finite numbers into strict JSON."""
    if isinstance(value, dict):
        return {str(k): make_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [make_json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return [make_json_safe(v) for v in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, (pd.Timestamp, pd.Timedelta)):
        return str(value)
    return value

# Include paths to sibling engines
from data_manager import DataManager
from stat_engine import StatEngine
from psychometrics import PsychometricsEngine
from financial import FinancialEngine
from viz_engine import VisualEngine
from analysis_config import resolve_analysis_config
import reporter

def parse_args():
    parser = argparse.ArgumentParser(description="STATISTICA Offline Engine Automated Runner")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input Excel or CSV dataset")
    parser.add_argument("--sheet", "-s", type=str, default=None, help="Name of active sheet if workbook inputs")
    parser.add_argument("--output", "-o", type=str, default=None, help="Destination folder for exported HTML/DOCX reports")
    parser.add_argument("--config", "-c", type=str, default=None, help="Optional raw JSON config query defining parameters")
    parser.add_argument("--open", action="store_true", help="Launch native explorer on completing analysis")
    return parser.parse_args()

def execute_automated_analytics(
    input_path: str,
    sheet_name: str = None,
    custom_output: str = None,
    raw_config: dict = None,
    open_folder: bool = False,
) -> str:
    """Core analytical dispatcher."""
    logger.info(f"Loading incoming dataset file: {input_path}")
    
    # 1. Initialize data manager
    manager = DataManager(input_path)
    effective_sheet = (raw_config or {}).get("sheet") or sheet_name
    df = manager.load_data(effective_sheet)
    diagnostics = manager.get_summary_stats()
    cfg = resolve_analysis_config(raw_config, diagnostics, df)
    
    # Determine column categories from diagnostics (numeric, categorical, etc.)
    num_cols = diagnostics["numericColumns"]
    cat_cols = diagnostics["categoricalColumns"]
    bin_cols = diagnostics["binaryColumns"]
    date_cols = diagnostics["dateColumns"]

    # Impute missing values if configured
    if cfg.impute_missing:
        df = StatEngine.impute_missing_values(df, num_cols, cat_cols)
    
    
    # Define primary dataset identifier
    dataset_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # Determine outputs directory path
    base_out = custom_output or "./output"
    output_dir = os.path.join(base_out, dataset_name)
    os.makedirs(output_dir, exist_ok=True)

    # 2. Setup engines
    viz = VisualEngine(output_dir, dpi=cfg.export_dpi)
    
    # Column lists already defined earlier; no need to redefine here.
    
    analysis_stats = {
        "fileName": diagnostics["fileName"],
        "rows": diagnostics["rows"],
        "columns": diagnostics["columns"],
        "duplicates": diagnostics["duplicates"],
        "recommendations": diagnostics["recommendations"],
        "appliedConfig": cfg.applied,
        "descriptive": {},
        "normality": {},
        "outliers": {}
    }
    
    # A. CORE STATISTICAL ANALYSES
    if cfg.descriptive_columns:
        analysis_stats["descriptive"] = StatEngine.descriptive_statistics(df, cfg.descriptive_columns)
        
        for col in cfg.normality_columns:
            analysis_stats["normality"][col] = StatEngine.normality_test(df, col)
            analysis_stats["outliers"][col] = StatEngine.detect_outliers(df, col)
            viz.generate_histogram(df, col)
            viz.generate_boxplot(df, col)
            viz.generate_qq_plot(df, col)
            
    if len(cfg.correlation_columns) >= 2:
        corr_pearson = StatEngine.correlation_matrix(df, cfg.correlation_columns, method='pearson')
        corr_spearman = StatEngine.correlation_matrix(df, cfg.correlation_columns, method='spearman')
        analysis_stats["correlation"] = corr_pearson
        analysis_stats["correlation_pearson"] = corr_pearson
        analysis_stats["correlation_spearman"] = corr_spearman
        viz.generate_heatmap(corr_pearson)
        
    if cfg.regression_target and cfg.regression_predictors:
        reg_res = StatEngine.linear_regression(df, cfg.regression_target, cfg.regression_predictors)
        analysis_stats["linear_regression"] = reg_res
        viz.generate_scatter_trend(df, cfg.regression_predictors[0], cfg.regression_target)
        
        # Random Forest Regression
        rf_reg = StatEngine.random_forest_regression(df, cfg.regression_target, cfg.regression_predictors)
        analysis_stats["random_forest_regression"] = rf_reg
        if not rf_reg.get("error"):
            viz.generate_feature_importance_plot(rf_reg, "random_forest_regression")

    if cfg.anova_group and cfg.anova_target:
        anova_res = StatEngine.one_way_anova(df, cfg.anova_target, cfg.anova_group)
        analysis_stats["one_way_anova"] = anova_res
        viz.generate_boxplot(df, cfg.anova_target, cfg.anova_group)
        # Non-parametric companion: Kruskal-Wallis H test
        kw_res = StatEngine.kruskal_wallis_test(df, cfg.anova_target, cfg.anova_group)
        analysis_stats["kruskal_wallis"] = kw_res

    if cfg.ttest_group and cfg.ttest_target:
        tt_res = StatEngine.independent_t_test(df, cfg.ttest_target, cfg.ttest_group)
        analysis_stats["independent_t_test"] = tt_res
        # Non-parametric companion: Mann-Whitney U test
        mw_res = StatEngine.mann_whitney_u_test(df, cfg.ttest_target, cfg.ttest_group)
        analysis_stats["mann_whitney_u"] = mw_res

    # One-sample T-test
    if cfg.one_sample_target:
        ost_res = StatEngine.one_sample_t_test(df, cfg.one_sample_target, cfg.one_sample_mean)
        analysis_stats["one_sample_t_test"] = ost_res

    if cfg.chi_square_col1 and cfg.chi_square_col2:
        chi_res = StatEngine.chi_square_test(df, cfg.chi_square_col1, cfg.chi_square_col2)
        analysis_stats["chi_square"] = chi_res

    if cfg.logistic_target and cfg.logistic_features:
        log_res = StatEngine.logistic_regression(df, cfg.logistic_target, cfg.logistic_features)
        analysis_stats["logistic_regression"] = log_res
        # Also run Random Forest Classification if predictors exist
        rf_clf = StatEngine.random_forest_classification(df, cfg.logistic_target, cfg.logistic_features)
        analysis_stats["random_forest_classification"] = rf_clf
        if not rf_clf.get("error"):
            viz.generate_feature_importance_plot(rf_clf, "random_forest_classification")
            viz.generate_confusion_matrix_heatmap(rf_clf)

    # Unsupervised Learning
    if cfg.cluster_features and len(cfg.cluster_features) >= 2:
        kmeans_res = StatEngine.kmeans_clustering(df, cfg.cluster_features, n_clusters=3)
        analysis_stats["kmeans_clustering"] = kmeans_res
        if not kmeans_res.get("error"):
            viz.generate_cluster_scatter_plot(df, kmeans_res, cfg.cluster_features)
            
        pca_res = StatEngine.pca_reduction(df, cfg.cluster_features)
        analysis_stats["pca_reduction"] = pca_res
        if not pca_res.get("error"):
            viz.generate_pca_variance_plot(pca_res)
        
    if cfg.paired_pre and cfg.paired_post:
        analysis_stats["paired_t_test"] = StatEngine.paired_t_test(df, cfg.paired_pre, cfg.paired_post)
        analysis_stats["n_gain_score"] = StatEngine.n_gain_score(df, cfg.paired_pre, cfg.paired_post)

    # B. PSYCHOMETRICS
    if len(cfg.psychometric_columns) >= 3:
        psy_cols = cfg.psychometric_columns
        analysis_stats["cronbach_alpha"] = StatEngine.cronbach_alpha(df, psy_cols)
        kmo_bart = PsychometricsEngine.calculate_kmo_bartlett(df, psy_cols)
        analysis_stats["kmo_bartlett"] = kmo_bart
        efa_scree = PsychometricsEngine.run_efa_scree(df, psy_cols, n_factors=2)
        analysis_stats["efa_scree"] = efa_scree
        if "eigenvalues" in efa_scree:
            viz.generate_scree_plot(efa_scree["eigenvalues"])

    if len(cfg.irt_columns) >= 5:
        irt_res = PsychometricsEngine.fit_irt_2pl(df, cfg.irt_columns)
        analysis_stats["irt_2pl"] = irt_res
        mirt_res = PsychometricsEngine.fit_mirt_2d(df, cfg.irt_columns)
        analysis_stats["mirt_2d"] = mirt_res
        if "items" in mirt_res and mirt_res["items"]:
            viz.generate_mirt_surface(mirt_res)

    # C. FINANCIAL
    if cfg.price_column:
        price_col = cfg.price_column
        df_ind = FinancialEngine.calculate_indicators(df, price_col)
        analysis_stats["financial_risk_reward"] = FinancialEngine.risk_return_metrics(df, price_col)
        analysis_stats["arima_pricing_forecast"] = FinancialEngine.arima_forecast(df, price_col)
        analysis_stats["garch_price_volatility"] = FinancialEngine.run_garch_volatility(df, price_col)
        viz.generate_financial_chart(df_ind, price_col)
        risk_metrics = analysis_stats["financial_risk_reward"]
        if "drawdowns_series" in risk_metrics:
            viz.generate_drawdown_plot(risk_metrics["drawdowns_series"])

    if len(cfg.portfolio_assets) >= 2:
        opt_port = FinancialEngine.optimize_portfolio(df, cfg.portfolio_assets)
        analysis_stats["portfolio_optimization"] = opt_port
        if "frontier_returns" in opt_port:
            viz.generate_efficient_frontier_plot(opt_port)

    # 3. WRITE EXPORT LOGS & PUBLISH PRESENTATIONS
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fs:
        # Keep output parseable by the Node API and browsers.
        raw_json_str = json.dumps(make_json_safe(analysis_stats), allow_nan=False)
        fs.write(raw_json_str)
        
    # Re-read to ensure clean templating feed
    clean_summary = json.loads(raw_json_str)
    
    # Build beautiful formats
    reporter.generate_docx_report(clean_summary, output_dir)
    reporter.generate_html_report(clean_summary, output_dir)
    
    # 4. Handle auto explorer open request
    if open_folder:
        try:
            logger.info(f"Opening generated output location: {output_dir}")
            if sys.platform.startswith('darwin'):
                os.system(f"open '{output_dir}'")
            elif os.name == 'nt':
                os.system(f"start explorer '{output_dir}'")
            elif os.name == 'posix':
                os.system(f"xdg-open '{output_dir}'")
        except Exception as e:
            logger.warning(f"Could not open workspace folder: {e}")
            
    logger.info("Automation workflow executed successfully. Diagnostic output package archived!")
    return output_dir

if __name__ == "__main__":
    args = parse_args()
    try:
        cfg = None
        if args.config:
            try:
                cfg = json.loads(args.config)
            except:
                with open(args.config, "r") as f:
                    cfg = json.load(f)
                    
        res_dir = execute_automated_analytics(
            input_path=args.input,
            sheet_name=args.sheet,
            custom_output=args.output,
            raw_config=cfg,
            open_folder=args.open,
        )
        print(f"SUCCESS|{os.path.abspath(res_dir)}")
    except Exception as err:
        logger.error(f"Core analysis cycle crashed: {err}")
        print(f"FAILED|{err}")
        sys.exit(1)
