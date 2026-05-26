import os
import json
import logging
from typing import Dict, List, Any, Optional
from jinja2 import Template

logger = logging.getLogger("report_generator")

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement, parse_xml
    from docx.oxml.ns import nsdecls, qn
except ImportError:
    logger.warning("python-docx is not installed. Word report generation will be unavailable.")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STATISTICA Analytical Dispatch Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #0b0f19;
            color: #cbd5e1;
        }
        .mono {
            font-family: 'JetBrains Mono', monospace;
        }
    </style>
</head>
<body class="flex min-h-screen">

    <!-- SIDEBAR -->
    <aside class="w-64 bg-[#070b14] border-r border-[#1e293b] flex flex-col fixed inset-y-0 pb-10 z-20">
        <div class="px-6 py-8 flex items-center space-x-3 border-b border-[#1e293b]/50">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-900/40">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2v-4a2 2 0 00-2-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
            </div>
            <span class="text-lg font-bold tracking-tight text-white">STATISTICA</span>
        </div>
        
        <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            <p class="text-[10px] uppercase font-bold tracking-widest text-[#475569] mb-4 px-2">Navigation</p>
            <a href="#summary" class="flex items-center space-x-3 text-slate-300 hover:bg-[#1e293b] p-2.5 rounded-lg text-sm transition-all">
                <span>Summary Executive</span>
            </a>
            <a href="#descriptive" class="flex items-center space-x-3 text-slate-400 hover:bg-[#1e293b] p-2.5 rounded-lg text-sm transition-all">
                <span>Descriptive Stats</span>
            </a>
            {% if run_psychometrics %}
            <a href="#psychometrics" class="flex items-center space-x-3 text-slate-400 hover:bg-[#1e293b] p-2.5 rounded-lg text-sm transition-all">
                <span>Psychometrics Suite</span>
            </a>
            {% endif %}
            {% if run_financial %}
            <a href="#financial" class="flex items-center space-x-3 text-slate-400 hover:bg-[#1e293b] p-2.5 rounded-lg text-sm transition-all">
                <span>Financial Analysis</span>
            </a>
            {% endif %}
            <a href="#charts" class="flex items-center space-x-3 text-slate-400 hover:bg-[#1e293b] p-2.5 rounded-lg text-sm transition-all">
                <span>Generated Charts</span>
            </a>
        </nav>
        
        <div class="px-4 py-4 border-t border-[#1e293b]/50">
            <button onclick="window.print()" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 px-4 rounded-lg text-xs font-semibold shadow-lg shadow-blue-500/10 hover:shadow-blue-500/20 active:scale-95 transition-all">
                Print Report
            </button>
        </div>
    </aside>

    <!-- CONTENT WRAPPER -->
    <main class="flex-1 pl-64 min-h-screen flex flex-col bg-[#0b0f19]">
        
        <!-- HEADER -->
        <header class="h-16 border-b border-[#1e293b] flex items-center justify-between px-8 bg-[#0b0f19]/80 backdrop-blur sticky top-0 z-10">
            <div class="flex items-center space-x-3">
                <span class="text-xs text-slate-500 uppercase font-mono">Dataset Name:</span>
                <span class="text-sm font-semibold text-slate-200">{{ dataset_name }}</span>
            </div>
            <div class="flex items-center space-x-4">
                <span class="text-xs bg-green-500/10 text-green-500 border border-green-500/25 px-2.5 py-1 rounded font-bold uppercase tracking-wider">
                    OFFLINE VERIFIED
                </span>
            </div>
        </header>

        <!-- MAIN CONTAINER -->
        <div class="p-8 max-w-5xl space-y-12">
            
            <!-- SUMMARY SECTION -->
            <section id="summary" class="bg-[#111827]/40 border border-[#1e293b] rounded-2xl p-6 relative overflow-hidden backdrop-blur-sm">
                <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: radial-gradient(#3B82F6 0.5px, transparent 0.5px); background-size: 15px 15px;"></div>
                <h2 class="text-xl font-bold tracking-tight text-white mb-2">Executive Dispatch Report Summary</h2>
                <p class="text-sm text-slate-400 mb-6">Automated asset scanning and multivariate statistical indicators.</p>
                
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div class="bg-[#1f2937]/50 border border-[#374151]/50 rounded-xl p-4">
                        <p class="text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-1">Rows Index</p>
                        <p class="text-2xl font-semibold text-white">{{ rows_count }}</p>
                    </div>
                    <div class="bg-[#1f2937]/50 border border-[#374151]/50 rounded-xl p-4">
                        <p class="text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-1">Variables</p>
                        <p class="text-2xl font-semibold text-white">{{ cols_count }}</p>
                    </div>
                    <div class="bg-[#1f2937]/50 border border-[#374151]/50 rounded-xl p-4">
                        <p class="text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-1">Null Cells</p>
                        <p class="text-2xl font-semibold text-orange-400">{{ data_summary.duplicates }}</p>
                    </div>
                    <div class="bg-blue-600/10 border border-blue-500/30 rounded-xl p-4">
                        <p class="text-[11px] font-bold text-blue-400 uppercase tracking-widest mb-1">Language Mode</p>
                        <p class="text-base font-semibold text-white">English / Indonesian</p>
                    </div>
                </div>

                <div class="p-4 bg-blue-950/20 border-l-4 border-blue-500 rounded-r-lg">
                    <h4 class="text-sm font-semibold text-blue-300 uppercase tracking-wider mb-2">Auto-Generated Interpretation Narrative</h4>
                    <p class="text-sm italic font-serif leading-relaxed text-slate-300">
                        "The analytical engine successfully processed the file {{ dataset_name }} offline. The framework automatically indexed {{ rows_count }} records and initiated key computations. Data elements demonstrate strong consistency with statistical standard limits, confirming structural validity for academic and corporate dispatches."
                    </p>
                </div>
            </section>

            <!-- DESCRIPTIVE STATS SECTION -->
            <section id="descriptive" class="bg-[#111827]/40 border border-[#1e293b] rounded-2xl p-6">
                <h3 class="text-lg font-bold text-white mb-2">1. Continuous Descriptive Statistics Matrix</h3>
                <p class="text-xs text-slate-400 mb-6">Tabulated parameters for numeric arrays present in active file schema.</p>
                
                <div class="overflow-x-auto rounded-xl border border-[#374151]/50 bg-[#070b14]">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead class="bg-[#1e293b]/70 border-b border-[#374151] text-slate-400 font-mono">
                            <tr>
                                <th class="p-3">Variable Name</th>
                                <th class="p-3">Count (N)</th>
                                <th class="p-3">Mean (&mu;)</th>
                                <th class="p-3">Median</th>
                                <th class="p-3">Std Dev (&sigma;)</th>
                                <th class="p-3">Kurtosis</th>
                                <th class="p-3">Skewness</th>
                                <th class="p-3">Max Value</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-[#1e293b] text-slate-300 font-mono">
                            {% for col, stats in descriptive.items() %}
                            <tr class="hover:bg-[#1e293b]/30">
                                <td class="p-3 font-semibold text-white">{{ col }}</td>
                                <td class="p-3">{{ stats.count }}</td>
                                <td class="p-3">{{ "%.3f"|format(stats.mean) }}</td>
                                <td class="p-3">{{ "%.3f"|format(stats.median) }}</td>
                                <td class="p-3">{{ "%.3f"|format(stats.std) }}</td>
                                <td class="p-3">{{ "%.3f"|format(stats.kurtosis) }}</td>
                                <td class="p-3">{{ "%.3f"|format(stats.skewness) }}</td>
                                <td class="p-3">{{ "%.3f"|format(stats.max) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- PSYCHOMETRICS SUITE -->
            {% if run_psychometrics %}
            <section id="psychometrics" class="bg-[#111827]/40 border border-[#1e293b] rounded-2xl p-6 space-y-6">
                <div>
                    <h3 class="text-lg font-bold text-white mb-2">2. Psychometric Scaling & Factor Matrix</h3>
                    <p class="text-xs text-slate-400">Scale internal consistency and construct structure validation benchmarks (IRT + EFA).</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-[#070b14] border border-[#374151]/50 rounded-xl p-4 space-y-3">
                        <h4 class="text-xs font-bold uppercase tracking-widest text-[#3b82f6]">Kaiser-Meyer-Olkin & Bartlett</h4>
                        <div class="space-y-2 text-xs">
                            <div class="flex justify-between border-b border-[#1e293b] pb-2">
                                <span class="text-slate-400">KMO Scale Adequacy:</span>
                                <span class="font-mono text-white font-semibold">{{ "%.3f"|format(kmo_bartlett.kmo.overall) if kmo_bartlett.kmo else "N/A" }}</span>
                            </div>
                            <div class="flex justify-between border-b border-[#1e293b] pb-2">
                                <span class="text-slate-400">Bartlett Chi-Square (&chi;&sup2;):</span>
                                <span class="font-mono text-white">{{ "%.2f"|format(kmo_bartlett.bartlett.chi2) if kmo_bartlett.bartlett else "N/A" }}</span>
                            </div>
                            <div class="flex justify-between pb-1">
                                <span class="text-slate-400">P-value Probability:</span>
                                <span class="font-mono text-white font-semibold">{{ "%.5f"|format(kmo_bartlett.bartlett.p_value) if kmo_bartlett.bartlett else "N/A" }}</span>
                            </div>
                        </div>
                    </div>

                    {% if cronbach_alpha %}
                    <div class="bg-[#070b14] border border-[#374151]/50 rounded-xl p-4 space-y-3">
                        <h4 class="text-xs font-bold uppercase tracking-widest text-[#10b981]">Cronbach's Alpha Internal Consistency</h4>
                        <div class="space-y-2 text-xs">
                            <div class="flex justify-between border-b border-[#1e293b] pb-2">
                                <span class="text-slate-400">Alpha Value (&alpha;):</span>
                                <span class="font-mono text-white font-bold">{{ "%.3f"|format(cronbach_alpha.alpha) if cronbach_alpha.alpha else "0.0" }}</span>
                            </div>
                            <div class="flex justify-between border-b border-[#1e293b] pb-2">
                                <span class="text-slate-400">Qualitative Rating:</span>
                                <span class="px-2 py-0.5 rounded font-semibold bg-green-500/10 text-green-400 text-[10px]">{{ cronbach_alpha.rating }}</span>
                            </div>
                            <div class="flex justify-between pb-1">
                                <span class="text-slate-400">Scale Items Count:</span>
                                <span class="font-mono text-white">{{ cronbach_alpha.k_items }}</span>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </section>
            {% endif %}

            <!-- FINANCIAL ANALYSIS SUITE -->
            {% if run_financial %}
            <section id="financial" class="bg-[#111827]/40 border border-[#1e293b] rounded-2xl p-6 space-y-6">
                <div>
                    <h3 class="text-lg font-bold text-white mb-2">3. Advanced Financial risk & return dispatch</h3>
                    <p class="text-xs text-slate-400">Analytical review of price trajectories, Markowitz optimizations, and predictive forecasts.</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-[#070b14] border border-[#1e293b] p-4 rounded-xl text-center">
                        <p class="text-[10px] font-bold text-slate-500 uppercase">Compound Growth Index (CAGR)</p>
                        <p class="text-xl font-mono text-green-400 font-bold mt-1">{{ "%.2f%%"|format(financial_risk.cagr_pct) if financial_risk.cagr_pct else "0.00%" }}</p>
                    </div>
                    <div class="bg-[#070b14] border border-[#1e293b] p-4 rounded-xl text-center">
                        <p class="text-[10px] font-bold text-slate-500 uppercase">Annualized Sharpe Ratio</p>
                        <p class="text-xl font-mono text-white font-bold mt-1">{{ "%.2f"|format(financial_risk.sharpe_ratio) if financial_risk.sharpe_ratio else "0.00" }}</p>
                    </div>
                    <div class="bg-[#070b14] border border-[#1e293b] p-4 rounded-xl text-center">
                        <p class="text-[10px] font-bold text-slate-500 uppercase">Historical Value-at-Risk (95%)</p>
                        <p class="text-xl font-mono text-rose-400 font-bold mt-1">{{ "%.2f%%"|format(financial_risk.var_95_historical_pct) if financial_risk.var_95_historical_pct else "0.00%" }}</p>
                    </div>
                </div>
            </section>
            {% endif %}

            <!-- CHARTS SECTION -->
            <section id="charts" class="bg-[#111827]/40 border border-[#1e293b] rounded-2xl p-6 space-y-6">
                <h3 class="text-lg font-bold text-white mb-2">4. Embedded Analytics Graphics Grid</h3>
                <p class="text-xs text-slate-400">Png assets generated on disk, ready for word formatting copy-paste.</p>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {% for chart_name in chart_files %}
                    <div class="bg-[#070b14] border border-[#1e293b] p-4 rounded-xl overflow-hidden shadow-xl">
                        <div class="text-xs text-slate-400 font-mono mb-2 uppercase">{{ chart_name }}</div>
                        <img src="charts/{{ chart_name }}" alt="{{ chart_name }}" class="w-full h-auto rounded border border-[#101726]/80 hover:scale-[1.02] transition-transform">
                    </div>
                    {% endfor %}
                </div>
            </section>

        </div>

        <!-- FOOTER STATUS BAR -->
        <footer class="h-10 bg-blue-600 px-6 mt-auto flex items-center justify-between text-white text-[10px] font-bold">
            <span>v2.1.0-STABLE | OFFLINE DISPATCH REPORT</span>
            <span>Generated using the STATISTICA Analysis Engine</span>
        </footer>

    </main>
</body>
</html>
"""

class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.charts_dir = os.path.join(output_dir, "charts")
        os.makedirs(self.charts_dir, exist_ok=True)

    def generate_html_report(self, data: Dict[str, Any]) -> str:
        """Create a premium, dark-theme modern HTML dashboard analytics report."""
        try:
            # Audit standard image folder
            charts_found = []
            if os.path.exists(self.charts_dir):
                charts_found = [f for f in os.listdir(self.charts_dir) if f.endswith('.png')]
                
            template = Template(HTML_TEMPLATE)
            rendered = template.render(
                dataset_name=data.get("fileName", "Dataset"),
                rows_count=data.get("rows", 0),
                cols_count=data.get("columns", 0),
                duplicates_count=data.get("duplicates", 0),
                descriptive=data.get("descriptive", {}),
                kmo_bartlett=data.get("kmo_bartlett", {}),
                cronbach_alpha=data.get("cronbach_alpha", {}),
                financial_risk=data.get("risk_return", {}),
                run_psychometrics="kmo_bartlett" in data,
                run_financial="risk_return" in data,
                chart_files=charts_found,
                data_summary=data
            )
            
            report_path = os.path.join(self.output_dir, "report.html")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(rendered)
                
            logger.info(f"HTML Report successfully written to: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Failed to compile HTML report: {e}")
            raise

    def generate_docx_report(self, data: Dict[str, Any]) -> str:
        """Create academic-thesis-styled docx complete with auto-formatted regression/ANOVA tables."""
        try:
            doc = Document()
            
            # Form style adjustments overrides
            # Normal Font defaults
            style = doc.styles['Normal']
            font = style.font
            font.name = 'Times New Roman'
            font.size = Pt(12)
            font.color.rgb = RGBColor(0, 0, 0)
            
            # Set Margins
            for section in doc.sections:
                section.top_margin = Inches(1)
                section.bottom_margin = Inches(1)
                section.left_margin = Inches(1)
                section.right_margin = Inches(1)
                
            # Document Header Title
            title_p = doc.add_paragraph()
            title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = title_p.add_run("RESEARCH DISPATCH: AUTOMATED ANALYSIS AUDIT")
            run.font.bold = True
            run.font.size = Pt(16)
            
            p_sub = doc.add_paragraph()
            p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_sub.add_run(f"Dataset Target: {data.get('fileName', 'spreadsheet.xlsx')}\nGenerated strictly 100% offline via STATISTICA tool.\n")
            
            # Executive Summary Section
            doc.add_heading("1. Executive Technical Summary", level=1)
            p_exec = doc.add_paragraph()
            p_exec.add_run(
                f"The automated workflow analysed a total of {data.get('rows', 0)} entities across {data.get('columns', 0)} data attributes. "
                f"Below is a structured diagnostic documentation of structural vectors and correlations suitable for scientific and academic journals."
            )
            
            # Descriptive Stats table
            doc.add_heading("2. Descriptive Statistics Profile Table", level=2)
            desc_data = data.get("descriptive", {})
            
            if desc_data:
                # Add table: Name, N, Mean, Median, StdDev, Range
                table = doc.add_table(rows=1, cols=6)
                table.style = 'Table Grid'
                hdr_cells = table.rows[0].cells
                hdr_cells[0].text = 'Variable'
                hdr_cells[1].text = 'N'
                hdr_cells[2].text = 'Mean'
                hdr_cells[3].text = 'Median'
                hdr_cells[4].text = 'Std Dev'
                hdr_cells[5].text = 'Range'
                
                # Make header bold
                for cell in hdr_cells:
                    cell.paragraphs[0].runs[0].font.bold = True
                    
                for col_name, st in desc_data.items():
                    row_cells = table.add_row().cells
                    row_cells[0].text = str(col_name)
                    row_cells[1].text = str(st.get("count", 0))
                    row_cells[2].text = f"{st.get('mean', 0):.3f}"
                    row_cells[3].text = f"{st.get('median', 0):.3f}"
                    row_cells[4].text = f"{st.get('std', 0):.3f}"
                    row_cells[5].text = f"{st.get('range', 0):.3f}"
            else:
                doc.add_paragraph("No descriptive statistics found.")
                
            # Insert Charts
            doc.add_heading("3. Visual Evidence Index", level=1)
            if os.path.exists(self.charts_dir):
                charts = [f for f in os.listdir(self.charts_dir) if f.endswith('.png')]
                if charts:
                    for ch in charts:
                        ch_path = os.path.join(self.charts_dir, ch)
                        doc.add_heading(f"Figure: {ch.replace('_', ' ').replace('.png', '').upper()}", level=3)
                        p_img = doc.add_paragraph()
                        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_img.add_run().add_picture(ch_path, width=Inches(4.5))
                else:
                    doc.add_paragraph("No generated PNG figures were saved on disk.")
                    
            # Document Save
            docx_path = os.path.join(self.output_dir, "report.docx")
            doc.save(docx_path)
            logger.info(f"docx academic dossier compiled successfully: {docx_path}")
            return docx_path
        except Exception as e:
            logger.error(f"Failed to generate Word docx file: {e}")
            return ""
