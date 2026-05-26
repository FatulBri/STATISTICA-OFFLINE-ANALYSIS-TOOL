import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import multer from 'multer';
import dotenv from 'dotenv';
import { GoogleGenAI } from '@google/genai';
import {
  resolvePythonCommand,
  checkPythonScientificStack,
  runStatistica,
  parseMarker,
  isPathInsideDir,
} from './server/pythonUtil.js';
import { generateOfflineNarrative } from './server/offlineNarrative.js';
import { slimSummaryForNarrative } from './server/slimSummary.js';
import { streamDatasetZip } from './server/zipExport.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = Number(process.env.PORT) || 3000;
const MAX_UPLOAD_MB = Number(process.env.MAX_UPLOAD_MB) || 100;
const MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024;
const ALLOWED_UPLOAD_EXTENSIONS = new Set(['.csv', '.xlsx', '.xls']);

// Setup directories
const UPLOADS_DIR = path.join(__dirname, 'uploads');
const OUTPUT_DIR = path.join(__dirname, 'output');
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR, { recursive: true });
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

// Multer storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, UPLOADS_DIR);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + ext);
  }
});
const upload = multer({
  storage,
  limits: { fileSize: MAX_UPLOAD_BYTES, files: 1 },
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (!ALLOWED_UPLOAD_EXTENSIONS.has(ext)) {
      cb(new Error('Only CSV and Excel files are supported'));
      return;
    }
    cb(null, true);
  },
});

const STATISTICA_SCRIPT = path.join(__dirname, 'statistica.py');

app.use(express.json({ limit: '25mb' }));

function assertUploadedFilePath(filePath: string): boolean {
  return isPathInsideDir(filePath, UPLOADS_DIR);
}

function artifactPath(...segments: string[]): string | null {
  const targetPath = path.join(OUTPUT_DIR, ...segments);
  return isPathInsideDir(targetPath, OUTPUT_DIR) ? targetPath : null;
}

function handleUpload(
  req: express.Request,
  res: express.Response,
  next: express.NextFunction
): void {
  upload.single('file')(req, res, (err: unknown) => {
    if (!err) {
      next();
      return;
    }

    const message = err instanceof multer.MulterError && err.code === 'LIMIT_FILE_SIZE'
      ? `File is too large. Maximum upload size is ${MAX_UPLOAD_MB} MB`
      : err instanceof Error
        ? err.message
        : 'Upload failed';
    res.status(400).json({ error: message });
  });
}

function handlePythonResult(
  stdout: string,
  stderr: string,
  marker: string,
  res: express.Response,
  onSuccess: (payload: string) => void,
  errorLabel: string
) {
  const payload = parseMarker(stdout, marker);
  if (!payload) {
    return res.status(500).json({
      error: errorLabel,
      details: stderr || stdout,
      pythonCommand: resolvePythonCommand(),
    });
  }
  onSuccess(payload);
}

function buildAnalysisPayload(outputFolder: string, lang: 'en' | 'id' = 'en') {
  const summaryJsonPath = path.join(outputFolder, 'summary.json');
  if (!fs.existsSync(summaryJsonPath)) {
    throw new Error('Summary file not found at ' + summaryJsonPath);
  }

  const summaryData = JSON.parse(fs.readFileSync(summaryJsonPath, 'utf8'));
  const chartsFolder = path.join(outputFolder, 'charts');
  let chartsList: string[] = [];
  let plotlyCharts: string[] = [];
  if (fs.existsSync(chartsFolder)) {
    const all = fs.readdirSync(chartsFolder);
    chartsList = all.filter((f) => f.endsWith('.png'));
    plotlyCharts = all.filter((f) => f.endsWith('.html'));
  }

  return {
    success: true,
    summary: summaryData,
    datasetKey: path.basename(outputFolder),
    charts: chartsList,
    plotlyCharts,
    offlineNarrative: generateOfflineNarrative(
      slimSummaryForNarrative(summaryData),
      lang
    ),
  };
}

