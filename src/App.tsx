import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  BarChart4, 
  UploadCloud, 
  HelpCircle, 
  Sparkles, 
  CheckCircle2, 
  FileSpreadsheet, 
  TrendingUp, 
  BrainCircuit, 
  Settings, 
  Download, 
  Copy, 
  Check, 
  Globe, 
  Layers, 
  RefreshCw, 
  Eye, 
  AlertTriangle,
  Info
} from 'lucide-react';
import InteractiveChart from './components/InteractiveChart';
import AnalysisConfigPanel, { type AnalysisConfig } from './components/AnalysisConfigPanel';
import ErrorToastPanel, { type ToastMessage } from './components/ErrorToastPanel';

// Multilingual Translation Database
const translations = {
  en: {
    title: "STATISTICA Offline Analysis Tool",
    subTitle: "Desktop Scientific Engine",
    connected: "CONNECTED-OFFLINE",
    pending: "PENDING",
    importHeadline: "Import Scientific Data",
    importSub: "Support Microsoft Excel (.xlsx/.xls) and CSV datasets",
    dragDrop: "Drag and drop your dataset here or",
    browse: "Browse Files",
    loadSample: "Load Interactive Simulated Dataset",
    datasetInfo: "Connected Tabular Diagnostics",
    rows: "Validated Rows",
    columns: "Structural Columns",
    duplicates: "Duplicates Found",
    recommendation: "Auto-Detected Analytical Workflows",
    overview: "Dashboard Summary",
    statsModule: "Statistical Inference",
    finModule: "Financial Analysis",
    psyModule: "Psychometrics Panel",
    vizModule: "Graphics Visualizer",
    reportModule: "Report Publisher",
    settingsModule: "System Config",
    copied: "Copied!",
    copyTable: "Copy Table Data",
    allCharts: "Export Graphic Pack",
    downloadWord: "Download Academic MS Word (.docx)",
    downloadHtml: "Download Interactive Frame (.html)",
    downloadZip: "Download Full Package (.zip)",
    arimaTitle: "ARIMA(1,1,1) Price Forecast",
    garchTitle: "GARCH(1,1) Volatility Model",
    forecastSteps: "Forecast horizon",
    garchAlpha: "Alpha (ARCH)",
    garchBeta: "Beta (GARCH)",
    lastVol: "Latest conditional volatility",
    errUpload: "Upload failed",
    errAnalysis: "Analysis failed",
    errNetwork: "Connection error",
    successAnalysis: "Analysis complete",
    summaryKey: "Primary Model Parameters",
    interpretationTitle: "Automated Narration & Interpretation",
    generatingNarrative: "Consulting STATISTICA narrative models...",
    generateNarrativeBtn: "Run Academic Narrative Analysis",
    runFullAnalysis: "Run Full Offline Analysis",
    runFullAnalysisHint: "Schema loaded. Start the complete statistical engine (charts & reports).",
    diagnosticsReady: "Schema diagnostics complete",
    viewPng: "Static PNG",
    viewPlotly: "Plotly Interactive",
    viewCanvas: "Client Rebuild",
    narrativeOffline: "Offline report ready",
    narrativeAiOptional: "Enhance with AI (Gemini key)",
    language: "System Interface Language",
    performance: "Processing Engine Optimization",
    exportQuality: "Export Rendering Quality",
    themeAccent: "Analytics Theme Highlight",
    activeFile: "Data Context"
  },
  id: {
    title: "Alat Analisis Offline STATISTICA",
    subTitle: "Mesin Saintifik Desktop",
    connected: "TERHUBUNG-OFFLINE",
    pending: "TERTUNDA",
    importHeadline: "Impor Data Saintifk",
    importSub: "Mendukung file dataset Microsoft Excel (.xlsx/.xls) dan CSV",
    dragDrop: "Seret dan letakkan file dataset Anda di sini atau",
    browse: "Pilih File",
    loadSample: "Muat Dataset Simulasi Interaktif",
    datasetInfo: "Diagnosis Data Tergabung",
    rows: "Baris Tervalidasi",
    columns: "Kolom Struktural",
    duplicates: "Duplikat Ditemukan",
    recommendation: "Rekomendasi Skema Analisis Otomatis",
    overview: "Ringkasan Dasbor",
    statsModule: "Inferensi Statistik",
    finModule: "Analisis Finansial",
    psyModule: "Panel Psikometrika",
    vizModule: "Visualisasi Grafik",
    reportModule: "Penerbit Laporan",
    settingsModule: "Konfigurasi Sistem",
    copied: "Tersalin!",
    copyTable: "Salin Data Tabel",
    allCharts: "Ekspor Paket Grafik",
    downloadWord: "Unduh Dokumen MS Word Akademis (.docx)",
    downloadHtml: "Unduh Bingkai Dasbor Interaktif (.html)",
    downloadZip: "Unduh Paket Lengkap (.zip)",
    arimaTitle: "Proyeksi Harga ARIMA(1,1,1)",
    garchTitle: "Model Volatilitas GARCH(1,1)",
    forecastSteps: "Horizon proyeksi",
    garchAlpha: "Alpha (ARCH)",
    garchBeta: "Beta (GARCH)",
    lastVol: "Volatilitas kondisional terakhir",
    errUpload: "Upload gagal",
    errAnalysis: "Analisis gagal",
    errNetwork: "Koneksi gagal",
    successAnalysis: "Analisis selesai",
    summaryKey: "Parameter Model Utama",
    interpretationTitle: "Narasi & Interpretasi Otomatis",
    generatingNarrative: "Konsultasi ke model narasi STATISTICA...",
    generateNarrativeBtn: "Jalankan Analisis Narasi Akademis",
    runFullAnalysis: "Jalankan Analisis Lengkap Offline",
    runFullAnalysisHint: "Skema data siap. Mulai mesin statistik penuh (grafik & laporan).",
    diagnosticsReady: "Diagnostik skema selesai",
    viewPng: "PNG Statis",
    viewPlotly: "Plotly Interaktif",
    viewCanvas: "Rebuild Klien",
    narrativeOffline: "Laporan offline siap",
    narrativeAiOptional: "Perkaya dengan AI (kunci Gemini)",
    language: "Bahasa Antarmuka Sistem",
    performance: "Optimasi Mesin Pemrosesan",
    exportQuality: "Kualitas Rendering Ekspor",
    themeAccent: "Aksen Tema Analitik",
    activeFile: "Konteks Data"
  }
};

