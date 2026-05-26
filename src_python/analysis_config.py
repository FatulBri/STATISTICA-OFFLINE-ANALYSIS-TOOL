"""Resolve user analysis configuration against dataset diagnostics."""
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd


class ResolvedAnalysisConfig:
    def __init__(
        self,
        sheet: Optional[str],
        descriptive_columns: List[str],
        normality_columns: List[str],
        correlation_columns: List[str],
        regression_target: Optional[str],
        regression_predictors: List[str],
        anova_target: Optional[str],
        anova_group: Optional[str],
        ttest_target: Optional[str],
        ttest_group: Optional[str],
        paired_pre: Optional[str],
        paired_post: Optional[str],
        psychometric_columns: List[str],
        irt_columns: List[str],
        price_column: Optional[str],
        portfolio_assets: List[str],
        chi_square_col1: Optional[str],
        chi_square_col2: Optional[str],
        logistic_target: Optional[str],
        logistic_features: List[str],
        cluster_features: List[str],
        one_sample_target: Optional[str],
        one_sample_mean: float,
        impute_missing: bool,
        export_dpi: int,
        applied: Dict[str, Any],
    ):
        self.sheet = sheet
        self.descriptive_columns = descriptive_columns
        self.normality_columns = normality_columns
        self.correlation_columns = correlation_columns
        self.regression_target = regression_target
        self.regression_predictors = regression_predictors
        self.anova_target = anova_target
        self.anova_group = anova_group
        self.ttest_target = ttest_target
        self.ttest_group = ttest_group
        self.paired_pre = paired_pre
        self.paired_post = paired_post
        self.psychometric_columns = psychometric_columns
        self.irt_columns = irt_columns
        self.price_column = price_column
        self.portfolio_assets = portfolio_assets
        self.chi_square_col1 = chi_square_col1
        self.chi_square_col2 = chi_square_col2
        self.logistic_target = logistic_target
        self.logistic_features = logistic_features
        self.cluster_features = cluster_features
        self.one_sample_target = one_sample_target
        self.one_sample_mean = one_sample_mean
        self.impute_missing = impute_missing
        self.export_dpi = export_dpi
        self.applied = applied


def _pick_existing(candidates: List[str], allowed: List[str], limit: Optional[int] = None) -> List[str]:
    out = [c for c in candidates if c in allowed]
    if limit is not None:
        return out[:limit]
    return out


def _auto_anova_group(df: pd.DataFrame, cat_cols: List[str]) -> Optional[str]:
    for c in cat_cols:
        n = df[c].dropna().nunique()
        if 3 <= n <= 8:
            return c
    return None


def _auto_ttest_group(df: pd.DataFrame, cat_cols: List[str]) -> Optional[str]:
    for c in cat_cols:
        if df[c].dropna().nunique() == 2:
            return c
    return None


def _auto_price_column(num_cols: List[str]) -> Optional[str]:
    for c in num_cols:
        low = c.lower()
        if any(k in low for k in ["price", "close", "adj close"]):
            return c
    return None


