# STATISTICA Offline Analysis Tool

STATISTICA is an offline-first desktop and web analysis workspace for tabular research data. It combines a React interface, an Express API, and a Python scientific engine for statistics, financial modeling, psychometrics, charts, and report exports.

Your uploaded datasets are processed locally. Gemini narrative enrichment is optional and only used when `GEMINI_API_KEY` is configured and the user explicitly requests AI enhancement from the interface.

## Capabilities

| Area | Features |
| --- | --- |
| Data | CSV, Excel `.xlsx` / `.xls`, workbook sheet selection, schema diagnostics |
| Statistics | Descriptives, normality, outliers, correlation, OLS, ANOVA with Tukey, t-tests, paired tests, N-Gain |
| Association | Chi-square and Cramer's V |
| Classification | Binary logistic regression |
| Psychometrics | Cronbach alpha, KMO/Bartlett, EFA scree, IRT/MIRT |
| Financial | RSI, MACD, VaR, Sharpe ratio, GARCH, ARIMA, portfolio frontier |
| Visuals | PNG export and interactive Plotly HTML charts |
| Reports | HTML and Microsoft Word `.docx` outputs |
| Narrative | Offline English/Indonesian interpretation with optional Gemini enrichment |

## Requirements

- Windows 10/11, macOS, or Linux
- Node.js 20+
- Python 3.10+
- Python scientific packages from `requirements.txt`

## Quick Start

For day-to-day Windows use, double-click:

```text
START_STATISTICA.bat
```

The launcher checks Node.js, creates `.venv-statistica`, installs Python scientific dependencies, starts the local server, and opens the browser.

Manual developer run:

```powershell
npm install
python -m pip install -r requirements.txt
npm run dev
```

Open `http://localhost:3000`.

On Windows you can also use:

```powershell
.\scripts\start-statistica.bat
```

## Configuration

Create `.env` from `.env.example` when you need optional runtime settings:

```env
PORT=3000
MAX_UPLOAD_MB=100
GEMINI_API_KEY=
APP_URL=http://localhost:3000
```

`GEMINI_API_KEY` is optional. Leave it blank for fully offline operation.

## Typical Workflow

1. Upload a CSV or Excel dataset.
2. Review the schema diagnostics and recommended analysis mapping.
3. Adjust variables for regression, ANOVA, chi-square, finance, or psychometrics.
4. Choose export DPI.
5. Run full offline analysis.
6. Review dashboard, charts, narrative, and generated reports.
7. Download `.docx`, `.html`, or full `.zip` output.

## CLI Usage

```bash
python statistica.py example_dataset.csv --output ./output
python statistica.py example_dataset.csv --diagnostics-only
python statistica.py data.csv -c config.json -o ./output
```

Example `config.json`:

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

## Scripts

```bash
npm run dev          # Express API with Vite middleware
npm run build        # Production frontend build
npm run start:prod   # Serve built frontend and API
npm run lint         # TypeScript check
npm run test:python  # Python smoke tests
```

## Python Runtime

The recommended launcher uses a project-managed environment at `.venv-statistica/`. The backend prefers this Python automatically when it exists, then falls back to system Python.

If the scientific stack looks broken, rerun `START_STATISTICA.bat`; it will repair missing dependencies without requiring users to type pip commands manually.

## Production Run

```powershell
npm run build
$env:NODE_ENV="production"
npm run start:prod
```

The production server serves `dist/` and the API on the configured port.

## Project Layout

```text
server.ts                  Express API and Vite/production server
server/                    API helper modules
src/                       React application
src_python/                Python analysis engines
tests/                     Python smoke tests
scripts/                   Windows launcher scripts
statistica.py              CLI entry point
example_dataset.csv        Demo dataset
output/                    Generated reports at runtime
uploads/                   Uploaded datasets at runtime
```

## Security Notes

- Uploads are limited by `MAX_UPLOAD_MB`.
- Only `.csv`, `.xlsx`, and `.xls` files are accepted by the web API.
- Runtime files are stored in `uploads/` and generated artifacts in `output/`.
- The API validates artifact paths before serving charts, reports, or ZIP exports.
- Python analysis is launched without shell interpolation to reduce command injection risk.

## Testing

```bash
npm run lint
npm run test:python
```

The Python smoke test runs diagnostics and a full example pipeline, then verifies that summary and report artifacts are created.

## Troubleshooting

| Issue | Fix |
| --- | --- |
| Python not found | Install Python 3.10+ and ensure it is available in PATH |
| Scientific stack missing | Run `python -m pip install -r requirements.txt` |
| Port already in use | Set `PORT` in `.env` or stop the existing process |
| Excel upload fails | Ensure `openpyxl` is installed |
| Logistic regression fails | Target column must contain exactly two classes |
| AI narrative unavailable | Configure `GEMINI_API_KEY` or use the offline narrative |

## License

Use for research, education, and professional analysis workflows. Always review statistical assumptions and validate results before publication or client delivery.
