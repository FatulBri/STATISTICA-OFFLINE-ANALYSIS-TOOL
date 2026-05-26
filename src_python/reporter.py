import os
import json
import logging
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from jinja2 import Template

logger = logging.getLogger("reporter")

def _set_cell_background(cell, fill_hex):
    """Set cell background shading."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def _set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell custom padding in dxas."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_docx_report(summary: dict, output_dir: str):
    """
    Generate an academic-style MS Word Report (.docx) in output_dir.
    Applies APA-aligned layouts, formal margins, custom header styling,
    and directly embeds PNG graphics and data summaries.
    """
    doc_path = os.path.join(output_dir, "report.docx")
    doc = docx.Document()
    
    # Page setup - APA Style Margins (1 inch or 2.54cm)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Styles
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    # Document Head
    title = doc.add_paragraph()
    title_run = title.add_run("STATISTICA Offline Analysis Report")
    title_run.font.name = 'Calibri'
    title_run.font.size = Pt(22)
    title_run.bold = True
    title_run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Deep Slate
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    meta_p = doc.add_paragraph()
    meta_p.add_run(f"Project Dataset: {summary.get('fileName', 'N/A')}\n")
    meta_p.add_run(f"Dimensions: {summary.get('rows', 0)} rows x {summary.get('columns', 0)} columns\n")
    meta_p.add_run("Generated with: STATISTICA Offline Analytical Engine\n")
    meta_p.runs[0].font.size = Pt(9.5)
    meta_p.runs[0].italic = True
    meta_p.runs[0].font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    
    doc.add_paragraph("").paragraph_format.space_after = Pt(12)
    
    # 1. Dataset Diagnostics
    h1 = doc.add_paragraph()
    h1_run = h1.add_run("1. Dataset Diagnostics & Auto-Recommendations")
    h1_run.bold = True
    h1_run.font.size = Pt(14)
    h1_run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A) # Navy Blue
    
    desc_p = doc.add_paragraph(
        f"An initial integrity review was performed on {summary.get('fileName', 'uploaded file')}. "
        f"The dataset consists of {summary.get('rows', 0)} observations tracking {summary.get('columns', 0)} structural items. "
        f"Missing cells rate was scanned at {summary.get('duplicates', 0)} total duplicated rows recorded across active columns."
    )
    desc_p.paragraph_format.line_spacing = 1.15
    desc_p.paragraph_format.space_after = Pt(8)
    
    # Recommendations bullet points
    recs = summary.get("recommendations", [])
    if recs:
        rec_title = doc.add_paragraph("Analytical Recommendations:")
        rec_title.bold = True
        rec_title.paragraph_format.space_after = Pt(2)
        for rec in recs:
            li = doc.add_paragraph(style='List Bullet')
            li.add_run(rec)
            li.paragraph_format.space_after = Pt(2)
            
    doc.add_page_break()
    
    # 2. Descriptive Core
    h2 = doc.add_paragraph()
    h2_run = h2.add_run("2. Structural Descriptives Table")
    h2_run.bold = True
    h2_run.font.size = Pt(14)
    h2_run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    
    desc_stats = summary.get("descriptive", {})
    if desc_stats:
        table = doc.add_table(rows=1, cols=7)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        headers = ["Column", "N Count", "Mean", "StdDev", "Skewness", "Kurtosis", "IQR Range"]
        hdr_cells = table.rows[0].cells
        for idx, h_text in enumerate(headers):
            hdr_cells[idx].text = h_text
            _set_cell_background(hdr_cells[idx], "1E3A8A")
            _set_cell_margins(hdr_cells[idx], top=80, bottom=80, left=100, right=100)
            p = hdr_cells[idx].paragraphs[0]
            p.runs[0].font.bold = True
            p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            p.runs[0].font.size = Pt(9.5)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        for col_name, stats_dict in desc_stats.items():
            row_cells = table.add_row().cells
            row_cells[0].text = str(col_name)
            row_cells[0].paragraphs[0].runs[0].font.bold = True
            row_cells[1].text = str(stats_dict.get("count", 0))
            row_cells[2].text = f"{stats_dict.get('mean', 0.0):.3f}"
            row_cells[3].text = f"{stats_dict.get('std', 0.0):.3f}"
            row_cells[4].text = f"{stats_dict.get('skewness', 0.0):.3f}"
            row_cells[5].text = f"{stats_dict.get('kurtosis', 0.0):.3f}"
            row_cells[6].text = f"{stats_dict.get('range', 0.0):.3f}"
            
            for cell in row_cells:
                _set_cell_margins(cell, top=60, bottom=60, left=85, right=85)
                p = cell.paragraphs[0]
                p.runs[0].font.size = Pt(9)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
        doc.add_paragraph("").paragraph_format.space_after = Pt(12)
        
    # Incorporate descriptive charts
    charts_folder = os.path.join(output_dir, "charts")
    if os.path.exists(charts_folder):
        jpgs = [f for f in os.listdir(charts_folder) if f.endswith(".png")]
        for jpg in jpgs:
            if "histogram_" in jpg or "boxplot_" in jpg or "heatmap" in jpg:
                chart_path = os.path.join(charts_folder, jpg)
                try:
                    doc.add_paragraph(f"Figure: {jpg.replace('_', ' ').replace('.png', '').upper()} distribution plot")
                    doc.add_picture(chart_path, width=Inches(4.5))
                    last_col = doc.paragraphs[-1]
                    last_col.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    last_col.paragraph_format.space_after = Pt(15)
                except Exception as ex:
                    logger.warning(f"Error appending descriptive picture {jpg}: {ex}")
                    
    # 3. Model Results & Interpretation Text
    h3 = doc.add_paragraph()
    h3_run = h3.add_run("3. Applied Inference Models (APA Formats)")
    h3_run.bold = True
    h3_run.font.size = Pt(14)
    h3_run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    
    inf_p = doc.add_paragraph(
        "STATISTICA implemented deep inferences based on columns structure configuration. "
        "Detailed testing outputs, coefficients, and parametric parameters are fully logged below."
    )
    inf_p.paragraph_format.line_spacing = 1.15
    
    # Check linear regression
    lin_reg = summary.get("linear_regression", {})
    if lin_reg and "error" not in lin_reg:
        doc.add_paragraph().add_run("OLS Linear Regression Summary").bold = True
        doc.add_paragraph(
            f"R-squared index explains {lin_reg.get('r_squared', 0.0):.4f} ({lin_reg.get('adj_r_squared', 0.0):.4f} adjusted) "
            f"of the variability in target column under F-statistic check of {lin_reg.get('f_statistic', 0.0):.3f} (p-value = {lin_reg.get('f_p_value', 0.0):.5f})."
        ).paragraph_format.space_after = Pt(6)
        
        table = doc.add_table(rows=1, cols=5)
        hdr_cells = table.rows[0].cells
        hdrs = ["Predictor Key", "Coefficient", "Std Error", "t Statistic", "P-Value"]
        for idx, h_text in enumerate(hdrs):
            hdr_cells[idx].text = h_text
            _set_cell_background(hdr_cells[idx], "3B82F6")
            p = hdr_cells[idx].paragraphs[0]
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(9.5)
            p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
        features = lin_reg.get("features", [])
        for feat in features:
            r_c = table.add_row().cells
            r_c[0].text = str(feat.get("feature"))
            r_c[1].text = f"{feat.get('coefficient', 0.0):.4f}"
            r_c[2].text = f"{feat.get('std_err', 0.0):.4f}"
            r_c[3].text = f"{feat.get('t_statistic', 0.0):.4f}"
            r_c[4].text = f"{feat.get('p_value', 0.0):.5f}"
            for c in r_c:
                c.paragraphs[0].runs[0].font.size = Pt(9)
                
        doc.add_paragraph("").paragraph_format.space_after = Pt(12)
        
    # One-Sample T-Test
    ost = summary.get("one_sample_t_test", {})
    if ost and "error" not in ost:
        doc.add_paragraph().add_run("One-Sample T-Test").bold = True
        doc.add_paragraph(
            f"Testing sample mean against population mean μ₀ = {ost.get('population_mean_tested', 0.0):.4f}. "
            f"Sample mean = {ost.get('sample_mean', 0.0):.4f}, t({ost.get('df', 0)}) = {ost.get('statistic', 0.0):.4f}, "
            f"p = {ost.get('p_value', 0.0):.5f}, Cohen's d = {ost.get('cohens_d', 0.0):.4f}. "
            f"{'Significant at α = 0.05.' if ost.get('significant') else 'Not significant at α = 0.05.'}"
        ).paragraph_format.space_after = Pt(8)

    # Independent T-Test + Mann-Whitney U side-by-side
    itt = summary.get("independent_t_test", {})
    mwu = summary.get("mann_whitney_u", {})
    if (itt and "error" not in itt) or (mwu and "error" not in mwu):
        doc.add_paragraph().add_run("Group Comparison: Parametric vs Non-Parametric").bold = True
        if itt and "error" not in itt:
            doc.add_paragraph(
                f"Independent Samples T-Test: t({itt.get('df', 0)}) = {itt.get('statistic', 0.0):.4f}, "
                f"p = {itt.get('p_value', 0.0):.5f}, Cohen's d = {itt.get('cohens_d', 0.0):.4f}. "
                f"Groups: {', '.join(itt.get('group_names', []))} (means: {', '.join(f'{m:.3f}' for m in itt.get('group_means', []))}). "
                f"{'Significant.' if itt.get('significant') else 'Not significant.'}"
            ).paragraph_format.space_after = Pt(4)
        if mwu and "error" not in mwu:
            doc.add_paragraph(
                f"Mann-Whitney U Test: U = {mwu.get('statistic', 0.0):.2f}, "
                f"p = {mwu.get('p_value', 0.0):.5f}. "
                f"Groups: {', '.join(mwu.get('group_names', []))} (medians: {', '.join(f'{m:.3f}' for m in mwu.get('group_medians', []))}). "
                f"{'Significant.' if mwu.get('significant') else 'Not significant.'}"
            ).paragraph_format.space_after = Pt(8)

    # ANOVA + Kruskal-Wallis side-by-side
    anova = summary.get("one_way_anova", {})
    kw = summary.get("kruskal_wallis", {})
    if (anova and "error" not in anova) or (kw and "error" not in kw):
        doc.add_paragraph().add_run("Multi-Group Comparison: Parametric vs Non-Parametric").bold = True
        if anova and "error" not in anova:
            doc.add_paragraph(
                f"One-Way ANOVA: F = {anova.get('f_statistic', 0.0):.4f}, "
                f"p = {anova.get('p_value', 0.0):.5f}, η² = {anova.get('eta_squared', 0.0):.4f}. "
                f"{'Significant.' if anova.get('significant') else 'Not significant.'}"
            ).paragraph_format.space_after = Pt(4)
        if kw and "error" not in kw:
            medians_str = ", ".join(f"{k}: {v:.3f}" for k, v in kw.get("group_medians", {}).items())
            doc.add_paragraph(
                f"Kruskal-Wallis H Test: H = {kw.get('statistic', 0.0):.4f}, "
                f"p = {kw.get('p_value', 0.0):.5f}. "
                f"Group medians: {medians_str}. "
                f"{'Significant.' if kw.get('significant') else 'Not significant.'}"
            ).paragraph_format.space_after = Pt(8)

    # Spearman correlation summary
    corr_sp = summary.get("correlation_spearman", {})
    if corr_sp and "error" not in corr_sp:
        doc.add_paragraph().add_run("Spearman Rank Correlation Summary").bold = True
        cols_list = corr_sp.get("columns", [])
        coeffs = corr_sp.get("coefficients", {})
        if cols_list and coeffs:
            table = doc.add_table(rows=1, cols=len(cols_list) + 1)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "Variable"
            _set_cell_background(hdr_cells[0], "6366F1")
            for idx, c in enumerate(cols_list):
                hdr_cells[idx + 1].text = c
                _set_cell_background(hdr_cells[idx + 1], "6366F1")
                p = hdr_cells[idx + 1].paragraphs[0]
                p.runs[0].font.bold = True
                p.runs[0].font.size = Pt(8)
                p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            p0 = hdr_cells[0].paragraphs[0]
            p0.runs[0].font.bold = True
            p0.runs[0].font.size = Pt(8)
            p0.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            for col_name in cols_list:
                r_cells = table.add_row().cells
                r_cells[0].text = col_name
                r_cells[0].paragraphs[0].runs[0].font.bold = True
                r_cells[0].paragraphs[0].runs[0].font.size = Pt(8)
                col_coeffs = coeffs.get(col_name, [])
                for idx, val in enumerate(col_coeffs if isinstance(col_coeffs, list) else []):
                    r_cells[idx + 1].text = f"{val:.3f}"
                    r_cells[idx + 1].paragraphs[0].runs[0].font.size = Pt(8)
            doc.add_paragraph("").paragraph_format.space_after = Pt(8)

    # Random Forest Regression & Classification
    rf_reg = summary.get("random_forest_regression", {})
    if rf_reg and "error" not in rf_reg:
        doc.add_paragraph().add_run("Random Forest Regression Model").bold = True
        doc.add_paragraph(
            f"The Random Forest regression ensemble explained {rf_reg.get('r_squared', 0.0):.4f} of the variance "
            f"with a Mean Squared Error (MSE) of {rf_reg.get('mse', 0.0):.4f} across {rf_reg.get('n_observations', 0)} observations."
        ).paragraph_format.space_after = Pt(4)
        if rf_reg.get("feature_importance"):
            top_feat = rf_reg["feature_importance"][0]["feature"]
            doc.add_paragraph(f"The most critical predictor was '{top_feat}'.")

    rf_clf = summary.get("random_forest_classification", {})
    if rf_clf and "error" not in rf_clf:
        doc.add_paragraph().add_run("Random Forest Classification Model").bold = True
        doc.add_paragraph(
            f"The Random Forest classifier achieved an overall accuracy of {rf_clf.get('accuracy', 0.0)*100.0:.2f}% "
            f"across {rf_clf.get('n_observations', 0)} observations."
        ).paragraph_format.space_after = Pt(4)
        if rf_clf.get("feature_importance"):
            top_feat = rf_clf["feature_importance"][0]["feature"]
            doc.add_paragraph(f"The most critical classification feature was '{top_feat}'.")

    kmeans = summary.get("kmeans_clustering", {})
    if kmeans and "error" not in kmeans:
        doc.add_paragraph().add_run("K-Means Clustering Analysis").bold = True
        doc.add_paragraph(
            f"Clustering partitioned the data into {kmeans.get('n_clusters')} segments across {kmeans.get('n_observations')} observations. "
            f"The clustering Silhouette Score is {kmeans.get('silhouette_score', 0.0):.4f}."
        ).paragraph_format.space_after = Pt(4)

    pca = summary.get("pca_reduction", {})
    if pca and "error" not in pca:
        doc.add_paragraph().add_run("Principal Component Analysis (PCA)").bold = True
        doc.add_paragraph(
            f"PCA successfully reduced dimensionality to {pca.get('n_components_used')} components. "
            f"The components capture {pca.get('cumulative_variance', [0])[-1]*100.0:.2f}% of the total cumulative variance in the subset."
        ).paragraph_format.space_after = Pt(4)


    # Check Psychometrics Cronbach etc
    alpha_calc = summary.get("cronbach_alpha", {})
    if alpha_calc and "error" not in alpha_calc:
        doc.add_paragraph().add_run("Psychometric Reliability Indices").bold = True
        doc.add_paragraph(
            f"Scale Consistency Alpha: {alpha_calc.get('alpha', 0.0):.4f} "
            f"classified as level '{alpha_calc.get('rating', 'Unknown')}' based on {alpha_calc.get('k_items', 0)} scale items."
        )
        
    # Check Portfolio Sharpe etc
    port_opt = summary.get("portfolio_optimization", {})
    if port_opt and "error" not in port_opt:
        doc.add_paragraph().add_run("Markowitz Portfolio Allocations Optimization").bold = True
        sharpe_weights = port_opt.get("max_sharpe", {}).get("weights", {})
        weight_str = ", ".join([f"{k}: {v*100.0:.1f}%" for k, v in sharpe_weights.items()])
        doc.add_paragraph(
            f"Max Sharpe Ratio achieved return of {port_opt.get('max_sharpe', {}).get('return', 0.0)*100.0:.2f}% "
            f"with risk indicator of {port_opt.get('max_sharpe', {}).get('risk', 0.0)*100.0:.2f}%. Optimal weighted breakdown: {weight_str}"
        )
        
    try:
        doc.save(doc_path)
        logger.info(f"DOCX Report created successfully at {doc_path}!")
    except Exception as e:
        logger.error(f"Failed to generate word presentation file: {e}")

def generate_html_report(summary: dict, output_dir: str):
    """
    Generate an interactive theme-ready glassmorphic dashboard report (.html).
    Embeds dynamic summaries, visual grids, interpretations, and interactive buttons.
    """
    html_path = os.path.join(output_dir, "report.html")
    
    # Beautiful responsive glassmorphic HTML report template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STATISTICA Premium Analytical Report</title>
    <!-- Tailwind v3 compiled link for isolated standalone offline style -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0b1020;
            color: #f1f5f9;
        }
        .glass-card {
            background: rgba(27, 35, 56, 0.45);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 1rem;
        }
    </style>
</head>
<body class="min-h-screen pb-12">
    <!-- Navbar / Header -->
    <header class="border-b border-slate-800 bg-[#0b1020]/90 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                </div>
                <div>
                    <h1 class="font-bold text-lg tracking-tight text-white">STATISTICA Report</h1>
                    <p class="text-[10px] uppercase tracking-wider text-blue-400 font-bold">Offline Analytics Node</p>
                </div>
            </div>
            <div class="flex items-center space-x-3">
                <button onclick="window.print()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition">
                    Print Report / Save PDF
                </button>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 mt-8 grid grid-cols-12 gap-8">
        <!-- Sidebar layout links -->
        <aside class="col-span-12 md:col-span-3 space-y-3">
            <div class="p-6 glass-card">
                <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Diagnostics</h3>
                <div class="space-y-3 text-sm">
                    <div class="flex justify-between">
                        <span class="text-slate-400">Total Rows:</span>
                        <span class="font-medium text-white">{{ summary.rows }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">Total Columns:</span>
                        <span class="font-medium text-white">{{ summary.columns }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">Duplicates:</span>
                        <span class="font-medium text-amber-500">{{ summary.duplicates }}</span>
                    </div>
                </div>
                <div class="mt-6 pt-6 border-t border-slate-800">
                    <p class="text-xs text-slate-400 italic">File: <span class="text-slate-200 font-semibold">{{ summary.fileName }}</span></p>
                </div>
            </div>

            <!-- Table of Contents widget -->
            <div class="glass-card p-6">
                <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Jump To:</h3>
                <ul class="space-y-2 text-xs font-medium text-slate-300">
                    <li><a href="#summary" class="hover:text-blue-500 block">1. Executive Summary</a></li>
                    <li><a href="#descriptive" class="hover:text-blue-500 block">2. Descriptive Statistics</a></li>
                    <li><a href="#models" class="hover:text-blue-500 block">3. Statistical Modeling</a></li>
                    <li><a href="#charts" class="hover:text-blue-500 block">4. Data Visualization</a></li>
                </ul>
            </div>
        </aside>

        <!-- Main widgets scroll area -->
        <div class="col-span-12 md:col-span-9 space-y-8">
            <!-- 1. EXECUTIVE SUMMARY SECTION -->
            <section id="summary" class="glass-card p-8">
                <h2 class="text-xl font-bold text-white mb-2">1. Executive Analytical Summary</h2>
                <p class="text-sm text-slate-300 leading-relaxed">
                    Based on the mathematical validation algorithms of STATISTICA, this dataset contains <span class="text-blue-400 font-semibold">{{ summary.rows }}</span> structural rows and <span class="text-blue-400 font-semibold">{{ summary.columns }}</span> analytical columns. An advanced scan of duplicate entries reported <span class="text-amber-500 font-semibold">{{ summary.duplicates }}</span> duplicates.
                </p>

                <!-- Recommendation box list -->
                <div class="mt-6 bg-slate-900/50 p-5 rounded-lg border border-slate-700/40">
                    <h3 class="text-xs font-bold uppercase text-slate-400 tracking-wider mb-3">Statistical Recommendations:</h3>
                    <ul class="space-y-2 text-xs text-slate-300">
                        {% for rec in summary.recommendations %}
                        <li class="flex items-start">
                            <span class="text-blue-500 mr-2">✦</span>
                            <span>{{ rec }}</span>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
                
                {% if summary.interpretation %}
                <div class="mt-6 border-t border-slate-800 pt-6">
                    <h3 class="text-xs font-bold uppercase text-blue-400 tracking-wider mb-2">AI Narrative Interpretation:</h3>
                    <div class="text-sm p-4 bg-blue-950/20 border-l-2 border-blue-500 rounded text-slate-200 leading-relaxed italic">
                        {{ summary.interpretation | replace('\\n', '<br>') }}
                    </div>
                </div>
                {% endif %}
            </section>

            <!-- 2. DESCRIPTIVE STATISTICS SECTION -->
            <section id="descriptive" class="glass-card p-8 overflow-hidden">
                <h2 class="text-xl font-bold text-white mb-4">2. Quantitative Descriptives Table</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs border-collapse">
                        <thead>
                            <tr class="bg-slate-800/60 text-slate-300 uppercase tracking-widest font-semibold border-b border-slate-700">
                                <th class="py-3 px-4">Variable</th>
                                <th class="py-3 px-4">Count</th>
                                <th class="py-3 px-4">Mean</th>
                                <th class="py-3 px-4">Std Dev</th>
                                <th class="py-3 px-4">Skewness</th>
                                <th class="py-3 px-4">Kurtosis</th>
                                <th class="py-3 px-4">IQR Range</th>
                            </tr>
                        </thead>
                        <tbody class="font-mono text-slate-300 divide-y divide-slate-800">
                            {% for col_name, stats in summary.descriptive.items() %}
                            <tr class="hover:bg-slate-800/30">
                                <td class="py-3 px-4 font-bold text-white font-sans">{{ col_name }}</td>
                                <td class="py-3 px-4">{{ stats.count }}</td>
                                <td class="py-3 px-4">{{ "%.4f"|format(stats.mean) }}</td>
                                <td class="py-3 px-4">{{ "%.4f"|format(stats.std) }}</td>
                                <td class="py-3 px-4">{{ "%.4f"|format(stats.skewness) }}</td>
                                <td class="py-3 px-4">{{ "%.4f"|format(stats.kurtosis) }}</td>
                                <td class="py-3 px-4">{{ "%.4f"|format(stats.range) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 3. INFERENCE MODELS -->
            <section id="models" class="glass-card p-8 space-y-6">
                <h2 class="text-xl font-bold text-white mb-2">3. Applied Computational Models</h2>
                
                <!-- Linear regression summary if exists -->
                {% if summary.linear_regression and summary.linear_regression.r_squared %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">OLS Linear Regression Analysis Summary</h3>
                    <p class="text-xs text-slate-400 mb-4 leading-relaxed">
                        The multiple linear regression fit reveals an R-Squared of <strong>{{ "%.4f"|format(summary.linear_regression.r_squared) }}</strong>, expressing substantial model variance representation.
                    </p>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="bg-slate-800/40 text-slate-300 uppercase font-semibold">
                                    <th class="py-2 px-3">Variable</th>
                                    <th class="py-2 px-3">Beta Coeff</th>
                                    <th class="py-2 px-3">Std Error</th>
                                    <th class="py-2 px-3">t value</th>
                                    <th class="py-2 px-3">Pr(&gt;|t|)</th>
                                </tr>
                            </thead>
                            <tbody class="font-mono divide-y divide-slate-800/55">
                                {% for item in summary.linear_regression.features %}
                                <tr>
                                    <td class="py-2 px-3 text-white font-sans">{{ item.feature }}</td>
                                    <td class="py-2 px-3">{{ "%.4f"|format(item.coefficient) }}</td>
                                    <td class="py-2 px-3">{{ "%.4f"|format(item.std_err) }}</td>
                                    <td class="py-2 px-3">{{ "%.4f"|format(item.t_statistic) }}</td>
                                    <td class="py-2 px-3 {% if item.significant %}text-green-400{% else %}text-slate-500{% endif %}">
                                        {{ "%.5f"|format(item.p_value) }} {% if item.significant %}* (Sig){% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% endif %}

                {% if summary.one_way_anova and summary.one_way_anova.f_statistic %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">One-Way ANOVA</h3>
                    <p class="text-xs text-slate-400 font-mono">
                        F = {{ "%.4f"|format(summary.one_way_anova.f_statistic) }},
                        p = {{ "%.5f"|format(summary.one_way_anova.p_value) }},
                        η² = {{ "%.4f"|format(summary.one_way_anova.eta_squared) }}
                    </p>
                </div>
                {% endif %}

                {% if summary.chi_square and summary.chi_square.chi2_statistic %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">Chi-Square Test of Independence</h3>
                    <p class="text-xs text-slate-400 font-mono">
                        χ² = {{ "%.4f"|format(summary.chi_square.chi2_statistic) }},
                        df = {{ summary.chi_square.dof }},
                        p = {{ "%.5f"|format(summary.chi_square.p_value) }},
                        Cramér's V = {{ "%.4f"|format(summary.chi_square.cramers_v) }}
                    </p>
                </div>
                {% endif %}

                {% if summary.logistic_regression and summary.logistic_regression.pseudo_r_squared %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">Logistic Regression</h3>
                    <p class="text-xs text-slate-400 mb-3">
                        Pseudo R² = {{ "%.4f"|format(summary.logistic_regression.pseudo_r_squared) }},
                        Accuracy = {{ "%.2f"|format(summary.logistic_regression.accuracy * 100) }}%
                    </p>
                    <table class="w-full text-left text-xs font-mono">
                        <thead><tr class="text-slate-500"><th class="py-1">Feature</th><th>Coef</th><th>p</th></tr></thead>
                        <tbody>
                        {% for item in summary.logistic_regression.features %}
                        <tr><td class="text-white">{{ item.feature }}</td><td>{{ "%.4f"|format(item.coefficient) }}</td><td>{{ "%.5f"|format(item.p_value) }}</td></tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
                </div>
                {% endif %}

                {% if summary.random_forest_regression and summary.random_forest_regression.r_squared %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">Random Forest Regression</h3>
                    <p class="text-xs text-slate-400 mb-3 font-mono">
                        R² = {{ "%.4f"|format(summary.random_forest_regression.r_squared) }},
                        MSE = {{ "%.4f"|format(summary.random_forest_regression.mse) }}
                    </p>
                    <table class="w-full text-left text-xs font-mono">
                        <thead><tr class="text-slate-500"><th class="py-1">Feature</th><th>Importance</th></tr></thead>
                        <tbody>
                        {% for item in summary.random_forest_regression.feature_importance[:5] %}
                        <tr><td class="text-white">{{ item.feature }}</td><td>{{ "%.4f"|format(item.importance) }}</td></tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endif %}

                {% if summary.random_forest_classification and summary.random_forest_classification.accuracy %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">Random Forest Classification</h3>
                    <p class="text-xs text-slate-400 mb-3 font-mono">
                        Accuracy = {{ "%.2f"|format(summary.random_forest_classification.accuracy * 100) }}%
                    </p>
                    <table class="w-full text-left text-xs font-mono">
                        <thead><tr class="text-slate-500"><th class="py-1">Feature</th><th>Importance</th></tr></thead>
                        <tbody>
                        {% for item in summary.random_forest_classification.feature_importance[:5] %}
                        <tr><td class="text-white">{{ item.feature }}</td><td>{{ "%.4f"|format(item.importance) }}</td></tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endif %}

                {% if summary.kmeans_clustering and summary.kmeans_clustering.silhouette_score is defined %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">K-Means Clustering</h3>
                    <p class="text-xs text-slate-400 mb-3 font-mono">
                        Clusters = {{ summary.kmeans_clustering.n_clusters }},
                        Silhouette Score = {{ "%.4f"|format(summary.kmeans_clustering.silhouette_score) }}
                    </p>
                    <div class="space-y-2">
                        {% for cluster in summary.kmeans_clustering.cluster_profiles %}
                        <div class="p-2 border border-slate-700 rounded bg-slate-800/20 text-xs">
                            <span class="text-white font-bold block mb-1">Cluster {{ cluster.cluster }} (N={{ cluster.size }})</span>
                            <div class="font-mono text-slate-400">
                                {% for k, v in cluster.means.items() %}
                                    <span class="inline-block mr-3">{{ k }}: <span class="text-blue-300">{{ "%.2f"|format(v) }}</span></span>
                                {% endfor %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}

                {% if summary.pca_reduction and summary.pca_reduction.n_components_used %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">Principal Component Analysis</h3>
                    <p class="text-xs text-slate-400 mb-3 font-mono">
                        Components used = {{ summary.pca_reduction.n_components_used }},
                        Cumulative Variance = {{ "%.2f"|format(summary.pca_reduction.cumulative_variance[-1] * 100) }}%
                    </p>
                </div>
                {% endif %}
                </div>

                <!-- One-Sample T-Test -->
                {% if summary.one_sample_t_test and summary.one_sample_t_test.p_value is defined %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">One-Sample T-Test</h3>
                    <p class="text-xs text-slate-400 font-mono">
                        Testing Sample Mean vs Population Mean μ₀ = {{ "%.4f"|format(summary.one_sample_t_test.population_mean_tested) }}.
                    </p>
                    <p class="text-xs text-slate-400 font-mono mt-1">
                        Sample Mean = {{ "%.4f"|format(summary.one_sample_t_test.sample_mean) }},
                        t({{ summary.one_sample_t_test.df }}) = {{ "%.4f"|format(summary.one_sample_t_test.statistic) }},
                        p = <span class="{% if summary.one_sample_t_test.significant %}text-green-400{% else %}text-slate-500{% endif %}">{{ "%.5f"|format(summary.one_sample_t_test.p_value) }}</span>,
                        Cohen's d = {{ "%.4f"|format(summary.one_sample_t_test.cohens_d) }}.
                    </p>
                </div>
                {% endif %}

                <!-- Group Comparison (Independent T-Test + Mann-Whitney U) -->
                {% if (summary.independent_t_test and summary.independent_t_test.p_value is defined) or (summary.mann_whitney_u and summary.mann_whitney_u.p_value is defined) %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-3">Group Comparison (2 Groups)</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {% if summary.independent_t_test and summary.independent_t_test.p_value is defined %}
                        <div class="p-3 bg-slate-800/20 rounded border border-slate-700/50">
                            <h4 class="text-[11px] uppercase tracking-wider text-slate-500 mb-1">Parametric: Independent T-Test</h4>
                            <p class="text-xs font-mono text-slate-300">
                                t({{ summary.independent_t_test.df }}) = {{ "%.4f"|format(summary.independent_t_test.statistic) }}<br>
                                p = <span class="{% if summary.independent_t_test.significant %}text-green-400 font-bold{% else %}text-slate-500{% endif %}">{{ "%.5f"|format(summary.independent_t_test.p_value) }}</span><br>
                                Cohen's d = {{ "%.4f"|format(summary.independent_t_test.cohens_d) }}
                            </p>
                            <p class="text-[10px] text-slate-500 mt-2">Groups: {{ summary.independent_t_test.group_names | join(' vs ') }}</p>
                        </div>
                        {% endif %}
                        
                        {% if summary.mann_whitney_u and summary.mann_whitney_u.p_value is defined %}
                        <div class="p-3 bg-slate-800/20 rounded border border-slate-700/50">
                            <h4 class="text-[11px] uppercase tracking-wider text-slate-500 mb-1">Non-Parametric: Mann-Whitney U</h4>
                            <p class="text-xs font-mono text-slate-300">
                                U = {{ "%.2f"|format(summary.mann_whitney_u.statistic) }}<br>
                                p = <span class="{% if summary.mann_whitney_u.significant %}text-green-400 font-bold{% else %}text-slate-500{% endif %}">{{ "%.5f"|format(summary.mann_whitney_u.p_value) }}</span>
                            </p>
                            <p class="text-[10px] text-slate-500 mt-2">Medians: {{ summary.mann_whitney_u.group_medians | join(' vs ') }}</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endif %}

                <!-- Multi-Group Comparison (ANOVA + Kruskal-Wallis) -->
                {% if (summary.one_way_anova and summary.one_way_anova.f_statistic is defined) or (summary.kruskal_wallis and summary.kruskal_wallis.statistic is defined) %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-3">Multi-Group Comparison</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {% if summary.one_way_anova and summary.one_way_anova.f_statistic is defined %}
                        <div class="p-3 bg-slate-800/20 rounded border border-slate-700/50">
                            <h4 class="text-[11px] uppercase tracking-wider text-slate-500 mb-1">Parametric: One-Way ANOVA</h4>
                            <p class="text-xs font-mono text-slate-300">
                                F = {{ "%.4f"|format(summary.one_way_anova.f_statistic) }}<br>
                                p = <span class="{% if summary.one_way_anova.significant %}text-green-400 font-bold{% else %}text-slate-500{% endif %}">{{ "%.5f"|format(summary.one_way_anova.p_value) }}</span><br>
                                η² = {{ "%.4f"|format(summary.one_way_anova.eta_squared) }}
                            </p>
                        </div>
                        {% endif %}
                        
                        {% if summary.kruskal_wallis and summary.kruskal_wallis.statistic is defined %}
                        <div class="p-3 bg-slate-800/20 rounded border border-slate-700/50">
                            <h4 class="text-[11px] uppercase tracking-wider text-slate-500 mb-1">Non-Parametric: Kruskal-Wallis H</h4>
                            <p class="text-xs font-mono text-slate-300">
                                H = {{ "%.4f"|format(summary.kruskal_wallis.statistic) }}<br>
                                p = <span class="{% if summary.kruskal_wallis.significant %}text-green-400 font-bold{% else %}text-slate-500{% endif %}">{{ "%.5f"|format(summary.kruskal_wallis.p_value) }}</span>
                            </p>
                            <p class="text-[10px] text-slate-500 mt-2 truncate" title="{{ summary.kruskal_wallis.groups | join(', ') }}">Groups: {{ summary.kruskal_wallis.groups | join(', ') }}</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endif %}

                <!-- Spearman Correlation -->
                {% if summary.correlation_spearman and summary.correlation_spearman.columns %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-2">Spearman Rank Correlation Summary</h3>
                    <div class="overflow-x-auto mt-4">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="text-slate-400 border-b border-slate-800">
                                    <th class="py-2 px-3 font-semibold">Variable</th>
                                    {% for col in summary.correlation_spearman.columns %}
                                    <th class="py-2 px-3 font-semibold">{{ col }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody class="font-mono divide-y divide-slate-800/55">
                                {% for row_col in summary.correlation_spearman.columns %}
                                <tr>
                                    <td class="py-2 px-3 text-white font-sans font-medium">{{ row_col }}</td>
                                    {% for val in summary.correlation_spearman.coefficients[row_col] %}
                                    <td class="py-2 px-3 {% if val >= 0.7 or val <= -0.7 %}text-indigo-400 font-bold{% elif val >= 0.4 or val <= -0.4 %}text-blue-300{% else %}text-slate-500{% endif %}">
                                        {{ "%.3f"|format(val) }}
                                    </td>
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% endif %}

                <!-- Psychometrics Cronbach if exists -->
                {% if summary.cronbach_alpha and summary.cronbach_alpha.alpha %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800 grid grid-cols-3 gap-4">
                    <div class="col-span-3">
                        <h3 class="text-sm font-semibold text-white mb-2">Psychometrics Internal Consistency Test</h3>
                    </div>
                    <div class="p-4 bg-slate-800/20 rounded-md">
                        <span class="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">Cronbach Alpha Coefficient</span>
                        <span class="text-lg font-mono font-bold text-blue-400">{{ "%.4f"|format(summary.cronbach_alpha.alpha) }}</span>
                    </div>
                    <div class="p-4 bg-slate-800/20 rounded-md">
                        <span class="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">Scale Items Reviewed</span>
                        <span class="text-lg font-mono font-bold text-white">{{ summary.cronbach_alpha.k_items }} Items</span>
                    </div>
                    <div class="p-4 bg-slate-800/20 rounded-md">
                        <span class="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">Classification Strength</span>
                        <span class="text-lg font-sans font-bold text-green-400">{{ summary.cronbach_alpha.rating }}</span>
                    </div>
                </div>
                {% endif %}

                <!-- Financial optimization Sharpe if exists -->
                {% if summary.portfolio_optimization and summary.portfolio_optimization.max_sharpe %}
                <div class="bg-slate-900/30 p-6 rounded-lg border border-slate-800">
                    <h3 class="text-sm font-semibold text-white mb-3">Portfolio Optimization Asset Weightings</h3>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="p-4 bg-blue-900/10 border border-blue-500/20 rounded-lg">
                            <span class="text-[10px] text-slate-400 block uppercase font-bold text-blue-400">Max Sharpe Allocation</span>
                            <div class="text-sm font-mono mt-1 text-slate-200">
                                Return: <strong>{{ "%.2f"|format(summary.portfolio_optimization.max_sharpe.return*100) }}%</strong><br>
                                Volatility: <strong>{{ "%.2f"|format(summary.portfolio_optimization.max_sharpe.risk*100) }}%</strong>
                            </div>
                        </div>
                        <div class="p-4 bg-indigo-900/10 border border-indigo-500/20 rounded-lg">
                            <span class="text-[10px] text-slate-400 block uppercase font-bold text-indigo-400">Min Variance Volatility Allocation</span>
                            <div class="text-sm font-mono mt-1 text-slate-200">
                                Return: <strong>{{ "%.2f"|format(summary.portfolio_optimization.min_variance.return*100) }}%</strong><br>
                                Volatility: <strong>{{ "%.2f"|format(summary.portfolio_optimization.min_variance.risk*100) }}%</strong>
                            </div>
                        </div>
                    </div>
                </div>
                {% endif %}
            </section>

            <!-- 4. VISUALIZATION ENGINE GALLERY -->
            <section id="charts" class="glass-card p-8">
                <h2 class="text-xl font-bold text-white mb-4">4. Graphics Gallery Visualizer</h2>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    {% for chart in charts %}
                    <div class="bg-slate-900/40 p-4 border border-slate-800/60 rounded-xl flex flex-col justify-between">
                        <div>
                            <span class="text-[10px] text-blue-500 font-bold uppercase tracking-widest font-mono">Static PNG Display</span>
                            <h4 class="text-xs font-semibold text-slate-200 mt-0.5 mb-3 uppercase tracking-wide">{{ chart.replace('.png', '').replace('_', ' ') }}</h4>
                        </div>
                        <div class="bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center p-2 min-h-[200px]">
                            <img src="charts/{{ chart }}" alt="{{ chart }}" class="max-h-56 hover:scale-105 transition-transform duration-300">
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
        </div>
    </main>

    <!-- Footer -->
    <footer class="max-w-7xl mx-auto px-6 mt-16 pt-6 border-t border-slate-800 text-center text-xs text-slate-500">
        <p>&copy; 2026 STATISTICA Offline Analytical Platform. Built for scientific and financial telemetry modeling.</p>
    </footer>
</body>
</html>
"""
    try:
        # Load directories contents
        charts_folder = os.path.join(output_dir, "charts")
        charts_list = []
        if os.path.exists(charts_folder):
            charts_list = [f for f in os.listdir(charts_folder) if f.endswith(".png")]
            
        t = Template(html_template)
        html_rendered = t.render(summary=summary, charts=charts_list)
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_rendered)
        logger.info(f"HTML presentation published successfully at {html_path}!")
    except Exception as e:
        logger.error(f"Failed to generate interactive HTML: {e}")