function findLatestOutputFolder(): string | null {
  if (!fs.existsSync(OUTPUT_DIR)) return null;
  const candidates = fs.readdirSync(OUTPUT_DIR)
    .map((name) => {
      const folder = path.join(OUTPUT_DIR, name);
      const summaryPath = path.join(folder, 'summary.json');
      if (!fs.statSync(folder).isDirectory() || !fs.existsSync(summaryPath)) return null;
      return {
        name,
        folder,
        mtimeMs: fs.statSync(summaryPath).mtimeMs,
      };
    })
    .filter(Boolean) as Array<{ name: string; folder: string; mtimeMs: number }>;

  const uploadedResults = candidates.filter((item) =>
    !item.name.startsWith('example_dataset') && !item.name.startsWith('_')
  );
  const pool = uploadedResults.length > 0 ? uploadedResults : candidates;
  pool.sort((a, b) => b.mtimeMs - a.mtimeMs);
  return pool[0]?.folder ?? null;
}

// API: System Status
app.get('/api/status', (req, res) => {
  const py = resolvePythonCommand();
  res.json({
    status: 'ONLINE',
    pythonReady: !!py,
    pythonScientificReady: checkPythonScientificStack(),
    pythonCommand: py,
    platform: process.platform,
    localTime: new Date().toISOString(),
    api_key_configured: !!process.env.GEMINI_API_KEY,
    example_available: fs.existsSync(path.join(__dirname, 'example_dataset.csv')),
  });
});

// API: Restore the latest completed analysis from disk
app.get('/api/latest-result', (req, res) => {
  try {
    const latestFolder = findLatestOutputFolder();
    if (!latestFolder) {
      return res.status(404).json({ error: 'No completed analysis output found' });
    }

    res.json(buildAnalysisPayload(latestFolder, req.query.lang === 'id' ? 'id' : 'en'));
  } catch (err: any) {
    res.status(500).json({ error: 'Failed to restore latest analysis', details: err.message });
  }
});

// API: Load Example Dataset
app.post('/api/load-example', (req, res) => {
  const exampleSrc = path.join(__dirname, 'example_dataset.csv');
  if (!fs.existsSync(exampleSrc)) {
    return res.status(404).json({ error: 'Example dataset not found' });
  }
  const destName = `example_dataset-${Date.now()}.csv`;
  const tempDest = path.join(UPLOADS_DIR, destName);
  fs.copyFileSync(exampleSrc, tempDest);
  
  res.json({
    success: true,
    filePath: tempDest,
    fileName: 'example_dataset.csv'
  });
});

// API: Upload file + fast schema diagnostics only (no full analysis)
app.post('/api/upload', handleUpload, (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const filePath = req.file.path;
  const originalName = req.file.originalname;

  runStatistica(
    STATISTICA_SCRIPT,
    filePath,
    { diagnosticsOnly: true },
    (error, stdout, stderr) => {
      if (error) {
        console.error(`Diagnostic runtime error: ${stderr}`);
        return res.status(500).json({
          error: 'Failed to diagnose file layout in Python',
          details: stderr || error.message,
          pythonCommand: resolvePythonCommand(),
        });
      }

      handlePythonResult(stdout, stderr, 'DIAGNOSTICS', res, (jsonPayload) => {
        try {
          const summaryData = JSON.parse(jsonPayload);
          res.json({
            success: true,
            filePath,
            fileName: originalName,
            diagnostics: summaryData,
          });
        } catch (parseErr: any) {
          res.status(500).json({ error: 'Failed to parse diagnostics JSON', details: parseErr.message });
        }
      }, 'Python diagnostics did not report DIAGNOSTICS marker');
    }
  );
});

