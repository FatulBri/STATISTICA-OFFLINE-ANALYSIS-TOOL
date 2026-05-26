import { execFile, execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

type PythonCandidate = {
  file: string;
  args: string[];
  label: string;
};

let cachedPythonCommand: string | null | undefined;

const PROJECT_ROOT = path.resolve(process.cwd());

function localPythonCandidates(): PythonCandidate[] {
  const candidates: PythonCandidate[] = [];

  if (process.env.STATISTICA_PYTHON) {
    candidates.push({
      file: process.env.STATISTICA_PYTHON,
      args: [],
      label: process.env.STATISTICA_PYTHON,
    });
  }

  if (process.platform === 'win32') {
    candidates.push(
      {
        file: path.join(PROJECT_ROOT, '.venv-statistica', 'Scripts', 'python.exe'),
        args: [],
        label: path.join(PROJECT_ROOT, '.venv-statistica', 'Scripts', 'python.exe'),
      },
      { file: 'python', args: [], label: 'python' },
      { file: 'python3', args: [], label: 'python3' },
      { file: 'py', args: ['-3'], label: 'py -3' },
    );
  } else {
    candidates.push(
      {
        file: path.join(PROJECT_ROOT, '.venv-statistica', 'bin', 'python'),
        args: [],
        label: path.join(PROJECT_ROOT, '.venv-statistica', 'bin', 'python'),
      },
      { file: 'python3', args: [], label: 'python3' },
      { file: 'python', args: [], label: 'python' },
    );
  }

  return candidates;
}

function candidateExists(candidate: PythonCandidate): boolean {
  return candidate.file.includes(path.sep) ? fs.existsSync(candidate.file) : true;
}

function candidateFromLabel(label: string): PythonCandidate {
  const exact = localPythonCandidates().find((candidate) => candidate.label === label);
  if (exact) return exact;
  if (label === 'py -3') return { file: 'py', args: ['-3'], label };
  return { file: label, args: [], label };
}

export function resolvePythonCommand(): string | null {
  if (cachedPythonCommand !== undefined) {
    return cachedPythonCommand;
  }

  for (const candidate of localPythonCandidates()) {
    if (!candidateExists(candidate)) continue;
    try {
      execFileSync(candidate.file, [...candidate.args, '--version'], {
        stdio: 'ignore',
        timeout: 8000,
        windowsHide: true,
      });
      cachedPythonCommand = candidate.label;
      return candidate.label;
    } catch {
      /* try next */
    }
  }

  cachedPythonCommand = null;
  return null;
}

export function checkPythonScientificStack(): boolean {
  const py = resolvePythonCommand();
  if (!py) return false;
  const candidate = candidateFromLabel(py);
  try {
    execFileSync(
      candidate.file,
      [
        ...candidate.args,
        '-c',
        'import pandas, numpy, scipy, statsmodels, matplotlib, plotly, openpyxl',
      ],
      {
        stdio: 'ignore',
        timeout: 15000,
        windowsHide: true,
      },
    );
    return true;
  } catch {
    return false;
  }
}

export function quoteShellArg(value: string): string {
  return `"${value.replace(/"/g, '')}"`;
}

export function buildStatisticaCommand(extraArgs: string[]): string | null {
  const py = resolvePythonCommand();
  if (!py) return null;
  return `${py} ${extraArgs.join(' ')}`;
}

export function runStatistica(
  scriptPath: string,
  datasetPath: string,
  options: {
    outputDir?: string;
    diagnosticsOnly?: boolean;
    sheet?: string;
    configPath?: string;
  },
  callback: (error: Error | null, stdout: string, stderr: string) => void
): void {
  const py = resolvePythonCommand();
  if (!py) {
    callback(new Error('Python tidak ditemukan. Pasang Python 3 dan jalankan: pip install -r requirements.txt'), '', '');
    return;
  }

  const invocation = candidateFromLabel(py);
  const args = [
    ...invocation.args,
    scriptPath,
    datasetPath,
  ];

  if (options.outputDir) {
    args.push('--output', options.outputDir);
  }
  if (options.diagnosticsOnly) {
    args.push('--diagnostics-only');
  }
  if (options.sheet) {
    args.push('--sheet', options.sheet);
  }
  if (options.configPath) {
    args.push('--config', options.configPath);
  }

  execFile(invocation.file, args, { maxBuffer: 30 * 1024 * 1024, windowsHide: true }, (error, stdout, stderr) => {
    callback(error, stdout?.toString() ?? '', stderr?.toString() ?? '');
  });
}

export function parseMarker(stdout: string, marker: string): string | null {
  const token = `${marker}|`;
  const idx = stdout.indexOf(token);
  if (idx === -1) return null;
  return stdout.substring(idx + token.length).trim().split('\n')[0].trim();
}

export function isPathInsideDir(targetPath: string, baseDir: string): boolean {
  const resolved = path.resolve(targetPath);
  const base = path.resolve(baseDir);
  return resolved === base || resolved.startsWith(base + path.sep);
}