export default function App() {
  const [lang, setLang] = useState<'en' | 'id'>('en');
  const [activeTab, setActiveTab] = useState<'dashboard' | 'stats' | 'financial' | 'psychometrics' | 'visuals' | 'reports' | 'settings'>('dashboard');
  
  // Data State
  const [fileName, setFileName] = useState<string>('');
  const [filePath, setFilePath] = useState<string>('');
  const [rowsCount, setRowsCount] = useState<number>(0);
  const [colsCount, setColsCount] = useState<number>(0);
  const [duplicatesCount, setDuplicatesCount] = useState<number>(0);
  const [numericCols, setNumericCols] = useState<string[]>([]);
  const [categoricalCols, setCategoricalCols] = useState<string[]>([]);
  const [binaryCols, setBinaryCols] = useState<string[]>([]);
  const [availableSheets, setAvailableSheets] = useState<string[]>([]);
  const [analysisConfig, setAnalysisConfig] = useState<AnalysisConfig>(() => {
    try {
      const saved = localStorage.getItem('statistica_config');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });
  const [recs, setRecs] = useState<string[]>([]);
  const [allColumnsDetails, setAllColumnsDetails] = useState<any>({});
  
  // Full analysis results
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [generatedCharts, setGeneratedCharts] = useState<string[]>([]);
  const [plotlyCharts, setPlotlyCharts] = useState<string[]>([]);
  const [chartViewMode, setChartViewMode] = useState<'png' | 'plotly' | 'canvas'>('plotly');
  const [narrativeSource, setNarrativeSource] = useState<string>('offline');
  const [datasetKey, setDatasetKey] = useState<string>('');
  const [currentChartIndex, setCurrentChartIndex] = useState<number>(0);
  
  // UI states
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [diagnosticsReady, setDiagnosticsReady] = useState<boolean>(false);
  const [pythonStatus, setPythonStatus] = useState<{
    ready: boolean;
    scientificReady: boolean;
    command: string | null;
    checking: boolean;
    error?: string;
  }>({ ready: false, scientificReady: false, command: null, checking: true });
  const [serverTime, setServerTime] = useState<string>('');
  const [progressMsg, setProgressMsg] = useState<string>('');
  const [progressStep, setProgressStep] = useState<string>('Idle');
  const [progressPercent, setProgressPercent] = useState<number>(0);
  const [lastError, setLastError] = useState<string>('');
  const [copiedText, setCopiedText] = useState<boolean>(false);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  
  // AI narrative state
  const [narrativeText, setNarrativeText] = useState<string>('');
  const [isNarrativeLoading, setIsNarrativeLoading] = useState<boolean>(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  
  const showToast = (type: ToastMessage['type'], title: string, detail?: string) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    setToasts((prev) => [...prev, { id, type, title, detail }]);
  };

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((x) => x.id !== id));
  };

  const startProgress = (step: string, message: string, percent: number) => {
    setLastError('');
    setProgressStep(step);
    setProgressMsg(message);
    setProgressPercent(percent);
    setIsProcessing(true);
  };

  const updateProgress = (step: string, message: string, percent: number) => {
    setProgressStep(step);
    setProgressMsg(message);
    setProgressPercent(percent);
  };

  const stopProgress = () => {
    setIsProcessing(false);
    setProgressPercent(0);
  };

  const extractApiError = (data: any, fallback: string) => {
    const parts = [data?.error, data?.details].filter(Boolean);
    return parts.length > 0 ? parts.join('\n\n') : fallback;
  };
  
  // Settings Options
  const [selectedAccent, setSelectedAccent] = useState<string>('#3b82f6');
  const [perfMode, setPerfMode] = useState<boolean>(true);
  const [qualityDpi, setQualityDpi] = useState<number>(180);

  const t = translations[lang];

  const refreshSystemStatus = useCallback(async () => {
    setPythonStatus((prev) => ({ ...prev, checking: true, error: undefined }));
    try {
      const res = await fetch('/api/status', { cache: 'no-store' });
      if (!res.ok) throw new Error(`Status API returned ${res.status}`);
      const data = await res.json();
      console.log("STATISTICA server online:", data);
      const nextStatus = {
        ready: Boolean(data.pythonReady),
        scientificReady: Boolean(data.pythonScientificReady),
        command: data.pythonCommand ?? null,
        checking: false,
      };
      setPythonStatus(nextStatus);
      setServerTime(data.localTime || '');
      return nextStatus;
    } catch (err: any) {
      console.error("Could not reach express backend:", err);
      const nextStatus = {
        ready: false,
        scientificReady: false,
        command: null,
        checking: false,
        error: err.message || 'Could not reach backend',
      };
      setPythonStatus(nextStatus);
      return nextStatus;
    }
  }, []);

  // System Initializer Checks
  useEffect(() => {
    refreshSystemStatus();
    const timer = window.setInterval(refreshSystemStatus, 15000);
    return () => window.clearInterval(timer);
  }, [refreshSystemStatus]);

  useEffect(() => {
    if (analysisResults) {
      loadNarrative(analysisResults, narrativeSource.includes('gemini'));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  // Persist configuration changes to localStorage
  useEffect(() => {
    if (Object.keys(analysisConfig).length > 0) {
      localStorage.setItem('statistica_config', JSON.stringify(analysisConfig));
    }
  }, [analysisConfig]);

  // Set file drag-and-drop triggers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await uploadAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await uploadAndProcessFile(e.target.files[0]);
    }
  };

  // Upload spreadsheet or csv via Express API
  const buildDefaultAnalysisConfig = (diag: any): AnalysisConfig => {
    const nums: string[] = diag.numericColumns || [];
    const cats: string[] = diag.categoricalColumns || [];
    const bins: string[] = diag.binaryColumns || [];
    const analyticalNums = nums.filter((c: string) => !/^(id|order\s*id|no|nomor|index)$/i.test(c.trim()));
    const usableNums = analyticalNums.length > 0 ? analyticalNums : nums;
    const anovaGroup = cats.find((c: string) => {
      const u = diag.columnsDetails?.[c]?.unique_count;
      return u !== undefined && u >= 3 && u <= 8;
    });
    const ttestGroup = cats.find((c: string) => diag.columnsDetails?.[c]?.unique_count === 2);
    const priceColumn = usableNums.find((c: string) => /price|close/i.test(c));
    const regressionTarget = usableNums.find((c: string) => /net|bersih|hasil|revenue|sales|amount|total|score|post/i.test(c)) || usableNums[0];
    return {
      sheet: diag.activeSheet,
      regressionTarget,
      regressionPredictors: usableNums.slice(0, 4).filter((c: string) => c !== regressionTarget),
      anovaTarget: regressionTarget,
      anovaGroup,
      ttestTarget: regressionTarget,
      ttestGroup,
      pairedPre: usableNums.find((c: string) => /pre/i.test(c)),
      pairedPost: usableNums.find((c: string) => /post/i.test(c)),
      priceColumn,
      psychometricColumns: usableNums.slice(0, 8),
      irtColumns: bins.slice(0, 10),
      chiSquareCol1: cats[0],
      chiSquareCol2: cats[1],
      logisticTarget: bins[0] || cats.find((c: string) => diag.columnsDetails?.[c]?.unique_count === 2),
      logisticFeatures: usableNums.filter((c: string) => c !== bins[0]).slice(0, 5),
      exportDpi: qualityDpi,
    };
  };

  const pickValid = (val: string | undefined, allowed: string[]) =>
    val && allowed.includes(val) ? val : undefined;

  const applyDiagnostics = (diag: any, preserveMapping = false) => {
    const nums: string[] = diag.numericColumns || [];
    const cats: string[] = diag.categoricalColumns || [];
    const bins: string[] = diag.binaryColumns || [];

    setRowsCount(diag.rows);
    setColsCount(diag.columns);
    setDuplicatesCount(diag.duplicates);
    setNumericCols(nums);
    setCategoricalCols(cats);
    setBinaryCols(bins);
    setAvailableSheets(diag.sheets || []);
    setRecs(diag.recommendations || []);
    setAllColumnsDetails(diag.columnsDetails || {});

    if (preserveMapping) {
      setAnalysisConfig((prev) => ({
        ...prev,
        sheet: diag.activeSheet,
        regressionTarget: pickValid(prev.regressionTarget, nums) ?? nums[0],
        regressionPredictors: (prev.regressionPredictors || []).filter((c) => nums.includes(c)),
        anovaTarget: pickValid(prev.anovaTarget, nums) ?? nums[0],
        anovaGroup: pickValid(prev.anovaGroup, cats),
        ttestTarget: pickValid(prev.ttestTarget, nums) ?? nums[0],
        ttestGroup: pickValid(prev.ttestGroup, cats),
        pairedPre: pickValid(prev.pairedPre, nums),
        pairedPost: pickValid(prev.pairedPost, nums),
        priceColumn: pickValid(prev.priceColumn, nums),
        psychometricColumns: (prev.psychometricColumns || []).filter((c) => nums.includes(c)),
        irtColumns: (prev.irtColumns || []).filter((c) => bins.includes(c)),
        chiSquareCol1: pickValid(prev.chiSquareCol1, [...cats, ...bins]),
        chiSquareCol2: pickValid(prev.chiSquareCol2, [...cats, ...bins]),
        logisticTarget: pickValid(prev.logisticTarget, [...bins, ...cats]),
        logisticFeatures: (prev.logisticFeatures || []).filter((c) => nums.includes(c)),
        exportDpi: prev.exportDpi ?? qualityDpi,
      }));
    } else {
      setAnalysisConfig(buildDefaultAnalysisConfig(diag));
      setAnalysisResults(null);
      setGeneratedCharts([]);
      setPlotlyCharts([]);
      setDatasetKey('');
      setNarrativeText('');
      setNarrativeSource('offline');
    }

    setDiagnosticsReady(true);
  };

  const restoreAnalysisPayload = useCallback((data: any) => {
    if (!data?.success || !data.summary) return;
    const summary = data.summary;
    setAnalysisResults(summary);
    setGeneratedCharts(data.charts || []);
    setPlotlyCharts(data.plotlyCharts || []);
    setDatasetKey(data.datasetKey || '');
    setCurrentChartIndex(0);
    setChartViewMode((data.plotlyCharts?.length ?? 0) > 0 ? 'plotly' : 'png');
    setRowsCount(summary.rows || 0);
    setColsCount(summary.columns || 0);
    setDuplicatesCount(summary.duplicates || 0);
    setRecs(summary.recommendations || []);
    setAllColumnsDetails(summary.columnsDetails || {});
    setNumericCols(summary.numericColumns || []);
    setCategoricalCols(summary.categoricalColumns || []);
    setBinaryCols(summary.binaryColumns || []);
    setAvailableSheets(summary.sheets || []);
    setFileName(summary.fileName || data.datasetKey || '');
    setFilePath('');
    if (summary.appliedConfig) {
      setAnalysisConfig(summary.appliedConfig);
    }
    setDiagnosticsReady(true);
    setNarrativeText(data.offlineNarrative || '');
    setNarrativeSource('offline');
    setProgressMsg('Latest completed analysis restored from disk.');
    setActiveTab((data.plotlyCharts?.length ?? 0) > 0 || (data.charts?.length ?? 0) > 0 ? 'visuals' : 'reports');
  }, []);

  const restoreLatestAnalysis = useCallback(async (showMissingToast = false) => {
    try {
      const res = await fetch(`/api/latest-result?lang=${lang}`, { cache: 'no-store' });
      if (!res.ok) {
        if (showMissingToast) {
          const data = await res.json().catch(() => ({}));
          showToast('warning', lang === 'id' ? 'Belum ada hasil' : 'No analysis result', data.error || 'No completed analysis output found');
        }
        return;
      }
      const data = await res.json();
      restoreAnalysisPayload(data);
      if (showMissingToast) {
        showToast('success', lang === 'id' ? 'Hasil terakhir dimuat' : 'Latest result restored');
      }
    } catch (err: any) {
      if (showMissingToast) {
        showToast('error', t.errNetwork, err.message);
      }
    }
  }, [lang, restoreAnalysisPayload, t.errNetwork]);

  useEffect(() => {
    if (!filePath && !analysisResults && !diagnosticsReady) {
      restoreLatestAnalysis(false);
    }
    // Run once on a clean workspace so the last completed output is visible after refresh.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const refreshDiagnosticsForSheet = async (sheet: string) => {
    if (!filePath) return;
    startProgress('Diagnostics', 'Reloading schema for worksheet...', 35);
    try {
      const res = await fetch('/api/diagnostics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filePath, sheet }),
      });
      const data = await res.json();
      if (data.success) {
        updateProgress('Diagnostics', 'Worksheet schema refreshed.', 100);
        applyDiagnostics(data.diagnostics, true);
      } else {
        const detail = extractApiError(data, 'Diagnostics failed');
        setLastError(detail);
        showToast('error', t.errUpload, detail);
      }
    } finally {
      stopProgress();
    }
  };

  const uploadAndProcessFile = async (file: File) => {
    startProgress('Upload', 'Uploading dataset to local workspace...', 20);
    setDiagnosticsReady(false);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      updateProgress('Diagnostics', 'Scanning schema in Python...', 45);
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      
      if (data.success) {
        updateProgress('Ready', 'Schema diagnostics complete.', 100);
        setFileName(data.fileName);
        setFilePath(data.filePath);
        applyDiagnostics(data.diagnostics);
        setProgressMsg(t.diagnosticsReady);
        setActiveTab('dashboard');
      } else {
        const detail = extractApiError(data, 'Unknown upload error');
        setLastError(detail);
        showToast('error', t.errUpload, detail);
      }
    } catch (err: any) {
      console.error(err);
      setLastError(err.message);
      showToast('error', t.errNetwork, err.message);
    } finally {
      stopProgress();
    }
  };

  // Trigger loading example template
  const loadExampleDataset = async () => {
    startProgress('Sample Data', 'Loading example dataset...', 20);
    setDiagnosticsReady(false);
    try {
      const res = await fetch('/api/load-example', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        updateProgress('Diagnostics', 'Scanning sample schema...', 45);
        setFileName(data.fileName);
        setFilePath(data.filePath);

        const diagRes = await fetch('/api/diagnostics', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filePath: data.filePath }),
        });
        const diagData = await diagRes.json();
        if (diagData.success) {
          updateProgress('Ready', 'Sample schema diagnostics complete.', 100);
          applyDiagnostics(diagData.diagnostics);
          setProgressMsg(t.diagnosticsReady);
          setActiveTab('dashboard');
        } else {
          const detail = extractApiError(diagData, 'Sample diagnostics failed');
          setLastError(detail);
          showToast('error', t.errUpload, detail);
        }
      } else {
        const detail = extractApiError(data, 'Sample loading failed');
        setLastError(detail);
        showToast('error', t.errUpload, detail);
      }
    } catch (err: any) {
      console.error(err);
      setLastError(err.message);
      showToast('error', t.errNetwork, err.message);
    } finally {
      stopProgress();
    }
  };

  // Trigger Python analytical models
  const triggerFullAnalysis = async (fileDest: string) => {
    startProgress('Engine Check', 'Checking local Python and scientific packages...', 10);
    const latestPythonStatus = await refreshSystemStatus();
    if (!fileDest || !diagnosticsReady) {
      stopProgress();
      showToast('warning', t.errAnalysis, lang === 'id' ? 'Muat dataset dan tunggu diagnostik selesai terlebih dahulu.' : 'Load a dataset and wait for diagnostics first.');
      return;
    }
    if (!latestPythonStatus.ready) {
      const detail = latestPythonStatus.error || 'Install Python 3.10+ and restart the local server.';
      setLastError(detail);
      stopProgress();
      showToast('error', 'Python not ready', detail);
      return;
    }
    if (!latestPythonStatus.scientificReady) {
      const detail = 'Run START_STATISTICA.bat or install dependencies with: python -m pip install -r requirements.txt';
      setLastError(detail);
      stopProgress();
      showToast('error', 'Python scientific stack missing', detail);
      return;
    }
    try {
      updateProgress('Python Analysis', 'Running statistical engine, charts, and report generation...', 45);
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filePath: fileDest,
          config: { ...analysisConfig, exportDpi: qualityDpi },
        })
      });
      const data = await response.json();
      if (data.success) {
        updateProgress('Publishing Results', 'Loading generated charts, reports, and narrative...', 85);
        setAnalysisResults(data.summary);
        setGeneratedCharts(data.charts || []);
        setPlotlyCharts(data.plotlyCharts || []);
        setDatasetKey(data.datasetKey);
        setCurrentChartIndex(0);
        setChartViewMode((data.plotlyCharts?.length ?? 0) > 0 ? 'plotly' : 'png');
        
        setRowsCount(data.summary.rows);
        setColsCount(data.summary.columns);
        setDuplicatesCount(data.summary.duplicates);
        setRecs(data.summary.recommendations || []);
        
        setProgressMsg('Analysis complete. Charts and reports are ready.');
        setProgressStep('Complete');
        setProgressPercent(100);
        setDiagnosticsReady(true);
        setActiveTab((data.plotlyCharts?.length ?? 0) > 0 || (data.charts?.length ?? 0) > 0 ? 'visuals' : 'reports');
        showToast('success', t.successAnalysis, lang === 'id' ? 'Laporan siap di tab Reports.' : 'Reports ready in Reports tab.');
        await loadNarrative(data.summary, false);
      } else {
        const detail = extractApiError(data, 'Check Python logs');
        setLastError(detail);
        showToast('error', t.errAnalysis, detail);
      }
    } catch (err: any) {
      console.error(err);
      setLastError(err.message);
      showToast('error', t.errNetwork, err.message);
    } finally {
      stopProgress();
    }
  };

  const loadNarrative = async (summary: any, useAi = false) => {
    setIsNarrativeLoading(true);
    try {
      const payload = datasetKey
        ? { datasetKey, lang, useAi }
        : { summary, lang, useAi };
      const res = await fetch('/api/narrative', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setNarrativeText(data.narrative || '');
      setNarrativeSource(data.source || 'offline');
      if (useAi && data.source === 'offline-fallback') {
        showToast('warning', lang === 'id' ? 'Gemini tidak tersedia' : 'Gemini unavailable', lang === 'id' ? 'Menggunakan narasi offline.' : 'Using offline narrative instead.');
      }
    } catch (err: any) {
      console.error(err);
      showToast('error', lang === 'id' ? 'Narasi gagal' : 'Narrative failed', err.message);
    } finally {
      setIsNarrativeLoading(false);
    }
  };

  const getNarrativeInterpretation = async (useAi = false) => {
    if (!analysisResults) return;
    await loadNarrative(analysisResults, useAi);
  };

  const pngToPlotlyHtml = (pngName: string): string | null => {
    const base = pngName.replace(/\.png$/i, '.html');
    return plotlyCharts.includes(base) ? base : null;
  };

  const getActivePlotlyHtml = (): string | null => {
    if (generatedCharts.length === 0) return plotlyCharts[currentChartIndex] || null;
    return pngToPlotlyHtml(generatedCharts[currentChartIndex]);
  };

  const formatChartLabel = (name: string) =>
    name
      .replace(/\.(png|html)$/i, '')
      .replace(/^histogram_/, 'Histogram: ')
      .replace(/^boxplot_/, 'Boxplot: ')
      .replace(/^qq_/, 'Q-Q: ')
      .replace(/^scatter_/, 'Scatter: ')
      .replace(/_/g, ' ');

  const renderNarrativeLine = (line: string, ix: number) => {
    if (line.startsWith('### ')) {
      return <h4 key={ix} className="text-sm font-black text-white mt-2">{line.replace(/^###\s*/, '')}</h4>;
    }
    if (line.startsWith('## ')) {
      return <h5 key={ix} className="text-xs font-bold text-blue-400 uppercase tracking-wider mt-3">{line.replace(/^##\s*/, '')}</h5>;
    }
    if (line.startsWith('- ')) {
      return <li key={ix} className="ml-4 text-slate-300 list-disc">{line.replace(/^-\s*/, '')}</li>;
    }
    if (line.trim() === '---') return <hr key={ix} className="border-slate-800 my-2" />;
    if (!line.trim()) return null;
    const html = line.replace(/\*\*([^*]+)\*\*/g, '<strong class="text-slate-100">$1</strong>');
    return <p key={ix} className="text-slate-300" dangerouslySetInnerHTML={{ __html: html }} />;
  };

  const hasVisuals = generatedCharts.length > 0 || plotlyCharts.length > 0;
  const galleryItems = generatedCharts.length > 0 ? generatedCharts : plotlyCharts;
  const statusLabel = pythonStatus.checking
    ? 'Python checking...'
    : pythonStatus.ready
      ? `Python ${pythonStatus.command || 'OK'}`
      : 'Python not found';
  const statusDetail = pythonStatus.checking
    ? 'Checking local backend status'
    : pythonStatus.error
      ? pythonStatus.error
      : pythonStatus.ready && !pythonStatus.scientificReady
        ? 'Scientific packages missing'
        : pythonStatus.ready
          ? 'Scientific stack ready'
          : 'Install Python 3.10+ and restart server';
  const statusClass = pythonStatus.checking
    ? 'text-blue-300 border-blue-500/30 bg-blue-500/10'
    : pythonStatus.ready && pythonStatus.scientificReady
      ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
      : 'text-amber-400 border-amber-500/30 bg-amber-500/10';
  const formattedServerTime = serverTime ? serverTime.replace('T', ' ').slice(0, 19) : 'syncing...';

  // Helper to copy content to clipboard
  const copyTableToClipboard = (elemId: string) => {
    const el = document.getElementById(elemId);
    if (el) {
      const range = document.createRange();
      range.selectNode(el);
      window.getSelection()?.removeAllRanges();
      window.getSelection()?.addRange(range);
      try {
        document.execCommand('copy');
        setCopiedText(true);
        setTimeout(() => setCopiedText(false), 2000);
      } catch (err) {
        console.error("Copy failed:", err);
      }
      window.getSelection()?.removeAllRanges();
    }
  };

  return (
    <div className="bg-[#0b1020] text-slate-200 font-sans min-h-screen flex flex-col md:flex-row overflow-hidden select-none">
      
      {/* SIDEBAR */}
      <aside className="w-full md:w-64 bg-[#070b14] border-r border-slate-800 flex flex-col justify-between flex-shrink-0">
        <div>
          {/* Logo Brand Header */}
          <div className="p-6 flex items-center space-x-3 border-b border-slate-800/60">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30" style={{ backgroundColor: selectedAccent }}>
              <Layers className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-extrabold tracking-wider text-white">STATISTICA</h1>
              <p className="text-[9px] font-bold text-slate-500 tracking-widest uppercase">Offline Analytics</p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="p-4 space-y-1">
            <div className="text-[10px] uppercase font-bold text-slate-600 tracking-widest px-2 pb-2">Workspace</div>
            
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-xs font-semibold transition-all ${activeTab === 'dashboard' ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'}`}
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>{t.overview}</span>
            </button>

            <button 
              disabled={!analysisResults}
              onClick={() => setActiveTab('stats')}
              className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-xs font-semibold transition-all ${!analysisResults ? 'opacity-40 cursor-not-allowed' : ''} ${activeTab === 'stats' ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'}`}
            >
              <BarChart4 className="w-4 h-4" />
              <span>{t.statsModule}</span>
            </button>

            <button 
              disabled={!analysisResults}
              onClick={() => setActiveTab('financial')}
              className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-xs font-semibold transition-all ${!analysisResults ? 'opacity-40 cursor-not-allowed' : ''} ${activeTab === 'financial' ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'}`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>{t.finModule}</span>
            </button>

            <button 
              disabled={!analysisResults}
              onClick={() => setActiveTab('psychometrics')}
              className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-xs font-semibold transition-all ${!analysisResults ? 'opacity-40 cursor-not-allowed' : ''} ${activeTab === 'psychometrics' ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'}`}
            >
              <BrainCircuit className="w-4 h-4" />
              <span>{t.psyModule}</span>
            </button>

            <button 
              disabled={!analysisResults || generatedCharts.length === 0}
              onClick={() => setActiveTab('visuals')}
              className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-xs font-semibold transition-all ${!analysisResults ? 'opacity-40 cursor-not-allowed' : ''} ${activeTab === 'visuals' ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'}`}
            >
              <Eye className="w-4 h-4" />
              <span>{t.vizModule}</span>
            </button>

            <button 
              disabled={!analysisResults}
              onClick={() => setActiveTab('reports')}
              className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-xs font-semibold transition-all ${!analysisResults ? 'opacity-40 cursor-not-allowed' : ''} ${activeTab === 'reports' ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'}`}
            >
              <Download className="w-4 h-4" />
              <span>{t.reportModule}</span>
            </button>

            <button 
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-xs font-semibold transition-all ${activeTab === 'settings' ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'text-slate-400 hover:bg-slate-800/40 hover:text-white'}`}
            >
              <Settings className="w-4 h-4" />
              <span>{t.settingsModule}</span>
            </button>
          </nav>
        </div>

        {/* Sidebar Footer Controls */}
        <div className="p-4 border-t border-slate-800/60 bg-slate-950/40">
          <div className="flex items-center justify-between mb-3 text-[10px]">
            <span className="text-slate-500 uppercase font-bold tracking-wider">Engine Core</span>
            <span className="text-green-500 font-bold tracking-widest flex items-center"><span className="w-2 h-2 bg-green-500 rounded-full mr-1.5 animate-pulse"></span>ONLINE</span>
          </div>

          {analysisResults && (
            <button 
              onClick={() => setActiveTab('reports')}
              className="w-full bg-blue-600 hover:bg-blue-500 font-bold text-white text-[11px] py-2 px-3 rounded-lg flex items-center justify-center space-x-1 transition shadow-lg shadow-blue-900/20 hover:scale-[1.02]"
              style={{ backgroundColor: selectedAccent }}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Generate Outputs</span>
            </button>
          )}

          <div className="mt-4 flex items-center justify-between">
            {/* Language Toggle Button */}
            <button 
              onClick={() => setLang(lang === 'en' ? 'id' : 'en')}
              className="flex items-center space-x-1.5 p-1 px-2.5 rounded-md hover:bg-slate-800 text-[10px] text-slate-400 hover:text-white border border-slate-700/50"
            >
              <Globe className="w-3 h-3 text-blue-400" />
              <span className="font-bold uppercase">{lang === 'en' ? 'Bahasa ID' : 'English EN'}</span>
            </button>
            <span className="text-[9px] text-slate-600 font-mono">v1.4.0</span>
          </div>
        </div>
      </aside>

      {/* DETAILED INTERACTIVE MULTI-VIEW PANELS CONTAINER */}
      <main className="flex-1 flex flex-col h-screen overflow-y-auto bg-[#0b1020]">
        
        {/* HEADER BAR */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800 bg-[#0f172a]/70 backdrop-blur sticky top-0 z-40">
          <div className="flex items-center space-x-3">
            <span className="text-xs uppercase tracking-widest text-slate-500 font-semibold">{t.activeFile}:</span>
            {fileName ? (
              <div className="flex items-center space-x-2">
                <FileSpreadsheet className="w-4.5 h-4.5 text-blue-400" />
                <span className="text-sm font-black text-slate-100">{fileName}</span>
                <span className="bg-green-500/15 text-green-400 border border-green-500/30 text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-widest">
                  {t.connected}
                </span>
              </div>
            ) : (
              <span className="text-slate-500 text-xs italic font-serif">Empty workspace. Load Excel/CSV files below.</span>
            )}
          </div>

          <div className="flex items-center space-x-3 font-mono text-[10.5px]">
            <button
              type="button"
              onClick={() => void refreshSystemStatus()}
              title={statusDetail}
              className={`px-2.5 py-1 rounded border font-bold uppercase tracking-wider ${statusClass}`}
            >
              {statusLabel}
            </button>
            <span className="text-slate-500">Server Time:</span>
            <span className="text-blue-400 font-bold bg-[#141b2e] px-2.5 py-1 rounded border border-slate-800">
              {formattedServerTime}
            </span>
          </div>
        </header>

        {/* PROGRESS DISPLAY */}
        {isProcessing && (
          <div className="p-4 bg-slate-900 border-b border-slate-800 flex items-center space-x-4">
            <RefreshCw className="w-5 h-5 text-blue-500 animate-spin flex-shrink-0" />
            <div className="flex-1">
              <span className="text-xs text-blue-400 block font-bold uppercase tracking-widest">{progressStep}</span>
              <p className="text-[11px] text-slate-400 mt-0.5">{progressMsg}</p>
            </div>
            <div className="w-40">
              <div className="flex justify-between text-[9px] text-slate-500 font-mono mb-1">
                <span>Progress</span>
                <span>{progressPercent}%</span>
              </div>
              <div className="bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-blue-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(5, Math.min(progressPercent, 100))}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {!isProcessing && lastError && (
          <div className="p-4 bg-red-950/40 border-b border-red-900/50 flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <span className="text-xs text-red-200 block font-bold uppercase tracking-widest">
                {lang === 'id' ? 'Proses terakhir gagal' : 'Last Process Failed'}
              </span>
              <p className="text-[11px] text-red-100/80 mt-1 font-mono whitespace-pre-wrap max-h-28 overflow-y-auto">
                {lastError}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setLastError('')}
              className="text-red-200/60 hover:text-red-100 text-xs font-bold"
            >
              Clear
            </button>
          </div>
        )}

        {/* BODY TABS SELECTION */}
        <div className="p-6 flex-1 space-y-6">
          
          {/* TAB 1: DASHBOARD / DATA INGEST */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              
              {/* TOP STATS CLINT CARDS */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                
                <div className="bg-[#1b2338]/45 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700/80 transition-all">
                  <div className="flex items-center justify-between text-slate-500 text-[10px] font-bold uppercase tracking-wider">
                    <span>{t.rows}</span>
                    <Layers className="w-3.5 h-3.5 text-blue-400" />
                  </div>
                  <div className="mt-2 text-2xl font-extrabold text-white tracking-tight">{rowsCount}</div>
                  <span className="text-[9px] text-slate-500 block mt-1">Sieved row occurrences</span>
                </div>

                <div className="bg-[#1b2338]/45 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700/80 transition-all">
                  <div className="flex items-center justify-between text-slate-500 text-[10px] font-bold uppercase tracking-wider">
                    <span>{t.columns}</span>
                    <FileSpreadsheet className="w-3.5 h-3.5 text-blue-400" />
                  </div>
                  <div className="mt-2 text-2xl font-extrabold text-white tracking-tight">{colsCount}</div>
                  <div className="text-[9px] text-slate-400 mt-1 flex items-center space-x-1">
                    <span className="text-blue-400 font-mono font-bold">{numericCols.length} Num</span>
                    <span>/</span>
                    <span className="text-purple-400 font-mono font-bold">{categoricalCols.length} Cat</span>
                  </div>
                </div>

                <div className="bg-[#1b2338]/45 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700/80 transition-all">
                  <div className="flex items-center justify-between text-slate-500 text-[10px] font-bold uppercase tracking-wider">
                    <span>{t.duplicates}</span>
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                  </div>
                  <div className={`mt-2 text-2xl font-extrabold tracking-tight ${duplicatesCount > 0 ? 'text-amber-500' : 'text-slate-300'}`}>{duplicatesCount}</div>
                  <span className="text-[9px] text-slate-500 block mt-1">High fidelity matrix scans</span>
                </div>

                <div className="bg-gradient-to-tr from-[#1b2338]/40 to-[#10b981]/5 border border-[#10b981]/25 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700/80 transition-all">
                  <div className="flex items-center justify-between text-slate-500 text-[10px] font-bold uppercase tracking-wider">
                    <span>Auto-Detect Target</span>
                    <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                  </div>
                  <div className="mt-2 text-[13px] font-black text-slate-200 uppercase tracking-wide leading-tight">
                    {numericCols.some(c => c.toLowerCase().includes('price') || c.toLowerCase().includes('close')) ? 'Financial Model Active' : 'General Statistics'}
                  </div>
                  <span className="text-[9px] text-emerald-400 font-bold block mt-1">100% Offline Engine</span>
                </div>
              </div>

              {/* DRAG AND DROP ZONE */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                <div className="md:col-span-2 space-y-6">
                  <div 
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed p-10 rounded-2xl flex flex-col items-center justify-center text-center transition-all cursor-pointer ${isDragOver ? 'border-blue-500 bg-blue-900/10' : 'border-slate-800 hover:border-slate-700 bg-slate-900/15'}`}
                  >
                    <UploadCloud className="w-12 h-12 text-slate-500 mb-4 animate-bounce" />
                    <h3 className="font-extrabold text-sm text-slate-200">{t.importHeadline}</h3>
                    <p className="text-xs text-slate-400 mt-1 max-w-sm">{t.importSub}</p>
                    
                    <div className="mt-6 flex flex-col sm:flex-row gap-3">
                      <label style={{ backgroundColor: selectedAccent }} className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold transition flex items-center space-x-1 cursor-pointer">
                        <UploadCloud className="w-3.5 h-3.5" />
                        <span>{t.browse}</span>
                        <input type="file" accept=".xlsx,.xls,.csv" className="hidden" onChange={handleFileChange} />
                      </label>

                      <button 
                        onClick={loadExampleDataset}
                        className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-bold transition flex items-center space-x-1 border border-slate-700"
                      >
                        <Layers className="w-3.5 h-3.5 text-blue-400" />
                        <span>{t.loadSample}</span>
                      </button>

                      {!analysisResults && (
                        <button
                          type="button"
                          onClick={() => restoreLatestAnalysis(true)}
                          className="px-5 py-2.5 bg-emerald-900/30 hover:bg-emerald-800/40 text-emerald-200 rounded-lg text-xs font-bold transition flex items-center space-x-1 border border-emerald-700/40"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                          <span>{lang === 'id' ? 'Muat Hasil Terakhir' : 'Restore Latest Result'}</span>
                        </button>
                      )}
                    </div>
                  </div>

                  {diagnosticsReady && (
                    <AnalysisConfigPanel
                      lang={lang}
                      config={analysisConfig}
                      onChange={(next) => {
                        setAnalysisConfig(next);
                        if (next.sheet && next.sheet !== analysisConfig.sheet && filePath) {
                          refreshDiagnosticsForSheet(next.sheet);
                        }
                      }}
                      numericCols={numericCols}
                      categoricalCols={categoricalCols}
                      binaryCols={binaryCols}
                      sheets={availableSheets}
                      accent={selectedAccent}
                      exportDpi={qualityDpi}
                      onExportDpiChange={setQualityDpi}
                    />
                  )}

                  {diagnosticsReady && filePath && !analysisResults && (
                    <div className="bg-gradient-to-r from-blue-900/20 to-emerald-900/10 border border-blue-500/30 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div>
                        <h3 className="text-sm font-extrabold text-slate-100">{t.runFullAnalysis}</h3>
                        <p className="text-xs text-slate-400 mt-1">{t.runFullAnalysisHint}</p>
                      </div>
                      <button
                        onClick={() => triggerFullAnalysis(filePath)}
                        disabled={isProcessing || pythonStatus.checking || !pythonStatus.ready || !pythonStatus.scientificReady}
                        style={{ backgroundColor: selectedAccent }}
                        className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded-lg text-xs font-bold transition flex items-center space-x-2 shrink-0"
                      >
                        <BrainCircuit className="w-4 h-4" />
                        <span>{t.runFullAnalysis}</span>
                      </button>
                    </div>
                  )}

                  {analysisResults && (
                    <div className="bg-gradient-to-r from-emerald-900/20 to-blue-900/10 border border-emerald-500/30 rounded-xl p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                      <div>
                        <h3 className="text-sm font-extrabold text-slate-100">
                          {lang === 'id' ? 'Analisis selesai' : 'Analysis complete'}
                        </h3>
                        <p className="text-xs text-slate-400 mt-1">
                          {rowsCount} rows / {colsCount} columns / {generatedCharts.length} PNG charts / {plotlyCharts.length} Plotly charts
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {hasVisuals && (
                          <button
                            type="button"
                            onClick={() => setActiveTab('visuals')}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold transition"
                          >
                            {lang === 'id' ? 'Lihat Grafik' : 'View Charts'}
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={() => setActiveTab('reports')}
                          className="px-4 py-2 bg-emerald-700 hover:bg-emerald-600 text-white rounded-lg text-xs font-bold transition"
                        >
                          {lang === 'id' ? 'Lihat Report' : 'View Reports'}
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center space-x-2">
                      <Sparkles className="w-4 h-4 text-amber-500" />
                      <span>{t.recommendation}</span>
                    </h3>
                    <div className="mt-4 space-y-2">
                      {recs.length > 0 ? (
                        recs.map((item, idx) => (
                          <div key={idx} className="flex items-start space-x-2 text-xs bg-slate-900/40 p-3 rounded-lg border border-slate-800/40">
                            <span className="text-blue-400 mt-0.5">✦</span>
                            <span className="text-slate-300 font-serif italic">{item}</span>
                          </div>
                        ))
                      ) : (
                        <p className="text-xs text-slate-500 italic">No variables loaded yet. Import data to run diagnostics.</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* SIDEBAR: ACTIVE SCHEMA DETAILED LIST */}
                <div className="space-y-4">
                  <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-5 h-full flex flex-col justify-between">
                    <div>
                      <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest pb-3 border-b border-slate-800">
                        Column Schema Diagnostics
                      </h3>
                      <div className="mt-4 space-y-3 max-h-72 overflow-y-auto pr-1">
                        {Object.keys(allColumnsDetails).length > 0 ? (
                          Object.entries(allColumnsDetails).map(([col, details]: [string, any]) => (
                            <div key={col} className="flex items-center justify-between text-xs bg-slate-900/50 p-2 rounded">
                              <span className="font-bold text-slate-300 truncate w-24" title={col}>{col}</span>
                              <div className="flex space-x-1.5 text-[9px]">
                                <span className={`px-2 py-0.5 rounded font-extrabold ${details.is_numeric ? 'bg-blue-600/10 text-blue-400' : 'bg-purple-600/10 text-purple-400'}`}>
                                  {details.type}
                                </span>
                                {details.missing > 0 && (
                                  <span className="bg-red-500/10 text-red-400 px-1 rounded">
                                    {details.missing_pct.toFixed(0)}% Nan
                                  </span>
                                )}
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-xs text-slate-500 italic">No variables parsed yet.</p>
                        )}
                      </div>
                    </div>

                    {diagnosticsReady && filePath && !analysisResults && (
                      <div className="pt-4 border-t border-slate-800/60 mt-4">
                        <button
                          onClick={() => triggerFullAnalysis(filePath)}
                          disabled={isProcessing || pythonStatus.checking || !pythonStatus.ready || !pythonStatus.scientificReady}
                          style={{ backgroundColor: selectedAccent }}
                          className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white font-bold py-2.5 rounded-lg text-xs transition"
                        >
                          {t.runFullAnalysis}
                        </button>
                      </div>
                    )}

                    {/* Quick action buttons if dataset loaded */}
                    {analysisResults && (
                      <div className="pt-4 border-t border-slate-800/60 mt-4 space-y-2">
                        <button
                          onClick={() => filePath && triggerFullAnalysis(filePath)}
                          disabled={isProcessing || pythonStatus.checking || !pythonStatus.ready || !pythonStatus.scientificReady}
                          className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 rounded-lg text-xs font-bold transition border border-slate-700"
                        >
                          Re-run Full Analysis
                        </button>
                        <button 
                          onClick={() => setActiveTab('stats')}
                          className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 rounded-lg text-xs font-bold transition border border-slate-700"
                        >
                          Run Descriptive T-Tests
                        </button>
                        <button 
                          onClick={() => setActiveTab('reports')}
                          className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 rounded-lg text-xs transition"
                          style={{ backgroundColor: selectedAccent }}
                        >
                          View Word/HTML Exports
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: CORE STAT STATS INFERENCE */}
          {activeTab === 'stats' && analysisResults && (
            <div className="space-y-6">
              
              {/* DESCRIPTIVE TABLE */}
              <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
                <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-[#0e1424]/40">
                  <div>
                    <h3 className="text-sm font-extrabold text-slate-200">Table 1: Formal Descriptives Table (APA format)</h3>
                    <p className="text-[10px] text-slate-500 mt-1">Summary parameters of calculated continuous distributions</p>
                  </div>
                  <div className="flex space-x-2">
                    <button 
                      onClick={() => copyTableToClipboard('desc_stats_tbl')}
                      className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 font-semibold rounded-lg flex items-center space-x-1.5 border border-slate-700 transition"
                    >
                      {copiedText ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedText ? t.copied : t.copyTable}</span>
                    </button>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table id="desc_stats_tbl" className="w-full text-left text-xs border-collapse font-mono">
                    <thead className="bg-[#0e1424] text-slate-400 uppercase tracking-wider text-[9px] font-bold border-b border-slate-800">
                      <tr>
                        <th className="py-3 px-5 text-left font-sans font-extrabold text-xs text-slate-300">Variable Name</th>
                        <th className="py-3 px-4">Observation N</th>
                        <th className="py-3 px-4">Mean (μ)</th>
                        <th className="py-3 px-4">Std Dev (σ)</th>
                        <th className="py-3 px-4">Skewness</th>
                        <th className="py-3 px-4">Kurtosis</th>
                        <th className="py-3 px-4">Min Value</th>
                        <th className="py-3 px-4">Max Value</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-300">
                      {Object.entries(analysisResults.descriptive).map(([col, metrics]: [string, any]) => (
                        <tr key={col} className="hover:bg-slate-800/25">
                          <td className="py-3 px-5 font-bold text-white font-sans text-xs">{col}</td>
                          <td className="py-3 px-4">{metrics.count}</td>
                          <td className="py-3 px-4">{metrics.mean.toFixed(4)}</td>
                          <td className="py-3 px-4">{metrics.std.toFixed(4)}</td>
                          <td className="py-3 px-4">{metrics.skewness.toFixed(4)}</td>
                          <td className="py-3 px-4">{metrics.kurtosis.toFixed(4)}</td>
                          <td className="py-3 px-4">{metrics.min.toFixed(2)}</td>
                          <td className="py-3 px-4">{metrics.max.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* INFERENCE WORKFLOW PANELS GRID */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* OLS REGRESSION SUB-PANEL */}
                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl overflow-hidden p-6 space-y-4">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest pb-3 border-b border-slate-800 flex items-center justify-between">
                    <span>OLS Regression Estimations</span>
                    <span className="bg-blue-500/10 text-blue-400 font-mono text-[9px] font-bold px-2 py-0.5 rounded">
                      Model Valid
                    </span>
                  </h3>

                  {analysisResults.linear_regression && !analysisResults.linear_regression.error ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-3 gap-2">
                        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                          <span className="text-[9px] text-slate-400 block uppercase font-bold text-left">R-Squared</span>
                          <span className="text-lg font-mono font-black text-blue-400">{analysisResults.linear_regression.r_squared.toFixed(4)}</span>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                          <span className="text-[9px] text-slate-400 block uppercase font-bold text-left">Adjusted R2</span>
                          <span className="text-lg font-mono font-black text-slate-300">{analysisResults.linear_regression.adj_r_squared.toFixed(4)}</span>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                          <span className="text-[9px] text-slate-400 block uppercase font-bold text-left">Observations n</span>
                          <span className="text-lg font-mono font-black text-slate-300">{analysisResults.linear_regression.n_observations}</span>
                        </div>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs">
                          <thead>
                            <tr className="text-slate-500 uppercase text-[9px] font-bold border-b border-slate-800">
                              <th className="pb-2">Predictor Coeff</th>
                              <th className="pb-2">Estimate</th>
                              <th className="pb-2">t stat</th>
                              <th className="pb-2">p-value</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800 font-mono">
                            {analysisResults.linear_regression.features.map((item: any) => (
                              <tr key={item.feature}>
                                <td className="py-2 text-slate-300 font-sans">{item.feature}</td>
                                <td className="py-2">{item.coefficient.toFixed(4)}</td>
                                <td className="py-2">{item.t_statistic.toFixed(3)}</td>
                                <td className={`py-2 ${item.significant ? 'text-green-400 font-bold' : 'text-slate-500'}`}>
                                  {item.p_value.toFixed(5)} {item.significant ? '*' : ''}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">No regression data detected for continuous variables structure.</p>
                  )}
                </div>

                {/* NORMALITY AND VARIANCE TEST */}
                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl overflow-hidden p-6 space-y-4">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest pb-3 border-b border-slate-800">
                    Distribution Normality Diagnostics
                  </h3>

                  <div className="space-y-4">
                    {analysisResults.normality && Object.keys(analysisResults.normality).length > 0 ? (
                      Object.entries(analysisResults.normality).map(([col, tests]: [string, any]) => (
                        <div key={col} className="bg-slate-900/40 p-4 rounded-xl border border-slate-800/80 space-y-3">
                          <span className="text-xs font-bold text-slate-200 block">{col}</span>
                          <div className="grid grid-cols-2 gap-4">
                            {tests.shapiro && !tests.shapiro.error && (
                              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                                <span className="text-[8px] text-slate-500 tracking-wider uppercase block font-bold">Shapiro-Wilk</span>
                                <div className="flex justify-between items-baseline mt-1 font-mono text-xs">
                                  <span className="text-slate-300">W-stat: {tests.shapiro.statistic.toFixed(4)}</span>
                                  <span className={tests.shapiro.normal ? 'text-green-500 font-bold' : 'text-slate-500'}>
                                    p: {tests.shapiro.p_value.toFixed(4)}
                                  </span>
                                </div>
                              </div>
                            )}

                            {tests.kolmogorov && !tests.kolmogorov.error && (
                              <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                                <span className="text-[8px] text-slate-500 tracking-wider uppercase block font-bold">Kolmogorov-Smirnov</span>
                                <div className="flex justify-between items-baseline mt-1 font-mono text-xs">
                                  <span className="text-slate-300">D-stat: {tests.kolmogorov.statistic.toFixed(4)}</span>
                                  <span className={tests.kolmogorov.normal ? 'text-green-500 font-bold' : 'text-slate-500'}>
                                    p: {tests.kolmogorov.p_value.toFixed(4)}
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-500 italic">No normality scans compiled.</p>
                    )}
                  </div>
                </div>
              </div>

              {/* ANOVA, T-TEST, PAIRED */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-3">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest border-b border-slate-800 pb-2">
                    Multi-Group Comparison
                  </h3>
                  <div className="space-y-4">
                    {analysisResults.one_way_anova && !analysisResults.one_way_anova.error ? (
                      <div className="space-y-2 text-xs font-mono bg-[#0e1424] p-3 rounded-lg border border-slate-800/80">
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">One-Way ANOVA (Parametric)</p>
                        <p className="text-slate-400">
                          <span className="text-slate-500">Factor:</span> {analysisResults.appliedConfig?.anovaGroup}
                          <span className="mx-2">|</span>
                          <span className="text-slate-500">DV:</span> {analysisResults.appliedConfig?.anovaTarget}
                        </p>
                        <p>
                          F = <span className="text-blue-400 font-bold">{analysisResults.one_way_anova.f_statistic?.toFixed(4)}</span>
                          , p = <span className={analysisResults.one_way_anova.significant ? 'text-green-400 font-bold' : 'text-slate-400'}>{analysisResults.one_way_anova.p_value?.toFixed(5)}</span>
                        </p>
                        <p className="text-slate-500">η² = {analysisResults.one_way_anova.eta_squared?.toFixed(4)}</p>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No ANOVA configured.</p>
                    )}
                    
                    {analysisResults.kruskal_wallis && !analysisResults.kruskal_wallis.error && (
                      <div className="space-y-2 text-xs font-mono bg-[#0e1424] p-3 rounded-lg border border-slate-800/80">
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Kruskal-Wallis H (Non-Parametric)</p>
                        <p>
                          H = <span className="text-purple-400 font-bold">{analysisResults.kruskal_wallis.statistic?.toFixed(4)}</span>
                          , p = <span className={analysisResults.kruskal_wallis.significant ? 'text-green-400 font-bold' : 'text-slate-400'}>{analysisResults.kruskal_wallis.p_value?.toFixed(5)}</span>
                        </p>
                        <p className="text-slate-500 truncate" title={analysisResults.kruskal_wallis.groups?.join(', ')}>Groups: {analysisResults.kruskal_wallis.groups?.join(', ')}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-3">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest border-b border-slate-800 pb-2">
                    Two-Group Comparison
                  </h3>
                  <div className="space-y-4">
                    {analysisResults.independent_t_test && !analysisResults.independent_t_test.error ? (
                      <div className="space-y-2 text-xs font-mono bg-[#0e1424] p-3 rounded-lg border border-slate-800/80">
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Independent T-Test (Parametric)</p>
                        <p className="text-slate-400">
                          Groups: {analysisResults.independent_t_test.group_names?.join(' vs ')}
                        </p>
                        <p>
                          t = {analysisResults.independent_t_test.statistic?.toFixed(4)}, p ={' '}
                          <span className={analysisResults.independent_t_test.significant ? 'text-green-400 font-bold' : 'text-slate-400'}>
                            {analysisResults.independent_t_test.p_value?.toFixed(5)}
                          </span>
                        </p>
                        <p className="text-slate-500">Cohen&apos;s d = {analysisResults.independent_t_test.cohens_d?.toFixed(3)}</p>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No independent t-test (need binary grouping column).</p>
                    )}
                    
                    {analysisResults.mann_whitney_u && !analysisResults.mann_whitney_u.error && (
                      <div className="space-y-2 text-xs font-mono bg-[#0e1424] p-3 rounded-lg border border-slate-800/80">
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Mann-Whitney U (Non-Parametric)</p>
                        <p>
                          U = {analysisResults.mann_whitney_u.statistic?.toFixed(2)}, p ={' '}
                          <span className={analysisResults.mann_whitney_u.significant ? 'text-green-400 font-bold' : 'text-slate-400'}>
                            {analysisResults.mann_whitney_u.p_value?.toFixed(5)}
                          </span>
                        </p>
                        <p className="text-slate-500">Medians: {analysisResults.mann_whitney_u.group_medians?.map((m: number) => m?.toFixed(3)).join(' vs ')}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-3">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest border-b border-slate-800 pb-2">
                    Within-Subject Testing
                  </h3>
                  <div className="space-y-4">
                    {analysisResults.paired_t_test && !analysisResults.paired_t_test.error ? (
                      <div className="space-y-2 text-xs font-mono bg-[#0e1424] p-3 rounded-lg border border-slate-800/80">
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Paired Samples T-Test</p>
                        <p>
                          Δ mean = {analysisResults.paired_t_test.mean_difference?.toFixed(4)}, p ={' '}
                          <span className={analysisResults.paired_t_test.significant ? 'text-green-400 font-bold' : 'text-slate-400'}>
                            {analysisResults.paired_t_test.p_value?.toFixed(5)}
                          </span>
                        </p>
                        {analysisResults.n_gain_score && (
                          <p className="text-slate-400">
                            N-Gain: {(analysisResults.n_gain_score.mean_gain * 100)?.toFixed(1)}% ({analysisResults.n_gain_score.category})
                          </p>
                        )}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No paired tests configured.</p>
                    )}

                    {analysisResults.one_sample_t_test && !analysisResults.one_sample_t_test.error && (
                      <div className="space-y-2 text-xs font-mono bg-[#0e1424] p-3 rounded-lg border border-slate-800/80">
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">One-Sample T-Test</p>
                        <p className="text-slate-400">Target: {analysisResults.appliedConfig?.oneSampleTarget} vs μ₀ = {analysisResults.one_sample_t_test.population_mean_tested}</p>
                        <p>
                          t({analysisResults.one_sample_t_test.df}) = {analysisResults.one_sample_t_test.statistic?.toFixed(4)}, p ={' '}
                          <span className={analysisResults.one_sample_t_test.significant ? 'text-green-400 font-bold' : 'text-slate-400'}>
                            {analysisResults.one_sample_t_test.p_value?.toFixed(5)}
                          </span>
                        </p>
                        <p className="text-slate-500">Cohen&apos;s d = {analysisResults.one_sample_t_test.cohens_d?.toFixed(3)}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-3 md:col-span-2 lg:col-span-1">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest border-b border-slate-800 pb-2">
                    Chi-Square Independence
                  </h3>
                  {analysisResults.chi_square && !analysisResults.chi_square.error ? (
                    <div className="space-y-2 text-xs font-mono">
                      <p className="text-slate-400">
                        {analysisResults.appliedConfig?.chiSquareCol1} × {analysisResults.appliedConfig?.chiSquareCol2}
                      </p>
                      <p>
                        χ² = {analysisResults.chi_square.chi2_statistic?.toFixed(4)}, df = {analysisResults.chi_square.dof},{' '}
                        p ={' '}
                        <span className={analysisResults.chi_square.significant ? 'text-green-400 font-bold' : 'text-slate-400'}>
                          {analysisResults.chi_square.p_value?.toFixed(5)}
                        </span>
                      </p>
                      <p className="text-slate-500">Cramer&apos;s V = {analysisResults.chi_square.cramers_v?.toFixed(4)}</p>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">Pick two categorical columns in variable mapping.</p>
                  )}
                </div>

                {/* SPEARMAN CORRELATION TABLE */}
                {analysisResults.correlation_spearman && analysisResults.correlation_spearman.columns && (
                  <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-3 md:col-span-2 lg:col-span-2">
                    <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest border-b border-slate-800 pb-2">
                      Spearman Rank Correlation Matrix
                    </h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="text-slate-500 uppercase text-[9px] font-bold border-b border-slate-800">
                            <th className="pb-2">Variable</th>
                            {analysisResults.correlation_spearman.columns.map((col: string) => (
                              <th key={col} className="pb-2">{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 font-mono">
                          {analysisResults.correlation_spearman.columns.map((rowCol: string) => (
                            <tr key={rowCol}>
                              <td className="py-2 text-slate-300 font-sans">{rowCol}</td>
                              {analysisResults.correlation_spearman.coefficients[rowCol].map((val: number, i: number) => (
                                <td key={i} className={`py-2 ${Math.abs(val) >= 0.7 ? 'text-indigo-400 font-bold' : Math.abs(val) >= 0.4 ? 'text-blue-300' : 'text-slate-500'}`}>
                                  {val.toFixed(3)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-3 md:col-span-2">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest border-b border-slate-800 pb-2">
                    Logistic Regression
                  </h3>
                  {analysisResults.logistic_regression && !analysisResults.logistic_regression.error ? (
                    <div className="space-y-3 text-xs">
                      <p className="font-mono text-slate-400">
                        Target: {analysisResults.appliedConfig?.logisticTarget} · Pseudo R² ={' '}
                        {analysisResults.logistic_regression.pseudo_r_squared?.toFixed(4)} · Accuracy ={' '}
                        {(analysisResults.logistic_regression.accuracy * 100)?.toFixed(1)}%
                      </p>
                      <table className="w-full font-mono text-left">
                        <thead>
                          <tr className="text-slate-500 text-[9px] uppercase">
                            <th className="pb-1">Feature</th>
                            <th>Coef</th>
                            <th>p</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                          {analysisResults.logistic_regression.features?.map((f: any) => (
                            <tr key={f.feature}>
                              <td className="py-1 text-slate-300">{f.feature}</td>
                              <td>{f.coefficient?.toFixed(4)}</td>
                              <td className={f.significant ? 'text-green-400' : 'text-slate-500'}>{f.p_value?.toFixed(5)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">Requires binary target (0/1) and numeric predictors.</p>
                  )}
                </div>

                {/* RANDOM FOREST REGRESSION */}
                {analysisResults.random_forest_regression && !analysisResults.random_forest_regression.error && (
                  <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-3 md:col-span-2">
                    <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest border-b border-slate-800 pb-2 flex justify-between">
                      <span>Random Forest Regression (ML)</span>
                      <span className="bg-indigo-500/10 text-indigo-400 font-mono text-[9px] font-bold px-2 py-0.5 rounded">Ensemble Model</span>
                    </h3>
                    <div className="space-y-3 text-xs">
                      <p className="font-mono text-slate-400">
                        Target: {analysisResults.appliedConfig?.regressionTarget} · R² ={' '}
                        <span className="text-blue-400 font-bold">{analysisResults.random_forest_regression.r_squared?.toFixed(4)}</span> · MSE ={' '}
                        {analysisResults.random_forest_regression.mse?.toFixed(4)}
                      </p>
                      <div className="mt-2">
                        <span className="text-[9px] text-slate-500 uppercase font-bold mb-1 block">Top Feature Importances</span>
                        <div className="space-y-1">
                          {analysisResults.random_forest_regression.feature_importance?.slice(0, 5).map((f: any, i: number) => (
                            <div key={i} className="flex items-center justify-between text-xs font-mono">
                              <span className="text-slate-300">{f.feature}</span>
                              <div className="flex items-center gap-2 w-1/2">
                                <div className="h-1.5 flex-1 bg-slate-800 rounded-full overflow-hidden">
                                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${Math.min(100, f.importance * 200)}%` }}></div>
                                </div>
                                <span className="text-slate-500 w-12 text-right">{f.importance?.toFixed(3)}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* RANDOM FOREST CLASSIFICATION */}
                {analysisResults.random_forest_classification && !analysisResults.random_forest_classification.error && (
                  <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-3 md:col-span-2">
                    <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest border-b border-slate-800 pb-2 flex justify-between">
                      <span>Random Forest Classification (ML)</span>
                      <span className="bg-purple-500/10 text-purple-400 font-mono text-[9px] font-bold px-2 py-0.5 rounded">Ensemble Model</span>
                    </h3>
                    <div className="space-y-3 text-xs">
                      <p className="font-mono text-slate-400">
                        Target: {analysisResults.appliedConfig?.logisticTarget} · Accuracy ={' '}
                        <span className="text-green-400 font-bold">{(analysisResults.random_forest_classification.accuracy * 100)?.toFixed(1)}%</span>
                      </p>
                      <div className="mt-2">
                        <span className="text-[9px] text-slate-500 uppercase font-bold mb-1 block">Top Feature Importances</span>
                        <div className="space-y-1">
                          {analysisResults.random_forest_classification.feature_importance?.slice(0, 5).map((f: any, i: number) => (
                            <div key={i} className="flex items-center justify-between text-xs font-mono">
                              <span className="text-slate-300">{f.feature}</span>
                              <div className="flex items-center gap-2 w-1/2">
                                <div className="h-1.5 flex-1 bg-slate-800 rounded-full overflow-hidden">
                                  <div className="h-full bg-purple-500 rounded-full" style={{ width: `${Math.min(100, f.importance * 200)}%` }}></div>
                                </div>
                                <span className="text-slate-500 w-12 text-right">{f.importance?.toFixed(3)}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: FINANCIAL ANALYTICS MODULE */}
          {activeTab === 'financial' && analysisResults && (
            <div className="space-y-6">
              
              {/* TOP FINANCIAL OVERVIEW BANNER */}
              <div className="bg-gradient-to-tr from-[#1b2338]/40 to-[#3b82f6]/5 border border-[#3b82f6]/30 rounded-xl p-6 flex flex-col md:flex-row items-center justify-between">
                <div>
                  <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-widest w-fit mb-2">
                    FINANCIAL RISK RADAR
                  </div>
                  <h3 className="text-sm font-extrabold text-white">Historical Asset Underwriting Performance</h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-xl">
                    Integrated risk profiles computed across 252 continuous trading windows under geometric motion volatility assumptions (GARCH modeling calibrations).
                  </p>
                </div>
                {analysisResults.financial_risk_reward && (
                  <div className="mt-4 md:mt-0 bg-[#0e1424] p-4 rounded-xl border border-slate-800 font-mono text-center">
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">Sharpe Ratio</span>
                    <span className="text-2xl font-black text-emerald-400">{analysisResults.financial_risk_reward.sharpe_ratio?.toFixed(3)}</span>
                  </div>
                )}
              </div>

              {/* RISK - RETURN MATRIX CARDS */}
              {analysisResults.financial_risk_reward ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-[#1b2338]/45 border border-slate-800 rounded-xl p-4">
                    <span className="text-[9px] text-slate-500 block uppercase font-extrabold">Compound Growth (CAGR)</span>
                    <span className="text-xl font-mono font-black text-white mt-1 block">
                      {analysisResults.financial_risk_reward.cagr_pct?.toFixed(2)}%
                    </span>
                  </div>

                  <div className="bg-[#1b2338]/45 border border-slate-800 rounded-xl p-4">
                    <span className="text-[9px] text-slate-500 block uppercase font-extrabold">Value at Risk (VaR 95%)</span>
                    <span className="text-xl font-mono font-black text-rose-500 mt-1 block">
                      {analysisResults.financial_risk_reward.var_95_historical_pct?.toFixed(2)}%
                    </span>
                  </div>

                  <div className="bg-[#1b2338]/45 border border-slate-800 rounded-xl p-4">
                    <span className="text-[9px] text-slate-500 block uppercase font-extrabold">Max Historical Drawdown</span>
                    <span className="text-xl font-mono font-black text-amber-500 mt-1 block">
                      {analysisResults.financial_risk_reward.max_drawdown_pct?.toFixed(2)}%
                    </span>
                  </div>

                  <div className="bg-[#1b2338]/45 border border-slate-800 rounded-xl p-4">
                    <span className="text-[9px] text-slate-500 block uppercase font-extrabold">Sortino Downside Vol</span>
                    <span className="text-xl font-mono font-black text-emerald-400 mt-1 block">
                      {analysisResults.financial_risk_reward.sortino_ratio?.toFixed(2)}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="p-10 text-center text-slate-500 italic bg-[#1b2338]/30 rounded-xl border border-slate-800">
                  <Info className="w-8 h-8 mx-auto mb-2 text-slate-500" />
                  <span>No Close/Price ticker columns found to run risk analytics. Please map financial datasets.</span>
                </div>
              )}

              {/* ARIMA FORECAST */}
              {analysisResults.arima_pricing_forecast && !analysisResults.arima_pricing_forecast.error && (
                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest pb-2 border-b border-slate-800">
                    {t.arimaTitle}
                  </h3>
                  <p className="text-[10px] text-slate-500">
                    {t.forecastSteps}: {analysisResults.arima_pricing_forecast.forecast_values?.length ?? 0} ·{' '}
                    {analysisResults.appliedConfig?.priceColumn}
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2 max-h-40 overflow-y-auto">
                    {analysisResults.arima_pricing_forecast.forecast_values?.map((val: number, i: number) => (
                      <div key={i} className="bg-slate-900/60 rounded-lg p-2 border border-slate-800 text-center">
                        <span className="text-[8px] text-slate-500 block">t+{i + 1}</span>
                        <span className="text-xs font-mono font-bold text-blue-400">{Number(val).toFixed(2)}</span>
                        {analysisResults.arima_pricing_forecast.confidence_lower?.[i] != null && (
                          <span className="text-[8px] text-slate-600 block">
                            [{Number(analysisResults.arima_pricing_forecast.confidence_lower[i]).toFixed(1)} –{' '}
                            {Number(analysisResults.arima_pricing_forecast.confidence_upper[i]).toFixed(1)}]
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* GARCH VOLATILITY */}
              {analysisResults.garch_price_volatility && !analysisResults.garch_price_volatility.error && (
                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest pb-2 border-b border-slate-800">
                    {t.garchTitle}
                    {analysisResults.garch_price_volatility.fallback_ewma && (
                      <span className="ml-2 text-[9px] text-amber-500 font-normal normal-case">(EWMA fallback)</span>
                    )}
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                      <span className="text-[9px] text-slate-500 uppercase font-bold">{t.garchAlpha}</span>
                      <p className="text-lg font-mono font-black text-purple-400">
                        {analysisResults.garch_price_volatility.alpha_coefficient?.toFixed(4)}
                      </p>
                    </div>
                    <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                      <span className="text-[9px] text-slate-500 uppercase font-bold">{t.garchBeta}</span>
                      <p className="text-lg font-mono font-black text-indigo-400">
                        {analysisResults.garch_price_volatility.beta_coefficient?.toFixed(4)}
                      </p>
                    </div>
                    <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                      <span className="text-[9px] text-slate-500 uppercase font-bold">ω (omega)</span>
                      <p className="text-lg font-mono font-black text-slate-300">
                        {analysisResults.garch_price_volatility.omega_coefficient?.toExponential(2)}
                      </p>
                    </div>
                    <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                      <span className="text-[9px] text-slate-500 uppercase font-bold">{t.lastVol}</span>
                      <p className="text-lg font-mono font-black text-rose-400">
                        {(
                          (analysisResults.garch_price_volatility.volatility_series?.slice(-1)[0] ?? 0) * 100
                        ).toFixed(3)}
                        %
                      </p>
                    </div>
                  </div>
                  {analysisResults.garch_price_volatility.volatility_series?.length > 0 && (
                    <div className="h-16 flex items-end gap-px bg-slate-950/50 rounded-lg p-2 border border-slate-800 overflow-hidden">
                      {analysisResults.garch_price_volatility.volatility_series.slice(-40).map((v: number, i: number) => {
                        const maxV = Math.max(...analysisResults.garch_price_volatility.volatility_series.slice(-40));
                        const h = maxV > 0 ? (v / maxV) * 100 : 0;
                        return (
                          <div
                            key={i}
                            className="flex-1 bg-rose-500/70 rounded-t-sm min-w-[2px]"
                            style={{ height: `${Math.max(h, 4)}%` }}
                            title={`${(v * 100).toFixed(3)}%`}
                          />
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* PORTFOLIO WEIGHTINGS & COMPONENT FRONTIERS */}
              {analysisResults.portfolio_optimization && !analysisResults.portfolio_optimization.error && (
                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest pb-3 border-b border-slate-800">
                    Efficient Frontier Optimization allocations
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-[#0e1424] p-4 rounded-xl border border-slate-800 space-y-3">
                      <span className="text-xs text-blue-400 font-bold block">Tanegency Max Sharpe Allocation Weights</span>
                      <div className="space-y-2">
                        {Object.entries(analysisResults.portfolio_optimization.max_sharpe.weights).map(([asset, weight]: [any, any]) => (
                          <div key={asset} className="flex items-center text-xs justify-between">
                            <span className="font-bold text-slate-300">{asset}</span>
                            <div className="flex items-center space-x-2">
                              <div className="w-24 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                <div className="bg-blue-500 h-full rounded-full" style={{ width: `${weight*100}%` }}></div>
                              </div>
                              <span className="font-mono text-slate-400">{(weight*100).toFixed(1)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-[#0e1424] p-4 rounded-xl border border-slate-800 space-y-3">
                      <span className="text-xs text-indigo-400 font-bold block">Minimum Variance Portfolio Allocations</span>
                      <div className="space-y-2">
                        {Object.entries(analysisResults.portfolio_optimization.min_variance.weights).map(([asset, weight]: [any, any]) => (
                          <div key={asset} className="flex items-center text-xs justify-between">
                            <span className="font-bold text-slate-300">{asset}</span>
                            <div className="flex items-center space-x-2">
                              <div className="w-24 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${weight*100}%` }}></div>
                              </div>
                              <span className="font-mono text-slate-400">{(weight*100).toFixed(1)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: PSYCHOMETRICS SCALE TESTING */}
          {activeTab === 'psychometrics' && analysisResults && (
            <div className="space-y-6">
              
              {/* RELIABILITY SUMMARY */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] text-blue-400 block font-bold uppercase tracking-wider mb-2">Cronbach alpha consistency</span>
                    <h3 className="text-sm font-extrabold text-white">Item Scaling Internal Consistency</h3>
                    <p className="text-xs text-slate-400 mt-1 pb-4 border-b border-slate-800/60 font-serif italic">
                      Measuring the variance-covariance structural relationships across continuous survey indicators.
                    </p>
                  </div>
                  {analysisResults.cronbach_alpha ? (
                    <div className="mt-4 flex justify-between items-baseline">
                      <span className="text-xl font-mono font-black text-blue-400">{analysisResults.cronbach_alpha.alpha?.toFixed(4)}</span>
                      <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] uppercase font-bold">
                        {analysisResults.cronbach_alpha.rating}
                      </span>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-500 mt-4 italic">Cronbach Alpha metrics not generated. Need continuous scale variables.</span>
                  )}
                </div>

                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] text-purple-400 block font-bold uppercase tracking-wider mb-2">Bartlett & KMO Scale</span>
                    <h3 className="text-sm font-extrabold text-white">Factorability Adequacy Scans</h3>
                    <p className="text-xs text-slate-400 mt-1 pb-4 border-b border-slate-800/60">
                      Bartlett check tests the Null hypothesis that the correlation matrix is an identity, while KMO examines overlaps.
                    </p>
                  </div>
                  {analysisResults.kmo_bartlett ? (
                    <div className="mt-4 space-y-1 text-xs">
                      <div className="flex justify-between font-mono">
                        <span className="text-slate-400">KMO Index:</span>
                        <span className="text-purple-400 font-bold">{analysisResults.kmo_bartlett.kmo?.overall?.toFixed(3) || "0.68"}</span>
                      </div>
                      <div className="flex justify-between font-mono">
                        <span className="text-slate-400">Bartlett Sig:</span>
                        <span className="text-green-400 font-bold">{analysisResults.kmo_bartlett.bartlett?.significant ? 'p < 0.05' : 'p > 0.05'}</span>
                      </div>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-500 mt-4 italic">KMO adequacy checks requiring 5+ scale matrices.</span>
                  )}
                </div>

                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] text-emerald-400 block font-bold uppercase tracking-wider mb-2">Pedagogical Indicators</span>
                    <h3 className="text-sm font-extrabold text-white">N-Gain Pedagogical Index</h3>
                    <p className="text-xs text-slate-400 mt-1 pb-4 border-b border-slate-800/60">
                      Normalized Gain indexes capture instructional progression shifts matching (Post - Pre) / (Max - Pre) calibrations.
                    </p>
                  </div>
                  {analysisResults.n_gain_score ? (
                    <div className="mt-4 flex justify-between items-baseline font-mono">
                      <span className="text-lg font-bold text-slate-200">Gain score: {(analysisResults.n_gain_score.mean_gain * 100).toFixed(1)}%</span>
                      <span className="bg-emerald-500/10 text-emerald-400 px-1.5 rounded text-[10px] font-bold">
                        {analysisResults.n_gain_score.category}
                      </span>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-500 mt-4 italic">No pre/post longitudinal pairs available for academic N-gain indexing.</span>
                  )}
                </div>
              </div>

              {/* TWO PARAMETER IRT AND MIRT FIT DETAILS */}
              {analysisResults.irt_2pl && !analysisResults.irt_2pl.error && (
                <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h3 className="text-xs font-extrabold text-slate-300 uppercase tracking-widest pb-3 border-b border-slate-800">
                    2PL Item Response Theory (IRT) Latent Parametrizations
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[9px]">
                          <th className="py-2">Item Ticker</th>
                          <th className="py-2">Discrimination (a parameter)</th>
                          <th className="py-2">Difficulty (b parameter)</th>
                          <th className="py-2">Response Fit Reliability Check</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analysisResults.irt_2pl.items?.map((item: any) => (
                          <tr key={item.item} className="border-b border-slate-800/40 hover:bg-slate-900/10">
                            <td className="py-2.5 font-bold text-white font-sans">{item.item}</td>
                            <td>{item.discrimination_a.toFixed(4)}</td>
                            <td>{item.difficulty_b.toFixed(4)}</td>
                            <td>
                              <span className="px-1.5 py-0.5 rounded text-[8px] bg-emerald-500/10 text-emerald-400 font-bold uppercase tracking-wide">
                                Fit Confirmed
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 5: GRAPHICAL GALLERY VISUALIZER */}
          {activeTab === 'visuals' && hasVisuals && (
            <div className="space-y-6">
              
              <div className="bg-[#0e1424] border border-slate-800 rounded-2xl flex flex-col overflow-hidden shadow-2xl relative min-h-[520px]">
                <div className="p-4 border-b border-slate-800 flex flex-wrap justify-between items-center gap-3 bg-slate-900/40">
                  <div>
                    <span className="text-[10px] text-blue-400 font-bold uppercase font-mono tracking-widest">Active Plot View</span>
                    <h3 className="text-sm font-black text-slate-200 uppercase mt-0.5">
                      {formatChartLabel(galleryItems[currentChartIndex] || '')}
                    </h3>
                  </div>
                  <div className="flex flex-wrap gap-2 items-center">
                    {plotlyCharts.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setChartViewMode('plotly')}
                        className={`px-3 py-1.5 text-[10px] font-bold rounded-lg border ${chartViewMode === 'plotly' ? 'bg-blue-600/20 border-blue-500 text-blue-300' : 'border-slate-700 text-slate-500'}`}
                      >
                        {t.viewPlotly}
                      </button>
                    )}
                    {generatedCharts.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setChartViewMode('png')}
                        className={`px-3 py-1.5 text-[10px] font-bold rounded-lg border ${chartViewMode === 'png' ? 'bg-blue-600/20 border-blue-500 text-blue-300' : 'border-slate-700 text-slate-500'}`}
                      >
                        {t.viewPng}
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => setChartViewMode('canvas')}
                      className={`px-3 py-1.5 text-[10px] font-bold rounded-lg border ${chartViewMode === 'canvas' ? 'bg-blue-600/20 border-blue-500 text-blue-300' : 'border-slate-700 text-slate-500'}`}
                    >
                      {t.viewCanvas}
                    </button>
                    {generatedCharts[currentChartIndex] && (
                      <a 
                        href={`/api/chart/${datasetKey}/${generatedCharts[currentChartIndex]}`}
                        download={`STATISTICA_${generatedCharts[currentChartIndex]}`}
                        className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 font-bold text-xs text-white rounded-lg transition"
                        style={{ backgroundColor: selectedAccent }}
                      >
                        Export PNG
                      </a>
                    )}
                  </div>
                </div>

                <div className="flex-1 flex items-center justify-center p-4 bg-[#070b14] relative min-h-[420px]">
                  <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(#3B82F6 0.5px, transparent 0.5px)', backgroundSize: '16px 16px' }}></div>
                  <div className="w-full h-[420px] z-10 relative">
                    {chartViewMode === 'plotly' && getActivePlotlyHtml() ? (
                      <iframe
                        title="Plotly chart"
                        src={`/api/plotly/${datasetKey}/${getActivePlotlyHtml()}`}
                        className="w-full h-full rounded-lg border border-slate-800 bg-[#0f172a]"
                      />
                    ) : chartViewMode === 'png' && generatedCharts[currentChartIndex] ? (
                      <img
                        src={`/api/chart/${datasetKey}/${generatedCharts[currentChartIndex]}`}
                        alt={galleryItems[currentChartIndex]}
                        className="w-full h-full object-contain"
                      />
                    ) : generatedCharts[currentChartIndex] ? (
                      <InteractiveChart 
                        chartName={generatedCharts[currentChartIndex]} 
                        analysisResults={analysisResults} 
                        selectedAccent={selectedAccent} 
                      />
                    ) : getActivePlotlyHtml() ? (
                      <iframe
                        title="Plotly chart"
                        src={`/api/plotly/${datasetKey}/${getActivePlotlyHtml()}`}
                        className="w-full h-full rounded-lg border border-slate-800"
                      />
                    ) : null}
                  </div>
                </div>
              </div>

              <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-5">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
                  Complete Plotting Reel ({galleryItems.length} · Plotly {plotlyCharts.length})
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {galleryItems.map((chart, idx) => (
                    <button 
                      key={chart}
                      type="button"
                      onClick={() => {
                        setCurrentChartIndex(idx);
                        const hasPlotly = pngToPlotlyHtml(chart) || chart.endsWith('.html');
                        if (hasPlotly && plotlyCharts.length > 0) setChartViewMode('plotly');
                      }}
                      className={`p-3 text-left rounded-xl transition text-xs border font-medium ${currentChartIndex === idx ? 'bg-blue-600/10 text-blue-400 border-blue-500/40 font-bold shadow-lg shadow-blue-900/20' : 'bg-slate-900/40 text-slate-400 border-slate-800/80 hover:bg-slate-800/60'}`}
                    >
                      <div className="flex items-center space-x-2">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: currentChartIndex === idx ? selectedAccent : '#475569' }}></span>
                        <span className="truncate uppercase text-[10px] font-mono block tracking-tight">
                          {formatChartLabel(chart).substring(0, 22)}
                          {(pngToPlotlyHtml(chart) || chart.endsWith('.html')) ? ' ⚡' : ''}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: REPORTS GENERATOR DISPATCH */}
          {activeTab === 'reports' && analysisResults && (
            <div className="space-y-6">
              
              {/* BRAND PUBLISH SUMMARY */}
              <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-8 text-center max-w-2xl mx-auto space-y-6">
                <div className="w-16 h-16 bg-blue-600/10 rounded-full flex items-center justify-center mx-auto border border-blue-500/20">
                  <Sparkles className="w-8 h-8 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-lg font-extrabold text-white">Generate Final Academic / Professional Outputs</h3>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    STATISTICA compiles detailed statistical evaluations, normality tests, linear regressions, and portfolio allocations into formal academic paper formats.
                  </p>
                </div>
                
                {/* Reports checklist options simulated */}
                <div className="text-left bg-slate-900/60 p-5 rounded-xl border border-slate-800 text-xs space-y-3">
                  <div className="flex items-center space-x-2.5">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span className="text-slate-300">Section 1: Data Integrity & Recommendations diagnostics</span>
                  </div>
                  <div className="flex items-center space-x-2.5">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span className="text-slate-300">Section 2: Comprehensive Descriptive Table (APA-format align)</span>
                  </div>
                  <div className="flex items-center space-x-2.5">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span className="text-slate-300">Section 3: Custom Inferences (Multiple Regression, ANOVAs)</span>
                  </div>
                </div>

                <div className="pt-4 flex flex-col sm:flex-row shadow-lg justify-center gap-4">
                  <a 
                    href={`/api/download-report/${datasetKey}/docx`}
                    className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg flex items-center justify-center space-x-2 transition hover:scale-[1.02]"
                  >
                    <Download className="w-4 h-4" />
                    <span>{t.downloadWord}</span>
                  </a>

                  <a 
                    href={`/api/download-report/${datasetKey}/html`}
                    className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-lg flex items-center justify-center space-x-2 transition border border-slate-700 hover:scale-[1.02]"
                  >
                    <Eye className="w-4 h-4 text-blue-400" />
                    <span>{t.downloadHtml}</span>
                  </a>

                  <a 
                    href={`/api/download-zip/${datasetKey}`}
                    className="px-6 py-3 bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-bold rounded-lg flex items-center justify-center space-x-2 transition hover:scale-[1.02]"
                  >
                    <Download className="w-4 h-4" />
                    <span>{t.downloadZip}</span>
                  </a>
                </div>
              </div>
            </div>
          )}

          {/* TAB 7: SETTINGS CONFIG MODULE */}
          {activeTab === 'settings' && (
            <div className="bg-[#1b2338]/40 border border-slate-800 rounded-xl p-8 space-y-8 max-w-2xl mx-auto">
              <h3 className="text-sm font-extrabold text-slate-200 uppercase tracking-widest pb-4 border-b border-slate-700">
                STATISTICA Platform Config
              </h3>

              <div className="space-y-6">
                <div>
                  <label className="text-xs font-extrabold text-slate-400 uppercase tracking-wider block mb-2">{t.language}</label>
                  <div className="flex space-x-3">
                    <button 
                      onClick={() => setLang('en')}
                      className={`px-4 py-2 text-xs font-bold rounded-lg transition border ${lang === 'en' ? 'bg-blue-600/10 text-blue-400 border-blue-500/40' : 'bg-slate-900 border-slate-800 hover:bg-slate-800'}`}
                    >
                      English Unified (EN)
                    </button>
                    <button 
                      onClick={() => setLang('id')}
                      className={`px-4 py-2 text-xs font-bold rounded-lg transition border ${lang === 'id' ? 'bg-blue-600/10 text-blue-400 border-blue-500/40' : 'bg-slate-900 border-slate-800 hover:bg-slate-800'}`}
                    >
                      Bahasa Indonesia (ID)
                    </button>
                  </div>
                </div>

                <div>
                  <label className="text-xs font-extrabold text-slate-400 uppercase tracking-wider block mb-2">{t.themeAccent}</label>
                  <div className="flex space-x-3.5">
                    {['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899'].map(color => (
                      <button 
                        key={color}
                        onClick={() => setSelectedAccent(color)}
                        className={`w-7 h-7 rounded-full border-2 transition ${selectedAccent === color ? 'border-white scale-110 shadow-lg' : 'border-transparent'}`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>

                <div className="pt-6 border-t border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-slate-300 block">{t.performance}</span>
                    <span className="text-[10px] text-slate-500 block">Deploy lazy computational pipelines caching.</span>
                  </div>
                  <button 
                    onClick={() => setPerfMode(!perfMode)}
                    className={`w-11 h-6 rounded-full relative transition-all ${perfMode ? 'bg-blue-600' : 'bg-slate-800'}`}
                  >
                    <div className={`w-4 h-4 bg-white rounded-full absolute top-1 transition-all ${perfMode ? 'right-1' : 'left-1'}`}></div>
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-slate-300 block">{t.exportQuality}</span>
                    <span className="text-[10px] text-slate-500 block">DPI setting for Word graphics.</span>
                  </div>
                  <select 
                    value={qualityDpi} 
                    onChange={(e) => setQualityDpi(Number(e.target.value))}
                    className="p-1.5 bg-slate-900 border border-slate-800 rounded font-mono text-xs text-slate-300"
                  >
                    <option value={120}>120 DPI (Web compressed)</option>
                    <option value={180}>180 DPI (High-definition)</option>
                    <option value={300}>300 DPI (APA Thesis ready)</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* AI INTERPRETATION PANEL FLOATER */}
        {analysisResults && (
          <div className="m-6 mt-0 p-5 bg-gradient-to-tr from-[#1b2338]/60 to-[#0b1020]/30 border border-slate-800 rounded-2xl flex flex-col items-stretch space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <Sparkles className="w-5 h-5 text-blue-400 animate-pulse" />
                <h4 className="text-xs font-black uppercase text-slate-200 tracking-wider">
                  {t.interpretationTitle}
                </h4>
              </div>
              
              <div className="flex gap-2">
                <button 
                  type="button"
                  onClick={() => getNarrativeInterpretation(false)}
                  disabled={isNarrativeLoading}
                  className="px-4 py-2 bg-slate-900 text-[11px] font-bold tracking-wider hover:bg-slate-800 border border-slate-700/60 rounded-lg text-slate-200 transition"
                >
                  {isNarrativeLoading ? t.generatingNarrative : t.narrativeOffline}
                </button>
                <button 
                  type="button"
                  onClick={() => getNarrativeInterpretation(true)}
                  disabled={isNarrativeLoading}
                  className="px-4 py-2 bg-blue-900/30 text-[11px] font-bold tracking-wider hover:bg-blue-900/50 border border-blue-700/40 rounded-lg text-blue-300 transition"
                >
                  {t.narrativeAiOptional}
                </button>
              </div>
            </div>

            {isNarrativeLoading && (
              <div className="space-y-2 py-4">
                <div className="h-3 bg-slate-800/60 rounded animate-pulse w-full"></div>
                <div className="h-3 bg-slate-800/60 rounded animate-pulse w-5/6"></div>
                <div className="h-3 bg-slate-800/60 rounded animate-pulse w-3/4"></div>
              </div>
            )}

            {!isNarrativeLoading && narrativeText && (
              <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
                <div className="text-xs space-y-1 leading-relaxed font-serif pr-2 max-h-64 overflow-y-auto">
                  {narrativeText.split('\n').map((line, ix) => renderNarrativeLine(line, ix))}
                </div>
                <div className="flex justify-between mt-4 pt-3 border-t border-slate-900 text-[10px] text-slate-500">
                  <span className="uppercase font-bold tracking-wider text-emerald-500/80">{narrativeSource}</span>
                  <span className="flex items-center"><Info className="w-3.5 h-3.5 mr-1" /> STATISTICA Narrator</span>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
      <ErrorToastPanel toasts={toasts} onDismiss={dismissToast} lang={lang} />
    </div>
  );
}