def resolve_analysis_config(
    raw_config: Optional[Dict[str, Any]],
    diagnostics: Dict[str, Any],
    df: pd.DataFrame,
) -> ResolvedAnalysisConfig:
    raw = raw_config or {}
    num_cols = list(diagnostics.get("numericColumns") or [])
    cat_cols = list(diagnostics.get("categoricalColumns") or [])
    bin_cols = list(diagnostics.get("binaryColumns") or [])

    sheet = raw.get("sheet") or diagnostics.get("activeSheet")

    desc = _pick_existing(raw.get("descriptiveColumns") or num_cols, num_cols, 15)
    normality = _pick_existing(raw.get("normalityColumns") or num_cols[:4], num_cols, 4)
    corr = _pick_existing(raw.get("correlationColumns") or num_cols[:10], num_cols, 10)

    reg_target = raw.get("regressionTarget") or (num_cols[0] if num_cols else None)
    reg_predictors = _pick_existing(
        raw.get("regressionPredictors") or [c for c in num_cols[1:4] if c != reg_target],
        num_cols,
    )
    reg_predictors = [c for c in reg_predictors if c != reg_target]

    anova_group = raw.get("anovaGroup") or _auto_anova_group(df, cat_cols)
    anova_target = raw.get("anovaTarget") or (num_cols[0] if num_cols else None)
    if raw.get("anovaGroup") is False or raw.get("runAnova") is False:
        anova_group = None

    ttest_group = raw.get("ttestGroup") or _auto_ttest_group(df, cat_cols)
    ttest_target = raw.get("ttestTarget") or (num_cols[0] if num_cols else None)
    if raw.get("runTtest") is False:
        ttest_group = None

    paired_pre = raw.get("pairedPre") or next((c for c in num_cols if "pre" in c.lower()), None)
    paired_post = raw.get("pairedPost") or next((c for c in num_cols if "post" in c.lower()), None)
    if raw.get("runPaired") is False:
        paired_pre = paired_post = None

    psy_cols = _pick_existing(
        raw.get("psychometricColumns") or (num_cols[:8] if len(bin_cols) < 5 else []),
        num_cols,
        12,
    )
    if raw.get("runPsychometrics") is False:
        psy_cols = []

    irt_cols = _pick_existing(raw.get("irtColumns") or bin_cols[:10], bin_cols, 15)
    if raw.get("runIrt") is False:
        irt_cols = []

    price_col = raw.get("priceColumn") or _auto_price_column(num_cols)
    if raw.get("runFinancial") is False:
        price_col = None

    portfolio = _pick_existing(
        raw.get("portfolioAssets")
        or [c for c in num_cols if any(k in c.lower() for k in ["price", "close", "equity", "asset", "stock"])],
        num_cols,
        5,
    )
    if raw.get("runPortfolio") is False:
        portfolio = []

    chi_cats = cat_cols + [c for c in bin_cols if c not in cat_cols]
    chi1 = raw.get("chiSquareCol1") or (chi_cats[0] if len(chi_cats) >= 1 else None)
    chi2 = raw.get("chiSquareCol2") or (chi_cats[1] if len(chi_cats) >= 2 else None)
    if chi1 == chi2:
        chi2 = chi_cats[2] if len(chi_cats) > 2 else None
    if raw.get("runChiSquare") is False:
        chi1 = chi2 = None

    log_target_candidates = list(bin_cols) + [
        c for c in cat_cols if df[c].dropna().nunique() == 2
    ]
    log_target = raw.get("logisticTarget") or (log_target_candidates[0] if log_target_candidates else None)
    log_features = _pick_existing(
        raw.get("logisticFeatures") or [c for c in num_cols if c != log_target][:5],
        num_cols,
        8,
    )
    if raw.get("runLogistic") is False or not log_target:
        log_target = None
        log_features = []

    cluster_features = _pick_existing(
        raw.get("clusterFeatures") or num_cols[:5],
        num_cols,
        15,
    )
    if raw.get("runClustering") is False:
        cluster_features = []

    one_sample_target = raw.get("oneSampleTarget") or None
    if one_sample_target not in num_cols:
        one_sample_target = None
    try:
        one_sample_mean = float(raw.get("oneSampleMean") if raw.get("oneSampleMean") is not None else 0.0)
    except (TypeError, ValueError):
        one_sample_mean = 0.0

    try:
        export_dpi = int(raw.get("exportDpi") or 180)
        export_dpi = max(72, min(export_dpi, 600))
    except (TypeError, ValueError):
        export_dpi = 180

    impute_missing = bool(raw.get("imputeMissing", False))

    applied = {
        "sheet": sheet,
        "regressionTarget": reg_target,
        "regressionPredictors": reg_predictors,
        "anovaTarget": anova_target,
        "anovaGroup": anova_group,
        "ttestTarget": ttest_target,
        "ttestGroup": ttest_group,
        "pairedPre": paired_pre,
        "pairedPost": paired_post,
        "psychometricColumns": psy_cols,
        "irtColumns": irt_cols,
        "priceColumn": price_col,
        "portfolioAssets": portfolio,
        "descriptiveColumns": desc,
        "chiSquareCol1": chi1,
        "chiSquareCol2": chi2,
        "logisticTarget": log_target,
        "logisticFeatures": log_features,
        "clusterFeatures": cluster_features,
        "oneSampleTarget": one_sample_target,
        "oneSampleMean": one_sample_mean,
        "imputeMissing": impute_missing,
        "exportDpi": export_dpi,
    }

    return ResolvedAnalysisConfig(
        sheet=sheet,
        descriptive_columns=desc,
        normality_columns=normality,
        correlation_columns=corr,
        regression_target=reg_target,
        regression_predictors=reg_predictors,
        anova_target=anova_target,
        anova_group=anova_group,
        ttest_target=ttest_target,
        ttest_group=ttest_group,
        paired_pre=paired_pre,
        paired_post=paired_post,
        psychometric_columns=psy_cols,
        irt_columns=irt_cols,
        price_column=price_col,
        portfolio_assets=portfolio,
        chi_square_col1=chi1,
        chi_square_col2=chi2,
        logistic_target=log_target,
        logistic_features=log_features,
        cluster_features=cluster_features,
        one_sample_target=one_sample_target,
        one_sample_mean=one_sample_mean,
        impute_missing=impute_missing,
        export_dpi=export_dpi,
        applied=applied,
    )
