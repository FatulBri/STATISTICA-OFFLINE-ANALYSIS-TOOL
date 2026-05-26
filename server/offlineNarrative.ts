type Lang = 'en' | 'id';

function sigLabel(p: number | undefined, lang: Lang): string {
  if (p === undefined || Number.isNaN(p)) return lang === 'id' ? 'tidak tersedia' : 'n/a';
  if (p < 0.001) return lang === 'id' ? 'sangat signifikan (p < .001)' : 'highly significant (p < .001)';
  if (p < 0.05) return lang === 'id' ? 'signifikan (p < .05)' : 'significant (p < .05)';
  return lang === 'id' ? 'tidak signifikan (p ≥ .05)' : 'not significant (p ≥ .05)';
}

function section(title: string, body: string[]): string {
  return `## ${title}\n\n${body.join('\n\n')}`;
}

export function generateOfflineNarrative(summary: Record<string, any>, lang: Lang = 'en'): string {
  const L = lang === 'id';
  const rows = summary.rows ?? 0;
  const cols = summary.columns ?? 0;
  const dup = summary.duplicates ?? 0;
  const cfg = summary.appliedConfig || {};
  const parts: string[] = [];

  parts.push(
    L
      ? `### Laporan Interpretasi STATISTICA (Offline)\n\nAnalisis otomatis atas **${rows}** baris dan **${cols}** kolom. Mesin berjalan sepenuhnya lokal tanpa mengirim data ke cloud.`
      : `### STATISTICA Offline Interpretation Report\n\nAutomated review of **${rows}** rows and **${cols}** columns. Engine ran fully locally with no data sent to the cloud.`
  );

  const integrity: string[] = [];
  integrity.push(
    L
      ? dup > 0
        ? `Ditemukan **${dup}** baris duplikat. Pertimbangkan deduplikasi sebelum inferensi parametrik.`
        : `Tidak ada duplikat baris penuh — integritas struktur baris baik.`
      : dup > 0
        ? `**${dup}** duplicate rows detected. Consider deduplication before parametric inference.`
        : `No full-row duplicates — row-level integrity looks acceptable.`
  );
  if (summary.recommendations?.length) {
    integrity.push(
      L ? '**Rekomendasi mesin:**' : '**Engine recommendations:**'
    );
    for (const r of summary.recommendations.slice(0, 4)) {
      integrity.push(`- ${r}`);
    }
  }
  parts.push(section(L ? 'Integritas Data' : 'Data Integrity', integrity));

  const desc = summary.descriptive || {};
  const descKeys = Object.keys(desc);
  if (descKeys.length) {
    const lines: string[] = [];
    lines.push(
      L
        ? `Deskriptif dihitung untuk ${descKeys.length} variabel numerik.`
        : `Descriptive statistics computed for ${descKeys.length} numeric variables.`
    );
    for (const col of descKeys.slice(0, 5)) {
      const m = desc[col];
      if (!m?.mean) continue;
      const skew = m.skewness ?? 0;
      const shape =
        Math.abs(skew) < 0.5
          ? L ? 'simetris mendekati normal' : 'approximately symmetric'
          : skew > 0
            ? L ? 'condong kanan (positif skew)' : 'right-skewed'
            : L ? 'condong kiri (negatif skew)' : 'left-skewed';
      lines.push(
        L
          ? `**${col}:** μ = ${m.mean.toFixed(3)}, σ = ${m.std?.toFixed(3)}, skew = ${skew.toFixed(2)} (${shape}).`
          : `**${col}:** μ = ${m.mean.toFixed(3)}, σ = ${m.std?.toFixed(3)}, skew = ${skew.toFixed(2)} (${shape}).`
      );
    }
    parts.push(section(L ? 'Ringkasan Deskriptif' : 'Descriptive Overview', lines));
  }

  const norm = summary.normality || {};
  if (Object.keys(norm).length) {
    const lines: string[] = [];
    for (const [col, tests] of Object.entries(norm).slice(0, 4)) {
      const t = tests as Record<string, any>;
      const sw = t.shapiro;
      if (sw && !sw.error) {
        lines.push(
          L
            ? `**${col}** (Shapiro-Wilk): ${sw.normal ? 'tidak menolak normalitas' : 'menolak normalitas'} (p = ${sw.p_value?.toFixed(4)}).`
            : `**${col}** (Shapiro-Wilk): ${sw.normal ? 'does not reject normality' : 'rejects normality'} (p = ${sw.p_value?.toFixed(4)}).`
        );
      }
    }
    parts.push(section(L ? 'Uji Normalitas' : 'Normality Assessment', lines));
  }

  const reg = summary.linear_regression;
  if (reg && !reg.error) {
    const lines: string[] = [];
    lines.push(
      L
        ? `Regresi OLS: **${cfg.regressionTarget || 'Y'}** ~ ${(cfg.regressionPredictors || []).join(', ') || 'prediktor'}.`
        : `OLS regression: **${cfg.regressionTarget || 'Y'}** ~ ${(cfg.regressionPredictors || []).join(', ') || 'predictors'}.`
    );
    lines.push(
      L
        ? `R² = ${reg.r_squared?.toFixed(4)}, R² adj = ${reg.adj_r_squared?.toFixed(4)}, n = ${reg.n_observations}.`
        : `R² = ${reg.r_squared?.toFixed(4)}, adj. R² = ${reg.adj_r_squared?.toFixed(4)}, n = ${reg.n_observations}.`
    );
    const sigFeat = (reg.features || []).filter((f: any) => f.significant);
    if (sigFeat.length) {
      lines.push(
        L
          ? `Prediktor signifikan: ${sigFeat.map((f: any) => `${f.feature} (β=${f.coefficient?.toFixed(3)}, p=${f.p_value?.toFixed(4)})`).join('; ')}.`
          : `Significant predictors: ${sigFeat.map((f: any) => `${f.feature} (β=${f.coefficient?.toFixed(3)}, p=${f.p_value?.toFixed(4)})`).join('; ')}.`
      );
    } else {
      lines.push(L ? 'Tidak ada prediktor signifikan pada α = .05.' : 'No predictors significant at α = .05.');
    }
    parts.push(section(L ? 'Regresi Linear' : 'Linear Regression', lines));
  }

  const anova = summary.one_way_anova;
  if (anova && !anova.error) {
    parts.push(
      section(
        L ? 'ANOVA Satu Arah' : 'One-Way ANOVA',
        [
          L
            ? `Membandingkan **${cfg.anovaTarget}** menurut faktor **${cfg.anovaGroup}** (${(anova.groups || []).length} grup).`
            : `Comparing **${cfg.anovaTarget}** across **${cfg.anovaGroup}** (${(anova.groups || []).length} groups).`,
          L
            ? `F = ${anova.f_statistic?.toFixed(4)}, p = ${anova.p_value?.toFixed(5)} — ${sigLabel(anova.p_value, lang)}. η² = ${anova.eta_squared?.toFixed(4)}.`
            : `F = ${anova.f_statistic?.toFixed(4)}, p = ${anova.p_value?.toFixed(5)} — ${sigLabel(anova.p_value, lang)}. η² = ${anova.eta_squared?.toFixed(4)}.`,
        ]
      )
    );
  }

  const tt = summary.independent_t_test;
  if (tt && !tt.error) {
    parts.push(
      section(
        L ? 'Uji-t Sampel Independen' : 'Independent Samples T-Test',
        [
          L
            ? `Grup: ${(tt.group_names || []).join(' vs ')} pada **${cfg.ttestTarget}**.`
            : `Groups: ${(tt.group_names || []).join(' vs ')} on **${cfg.ttestTarget}**.`,
          L
            ? `t = ${tt.statistic?.toFixed(4)}, p = ${tt.p_value?.toFixed(5)} — ${sigLabel(tt.p_value, lang)}. Cohen's d = ${tt.cohens_d?.toFixed(3)}.`
            : `t = ${tt.statistic?.toFixed(4)}, p = ${tt.p_value?.toFixed(5)} — ${sigLabel(tt.p_value, lang)}. Cohen's d = ${tt.cohens_d?.toFixed(3)}.`,
        ]
      )
    );
  }

  const chi = summary.chi_square;
  if (chi && !chi.error) {
    parts.push(
      section(
        L ? 'Chi-Square' : 'Chi-Square Test',
        [
          L
            ? `**${cfg.chiSquareCol1}** × **${cfg.chiSquareCol2}**: χ² = ${chi.chi2_statistic?.toFixed(4)}, p = ${chi.p_value?.toFixed(5)} (${sigLabel(chi.p_value, lang)}). Cramer V = ${chi.cramers_v?.toFixed(4)}.`
            : `**${cfg.chiSquareCol1}** × **${cfg.chiSquareCol2}**: χ² = ${chi.chi2_statistic?.toFixed(4)}, p = ${chi.p_value?.toFixed(5)} (${sigLabel(chi.p_value, lang)}). Cramer's V = ${chi.cramers_v?.toFixed(4)}.`,
        ]
      )
    );
  }

  const logit = summary.logistic_regression;
  if (logit && !logit.error) {
    parts.push(
      section(
        L ? 'Regresi Logistik' : 'Logistic Regression',
        [
          L
            ? `Target **${cfg.logisticTarget}**: pseudo R² = ${logit.pseudo_r_squared?.toFixed(4)}, akurasi klasifikasi = ${((logit.accuracy || 0) * 100).toFixed(1)}%.`
            : `Target **${cfg.logisticTarget}**: pseudo R² = ${logit.pseudo_r_squared?.toFixed(4)}, classification accuracy = ${((logit.accuracy || 0) * 100).toFixed(1)}%.`,
        ]
      )
    );
  }

  const paired = summary.paired_t_test;
  if (paired && !paired.error) {
    parts.push(
      section(
        L ? 'Uji-t Berpasangan' : 'Paired T-Test',
        [
          L
            ? `**${cfg.pairedPre}** vs **${cfg.pairedPost}**: perbedaan mean = ${paired.mean_difference?.toFixed(4)}, p = ${paired.p_value?.toFixed(5)} (${sigLabel(paired.p_value, lang)}).`
            : `**${cfg.pairedPre}** vs **${cfg.pairedPost}**: mean diff = ${paired.mean_difference?.toFixed(4)}, p = ${paired.p_value?.toFixed(5)} (${sigLabel(paired.p_value, lang)}).`,
          summary.n_gain_score
            ? L
              ? `N-Gain rata-rata: ${((summary.n_gain_score.mean_gain || 0) * 100).toFixed(1)}% (${summary.n_gain_score.category}).`
              : `Mean N-Gain: ${((summary.n_gain_score.mean_gain || 0) * 100).toFixed(1)}% (${summary.n_gain_score.category}).`
            : '',
        ].filter(Boolean)
      )
    );
  }

  const alpha = summary.cronbach_alpha;
  if (alpha && !alpha.error) {
    const a = alpha.alpha ?? alpha.cronbach_alpha;
    parts.push(
      section(
        L ? 'Psikometri — Reliabilitas' : 'Psychometrics — Reliability',
        [
          L
            ? `Cronbach α = ${typeof a === 'number' ? a.toFixed(3) : a}. ${a >= 0.8 ? 'Konsistensi internal kuat.' : a >= 0.7 ? 'Dapat diterima untuk penelitian eksploratori.' : 'Perlu revisi butir skala.'}`
            : `Cronbach α = ${typeof a === 'number' ? a.toFixed(3) : a}. ${a >= 0.8 ? 'Strong internal consistency.' : a >= 0.7 ? 'Acceptable for exploratory research.' : 'Consider item revision.'}`,
        ]
      )
    );
  }

  const fin = summary.financial_risk_reward;
  const arima = summary.arima_pricing_forecast;
  const garch = summary.garch_price_volatility;
  if (fin && !fin.error) {
    const finLines = [
      L
        ? `Seri harga: **${cfg.priceColumn}**. CAGR ≈ ${fin.cagr_pct?.toFixed(2)}%, Sharpe ≈ ${fin.sharpe_ratio?.toFixed(3)}, max drawdown ≈ ${fin.max_drawdown_pct?.toFixed(2)}%.`
        : `Price series: **${cfg.priceColumn}**. CAGR ≈ ${fin.cagr_pct?.toFixed(2)}%, Sharpe ≈ ${fin.sharpe_ratio?.toFixed(3)}, max drawdown ≈ ${fin.max_drawdown_pct?.toFixed(2)}%.`,
      L
        ? `VaR historis 95% ≈ ${fin.var_95_historical_pct?.toFixed(2)}%.`
        : `Historical 95% VaR ≈ ${fin.var_95_historical_pct?.toFixed(2)}%.`,
    ];
    if (arima && !arima.error && arima.forecast_values?.length) {
      const lastFc = arima.forecast_values[arima.forecast_values.length - 1];
      finLines.push(
        L
          ? `**ARIMA(1,1,1):** proyeksi harga terakhir ≈ ${Number(lastFc).toFixed(2)} (${arima.forecast_values.length} langkah).`
          : `**ARIMA(1,1,1):** last price forecast ≈ ${Number(lastFc).toFixed(2)} (${arima.forecast_values.length} steps).`
      );
    }
    if (garch && !garch.error) {
      const vols = garch.volatility_series as number[] | undefined;
      const lastVol = vols?.length ? vols[vols.length - 1] : null;
      finLines.push(
        L
          ? `**GARCH(1,1):** α=${garch.alpha_coefficient?.toFixed(4)}, β=${garch.beta_coefficient?.toFixed(4)}${lastVol != null ? `, vol ≈ ${(lastVol * 100).toFixed(3)}%` : ''}${garch.fallback_ewma ? ' (EWMA fallback)' : ''}.`
          : `**GARCH(1,1):** α=${garch.alpha_coefficient?.toFixed(4)}, β=${garch.beta_coefficient?.toFixed(4)}${lastVol != null ? `, vol ≈ ${(lastVol * 100).toFixed(3)}%` : ''}${garch.fallback_ewma ? ' (EWMA fallback)' : ''}.`
      );
    }
    parts.push(section(L ? 'Analisis Finansial' : 'Financial Analysis', finLines));
  }

  parts.push(
    section(
      L ? 'Kesimpulan Eksekutif' : 'Executive Conclusion',
      [
        L
          ? `Temuan di atas dihasilkan secara reproducible dari konfigurasi variabel yang Anda pilih. Grafik diekspor pada ${cfg.exportDpi || 180} DPI. Untuk publikasi, verifikasi asumsi (normalitas, homogenitas varians, linearitas) dan lampirkan tabel lengkap dari ekspor Word/HTML.`
          : `Findings above are reproducible from your selected variable mapping. Charts exported at ${cfg.exportDpi || 180} DPI. For publication, verify assumptions (normality, homogeneity, linearity) and attach full tables from Word/HTML exports.`,
        L
          ? '_Narasi offline STATISTICA. Opsional: aktifkan GEMINI_API_KEY untuk laporan bahasa alami yang diperkaya AI._'
          : '_STATISTICA offline narrative. Optional: set GEMINI_API_KEY for AI-enriched natural language._',
      ]
    )
  );

  return parts.join('\n\n');
}
