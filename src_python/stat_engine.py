import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from typing import Dict, List, Any, Tuple, Optional
try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.metrics import confusion_matrix, accuracy_score, r2_score, mean_squared_error, silhouette_score
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
import logging

logger = logging.getLogger("stat_engine")

class StatEngine:
    @staticmethod
    def descriptive_statistics(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Generate descriptive summary table for numerical columns."""
        res = {}
        for col in columns:
            series = df[col].dropna()
            if len(series) == 0:
                continue
            
            mean_val = float(series.mean())
            median_val = float(series.median())
            try:
                mode_val = float(series.mode().iloc[0])
            except:
                mode_val = np.nan
                
            sd_val = float(series.std())
            var_val = float(series.var())
            skew_val = float(series.skew())
            kurt_val = float(series.kurt())
            min_val = float(series.min())
            max_val = float(series.max())
            count_val = int(series.count())
            
            p25 = float(np.percentile(series, 25))
            p50 = float(np.percentile(series, 50))
            p75 = float(np.percentile(series, 75))
            
            res[col] = {
                "count": count_val,
                "mean": mean_val,
                "median": median_val,
                "mode": mode_val,
                "std": sd_val,
                "variance": var_val,
                "skewness": skew_val,
                "kurtosis": kurt_val,
                "min": min_val,
                "max": max_val,
                "p25": p25,
                "p50": p50,
                "p75": p75,
                "range": max_val - min_val
            }
        return res

    @staticmethod
    def normality_test(df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Run Shapiro-Wilk, Kolmogorov-Smirnov, and D'Agostino K2 tests."""
        series = df[col].dropna()
        if len(series) < 3:
            return {"error": "Insufficient data (n < 3)"}
            
        res = {}
        # Shapiro-Wilk (Ideal for small datasets < 5000)
        try:
            sw_stat, sw_p = stats.shapiro(series)
            res["shapiro"] = {"statistic": float(sw_stat), "p_value": float(sw_p), "normal": bool(sw_p > 0.05)}
        except Exception as e:
            res["shapiro"] = {"error": str(e)}
            
        # Kolmogorov-Smirnov (relative to standard normal)
        try:
            # Normalize series to perform test
            normed = (series - series.mean()) / series.std()
            ks_stat, ks_p = stats.kstest(normed, 'norm')
            res["kolmogorov"] = {"statistic": float(ks_stat), "p_value": float(ks_p), "normal": bool(ks_p > 0.05)}
        except Exception as e:
            res["kolmogorov"] = {"error": str(e)}

        # D'Agostino-Pearson
        try:
            if len(series) >= 8:
                dp_stat, dp_p = stats.normaltest(series)
                res["dagostino"] = {"statistic": float(dp_stat), "p_value": float(dp_p), "normal": bool(dp_p > 0.05)}
            else:
                res["dagostino"] = {"error": "D'Agostino-Pearson requires N >= 8"}
        except Exception as e:
            res["dagostino"] = {"error": str(e)}
            
        return res

    @staticmethod
    def impute_missing_values(df: pd.DataFrame, num_cols: List[str], cat_cols: List[str]) -> pd.DataFrame:
        """Impute missing values: mean for numeric, mode for categorical."""
        df_clean = df.copy()
        for col in num_cols:
            if col in df_clean.columns and df_clean[col].isnull().any():
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        for col in cat_cols:
            if col in df_clean.columns and df_clean[col].isnull().any():
                mode_vals = df_clean[col].mode()
                if not mode_vals.empty:
                    df_clean[col] = df_clean[col].fillna(mode_vals.iloc[0])
        return df_clean

    @staticmethod
    def random_forest_regression(df: pd.DataFrame, target: str, predictors: List[str]) -> Dict[str, Any]:
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn is not available"}
        
        try:
            valid_df = df[[target] + predictors].dropna()
            if len(valid_df) < 5:
                return {"error": "Insufficient data"}
                
            X = valid_df[predictors]
            y = valid_df[target]
            
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X, y)
            preds = rf.predict(X)
            
            r2 = float(r2_score(y, preds))
            mse = float(mean_squared_error(y, preds))
            
            feat_imp = [
                {"feature": f, "importance": float(imp)} 
                for f, imp in zip(predictors, rf.feature_importances_)
            ]
            feat_imp.sort(key=lambda x: x["importance"], reverse=True)
            
            return {
                "r_squared": r2,
                "mse": mse,
                "feature_importance": feat_imp,
                "n_observations": len(valid_df)
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def random_forest_classification(df: pd.DataFrame, target: str, predictors: List[str]) -> Dict[str, Any]:
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn is not available"}
            
        try:
            valid_df = df[[target] + predictors].dropna()
            if len(valid_df) < 5 or valid_df[target].nunique() < 2:
                return {"error": "Insufficient data or target does not have multiple classes"}
                
            X = valid_df[predictors]
            y = valid_df[target]
            
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(X, y)
            preds = rf.predict(X)
            
            acc = float(accuracy_score(y, preds))
            labels = sorted(list(y.unique()))
            cm = confusion_matrix(y, preds, labels=labels).tolist()
            
            feat_imp = [
                {"feature": f, "importance": float(imp)} 
                for f, imp in zip(predictors, rf.feature_importances_)
            ]
            feat_imp.sort(key=lambda x: x["importance"], reverse=True)
            
            return {
                "accuracy": acc,
                "confusion_matrix": cm,
                "labels": [str(l) for l in labels],
                "feature_importance": feat_imp,
                "n_observations": len(valid_df)
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def detect_outliers(df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Detect outliers using IQR and Z-scores."""
        series = df[col].dropna()
        if len(series) == 0:
            return {}
            
        # IQR method
        q1 = np.percentile(series, 25)
        q3 = np.percentile(series, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        iqr_outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        # Z-score method (threshold = 3)
        mean_val = series.mean()
        std_val = series.std()
        if std_val > 0:
            z_scores = (series - mean_val) / std_val
            z_outliers = series[np.abs(z_scores) > 3]
        else:
            z_outliers = pd.Series([], dtype=float)
            
        return {
            "iqr_bounds": [float(lower_bound), float(upper_bound)],
            "iqr_outliers_count": len(iqr_outliers),
            "z_outliers_count": len(z_outliers),
            "total_rows": len(series)
        }

    @staticmethod
    def one_sample_t_test(df: pd.DataFrame, col: str, population_mean: float) -> Dict[str, Any]:
        """One sample student T-test."""
        series = df[col].dropna()
        if len(series) < 2:
            return {"error": "Insufficient data"}
            
        stat, p_val = stats.ttest_1samp(series, population_mean)
        mean_diff = float(series.mean() - population_mean)
        
        # Cohen's d
        s_std = series.std()
        cohen_d = mean_diff / s_std if s_std > 0 else 0
        
        return {
            "statistic": float(stat),
            "p_value": float(p_val),
            "df": len(series) - 1,
            "mean_difference": mean_diff,
            "sample_mean": float(series.mean()),
            "population_mean_tested": population_mean,
            "cohens_d": float(cohen_d),
            "significant": bool(p_val < 0.05)
        }

    @staticmethod
    def independent_t_test(df: pd.DataFrame, numeric_col: str, group_col: str) -> Dict[str, Any]:
        """Two group independent samples T-test."""
        groups = df[group_col].dropna().unique()
        if len(groups) != 2:
            return {"error": "Grouping column must contain exactly 2 unique tags for T-test."}
            
        g1_data = df[df[group_col] == groups[0]][numeric_col].dropna()
        g2_data = df[df[group_col] == groups[1]][numeric_col].dropna()
        
        if len(g1_data) < 2 or len(g2_data) < 2:
            return {"error": "Insufficient items in group subsets."}
            
        # Levene's test for variance homogeneity
        lev_stat, lev_p = stats.levene(g1_data, g2_data)
        equal_var = bool(lev_p > 0.05)
        
        # Welchs or standard T test
        stat, p_val = stats.ttest_ind(g1_data, g2_data, equal_var=equal_var)
        
        # Cohen's d (pooled standard deviation)
        n1, n2 = len(g1_data), len(g2_data)
        v1, v2 = g1_data.var(), g2_data.var()
        pooled_std = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
        raw_diff = float(g1_data.mean() - g2_data.mean())
        cohen_d = raw_diff / pooled_std if pooled_std > 0 else 0
        
        return {
            "group_names": [str(groups[0]), str(groups[1])],
            "group_sizes": [n1, n2],
            "group_means": [float(g1_data.mean()), float(g2_data.mean())],
            "levenes_p": float(lev_p),
            "equal_variances_assumed": equal_var,
            "statistic": float(stat),
            "p_value": float(p_val),
            "df": int(n1 + n2 - 2),
            "cohens_d": float(cohen_d),
            "significant": bool(p_val < 0.05)
        }

    @staticmethod
    def mann_whitney_u_test(df: pd.DataFrame, numeric_col: str, group_col: str) -> Dict[str, Any]:
        """Two group Mann-Whitney U test (non-parametric)."""
        groups = df[group_col].dropna().unique()
        if len(groups) != 2:
            return {"error": "Grouping column must contain exactly 2 unique tags for Mann-Whitney."}
            
        g1_data = df[df[group_col] == groups[0]][numeric_col].dropna()
        g2_data = df[df[group_col] == groups[1]][numeric_col].dropna()
        
        if len(g1_data) < 2 or len(g2_data) < 2:
            return {"error": "Insufficient items in group subsets."}
            
        stat, p_val = stats.mannwhitneyu(g1_data, g2_data, alternative='two-sided')
        
        # Calculate group medians
        median1 = float(g1_data.median())
        median2 = float(g2_data.median())
        
        return {
            "group_names": [str(groups[0]), str(groups[1])],
            "group_sizes": [len(g1_data), len(g2_data)],
            "group_medians": [median1, median2],
            "statistic": float(stat),
            "p_value": float(p_val),
            "significant": bool(p_val < 0.05)
        }

    @staticmethod
    def paired_t_test(df: pd.DataFrame, pre_col: str, post_col: str) -> Dict[str, Any]:
        """Paired T-test for longitudinal comparison."""
        sub = df[[pre_col, post_col]].dropna()
        if len(sub) < 3:
            return {"error": "Insufficient paired pairs (N < 3)"}
            
        g1 = sub[pre_col]
        g2 = sub[post_col]
        
        stat, p_val = stats.ttest_rel(g1, g2)
        diff_series = g2 - g1
        mean_diff = float(diff_series.mean())
        std_diff = diff_series.std()
        cohen_d = mean_diff / std_diff if std_diff > 0 else 0
        
        return {
            "n": len(sub),
            "pre_mean": float(g1.mean()),
            "post_mean": float(g2.mean()),
            "mean_difference": mean_diff,
            "statistic": float(stat),
            "p_value": float(p_val),
            "cohens_d": float(cohen_d),
            "significant": bool(p_val < 0.05)
        }

    @staticmethod
    def one_way_anova(df: pd.DataFrame, numeric_col: str, group_col: str) -> Dict[str, Any]:
        """One-way ANOVA + Post hoc Tukey HSD."""
        sub = df[[numeric_col, group_col]].dropna()
        groups = sub[group_col].unique()
        
        if len(groups) < 3:
            return {"error": "ANOVA requires 3 or more categorical factor groups."}
            
        group_data = [sub[sub[group_col] == g][numeric_col] for g in groups]
        
        if any(len(g) < 2 for g in group_data):
            return {"error": "One or more factors has insufficient numeric items."}
            
        # ANOVA calculation
        f_stat, p_val = stats.f_oneway(*group_data)
        
        # Tukey HSD
        tukey = pairwise_tukeyhsd(endog=sub[numeric_col], groups=sub[group_col], alpha=0.05)
        
        # Extract Tukey results
        tukey_results = []
        # tukey.summary() yields a table, parse it
        for row in range(1, len(tukey.summary().data)):
            row_data = tukey.summary().data[row]
            tukey_results.append({
                "group1": str(row_data[0]),
                "group2": str(row_data[1]),
                "meandiff": float(row_data[2]),
                "p_adj": float(row_data[3]),
                "lower": float(row_data[4]),
                "upper": float(row_data[5]),
                "reject": bool(row_data[6])
            })
            
        # Effect size (eta-squared)
        grand_mean = sub[numeric_col].mean()
        ss_total = ((sub[numeric_col] - grand_mean) ** 2).sum()
        ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in group_data)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0
        
        return {
            "groups": [str(g) for g in groups],
            "f_statistic": float(f_stat),
            "p_value": float(p_val),
            "eta_squared": float(eta_sq),
            "tukey_hsd": tukey_results,
            "significant": bool(p_val < 0.05)
        }

    @staticmethod
    def kruskal_wallis_test(df: pd.DataFrame, numeric_col: str, group_col: str) -> Dict[str, Any]:
        """Kruskal-Wallis H-test for 3+ independent groups (non-parametric)."""
        sub = df[[numeric_col, group_col]].dropna()
        groups = sub[group_col].unique()
        
        if len(groups) < 3:
            return {"error": "Kruskal-Wallis requires 3 or more categorical factor groups."}
            
        group_data = [sub[sub[group_col] == g][numeric_col] for g in groups]
        
        if any(len(g) < 2 for g in group_data):
            return {"error": "One or more factors has insufficient numeric items."}
            
        stat, p_val = stats.kruskal(*group_data)
        
        # Calculate group medians
        medians = {}
        for g in groups:
            medians[str(g)] = float(sub[sub[group_col] == g][numeric_col].median())
            
        return {
            "groups": [str(g) for g in groups],
            "statistic": float(stat),
            "p_value": float(p_val),
            "significant": bool(p_val < 0.05),
            "group_medians": medians
        }

    @staticmethod
    def correlation_matrix(df: pd.DataFrame, columns: List[str], method: str = 'pearson') -> Dict[str, Any]:
        """Compute Correlation Matrix coefficients and p-values."""
        sub = df[columns].dropna()
        if len(sub) < 3:
            return {"error": "Insufficient rows for correlation."}
            
        corr_df = sub.corr(method=method)
        
        # Calculate p-values
        n = len(sub)
        p_values = pd.DataFrame(np.zeros((len(columns), len(columns))), columns=columns, index=columns)
        for i in range(len(columns)):
            for j in range(len(columns)):
                if i == j:
                    p_values.iloc[i, j] = 0.0
                else:
                    r = corr_df.iloc[i, j]
                    if method == 'spearman':
                        coef, p_p = stats.spearmanr(sub[columns[i]], sub[columns[j]])
                        if np.isnan(p_p):
                            p_p = 1.0
                    else:
                        # t = r * sqrt(n-2) / sqrt(1-r^2)
                        if abs(r) >= 1.0:
                            p_p = 0.0
                        else:
                            t = r * np.sqrt(n - 2) / np.sqrt(1 - r**2)
                            p_p = stats.t.sf(np.abs(t), n - 2) * 2
                    p_values.iloc[i, j] = float(p_p)
                    
        return {
            "columns": columns,
            "coefficients": corr_df.to_dict(orient="list"),
            "p_values": p_values.to_dict(orient="list")
        }

    @staticmethod
    def linear_regression(df: pd.DataFrame, target_col: str, feature_cols: List[str]) -> Dict[str, Any]:
        """Perform OLS Multiple Linear Regression."""
        sub = df[[target_col] + feature_cols].dropna()
        if len(sub) < len(feature_cols) + 2:
            return {"error": "Too few observations relative to predictors."}
            
        y = sub[target_col]
        X = sub[feature_cols]
        X = sm.add_constant(X)
        
        model = sm.OLS(y, X).fit()
        
        coefs = model.params.to_dict()
        p_vals = model.pvalues.to_dict()
        std_errs = model.bse.to_dict()
        t_values = model.tvalues.to_dict()
        
        features_summary = []
        for feat in X.columns:
            features_summary.append({
                "feature": feat,
                "coefficient": float(coefs[feat]),
                "std_err": float(std_errs[feat]),
                "t_statistic": float(t_values[feat]),
                "p_value": float(p_vals[feat]),
                "significant": bool(p_vals[feat] < 0.05)
            })
            
        return {
            "r_squared": float(model.rsquared),
            "adj_r_squared": float(model.rsquared_adj),
            "f_statistic": float(model.fvalue),
            "f_p_value": float(model.f_pvalue),
            "n_observations": int(model.nobs),
            "features": features_summary
        }

    @staticmethod
    def logistic_regression(df: pd.DataFrame, target_col: str, feature_cols: List[str]) -> Dict[str, Any]:
        """Perform Binary Logistic Regression."""
        sub = df[[target_col] + feature_cols].dropna()
        y = sub[target_col].astype(int)
        
        if len(y.unique()) != 2:
            return {"error": "Logistic Regression target must be strictly binary class (0/1)."}
            
        X = sub[feature_cols]
        X = sm.add_constant(X)
        
        try:
            model = sm.Logit(y, X).fit(disp=0)
            
            coefs = model.params.to_dict()
            p_vals = model.pvalues.to_dict()
            std_errs = model.bse.to_dict()
            z_values = model.tvalues.to_dict() # statsmodels Logit uses tvalues field name for zvalues
            
            # Classification accuracy
            preds = (model.predict(X) >= 0.5).astype(int)
            accuracy = float((preds == y).mean())
            
            features_summary = []
            for feat in X.columns:
                features_summary.append({
                    "feature": feat,
                    "coefficient": float(coefs[feat]),
                    "std_err": float(std_errs[feat]),
                    "z_statistic": float(z_values[feat]),
                    "p_value": float(p_vals[feat]),
                    "significant": bool(p_vals[feat] < 0.05)
                })
                
            return {
                "pseudo_r_squared": float(model.prsquared),
                "llr_p_value": float(model.llr_pvalue),
                "accuracy": accuracy,
                "n_observations": int(model.nobs),
                "features": features_summary
            }
        except Exception as e:
            logger.error(f"Logistic regression convergence failed: {e}")
            return {"error": f"Model failed to converge: {e}"}

    @staticmethod
    def chi_square_test(df: pd.DataFrame, col1: str, col2: str) -> Dict[str, Any]:
        """Chi-square test of independence for categorical associations."""
        contingency_table = pd.crosstab(df[col1], df[col2])
        if contingency_table.size <= 1:
            return {"error": "Contingency table is too small."}
            
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Cramer's V (Effect size)
        n = contingency_table.sum().sum()
        r, c = contingency_table.shape
        cramers_v = np.sqrt(chi2 / (n * min(r - 1, c - 1))) if n > 0 and min(r - 1, c - 1) > 0 else 0
        
        return {
            "contingency_table": contingency_table.to_dict(orient="index"),
            "chi2_statistic": float(chi2),
            "p_value": float(p_val),
            "dof": int(dof),
            "cramers_v": float(cramers_v),
            "significant": bool(p_val < 0.05)
        }

    @staticmethod
    def cronbach_alpha(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Calculate scale internal reliability Cronbach Alpha coefficient."""
        sub = df[columns].dropna()
        k = len(columns)
        if k < 2:
            return {"error": "Requires at least 2 item columns."}
            
        item_variances = sub.var(ddof=1).sum()
        total_score_variance = sub.sum(axis=1).var(ddof=1)
        
        if total_score_variance == 0:
            return {"alpha": 0.0, "rating": "No variance"}
            
        alpha = (k / (k - 1)) * (1 - (item_variances / total_score_variance))
        
        # Qualitative thresholds
        if alpha >= 0.9:
            rating = "Excellent"
        elif alpha >= 0.8:
            rating = "Good"
        elif alpha >= 0.7:
            rating = "Acceptable"
        elif alpha >= 0.6:
            rating = "Questionable"
        elif alpha >= 0.5:
            rating = "Poor"
        else:
            rating = "Unacceptable"
            
        return {
            "alpha": float(alpha),
            "rating": rating,
            "k_items": k,
            "n_observations": len(sub)
        }

    @staticmethod
    def n_gain_score(df: pd.DataFrame, pre_col: str, post_col: str, max_score: float = 100.0) -> Dict[str, Any]:
        """Pedagogical Normalised Gain Index comparison."""
        sub = df[[pre_col, post_col]].dropna()
        if len(sub) == 0:
            return {"error": "No pairs available."}
            
        # N-Gain for each student
        # N-gain = (post - pre) / (max - pre)
        denom = max_score - sub[pre_col]
        # Avoid division by zero
        num_gain = sub[post_col] - sub[pre_col]
        
        gains = []
        for n, d in zip(num_gain, denom):
            if d <= 0:
                gains.append(np.nan)
            else:
                g_val = n / d
                gains.append(min(max(g_val, -1.0), 1.0)) # bounding
                
        sub["n_gain"] = gains
        mean_gain = float(sub["n_gain"].dropna().mean())
        
        # Classifications
        if mean_gain >= 0.7:
            category = "High Gain"
        elif mean_gain >= 0.3:
            category = "Medium Gain"
        else:
            category = "Low Gain"
            
        return {
            "mean_gain": mean_gain,
            "category": category,
            "n_students": int(sub["n_gain"].dropna().count())
        }

    @staticmethod
    def simple_time_series(df: pd.DataFrame, date_col: str, value_col: str) -> Dict[str, Any]:
        """Temporal structure diagnostics: stationarity and autocorrelations."""
        try:
            temp_df = df[[date_col, value_col]].dropna()
            temp_df[date_col] = pd.to_datetime(temp_df[date_col])
            temp_df = temp_df.sort_values(by=date_col)
            
            series = temp_df[value_col].values
            if len(series) < 10:
                return {"error": "Time series is too short for comprehensive diagnostics (require N >= 10)."}
                
            # Augmented Dickey-Fuller stationarity test
            try:
                from statsmodels.tsa.stattools import adfuller
                adf_res = adfuller(series)
                stationary = bool(adf_res[1] < 0.05)
                adf_p = float(adf_res[1])
                adf_stat = float(adf_res[0])
            except Exception as e:
                stationary = False
                adf_p = 1.0
                adf_stat = 0.0
                logger.warning(f"ADF test failed: {e}")
                
            # Autocorr values
            autocorr_lags = []
            for lag in range(1, min(6, len(series) // 2)):
                autocorr_lags.append({
                    "lag": lag,
                    "coefficient": float(pd.Series(series).autocorr(lag=lag))
                })
                
            return {
                "length": len(series),
                "stationary_adf": stationary,
                "adf_p_value": adf_p,
                "adf_statistic": adf_stat,
                "autocorrelation_lags": autocorr_lags
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def kmeans_clustering(df: pd.DataFrame, features: List[str], n_clusters: int = 3) -> Dict[str, Any]:
        """Perform K-Means clustering and calculate silhouette score."""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn is not available"}
        
        try:
            valid_df = df[features].dropna()
            if len(valid_df) < n_clusters:
                return {"error": "Not enough data points for the number of clusters."}
                
            X = valid_df[features].values
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            labels = kmeans.fit_predict(X)
            
            # Silhouette Score requires at least 2 clusters and more than 2 samples
            if 1 < n_clusters < len(valid_df):
                silhouette = float(silhouette_score(X, labels))
            else:
                silhouette = 0.0
                
            # Profile the clusters (mean value of features per cluster)
            valid_df['cluster'] = labels
            profiles = valid_df.groupby('cluster').mean().to_dict(orient='index')
            
            # Convert profiles to a list format
            cluster_profiles = []
            for cluster_id, means in profiles.items():
                cluster_profiles.append({
                    "cluster": int(cluster_id),
                    "size": int(sum(labels == cluster_id)),
                    "means": {feat: float(val) for feat, val in means.items()}
                })
                
            return {
                "n_clusters": n_clusters,
                "silhouette_score": silhouette,
                "cluster_profiles": cluster_profiles,
                "labels": labels.tolist(),
                "n_observations": len(valid_df)
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def pca_reduction(df: pd.DataFrame, features: List[str], n_components: int = 3) -> Dict[str, Any]:
        """Perform Principal Component Analysis for dimensionality reduction."""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn is not available"}
            
        try:
            valid_df = df[features].dropna()
            if len(valid_df) < 2 or len(features) < 2:
                return {"error": "Insufficient data or features for PCA."}
                
            X = valid_df[features]
            # Standardize features before PCA
            X_std = (X - X.mean()) / X.std()
            
            pca_components = min(n_components, len(features), len(valid_df))
            pca = PCA(n_components=pca_components)
            components = pca.fit_transform(X_std)
            
            explained_variance = pca.explained_variance_ratio_.tolist()
            cumulative_variance = np.cumsum(pca.explained_variance_ratio_).tolist()
            
            loadings = []
            for i, comp in enumerate(pca.components_):
                loadings.append({
                    "component": f"PC{i+1}",
                    "weights": {feat: float(weight) for feat, weight in zip(features, comp)}
                })
                
            # Provide 2D coordinates if possible
            coords_2d = None
            if pca_components >= 2:
                coords_2d = {
                    "x": components[:, 0].tolist(),
                    "y": components[:, 1].tolist()
                }
                
            return {
                "n_components_used": pca_components,
                "explained_variance_ratio": [float(v) for v in explained_variance],
                "cumulative_variance": [float(v) for v in cumulative_variance],
                "loadings": loadings,
                "coords_2d": coords_2d,
                "n_observations": len(valid_df)
            }
        except Exception as e:
            return {"error": str(e)}

