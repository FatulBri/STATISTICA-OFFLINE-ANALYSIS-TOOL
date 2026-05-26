/** Remove bulky time-series blobs before narrative / Gemini (keeps inference tables). */
export function slimSummaryForNarrative(summary: Record<string, any>): Record<string, any> {
  const slim = JSON.parse(JSON.stringify(summary));

  const stripKeys = ['drawdowns_series', 'returns_series', 'forecast_series', 'volatility_series', 'equity_curve'];

  const walk = (obj: Record<string, unknown>) => {
    if (!obj || typeof obj !== 'object') return;
    for (const key of Object.keys(obj)) {
      const val = obj[key];
      if (stripKeys.includes(key) && Array.isArray(val) && val.length > 20) {
        delete obj[key];
      } else if (val && typeof val === 'object' && !Array.isArray(val)) {
        walk(val as Record<string, unknown>);
      }
    }
  };

  walk(slim);
  return slim;
}
