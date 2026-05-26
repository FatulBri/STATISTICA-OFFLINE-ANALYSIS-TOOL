import sys
import subprocess
import logging
import importlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] STATISTICA: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("bootstrap")

REQUIRED_MODULES = [
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("scipy", "scipy"),
    ("statsmodels", "statsmodels"),
    ("matplotlib", "matplotlib"),
    ("plotly", "plotly"),
    ("openpyxl", "openpyxl"),
    ("sklearn", "scikit-learn"),
    ("docx", "python-docx"),
    ("jinja2", "jinja2"),
    ("seaborn", "seaborn"),
    ("factor_analyzer", "factor_analyzer"),
    ("arch", "arch")
]

def check_and_install_dependencies():
    """Verify that required packages are installed and attempt to install if missing."""
    missing_packages = []
    for import_name, package_name in REQUIRED_MODULES:
        try:
            importlib.import_module(import_name)
        except ImportError:
            logger.warning(f"Required package '{package_name}' is not installed.")
            missing_packages.append(package_name)
    
    if missing_packages:
        logger.info(f"Attempting to install missing dependencies: {missing_packages}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
            logger.info("Dependencies installed successfully!")
        except Exception as e:
            logger.error(f"Failed to auto-install dependencies: {e}")
            logger.warning("Please install them manually using: pip install -r requirements.txt")
            return False
    return True
