import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy import stats
from typing import Dict, List, Any, Tuple, Optional
import statsmodels.api as sm
import logging

logger = logging.getLogger("financial")

class FinancialEngine:
    @staticmethod
    def calculate_indicators(df: pd.DataFrame, price_col: str) -> pd.DataFrame:
        """Calculate high-end technical analysis overlays: SMA, EMA, BB, RSI, MACD."""
        df_ind = df.copy()
        prices = df_ind[price_col]
        
        # 1. SMA & EMA
        df_ind["SMA_20"] = prices.rolling(window=20, min_periods=1).mean()
        df_ind["EMA_20"] = prices.ewm(span=20, adjust=False).mean()
        
        # 2. Bollinger Bands
        std_20 = prices.rolling(window=20, min_periods=1).std()
        df_ind["BB_Middle"] = df_ind["SMA_20"]
        df_ind["BB_Upper"] = df_ind["SMA_20"] + (std_20 * 2)
        df_ind["BB_Lower"] = df_ind["SMA_20"] - (std_20 * 2)
        
        # 3. RSI (Relative Strength Index)
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-10)
        df_ind["RSI_14"] = np.where(loss == 0, 100.0, 100.0 - (100.0 / (1.0 + rs)))
        
        # 4. MACD (Moving Average Convergence Divergence)
        ema_12 = prices.ewm(span=12, adjust=False).mean()
        ema_26 = prices.ewm(span=26, adjust=False).mean()
        df_ind["MACD_Line"] = ema_12 - ema_26
        df_ind["MACD_Signal"] = df_ind["MACD_Line"].ewm(span=9, adjust=False).mean()
        df_ind["MACD_Hist"] = df_ind["MACD_Line"] - df_ind["MACD_Signal"]
        
        return df_ind

    @staticmethod
    def risk_return_metrics(df: pd.DataFrame, price_col: str, rf_rate: float = 0.02) -> Dict[str, Any]:
        """Perform comprehensive financial risk and reward audit of the asset."""
        prices = df[price_col].dropna().values
        if len(prices) < 3:
            return {"error": "Insufficient historical context."}
            
        returns = np.diff(prices) / prices[:-1]
        
        # CAGR
        years = len(prices) / 252.0  # assuming daily data (252 trading days/yr)
        total_return = (prices[-1] / prices[0]) - 1.0
        cagr = (prices[-1] / prices[0]) ** (1.0 / max(years, 0.01)) - 1.0 if prices[0] > 0 else 0.0
        
        # Annualized Vol & Mean Return
        mean_ret = float(np.mean(returns))
        ann_ret = (1.0 + mean_ret) ** 252.0 - 1.0
        ann_vol = float(np.std(returns) * np.sqrt(252.0))
        
        # Sharpe Ratio
        sharpe = (ann_ret - rf_rate) / ann_vol if ann_vol > 0 else 0.0
        
        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_deviation = float(np.std(downside_returns) * np.sqrt(252.0)) if len(downside_returns) > 0 else 1.0
        sortino = (ann_ret - rf_rate) / downside_deviation if downside_deviation > 0 else 0.0
        
        # Drawdowns
        cum_returns = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(cum_returns)
        drawdowns = (cum_returns - running_max) / running_max
        max_dd = float(np.min(drawdowns)) if len(drawdowns) > 0 else 0.0
        
        # Value at Risk (VaR) & CVaR (Historical 95% Confidence)
        var_95_hist = float(-np.percentile(returns, 5))
        cvar_95_hist = float(-np.mean(returns[returns <= -var_95_hist])) if len(returns[returns <= -var_95_hist]) > 0 else var_95_hist
        
        return {
            "total_return_pct": total_return * 100.0,
            "cagr_pct": cagr * 100.0,
            "annualized_return_pct": ann_ret * 100.0,
            "annualized_volatility_pct": ann_vol * 100.0,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown_pct": max_dd * 100.0,
            "var_95_historical_pct": var_95_hist * 100.0,
            "cvar_95_historical_pct": cvar_95_hist * 100.0,
            "drawdowns_series": drawdowns.tolist() if len(drawdowns) < 500 else drawdowns[::len(drawdowns)//200].tolist()
        }

    @staticmethod
    def arima_forecast(df: pd.DataFrame, price_col: str, steps: int = 15) -> Dict[str, Any]:
        """Generate automatic ARIMA(1,1,1) forward asset pricing forecasts."""
        prices = df[price_col].dropna().values
        if len(prices) < 8:
            return {"error": "Too little data for ARIMA."}
            
        try:
            from statsmodels.tsa.arima.model import ARIMA
            # Fitting log prices is statistically sounder for stocks
            log_prices = np.log(prices)
            model = ARIMA(log_prices, order=(1, 1, 1)).fit()
            
            # Predict log bounds
            forecast_obj = model.get_forecast(steps=steps)
            fc_log_mean = forecast_obj.predicted_mean
            fc_log_conf = forecast_obj.conf_int(alpha=0.05)
            
            # Convert back to regular price space
            fc_mean = list(np.exp(fc_log_mean))
            fc_lower = list(np.exp(fc_log_conf[:, 0]))
            fc_upper = list(np.exp(fc_log_conf[:, 1]))
            
            return {
                "forecast_index": [int(i + len(prices)) for i in range(steps)],
                "forecast_values": fc_mean,
                "confidence_lower": fc_lower,
                "confidence_upper": fc_upper
            }
        except Exception as e:
            logger.warning(f"ARIMA fit failed, building linear trend forecast: {e}")
            # Linear trend fallback
            x = np.arange(len(prices))
            slope, intercept, _, _, _ = stats.linregress(x, prices)
            future_x = np.arange(len(prices), len(prices) + steps)
            fc_mean = future_x * slope + intercept
            fc_lower = fc_mean * 0.95
            fc_upper = fc_mean * 1.05
            return {
                "forecast_index": list(range(len(prices), len(prices) + steps)),
                "forecast_values": fc_mean.tolist(),
                "confidence_lower": fc_lower.tolist(),
                "confidence_upper": fc_upper.tolist(),
                "fallback": True
            }

    @staticmethod
    def run_garch_volatility(df: pd.DataFrame, price_col: str) -> Dict[str, Any]:
        """Analyze asset GARCH(1,1) clustering conditional variances."""
        prices = df[price_col].dropna().values
        if len(prices) < 15:
            return {"error": "Volatility fitting requires N >= 15 historical values."}
            
        returns = np.diff(prices) / prices[:-1]
        
        # Check if arch is installed
        try:
            from arch import arch_model
            # Scale returns to improve optimizer convergence
            scale_factor = 100.0
            am = arch_model(returns * scale_factor, vol='Garch', p=1, q=1, dist='Normal')
            garch_fit = am.fit(disp='off')
            
            # Unscale conditional volatility back to standard series
            cond_vol = garch_fit.conditional_volatility / scale_factor
            
            return {
                "alpha_coefficient": float(garch_fit.params["alpha[1]"]),
                "beta_coefficient": float(garch_fit.params["beta[1]"]),
                "omega_coefficient": float(garch_fit.params["omega"]) / (scale_factor**2),
                "volatility_series": cond_vol.tolist()
            }
        except Exception as e:
            logger.warning(f"arch package GARCH convergence failed, constructing EWMA volatility: {e}")
            # Robust Numeric GARCH(1,1) or EWMA Fallback
            # EWMA Volatility: sigma_t^2 = lambda * sigma_{t-1}^2 + (1-lambda) * r_t^2
            decay_lambda = 0.94
            vols = []
            current_var = np.var(returns)
            for r in returns:
                current_var = decay_lambda * current_var + (1.0 - decay_lambda) * (r**2)
                vols.append(np.sqrt(current_var))
                
            return {
                "alpha_coefficient": 0.06,
                "beta_coefficient": 0.94,
                "omega_coefficient": 0.00001,
                "volatility_series": vols,
                "fallback_ewma": True
            }

    @staticmethod
    def optimize_portfolio(df: pd.DataFrame, asset_columns: List[str]) -> Dict[str, Any]:
        """
        Compute Efficient Frontier and optimum portfolio allocations.
        Returns minimum variance and maximum Sharpe allocations.
        """
        # Close prices database
        prices = df[asset_columns].dropna()
        if len(prices) < 10:
            return {"error": "Insufficient history across assets."}
            
        returns_df = prices.pct_change().dropna()
        mean_returns = returns_df.mean() * 252 # Annualized
        cov_matrix = returns_df.cov() * 252 # Annualized
        
        num_assets = len(asset_columns)
        
        # Monte-Carlo Simulation for frontier tracing
        num_portfolios = 1000
        sim_results = np.zeros((3 + num_assets, num_portfolios))
        
        np.random.seed(42)
        for i in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            
            p_return = np.sum(mean_returns * weights)
            p_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            p_sharpe = p_return / p_std if p_std > 0 else 0.0
            
            sim_results[0, i] = p_return
            sim_results[1, i] = p_std
            sim_results[2, i] = p_sharpe
            for w in range(num_assets):
                sim_results[3 + w, i] = weights[w]
                
        # Locate tangible anchors
        max_sharpe_idx = np.argmax(sim_results[2])
        min_vol_idx = np.argmin(sim_results[1])
        
        max_sharpe_allocation = {asset_columns[a]: float(sim_results[3 + a, max_sharpe_idx]) for a in range(num_assets)}
        min_vol_allocation = {asset_columns[a]: float(sim_results[3 + a, min_vol_idx]) for a in range(num_assets)}
        
        return {
            "assets": asset_columns,
            "max_sharpe": {
                "return": float(sim_results[0, max_sharpe_idx]),
                "risk": float(sim_results[1, max_sharpe_idx]),
                "sharpe": float(sim_results[2, max_sharpe_idx]),
                "weights": max_sharpe_allocation
            },
            "min_variance": {
                "return": float(sim_results[0, min_vol_idx]),
                "risk": float(sim_results[1, min_vol_idx]),
                "sharpe": float(sim_results[2, min_vol_idx]),
                "weights": min_vol_allocation
            },
            "frontier_returns": sim_results[0].tolist(),
            "frontier_risks": sim_results[1].tolist()
        }
