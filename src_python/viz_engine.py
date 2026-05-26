import os
import io
import numpy as np
import pandas as pd

# Safe Matplotlib setup for server/container execution
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger("viz_engine")

class VisualEngine:
    def __init__(self, output_dir: str, dpi: int = 180):
        self.output_dir = output_dir
        self.charts_dir = os.path.join(output_dir, "charts")
        self.dpi = max(72, min(int(dpi), 600))
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # Professional Styling setups
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
        sns.set_palette("muted")
        
    def _save_png(self, filename: str) -> str:
        """Helper to save clean Matplotlib charts and close figure safely."""
        path = os.path.join(self.charts_dir, filename)
        plt.tight_layout()
        plt.savefig(path, dpi=self.dpi, facecolor='#ffffff', edgecolor='none')
        plt.close()
        return path

    def generate_histogram(self, df: pd.DataFrame, col: str) -> Tuple[str, str]:
        """Draw distribution histogram with KDE overlay (PNG & Interactive)."""
        series = df[col].dropna()
        
        # 1. PNG Chart
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(series, kde=True, color="#0284c7", alpha=0.6, ax=ax)
        ax.set_title(f"Distribution Analysis: {col}", fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel(col)
        ax.set_ylabel("Frequencies")
        png_path = self._save_png(f"histogram_{col}.png")
        
        # 2. Plotly HTML
        fig_ly = px.histogram(df, x=col, marginal="box", title=f"Visual Distribution: {col}", color_discrete_sequence=["#0284c7"])
        fig_ly.update_layout(template="plotly_dark", plot_bgcolor="#1e293b", paper_bgcolor="#0f172a")
        html_path = os.path.join(self.charts_dir, f"histogram_{col}.html")
        fig_ly.write_html(html_path)
        
        return png_path, html_path

    def generate_boxplot(self, df: pd.DataFrame, numeric_col: str, group_col: Optional[str] = None) -> Tuple[str, str]:
        """Draw distribution Boxplot comparisons."""
        sub = df[[numeric_col] + ([group_col] if group_col else [])].dropna()
        
        # 1. PNG Chart
        fig, ax = plt.subplots(figsize=(6, 4))
        if group_col:
            sns.boxplot(data=sub, x=group_col, y=numeric_col, ax=ax, palette="Blues")
            ax.set_title(f"Box Plot comparison of '{numeric_col}' across '{group_col}'", fontsize=10, fontweight='bold')
        else:
            sns.boxplot(data=sub, y=numeric_col, ax=ax, color="#0ea5e9")
            ax.set_title(f"Box Plot: {numeric_col}", fontsize=11, fontweight='bold')
            
        png_path = self._save_png(f"boxplot_{numeric_col}.png")
        
        # 2. Interactive
        fig_ly = px.box(sub, x=group_col, y=numeric_col, color=group_col, points="all", title=f"Interactive Dispersion: {numeric_col}", template="plotly_dark")
        fig_ly.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#0f172a")
        html_path = os.path.join(self.charts_dir, f"boxplot_{numeric_col}.html")
        fig_ly.write_html(html_path)
        
        return png_path, html_path

    def generate_scatter_trend(self, df: pd.DataFrame, x_col: str, y_col: str) -> Tuple[str, str]:
        """Generate Scatter plots with OLS regression trends."""
        sub = df[[x_col, y_col]].dropna()
        
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.regplot(data=sub, x=x_col, y=y_col, ax=ax, scatter_kws={"color": "#6366f1", "alpha": 0.5}, line_kws={"color": "#ef4444", "linewidth": 2})
        ax.set_title(f"Correlation Scatter: {x_col} vs {y_col}", fontsize=11, fontweight='bold')
        png_path = self._save_png(f"scatter_{x_col}_{y_col}.png")
        
        fig_ly = px.scatter(sub, x=x_col, y=y_col, trendline="ols", title=f"Regression trend: {x_col} vs {y_col}", template="plotly_dark")
        fig_ly.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#0f172a")
        html_path = os.path.join(self.charts_dir, f"scatter_{x_col}_{y_col}.html")
        fig_ly.write_html(html_path)
        
        return png_path, html_path

    def generate_qq_plot(self, df: pd.DataFrame, col: str) -> str:
        """Create Q-Q Plot for Normality verification (PNG only)."""
        series = df[col].dropna()
        fig, ax = plt.subplots(figsize=(6, 4))
        stats.probplot(series, dist="norm", plot=ax)
        ax.set_title(f"Q-Q Probability Plot: {col}", fontsize=11, fontweight='bold')
        ax.get_lines()[0].set_color("#6b7280")
        ax.get_lines()[0].set_alpha(0.6)
        ax.get_lines()[1].set_color("#ef4444")
        return self._save_png(f"qq_{col}.png")

    def generate_heatmap(self, corr_output: Dict[str, Any]) -> Tuple[str, str]:
        """Draw gorgeous glowing correlation heatmaps."""
        cols = corr_output["columns"]
        coeffs = pd.DataFrame(corr_output["coefficients"], index=cols)
        
        # 1. PNG heat
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(coeffs, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f", ax=ax, linewidths=0.5)
        ax.set_title("Correlation Heatmap Matrix", fontsize=11, fontweight='bold', pad=10)
        png_path = self._save_png("correlation_heatmap.png")
        
        # 2. Plotly Interactive
        fig_ly = go.Figure(data=go.Heatmap(
            z=coeffs.values,
            x=cols,
            y=cols,
            colorscale='RdBu',
            zmin=-1,
            zmax=1,
            text=np.round(coeffs.values, 2),
            texttemplate="%{text}",
            hoverongaps = False
        ))
        fig_ly.update_layout(title="Interactive Heatmap", template="plotly_dark", plot_bgcolor="#1e293b", paper_bgcolor="#0f172a")
        html_path = os.path.join(self.charts_dir, "correlation_heatmap.html")
        fig_ly.write_html(html_path)
        
        return png_path, html_path

    def generate_scree_plot(self, eigenvalues: List[float]) -> Tuple[str, str]:
        """Draw EFA Scree eigenvalues graph to identify latent components."""
        factors = list(range(1, len(eigenvalues) + 1))
        
        # PNG
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(factors, eigenvalues, 'o-', color='#e11d48', linewidth=2, markersize=6)
        ax.axhline(y=1, color='#475569', linestyle='--')
        ax.set_title("Scree Plot: Latent Factor Eigenvalues", fontsize=11, fontweight='bold')
        ax.set_xlabel("Factor Numbers")
        ax.set_ylabel("Eigenvalues")
        png_path = self._save_png("scree_plot.png")
        
        # Interactive
        fig_ly = go.Figure()
        fig_ly.add_trace(go.Scatter(x=factors, y=eigenvalues, mode='lines+markers', name='Eigenvalue', line=dict(color='#e11d48', width=3)))
        fig_ly.add_shape(type="line", x0=1, y0=1, x1=len(factors), y1=1, line=dict(color="#475569", dash="dash"))
        fig_ly.update_layout(title="Scree Plot (Kaiser Criterion: eigenvalue > 1.0)", xaxis_title="Factors", yaxis_title="Eigenvalue", template="plotly_dark", plot_bgcolor="#1e293b", paper_bgcolor="#0f172a")
        
        html_path = os.path.join(self.charts_dir, "scree_plot.html")
        fig_ly.write_html(html_path)
        
        return png_path, html_path

    def generate_roc_curve(self, y_true: list, y_prob: list) -> str:
        """Draw Receiver Operating Characteristic (ROC) curve analysis (PNG to go in reports)."""
        from sklearn.metrics import roc_curve, auc
        fpr, tpr, thresh = roc_curve(y_true, y_prob)
        roc_auc = auc(fpr, tpr)
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(fpr, tpr, color='#0ea5e9', lw=2, label=f'Model ROC (AUC = {roc_auc:.3f})')
        ax.plot([0, 1], [0, 1], color='#64748b', lw=1.5, linestyle='--')
        ax.set_xlabel('False Positive Rates')
        ax.set_ylabel('True Positive Rates')
        ax.set_title('ROC Curve Performance Diagnostics', fontsize=11, fontweight='bold')
        ax.legend(loc="lower right")
        return self._save_png("roc_curve.png")

    def generate_pie_chart(self, df: pd.DataFrame, col: str) -> Tuple[str, str]:
        """Pie/donut chart summaries for categorical variables."""
        counts = df[col].dropna().value_counts()
        
        # PNG
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Pastel1"))
        ax.set_title(f"Distribution of Items: {col}", fontsize=11, fontweight='bold')
        png_path = self._save_png(f"pie_{col}.png")
        
        # Interactive Donut
        fig_ly = px.pie(values=counts.values, names=counts.index, hole=.4, title=f"Interactive Shares: {col}", template="plotly_dark")
        fig_ly.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#0f172a")
        html_path = os.path.join(self.charts_dir, f"pie_{col}.html")
        fig_ly.write_html(html_path)
        
        return png_path, html_path

    def generate_financial_chart(self, df_ind: pd.DataFrame, price_col: str) -> Tuple[str, str]:
        """Price charts and Bollinger Technical analytics panels."""
        sub = df_ind.tail(100) # zoom last 100 periods
        indices = np.arange(len(sub))
        
        # 1. Matplotlib Panels
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
        
        # Price panel
        ax1.plot(indices, sub[price_col], label="Asset Price", color="#1e1b4b", lw=1.5)
        ax1.plot(indices, sub["SMA_20"], label="SMA 20", color="#f97316", linestyle="--", lw=1)
        ax1.fill_between(indices, sub["BB_Lower"], sub["BB_Upper"], alpha=0.1, color="#3b82f6", label="Bollinger Bands")
        ax1.set_title("Historical Asset Price & Bollinger Overlays", fontsize=11, fontweight="bold")
        ax1.legend(loc="upper left", fontsize=8)
        
        # RSI panel
        ax2.plot(indices, sub["RSI_14"], color="#8b5cf6", lw=1.2, label="RSI 14")
        ax2.axhline(y=70, color='#ef4444', linestyle=':', lw=1)
        ax2.axhline(y=30, color='#22c55e', linestyle=':', lw=1)
        ax2.set_ylabel("RSI Index")
        ax2.set_ylim(10, 90)
        ax2.legend(loc="upper left", fontsize=8)
        
        png_path = self._save_png("financial_analysis.png")
        
        # 2. Plotly Candlestick or OHLC with technical overlays (uses line graph since standalone uploads may lack Open/High/Low)
        fig_ly = go.Figure()
        fig_ly.add_trace(go.Scatter(x=df_ind.index, y=df_ind[price_col], name='Asset price', line=dict(color='#3b82f6', width=2)))
        fig_ly.add_trace(go.Scatter(x=df_ind.index, y=df_ind["BB_Upper"], name='BB Upper', line=dict(color='#475569', dash='dash', width=1)))
        fig_ly.add_trace(go.Scatter(x=df_ind.index, y=df_ind["BB_Lower"], name='BB Lower', line=dict(color='#475569', dash='dash', width=1), fill='tonexty'))
        fig_ly.update_layout(title="Market Price & Tech Channels", template="plotly_dark", plot_bgcolor="#1e293b", paper_bgcolor="#0f172a")
        
        html_path = os.path.join(self.charts_dir, "financial_analysis.html")
        fig_ly.write_html(html_path)
        
        return png_path, html_path

    def generate_drawdown_plot(self, dd_series: List[float]) -> str:
        """Asset peak-to-trough Drawdown curve."""
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.fill_between(np.arange(len(dd_series)), dd_series, 0, color='#ef4444', alpha=0.3)
        ax.plot(dd_series, color='#ef4444', lw=1.5, label='Drawdown %')
        ax.set_title("Premium Trading Peak-to-Trough Drawdowns", fontsize=11, fontweight="bold")
        ax.set_ylabel("Percentage Loss")
        ax.legend()
        return self._save_png("drawdown_analysis.png")

    def generate_feature_importance_plot(self, model_res: Dict[str, Any], prefix: str):
        """Generate a horizontal bar chart for Random Forest feature importances."""
        if "feature_importance" not in model_res or not model_res["feature_importance"]:
            return
            
        try:
            feats = [f["feature"] for f in model_res["feature_importance"]][:15] # Top 15
            imps = [f["importance"] for f in model_res["feature_importance"]][:15]
            
            # Reverse to have highest on top of horizontal bar
            feats.reverse()
            imps.reverse()
            
            fig = px.bar(
                x=imps, y=feats, orientation='h',
                title="Random Forest Feature Importance",
                labels={"x": "Importance", "y": "Feature"},
                color=imps,
                color_continuous_scale="Blues"
            )
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
            
            fig.write_html(os.path.join(self.charts_dir, f"{prefix}_feat_imp.html"), include_plotlyjs=False)
            fig.write_image(os.path.join(self.charts_dir, f"{prefix}_feat_imp.png"), scale=2, width=800, height=500)
        except Exception as e:
            logger.warning(f"Could not generate feature importance plot: {e}")

    def generate_confusion_matrix_heatmap(self, model_res: Dict[str, Any]):
        """Generate a heatmap for Random Forest classification confusion matrix."""
        if "confusion_matrix" not in model_res or "labels" not in model_res:
            return
            
        try:
            cm = np.array(model_res["confusion_matrix"])
            labels = model_res["labels"]
            
            fig = px.imshow(
                cm, text_auto=True, 
                labels=dict(x="Predicted Label", y="True Label", color="Count"),
                x=labels, y=labels,
                color_continuous_scale="Blues",
                title="Confusion Matrix"
            )
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
            
            fig.write_html(os.path.join(self.charts_dir, "random_forest_confusion_matrix.html"), include_plotlyjs=False)
            fig.write_image(os.path.join(self.charts_dir, "random_forest_confusion_matrix.png"), scale=2, width=600, height=500)
        except Exception as e:
            logger.warning(f"Could not generate confusion matrix plot: {e}")

    def generate_efficient_frontier_plot(self, opt_output: Dict[str, Any]) -> Tuple[str, str]:
        """Draw Markowitz Mean-Variance Portfolio Frontiers."""
        risks = opt_output["frontier_risks"]
        rets = opt_output["frontier_returns"]
        
        ms_port = opt_output["max_sharpe"]
        mv_port = opt_output["min_variance"]
        
        # Matplotlib PNG
        fig, ax = plt.subplots(figsize=(6, 4))
        sc = ax.scatter(risks, rets, c=np.array(rets)/np.array(risks), cmap='viridis', marker='o', s=10, alpha=0.3)
        ax.plot(ms_port["risk"], ms_port["return"], 'r*', markersize=15, label='Max Sharpe Allocation')
        ax.plot(mv_port["risk"], mv_port["return"], 'b*', markersize=15, label='Min Volatility Allocation')
        ax.set_title("Efficient Portfolio Frontier Boundary (Markowitz)", fontsize=11, fontweight='bold')
        ax.set_xlabel("Annualized Portfolio Risk (StDev)")
        ax.set_ylabel("Annualized Expected Return")
        ax.legend()
        png_path = self._save_png("portfolio_efficient_frontier.png")
        
        # Interactive bubble tracer
        fig_ly = go.Figure()
        fig_ly.add_trace(go.Scatter(x=risks, y=rets, mode='markers', marker=dict(color=np.array(rets)/np.array(risks), colorscale='Viridis', showscale=True), name='Portfolios'))
        fig_ly.add_trace(go.Scatter(x=[ms_port["risk"]], y=[ms_port["return"]], mode='markers', marker=dict(color='red', size=15, symbol='star'), name='Model Tangency (Max Sharpe)'))
        fig_ly.add_trace(go.Scatter(x=[mv_port["risk"]], y=[mv_port["return"]], mode='markers', marker=dict(color='blue', size=15, symbol='star'), name='Min Volatility'))
        fig_ly.update_layout(title="Markowitz Portfolio Optimization Frontier", xaxis_title="Standard Deviation", yaxis_title="Annualized Return", template="plotly_dark", plot_bgcolor="#1e293b", paper_bgcolor="#0f172a")
        
        html_path = os.path.join(self.charts_dir, "portfolio_efficient_frontier.html")
        fig_ly.write_html(html_path)
        
        return png_path, html_path

    def generate_mirt_surface(self, mirt_output: Dict[str, Any]) -> str:
        """Create beautiful interactive 3D WebGL probability surfaces for 2D MIRT."""
        x = mirt_output["theta1_grid"]
        y = mirt_output["theta2_grid"]
        
        # Take item 0 as showcase surface
        if not mirt_output.get("items"):
            return ""
            
        item = mirt_output["items"][0]
        surf = item["surface"]
        
        fig = go.Figure(data=[go.Surface(z=surf, x=x, y=y, colorscale='Cividis')])
        fig.update_layout(
            title=f"3D Multidimensional Item Response Curve: {item['item']}",
            scene = dict(
                xaxis_title='Latent Dimension 1 (Theta 1)',
                yaxis_title='Latent Dimension 2 (Theta 2)',
                zaxis_title='Correct Answer Probability P(Theta)'
            ),
            template="plotly_dark",
            margin=dict(l=0, r=0, b=0, t=40),
            plot_bgcolor="#1e293b", paper_bgcolor="#0f172a"
        )
        
        html_path = os.path.join(self.charts_dir, "mirt_response_surface.html")
        fig.write_html(html_path)
        return html_path

    def generate_cluster_scatter_plot(self, df: pd.DataFrame, cluster_res: Dict[str, Any], features: List[str]):
        """Generate a 2D or 3D scatter plot of K-Means clusters."""
        if "labels" not in cluster_res:
            return
            
        try:
            plot_df = df[features].copy()
            plot_df['Cluster'] = [str(lbl) for lbl in cluster_res["labels"]]
            
            if len(features) >= 3:
                # 3D Plot using first 3 features
                fig = px.scatter_3d(
                    plot_df, x=features[0], y=features[1], z=features[2],
                    color='Cluster', title="3D K-Means Cluster Segmentation",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
            elif len(features) == 2:
                # 2D Plot
                fig = px.scatter(
                    plot_df, x=features[0], y=features[1],
                    color='Cluster', title="2D K-Means Cluster Segmentation",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
            else:
                return # Need at least 2 features to scatter
                
            fig.update_layout(template="plotly_dark", plot_bgcolor="#1e293b", paper_bgcolor="#0f172a")
            fig.write_html(os.path.join(self.charts_dir, "cluster_scatter.html"), include_plotlyjs=False)
            fig.write_image(os.path.join(self.charts_dir, "cluster_scatter.png"), scale=2, width=800, height=600)
        except Exception as e:
            logger.warning(f"Could not generate cluster scatter plot: {e}")

    def generate_pca_variance_plot(self, pca_res: Dict[str, Any]):
        """Generate Scree plot for PCA explained variance."""
        if "explained_variance_ratio" not in pca_res:
            return
            
        try:
            explained_var = pca_res["explained_variance_ratio"]
            cumulative_var = pca_res["cumulative_variance"]
            components = [f"PC{i+1}" for i in range(len(explained_var))]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=components, y=explained_var,
                name="Individual Variance",
                marker_color="#0284c7"
            ))
            fig.add_trace(go.Scatter(
                x=components, y=cumulative_var,
                mode="lines+markers",
                name="Cumulative Variance",
                line=dict(color="#f43f5e", width=3)
            ))
            
            fig.update_layout(
                title="PCA Explained Variance Ratio",
                xaxis_title="Principal Components",
                yaxis_title="Explained Variance (%)",
                template="plotly_dark",
                plot_bgcolor="#1e293b", paper_bgcolor="#0f172a",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            fig.write_html(os.path.join(self.charts_dir, "pca_variance.html"), include_plotlyjs=False)
            fig.write_image(os.path.join(self.charts_dir, "pca_variance.png"), scale=2, width=800, height=500)
        except Exception as e:
            logger.warning(f"Could not generate PCA variance plot: {e}")

