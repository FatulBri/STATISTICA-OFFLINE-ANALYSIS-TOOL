# STATISTICA Offline Analysis Tool

STATISTICA adalah aplikasi analisis data offline untuk CSV dan Excel. Project ini menggabungkan antarmuka React, API Express, dan engine Python scientific untuk menjalankan statistik, visualisasi, analisis finansial, psikometrika, serta export laporan profesional.

Fokus utama project ini sederhana: **data tetap di komputer pengguna, analisis tetap jalan lokal, output tetap siap dipakai.**

> Cocok untuk riset kampus, skripsi/tesis, laporan operasional, analisis transaksi, eksperimen edukasi, dan workflow data tabular yang butuh hasil cepat tanpa harus upload data ke cloud.

## Kenapa Project Ini Dibuat

Banyak orang punya data Excel, tapi proses analisisnya masih lompat-lompat:

- bersihkan data manual
- pindah ke software statistik
- screenshot grafik
- tulis interpretasi manual
- susun laporan lagi

STATISTICA mencoba merapikan alur itu menjadi satu workspace lokal:

1. Upload dataset.
2. Cek struktur data.
3. Pilih mapping analisis.
4. Jalankan full offline analysis.
5. Ambil grafik, ringkasan, narasi, dan report.

## Fitur Utama

| Modul | Kemampuan |
| --- | --- |
| Data | CSV, Excel `.xlsx` / `.xls`, sheet selection, schema diagnostics |
| Statistik | Descriptive stats, normality test, outlier, correlation, OLS regression, ANOVA, Tukey, t-test, paired test, N-Gain |
| Asosiasi | Chi-square dan Cramer's V |
| Klasifikasi | Logistic regression untuk target binary |
| Psikometrika | Cronbach alpha, KMO/Bartlett, EFA scree, IRT/MIRT |
| Finansial | RSI, MACD, VaR, Sharpe ratio, GARCH, ARIMA, portfolio frontier |
| Visualisasi | Export PNG dan chart interaktif Plotly HTML |
| Report | Export HTML, Microsoft Word `.docx`, dan paket `.zip` |
| Narasi | Interpretasi offline Bahasa Indonesia/English, optional Gemini jika API key tersedia |

## Privasi Data

STATISTICA dibuat dengan pendekatan **offline-first**.

- File dataset diproses lokal.
- Upload runtime disimpan di folder `uploads/`.
- Output analisis disimpan di folder `output/`.
- Gemini hanya digunakan jika `GEMINI_API_KEY` diisi dan user memilih enrichment AI.
- Tanpa Gemini, analisis tetap berjalan offline.

## Quick Start Windows

Cara paling mudah:

```text
Double-click START_STATISTICA.bat
```

Launcher akan otomatis:

- mengecek Node.js
- membuat environment Python `.venv-statistica`
- menginstall dependency Python scientific
- menginstall dependency Node jika belum ada
- menjalankan server lokal
- membuka browser ke `http://localhost:3000`

## Quick Start Manual

```powershell
npm install
python -m pip install -r requirements.txt
npm run dev
```

Lalu buka:

```text
http://localhost:3000
```

## Alur Penggunaan

1. Upload file CSV atau Excel.
2. Tunggu schema diagnostics muncul.
3. Cek variable mapping untuk regression, ANOVA, chi-square, finance, atau psychometrics.
4. Pilih DPI export.
5. Klik **Run Full Offline Analysis**.
6. Buka tab Graphics, Statistics, Financial, Psychometrics, atau Reports.
7. Download report `.docx`, `.html`, atau paket `.zip`.

## CLI Usage

```bash
python statistica.py example_dataset.csv --output ./output
python statistica.py example_dataset.csv --diagnostics-only
python statistica.py data.csv -c config.json -o ./output
```

Contoh `config.json`:

```json
{
  "regressionTarget": "Post_Test",
  "regressionPredictors": ["Pre_Test", "Income"],
  "anovaTarget": "Post_Test",
  "anovaGroup": "Group_Factor",
  "chiSquareCol1": "Group_Factor",
  "chiSquareCol2": "Satisfaction",
  "logisticTarget": "Binary_Item1",
  "logisticFeatures": ["Income", "Pre_Test"],
  "exportDpi": 300
}
```

## Tech Stack

- React
- TypeScript
- Vite
- Express
- Python
- pandas
- NumPy
- SciPy
- statsmodels
- scikit-learn
- matplotlib
- Plotly
- python-docx

## Script Penting

```bash
npm run dev          # Jalankan Express API + Vite middleware
npm run build        # Build frontend production
npm run start:prod   # Jalankan server production
npm run lint         # TypeScript check
npm run test:python  # Smoke test Python pipeline
```

## Struktur Project

```text
server.ts                  Express API dan Vite/production server
server/                    Helper backend
src/                       React frontend
src_python/                Python analysis engine
tests/                     Smoke test Python
scripts/                   Launcher Windows
statistica.py              CLI entry point
example_dataset.csv        Dataset demo
uploads/                   File upload runtime
output/                    Hasil report runtime
```

## Deployment Note

Project ini paling cocok berjalan sebagai aplikasi lokal atau server backend penuh, karena membutuhkan:

- proses Python scientific
- upload file
- generate chart/report
- penyimpanan output runtime

Frontend bisa dihosting di Vercel, tetapi backend analyzer lebih cocok di VPS, Railway, Render, Fly.io, atau server sendiri.

## Testing

```bash
npm run lint
npm run test:python
```

Smoke test menjalankan diagnostics dan full pipeline pada dataset contoh, lalu memastikan `summary.json`, `report.html`, dan `report.docx` berhasil dibuat.

## Troubleshooting

| Masalah | Solusi |
| --- | --- |
| Python tidak terdeteksi | Jalankan `START_STATISTICA.bat` atau install Python 3.10+ |
| Dependency Python belum lengkap | Jalankan ulang `START_STATISTICA.bat` |
| Port 3000 sudah dipakai | Buka `http://localhost:3000` atau hentikan proses lama |
| Excel gagal dianalisis | Pastikan `openpyxl` terinstall |
| Logistic regression gagal | Target harus punya tepat dua kelas |
| AI narrative tidak muncul | Isi `GEMINI_API_KEY` atau gunakan narasi offline |

## Roadmap

- Packaging desktop app
- Mode production server yang lebih rapi
- Queue/background job untuk dataset besar
- Template report yang lebih formal
- Export PDF langsung dari report
- Multi-user workspace
- Storage adapter untuk S3-compatible object storage
