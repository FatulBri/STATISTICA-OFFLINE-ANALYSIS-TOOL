import os
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger("data_manager")

class DataManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_ext = os.path.splitext(file_path)[1].lower()
        self.sheets: List[str] = []
        self.active_df: Optional[pd.DataFrame] = None
        self.active_sheet: Optional[str] = None
        self._inspect_file()

    def _inspect_file(self) -> None:
        """Inspect sheets if file is Excel."""
        if self.file_ext in [".xlsx", ".xls"]:
            try:
                xl = pd.ExcelFile(self.file_path)
                self.sheets = xl.sheet_names
                if self.sheets:
                    self.active_sheet = self.sheets[0]
            except Exception as e:
                logger.error(f"Error inspecting Excel file {self.file_path}: {e}")
                self.sheets = []
        else:
            self.sheets = []

    def load_data(self, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Load data from active sheet or file into pandas DataFrame."""
        try:
            if self.file_ext in [".xlsx", ".xls"]:
                target_sheet = sheet_name or self.active_sheet or (self.sheets[0] if self.sheets else None)
                if not target_sheet:
                    self.active_df = pd.read_excel(self.file_path)
                else:
                    self.active_df = pd.read_excel(self.file_path, sheet_name=target_sheet)
                    self.active_sheet = target_sheet
            elif self.file_ext == ".csv":
                self.active_df = pd.read_csv(self.file_path)
            else:
                raise ValueError("Unsupported file format. Please use Excel (.xlsx/.xls) or CSV.")
            
            # Basic cleanup: remove entirely empty rows/columns
            self.active_df.dropna(how="all", inplace=True)
            return self.active_df
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise

    def get_summary_stats(self) -> Dict[str, Any]:
        """Generate comprehensive diagnostic summary of loaded active dataset."""
        if self.active_df is None:
            raise ValueError("No dataset loaded. Run load_data() first.")
        
        df = self.active_df
        num_rows, num_cols = df.shape
        columns_info = {}
        
        # Missing values detection
        missing_counts = df.isnull().sum().to_dict()
        duplicates_count = int(df.duplicated().sum())
        
        numeric_cols = []
        categorical_cols = []
        date_cols = []
        binary_cols = []
        
        for col in df.columns:
            series = df[col]
            missing = int(missing_counts[col])
            missing_pct = float(missing / num_rows) * 100 if num_rows > 0 else 0
            
            # Detect dates
            is_date = False
            if pd.api.types.is_datetime64_any_dtype(series):
                is_date = True
            else:
                try:
                    # check if string column can be parsed into dates successfully
                    if series.dtype == 'object' and series.dropna().astype(str).str.match(r'\d{4}-\d{2}-\d{2}').all():
                        is_date = True
                except:
                    pass
            
            # Unique counts
            unique_values = series.dropna().unique()
            num_unique = len(unique_values)
            
            # Check numeric. Fully empty columns should not be treated as usable numeric variables.
            non_missing_count = int(num_rows - missing)
            is_numeric = pd.api.types.is_numeric_dtype(series) and non_missing_count > 0
            
            # Check binary (0/1 or False/True or exactly 2 classes)
            is_binary = False
            if num_unique == 2:
                # If numeric or simple codes
                set_vals = set(unique_values)
                if set_vals.issubset({0, 1, 0.0, 1.0}) or set_vals.issubset({False, True}) or set_vals.issubset({"0", "1"}):
                    is_binary = True

            col_type = "Numeric" if is_numeric else "Categorical"
            if is_date:
                col_type = "Date/Time"
                date_cols.append(col)
            elif is_binary:
                col_type = "Binary"
                binary_cols.append(col)
                numeric_cols.append(col)  # Binary is treated as numeric for psychometrics IRT
            elif is_numeric:
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)
                
            columns_info[col] = {
                "type": col_type,
                "missing": missing,
                "missing_pct": missing_pct,
                "unique_count": num_unique,
                "is_binary": is_binary,
                "is_numeric": is_numeric,
                "is_date": is_date
            }
            
        auto_recommendations = self._generate_recommendations(df, columns_info, date_cols, binary_cols, numeric_cols, categorical_cols)
        
        return {
            "fileName": os.path.basename(self.file_path),
            "rows": num_rows,
            "columns": num_cols,
            "sheets": self.sheets,
            "activeSheet": self.active_sheet,
            "duplicates": duplicates_count,
            "columnsList": list(df.columns),
            "columnsDetails": columns_info,
            "numericColumns": numeric_cols,
            "categoricalColumns": categorical_cols,
            "dateColumns": date_cols,
            "binaryColumns": binary_cols,
            "recommendations": auto_recommendations
        }

    def _generate_recommendations(self, df: pd.DataFrame, columns_info: Dict[str, Any], date_cols: List[str], binary_cols: List[str], numeric_cols: List[str], categorical_cols: List[str]) -> List[str]:
        """Automatically list analytical workflows to recommend based on column types."""
        recs = []
        
        if len(binary_cols) >= 5:
            recs.append("PSYCHOMETRICS: High number of binary columns detected. Formulating Item Response Theory (IRT) modeling is recommended.")
        
        # Financial indicator columns
        finance_keywords = ["price", "close", "open", "adj close", "high", "low", "volume", "returns", "return"]
        has_finance_cols = False
        for col in df.columns:
            if any(kw in col.lower() for kw in finance_keywords):
                has_finance_cols = True
                break
                
        if has_finance_cols and (len(date_cols) > 0 or "date" in [c.lower() for c in df.columns]):
            recs.append("FINANCIAL: Dataset contains market keywords and dates. Time-series core, portfolio optimization, VaR/CVaR, GARCH price volatility, and ARIMA forecasting are recommended.")
            
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            recs.append("GROUP COMPARISON: Continuous numerical response columns paired with discrete factor categorical levels. Run One-Way ANOVA + post-hoc Tukey HSD and Paired/Independent T-Tests.")
            
        if len(date_cols) > 0:
            recs.append("STATISTICAL: Temporal date/time indices available. Carry out time series analysis and forecasts (smoothing, trend, seasonal decompositions).")
            
        if len(numeric_cols) >= 5 and len(binary_cols) < 5:
            recs.append("PSYCHOMETRICS: Multiple continuous scale metrics. Consider Exploratory Factor Analysis (EFA), KMO scale adequacy, Bartlett Sphericity, and Cronbach's Alpha internal consistency.")
            
        if len(numeric_cols) >= 2:
            recs.append("STATISTICAL: Run multi-variable Pearson/Spearman correlation matrices and Linear/Logistic regression forecasting.")
            
        if df.isnull().sum().sum() > 0:
            recs.append("DATA HEALTH: Missing entries detected. Use statistical imputation or pairwise/listwise deletions prior to processing.")
            
        if len(recs) == 0:
            recs.append("STATISTICAL: General tabular dataset. Run standard Descriptive summaries, distribution normality reports, and outlier detection.")
            
        return recs
