import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger("psychometrics")

class PsychometricsEngine:
    @staticmethod
    def check_factor_analyzer_available() -> bool:
        try:
            import factor_analyzer
            return True
        except ImportError:
            return False

    @staticmethod
    def calculate_kmo_bartlett(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Calculate Kaiser-Meyer-Olkin (KMO) index and Bartlett's Sphericity Test."""
        sub = df[columns].dropna()
        if len(sub) < len(columns):
            return {"error": "Insufficient data records for psychometrics indices."}

        res = {}
        
        # Safe try-except for factor_analyzer
        if PsychometricsEngine.check_factor_analyzer_available():
            try:
                from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
                chi2, p_val = calculate_bartlett_sphericity(sub)
                kmo_all, kmo_model = calculate_kmo(sub)
                
                res["kmo"] = {
                    "overall": float(kmo_model),
                    "items": {col: float(val) for col, val in zip(columns, kmo_all)}
                }
                res["bartlett"] = {
                    "chi2": float(chi2),
                    "p_value": float(p_val),
                    "significant": bool(p_val < 0.05)
                }
                return res
            except Exception as e:
                logger.warning(f"factor_analyzer library failed with error: {e}. Falling back to custom indices.")

        # Robust Custom Fallbacks
        # Bartlett custom check: Null model: corr matrix is Identity.
        corr_matrix = sub.corr().values
        n = len(sub)
        p = len(columns)
        det_corr = np.linalg.det(corr_matrix)
        
        if det_corr <= 0:
            det_corr = 1e-10  # proxy
            
        # Bartlett Chi2 = - (n - 1 - (2p + 5)/6) * ln(det(R))
        factor_mult = (n - 1.0 - (2.0 * p + 5.0) / 6.0)
        chi2_calc = - factor_mult * np.log(det_corr)
        dof = int(p * (p - 1.0) / 2.0)
        p_val_calc = stats.chi2.sf(chi2_calc, dof)
        
        # Custom KMO calculation
        # KMO = sum(r^2) / (sum(r^2) + sum(a^2)) where a^2 is anti-image correlation
        try:
            inv_corr = np.linalg.inv(corr_matrix)
            diag_inv = np.diag(inv_corr)
            diag_inv_sqrt = np.sqrt(diag_inv)
            anti_corr = - inv_corr / np.outer(diag_inv_sqrt, diag_inv_sqrt)
            np.fill_diagonal(anti_corr, 1.0)
            
            sum_r2 = np.sum(corr_matrix**2) - p
            sum_a2 = np.sum(anti_corr**2) - p
            kmo_val = sum_r2 / (sum_r2 + sum_a2) if (sum_r2 + sum_a2) > 0 else 0.5
        except:
            kmo_val = 0.5 # proxy
            
        res["kmo"] = {
            "overall": float(kmo_val),
            "custom": True
        }
        res["bartlett"] = {
            "chi2": float(chi2_calc),
            "p_value": float(p_val_calc),
            "significant": bool(p_val_calc < 0.05),
            "df": dof,
            "custom": True
        }
        return res

    @staticmethod
    def run_efa_scree(df: pd.DataFrame, columns: List[str], n_factors: int = 2) -> Dict[str, Any]:
        """Perform Exploratory Factor Analysis and extract Scree Plot eigenvalues."""
        sub = df[columns].dropna()
        if len(sub) < 3:
            return {"error": "Insufficient observations."}
            
        corr_matrix = sub.corr().values
        eigenvalues, eigenvectors = np.linalg.eig(corr_matrix)
        
        # Sort eigenvalues descending
        idx = eigenvalues.argsort()[::-1]
        sorted_eigenvalues = np.real(eigenvalues[idx])
        sorted_eigenvectors = np.real(eigenvectors[:, idx])
        
        # Total variance explained
        total_var = len(columns)
        var_explained = [float(ev / total_var * 100) for ev in sorted_eigenvalues]
        cum_var_explained = list(np.cumsum(var_explained))
        
        # Safe Factor Loadings (using principal component method or FactorAnalyzer)
        loadings_dict = {}
        if PsychometricsEngine.check_factor_analyzer_available() and n_factors <= len(columns):
            try:
                from factor_analyzer import FactorAnalyzer
                fa = FactorAnalyzer(n_factors=n_factors, rotation="varimax")
                fa.fit(sub)
                loadings_matrix = fa.loadings_
                for i, col in enumerate(columns):
                    loadings_dict[col] = [float(loadings_matrix[i, f]) for f in range(n_factors)]
            except Exception as e:
                logger.warning(f"FactorAnalyzer failed rotation, falling back: {e}")

        if not loadings_dict:
            # SVD or PCA Loading approximations: Loading = Eigenvector * sqrt(Eigenvalue)
            # Take top n_factors
            for i, col in enumerate(columns):
                loadings_col = []
                for f in range(min(n_factors, len(columns))):
                    ev_val = sorted_eigenvalues[f]
                    loadings_col.append(float(sorted_eigenvectors[i, f] * np.sqrt(max(0, ev_val))))
                loadings_dict[col] = loadings_col
                
        return {
            "eigenvalues": [float(v) for v in sorted_eigenvalues],
            "variance_explained_pct": var_explained,
            "cumulative_variance_explained_pct": cum_var_explained,
            "factor_loadings": loadings_dict,
            "n_factors": n_factors,
            "item_labels": columns
        }

    @staticmethod
    def fit_irt_2pl(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """
        Fit 2-Parameter Logistic (2PL) Item Response Theory model.
        Returns discrimination (a) and difficulty (b) parameters.
        Uses a robust Standardized Latent Ability Proxy technique.
        """
        sub = df[columns].dropna()
        if len(sub) < 10:
            return {"error": "Insufficient lines for IRT modeling."}
            
        # 1. LATENT ABILITY PROXY (Theta estimation): Total standardized score
        sum_scores = sub.sum(axis=1)
        theta_raw = sum_scores.values
        theta = (theta_raw - np.mean(theta_raw)) / (np.std(theta_raw) or 1.0)
        
        items_summary = []
        # Build Item Response Functions
        theta_grid = np.linspace(-3, 3, 50)
        
        for col in columns:
            y = sub[col].values
            # Fit Logistic Regression of Item Y against Theta
            try:
                clf = LogisticRegression(penalty=None, solver='lbfgs')
            except:
                # compatibility for older scikit-learn
                clf = LogisticRegression(penalty='none', solver='lbfgs')
                
            try:
                clf.fit(theta.reshape(-1, 1), y)
                beta1 = float(clf.coef_[0, 0])
                beta0 = float(clf.intercept_[0])
                
                # Convert logit coefficients to IRT indices: 
                # Logit probability = beta1 * theta + beta0 = a * (theta - b)
                # a = beta1
                # b = -beta0 / beta1
                disc = beta1
                diff = -beta0 / beta1 if abs(beta1) > 1e-4 else 0.0
                
                # Items boundary adjustments for extreme fits
                disc = min(max(disc, 0.1), 5.0) # discrimination bounds [0.1, 5]
                diff = min(max(diff, -4.0), 4.0) # difficulty bounds [-4, 4]
                
                # Compute IRF Probability curve on grid: P(theta) = 1 / (1 + exp(-a * (theta - b)))
                irf_curve = list(1.0 / (1.0 + np.exp(-disc * (theta_grid - diff))))
                
                # Item Information Curve: I(theta) = a^2 * P(theta) * (1 - P(theta))
                irf_array = np.array(irf_curve)
                inf_curve = list(disc**2 * irf_array * (1.0 - irf_array))
                
                items_summary.append({
                    "item": col,
                    "discrimination_a": disc,
                    "difficulty_b": diff,
                    "irf_grid": irf_curve,
                    "info_grid": inf_curve
                })
            except Exception as e:
                logger.error(f"Failed to fit IRT item {col}: {e}")
                
        # Calculate Test Information Function: Sum(Item Information)
        tif_grid = np.zeros(len(theta_grid))
        for item in items_summary:
            tif_grid += np.array(item["info_grid"])
            
        return {
            "theta_grid": list(theta_grid),
            "test_information_grid": list(tif_grid),
            "items": items_summary
        }

    @staticmethod
    def fit_mirt_2d(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """
        Fit standard 2-Dimensional Multidimensional Item Response Theory (MIRT).
        Returns item discrimination (a1, a2) and intercept (d) parameters.
        """
        sub = df[columns].dropna()
        if len(sub) < 15:
            return {"error": "MIRT 2D requires larger sample sizes (N >= 15)."}
            
        # 1. Latent dimensions: Multi-dimensional PCA
        pca = PCA(n_components=2)
        theta_2d = pca.fit_transform(sub)
        theta1 = (theta_2d[:, 0] - np.mean(theta_2d[:, 0])) / (np.std(theta_2d[:, 0]) or 1.0)
        theta2 = (theta_2d[:, 1] - np.mean(theta_2d[:, 1])) / (np.std(theta_2d[:, 1]) or 1.0)
        
        items_summary = []
        
        # Theta coordinate mesh grid for 3D surface mapping
        x = np.linspace(-3, 3, 20)
        y = np.linspace(-3, 3, 20)
        X, Y = np.meshgrid(x, y)
        
        for col in columns:
            res_binary = sub[col].values
            try:
                clf = LogisticRegression(penalty=None, solver='lbfgs')
            except:
                clf = LogisticRegression(penalty='none', solver='lbfgs')
                
            try:
                features = np.column_stack((theta1, theta2))
                clf.fit(features, res_binary)
                
                a1 = float(clf.coef_[0, 0])
                a2 = float(clf.coef_[0, 1])
                d = float(clf.intercept_[0])
                
                # Bounds clamping
                a1 = min(max(a1, -4.0), 4.0)
                a2 = min(max(a2, -4.0), 4.0)
                d = min(max(d, -4.0), 4.0)
                
                # Probability surface P(theta1, theta2) = 1 / (1 + exp(-(a1 * theta1 + a2 * theta2 + d)))
                surf_matrix = 1.0 / (1.0 + np.exp(-(a1 * X + a2 * Y + d)))
                
                items_summary.append({
                    "item": col,
                    "discrimination_a1": a1,
                    "discrimination_a2": a2,
                    "intercept_d": d,
                    "surface": surf_matrix.tolist()
                })
            except Exception as e:
                logger.error(f"Failed to fit MIRT 2D for item {col}: {e}")
                
        return {
            "theta1_grid": x.tolist(),
            "theta2_grid": y.tolist(),
            "items": items_summary
        }
