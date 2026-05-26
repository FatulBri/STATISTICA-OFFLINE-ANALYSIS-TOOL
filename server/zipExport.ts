import archiver from 'archiver';
import fs from 'fs';
import path from 'path';
import type { Response } from 'express';

export function streamDatasetZip(outputDir: string, datasetKey: string, res: Response): void {
  const folder = path.join(outputDir, datasetKey);
  const resolvedFolder = path.resolve(folder);
  const resolvedOutputDir = path.resolve(outputDir);
  if (resolvedFolder !== resolvedOutputDir && !resolvedFolder.startsWith(resolvedOutputDir + path.sep)) {
    res.status(403).json({ error: 'Forbidden path' });
    return;
  }

  if (!fs.existsSync(folder)) {
    res.status(404).json({ error: 'Dataset output folder not found' });
    return;
  }

  res.setHeader('Content-Type', 'application/zip');
  res.setHeader('Content-Disposition', `attachment; filename="${datasetKey}_STATISTICA.zip"`);

  const archive = archiver('zip', { zlib: { level: 6 } });
  archive.on('error', (err) => {
    console.error('ZIP archive error:', err);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Failed to build ZIP archive', details: err.message });
    }
  });

  archive.pipe(res);
  archive.directory(folder, datasetKey);
  archive.finalize();
}
