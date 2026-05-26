import React from 'react';
import { Settings2 } from 'lucide-react';

export interface AnalysisConfig {
  sheet?: string;
  regressionTarget?: string;
  regressionPredictors?: string[];
  anovaTarget?: string;
  anovaGroup?: string;
  ttestTarget?: string;
  ttestGroup?: string;
  oneSampleTarget?: string;
  oneSampleMean?: string;
  pairedPre?: string;
  pairedPost?: string;
  priceColumn?: string;
  portfolioAssets?: string[];
  psychometricColumns?: string[];
  irtColumns?: string[];
  chiSquareCol1?: string;
  chiSquareCol2?: string;
  logisticTarget?: string;
  logisticFeatures?: string[];
  exportDpi?: number;
  imputeMissing?: boolean;
  clusterFeatures?: string[];
}

interface Props {
  lang: 'en' | 'id';
  config: AnalysisConfig;
  onChange: (next: AnalysisConfig) => void;
  numericCols: string[];
  categoricalCols: string[];
  binaryCols: string[];
  sheets: string[];
  accent: string;
  exportDpi?: number;
  onExportDpiChange?: (dpi: number) => void;
}

const labels = {
  en: {
    title: 'Analysis Variable Mapping',
    subtitle: 'Choose columns before running the full engine. Empty fields use smart defaults.',
    sheet: 'Excel worksheet',
    regressionY: 'Regression target (Y)',
    regressionX: 'Predictors (X)',
    anovaY: 'ANOVA dependent (numeric)',
    anovaGroup: 'ANOVA factor (group)',
    ttestY: 'T-test dependent (numeric)',
    ttestGroup: 'T-test grouping (2 levels)',
    oneSampleY: 'One-Sample T-test (numeric)',
    oneSampleMean: 'Population Mean (μ₀)',
    pairedPre: 'Paired: Pre / Before',
    pairedPost: 'Paired: Post / After',
    price: 'Financial price series',
    psych: 'Psychometric scale items',
    irt: 'IRT binary items',
    chi1: 'Chi-square variable A',
    chi2: 'Chi-square variable B',
    logTarget: 'Logistic target (binary 0/1)',
    logFeat: 'Logistic predictors (numeric)',
    clusterFeatures: 'Clustering Features (numeric)',
    exportDpi: 'Chart export DPI (APA: 300)',
    none: '— Not used —',
    holdCtrl: 'Hold Ctrl to select multiple predictors',
    saveConfig: 'Save Configuration',
    loadConfig: 'Load Configuration',
    imputeMissing: 'Impute Missing Values (Mean/Mode)',
  },
  id: {
    title: 'Pemetaan Variabel Analisis',
    subtitle: 'Pilih kolom sebelum analisis lengkap. Kosongkan untuk default otomatis.',
    sheet: 'Lembar Excel',
    regressionY: 'Target regresi (Y)',
    regressionX: 'Prediktor (X)',
    anovaY: 'ANOVA dependen (numerik)',
    anovaGroup: 'ANOVA faktor (grup)',
    ttestY: 'T-test dependen (numerik)',
    ttestGroup: 'T-test grup (2 level)',
    oneSampleY: 'One-Sample T-test (numerik)',
    oneSampleMean: 'Rata-rata Populasi (μ₀)',
    pairedPre: 'Paired: Pre / Sebelum',
    pairedPost: 'Paired: Post / Sesudah',
    price: 'Seri harga finansial',
    psych: 'Item skala psikometri',
    irt: 'Item biner IRT',
    chi1: 'Chi-square variabel A',
    chi2: 'Chi-square variabel B',
    logTarget: 'Target logistik (biner 0/1)',
    logFeat: 'Prediktor logistik (numerik)',
    clusterFeatures: 'Fitur Clustering (numerik)',
    exportDpi: 'DPI ekspor grafik (APA: 300)',
    none: '— Tidak dipakai —',
    holdCtrl: 'Tahan Ctrl untuk pilih beberapa prediktor',
    saveConfig: 'Simpan Konfigurasi',
    loadConfig: 'Muat Konfigurasi',
    imputeMissing: 'Imputasi Nilai Kosong (Mean/Modus)',
  },
};