// API: Re-run diagnostics on an already uploaded file
app.post('/api/diagnostics', (req, res) => {
  const { filePath, sheet } = req.body as { filePath?: string; sheet?: string };
  if (!filePath || !fs.existsSync(filePath) || !assertUploadedFilePath(filePath)) {
    return res.status(400).json({ error: 'Valid uploaded file path is required' });
  }

  runStatistica(
    STATISTICA_SCRIPT,
    filePath,
    { diagnosticsOnly: true, sheet },
    (error, stdout, stderr) => {
      if (error) {
        return res.status(500).json({ error: 'Diagnostics failed', details: stderr || error.message });
      }

      handlePythonResult(stdout, stderr, 'DIAGNOSTICS', res, (jsonPayload) => {
        try {
          res.json({ success: true, diagnostics: JSON.parse(jsonPayload) });
        } catch (parseErr: any) {
          res.status(500).json({ error: 'Failed to parse diagnostics JSON', details: parseErr.message });
        }
      }, 'Python diagnostics did not report DIAGNOSTICS marker');
    }
  );
});

// API: Full offline analysis (charts, reports, summary.json)
app.post('/api/analyze', (req, res) => {
  const { filePath, sheet, config } = req.body as {
    filePath?: string;
    sheet?: string;
    config?: Record<string, unknown>;
  };
  if (!filePath || !fs.existsSync(filePath) || !assertUploadedFilePath(filePath)) {
    return res.status(400).json({ error: 'Valid uploaded file path is required to launch engines' });
  }

  let configPath: string | undefined;
  if (config && Object.keys(config).length > 0) {
    const merged = { ...config, ...(sheet ? { sheet } : {}) };
    configPath = path.join(UPLOADS_DIR, `analysis-config-${Date.now()}.json`);
    fs.writeFileSync(configPath, JSON.stringify(merged), 'utf8');
  }

  runStatistica(
    STATISTICA_SCRIPT,
    filePath,
    { outputDir: OUTPUT_DIR, sheet: sheet || (config?.sheet as string | undefined), configPath },
    (error, stdout, stderr) => {
      if (error) {
        console.error(`Execution error: ${stderr}`);
        return res.status(500).json({
          error: 'Core engine computations failed',
          details: [stderr, stdout, error.message].filter(Boolean).join('\n\n'),
          pythonCommand: resolvePythonCommand(),
        });
      }

      handlePythonResult(stdout, stderr, 'SUCCESS', res, (outputFolder) => {
        try {
          res.json(buildAnalysisPayload(outputFolder, 'en'));
        } catch (err: any) {
          res.status(500).json({ error: 'Analysis succeeded but results were unreadable', details: err.message });
        } finally {
          if (configPath && fs.existsSync(configPath)) {
            try { fs.unlinkSync(configPath); } catch { /* ignore */ }
          }
        }
      }, 'Python analyzer did not report SUCCESS marker');
    }
  );
});

// Serve Charts assets (PNGs) statically
app.get('/api/chart/:datasetKey/:chartName', (req, res) => {
  const { datasetKey, chartName } = req.params;
  const targetPath = artifactPath(datasetKey, 'charts', chartName);
  if (!targetPath) return res.status(403).json({ error: 'Forbidden path' });
  if (fs.existsSync(targetPath)) {
    res.sendFile(targetPath);
  } else {
    res.status(404).json({ error: 'Chart artifact not found' });
  }
});

// Serve Interactive Plotly HTML Widgets
app.get('/api/plotly/:datasetKey/:widgetName', (req, res) => {
  const { datasetKey, widgetName } = req.params;
  const targetPath = artifactPath(datasetKey, 'charts', widgetName);
  if (!targetPath) return res.status(403).json({ error: 'Forbidden path' });
  if (fs.existsSync(targetPath)) {
    res.sendFile(targetPath);
  } else {
    res.status(404).json({ error: 'Plotly chart not found' });
  }
});

// API: Download full output bundle (charts + reports + summary.json)
app.get('/api/download-zip/:datasetKey', (req, res) => {
  const { datasetKey } = req.params;
  const folderPath = artifactPath(datasetKey);
  if (!folderPath) {
    return res.status(403).json({ error: 'Forbidden path' });
  }
  streamDatasetZip(OUTPUT_DIR, datasetKey, res);
});