function SelectField({
  label,
  value,
  options,
  onChange,
  allowEmpty = true,
}: {
  label: string;
  value?: string;
  options: string[];
  onChange: (v: string) => void;
  allowEmpty?: boolean;
}) {
  return (
    <label className="block">
      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{label}</span>
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2 py-2 focus:border-blue-500 outline-none"
      >
        {allowEmpty && <option value="">—</option>}
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function AnalysisConfigPanel({
  lang,
  config,
  onChange,
  numericCols,
  categoricalCols,
  binaryCols,
  sheets,
  accent,
  exportDpi = 180,
  onExportDpiChange,
}: Props) {
  const t = labels[lang];

  const patch = (partial: Partial<AnalysisConfig>) => onChange({ ...config, ...partial });

  const toggleMulti = (
    key: 'regressionPredictors' | 'psychometricColumns' | 'irtColumns' | 'logisticFeatures' | 'clusterFeatures',
    col: string
  ) => {
    const current = config[key] || [];
    const next = current.includes(col) ? current.filter((c) => c !== col) : [...current, col];
    patch({ [key]: next } as Partial<AnalysisConfig>);
  };

  return (
    <div className="bg-[#1b2338]/50 border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-start space-x-2">
        <Settings2 className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" style={{ color: accent }} />
        <div>
          <h3 className="text-sm font-extrabold text-slate-100">{t.title}</h3>
          <p className="text-[10px] text-slate-500 mt-0.5">{t.subtitle}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {sheets.length > 1 && (
          <SelectField
            label={t.sheet}
            value={config.sheet}
            options={sheets}
            onChange={(v) => patch({ sheet: v || undefined })}
            allowEmpty={false}
          />
        )}
        <SelectField
          label={t.regressionY}
          value={config.regressionTarget}
          options={numericCols}
          onChange={(v) => patch({ regressionTarget: v || undefined })}
        />
        <SelectField
          label={t.anovaY}
          value={config.anovaTarget}
          options={numericCols}
          onChange={(v) => patch({ anovaTarget: v || undefined })}
        />
        <SelectField
          label={t.anovaGroup}
          value={config.anovaGroup}
          options={categoricalCols}
          onChange={(v) => patch({ anovaGroup: v || undefined })}
        />
        <SelectField
          label={t.ttestY}
          value={config.ttestTarget}
          options={numericCols}
          onChange={(v) => patch({ ttestTarget: v || undefined })}
        />
        <SelectField
          label={t.ttestGroup}
          value={config.ttestGroup}
          options={categoricalCols}
          onChange={(v) => patch({ ttestGroup: v || undefined })}
        />
        <SelectField
          label={t.oneSampleY}
          value={config.oneSampleTarget}
          options={numericCols}
          onChange={(v) => patch({ oneSampleTarget: v || undefined })}
        />
        <label className="block">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{t.oneSampleMean}</span>
          <input
            type="number"
            step="any"
            value={config.oneSampleMean || ''}
            onChange={(e) => patch({ oneSampleMean: e.target.value })}
            className="mt-1 w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2 py-2 focus:border-blue-500 outline-none"
            placeholder="0.0"
          />
        </label>
        <SelectField
          label={t.pairedPre}
          value={config.pairedPre}
          options={numericCols}
          onChange={(v) => patch({ pairedPre: v || undefined })}
        />
        <SelectField
          label={t.pairedPost}
          value={config.pairedPost}
          options={numericCols}
          onChange={(v) => patch({ pairedPost: v || undefined })}
        />
        <SelectField
          label={t.price}
          value={config.priceColumn}
          options={numericCols}
          onChange={(v) => patch({ priceColumn: v || undefined })}
        />
        <SelectField
          label={t.chi1}
          value={config.chiSquareCol1}
          options={[...categoricalCols, ...binaryCols.filter((b) => !categoricalCols.includes(b))]}
          onChange={(v) => patch({ chiSquareCol1: v || undefined })}
        />
        <SelectField
          label={t.chi2}
          value={config.chiSquareCol2}
          options={[...categoricalCols, ...binaryCols.filter((b) => !categoricalCols.includes(b))]}
          onChange={(v) => patch({ chiSquareCol2: v || undefined })}
        />
        <SelectField
          label={t.logTarget}
          value={config.logisticTarget}
          options={[...binaryCols, ...categoricalCols]}
          onChange={(v) => patch({ logisticTarget: v || undefined })}
        />
        <label className="block">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{t.exportDpi}</span>
          <select
            value={exportDpi}
            onChange={(e) => onExportDpiChange?.(Number(e.target.value))}
            className="mt-1 w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2 py-2"
          >
            <option value={96}>96 DPI</option>
            <option value={150}>150 DPI</option>
            <option value={180}>180 DPI</option>
            <option value={300}>300 DPI (APA thesis)</option>
          </select>
        </label>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{t.regressionX}</span>
          <p className="text-[9px] text-slate-600 mb-2">{t.holdCtrl}</p>
          <div className="max-h-28 overflow-y-auto space-y-1 bg-slate-900/50 rounded-lg p-2 border border-slate-800">
            {numericCols.map((col) => (
              <label key={col} className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={(config.regressionPredictors || []).includes(col)}
                  onChange={() => toggleMulti('regressionPredictors', col)}
                  className="rounded border-slate-600"
                />
                <span>{col}</span>
              </label>
            ))}
          </div>
        </div>
        <div>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{t.psych}</span>
          <div className="max-h-28 overflow-y-auto space-y-1 bg-slate-900/50 rounded-lg p-2 border border-slate-800 mt-1">
            {numericCols.map((col) => (
              <label key={`psy-${col}`} className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={(config.psychometricColumns || []).includes(col)}
                  onChange={() => toggleMulti('psychometricColumns', col)}
                  className="rounded border-slate-600"
                />
                <span>{col}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <div>
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{t.logFeat}</span>
        <div className="max-h-24 overflow-y-auto space-y-1 bg-slate-900/50 rounded-lg p-2 border border-slate-800 mt-1">
          {numericCols.map((col) => (
            <label key={`log-${col}`} className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={(config.logisticFeatures || []).includes(col)}
                onChange={() => toggleMulti('logisticFeatures', col)}
                className="rounded border-slate-600"
              />
              <span>{col}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{t.clusterFeatures}</span>
        <div className="max-h-24 overflow-y-auto flex flex-wrap gap-2 mt-2">
          {numericCols.map((col) => {
            const on = (config.clusterFeatures || []).includes(col);
            return (
              <button
                key={`cluster-${col}`}
                type="button"
                onClick={() => toggleMulti('clusterFeatures', col)}
                className={`text-[10px] px-2 py-1 rounded border font-bold ${on ? 'bg-purple-600/20 border-purple-500 text-purple-300' : 'bg-slate-900 border-slate-700 text-slate-400'}`}
              >
                {col}
              </button>
            );
          })}
        </div>
      </div>

      {binaryCols.length > 0 && (
        <div>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{t.irt}</span>
          <div className="max-h-24 overflow-y-auto flex flex-wrap gap-2 mt-2">
            {binaryCols.map((col) => {
              const on = (config.irtColumns || []).includes(col);
              return (
                <button
                  key={col}
                  type="button"
                  onClick={() => toggleMulti('irtColumns', col)}
                  className={`text-[10px] px-2 py-1 rounded border font-bold ${on ? 'bg-blue-600/20 border-blue-500 text-blue-300' : 'bg-slate-900 border-slate-700 text-slate-400'}`}
                >
                  {col}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Preprocessing Section */}
      <div className="pt-2 border-t border-slate-800">
        <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
          <input
            type="checkbox"
            checked={!!config.imputeMissing}
            onChange={(e) => patch({ imputeMissing: e.target.checked })}
            className="rounded border-slate-600 bg-slate-900"
          />
          <span className="font-bold">{t.imputeMissing}</span>
        </label>
      </div>

      <div className="pt-4 border-t border-slate-800 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(config, null, 2));
            const dlAnchorElem = document.createElement('a');
            dlAnchorElem.setAttribute("href", dataStr);
            dlAnchorElem.setAttribute("download", "analysis_config.json");
            dlAnchorElem.click();
          }}
          className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-1.5 px-3 rounded border border-slate-700 flex items-center transition-colors"
        >
          {t.saveConfig}
        </button>
        <label className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-1.5 px-3 rounded border border-slate-700 flex items-center transition-colors cursor-pointer">
          <span>{t.loadConfig}</span>
          <input
            type="file"
            accept=".json"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (!file) return;
              const reader = new FileReader();
              reader.onload = (ev) => {
                try {
                  const content = ev.target?.result as string;
                  const loadedConfig = JSON.parse(content);
                  onChange({ ...config, ...loadedConfig });
                } catch (err) {
                  console.error('Failed to parse config JSON', err);
                  alert('Invalid configuration file.');
                }
              };
              reader.readAsText(file);
              // Reset input so the same file can be loaded again if needed
              e.target.value = '';
            }}
          />
        </label>
      </div>
    </div>
  );
}