// API: Download MS Word Report template
app.get('/api/download-report/:datasetKey/:format', (req, res) => {
  const { datasetKey, format } = req.params;
  const fileName = format === 'docx' ? 'report.docx' : 'report.html';
  const targetPath = artifactPath(datasetKey, fileName);
  if (!targetPath) return res.status(403).json({ error: 'Forbidden path' });
  
  if (fs.existsSync(targetPath)) {
    res.download(targetPath, `${datasetKey}_STATISTICA_REPORT.${format}`);
  } else {
    res.status(404).json({ error: 'Report binary generation pending or unavailable' });
  }
});

// API: Narrative — offline rule engine (default) + optional Gemini enrichment
app.post('/api/narrative', async (req, res) => {
  const { summary, datasetKey, lang = 'en', useAi = false } = req.body as {
    summary?: Record<string, unknown>;
    datasetKey?: string;
    lang?: 'en' | 'id';
    useAi?: boolean;
  };

  let rawSummary = summary;
  if (!rawSummary && datasetKey) {
    const summaryPath = artifactPath(datasetKey, 'summary.json');
    if (summaryPath && fs.existsSync(summaryPath)) {
      rawSummary = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
    }
  }

  if (!rawSummary || typeof rawSummary !== 'object') {
    return res.status(400).json({ error: 'summary or valid datasetKey required' });
  }

  const slim = slimSummaryForNarrative(rawSummary as Record<string, any>);
  const offlineText = generateOfflineNarrative(slim, lang === 'id' ? 'id' : 'en');

  if (!useAi || !process.env.GEMINI_API_KEY) {
    return res.json({
      narrative: offlineText,
      source: 'offline',
    });
  }

  try {
    const ai = new GoogleGenAI({
      apiKey: process.env.GEMINI_API_KEY,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        }
      }
    });
    const prompt = `You are a Senior Statistical Consultant and Finance Advisor at STATISTICA Offline platform.
Given this dataset summary JSON, generate a high-end academic interpretative summary writeup.
Make the layout professional, clear, using detailed bullet points, mathematical notations, and APA formatting suggestions.
Analyze actual regression parameter scores or psychometric alpha ratings if present. Do safe checks.

SUMMARY JSON:
${JSON.stringify(slim, null, 2)}

Provide your analysis in Markdown (English or Indonesian based on user preferences). Include clear subheaders like "## Visual & Distribution Core" and "## Executive Statistical Forecast".`;

    const response = await ai.models.generateContent({
      model: 'gemini-3.5-flash',
      contents: prompt,
    });

    res.json({
      narrative: `${response.text || ''}\n\n---\n\n${offlineText}`,
      source: 'gemini+offline',
    });
  } catch (err: any) {
    console.error("Gemini invocation error:", err);
    res.json({ narrative: offlineText, source: 'offline-fallback' });
  }
});

// Start dev mode or static files server
const startServer = async () => {
  if (process.env.NODE_ENV !== 'production') {
    // Development Mode with Vite Dev Middleware on Port 3000
    const viteInstance = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    
    app.use(viteInstance.middlewares);
    console.log('STATISTICA: Dev Express Server hooked with Vite middleware successfully.');
  } else {
    // Production Mode: serve pre-compiled assets from dist
    app.use(express.static(path.join(__dirname, 'dist')));
    app.get('*', (req, res) => {
      res.sendFile(path.join(__dirname, 'dist', 'index.html'));
    });
    console.log('STATISTICA: Production Express Server loaded.');
  }

  app.listen(port, () => {
    console.log(`STATISTICA Offline Analysis Tool online on http://localhost:${port}`);
  }).on('error', (err: NodeJS.ErrnoException) => {
    if (err.code === 'EADDRINUSE') {
      console.error(`\nPort ${port} sudah dipakai. Server STATISTICA mungkin sudah jalan.`);
      console.error(`  → Buka http://localhost:${port} di browser`);
      console.error(`  → Atau hentikan proses lama: netstat -ano | findstr :${port}`);
      process.exit(1);
    }
    throw err;
  });
};

startServer().catch(err => {
  console.error('Failed to initialize server instance:', err);
});
