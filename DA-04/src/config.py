"""
src/config.py
=============
Configuration loader for the Financial Analytics and Risk Reporting System.

Loads config.yaml and metric_definitions.yaml using PyYAML, provides a typed
Config dataclass, sets up logging, and exposes helper path functions.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"
METRIC_DEFINITIONS_PATH = PROJECT_ROOT / "config" / "metric_definitions.yaml"
LOG_DIR = PROJECT_ROOT / "logs"


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Configure root logger with console (and optional file) handlers.

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional absolute path to a log file.

    Returns:
        Configured root logger.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    else:
        handlers.append(
            logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8")
        )

    logging.basicConfig(level=numeric_level, format=fmt, datefmt=datefmt, handlers=handlers)
    return logging.getLogger(__name__)


logger = setup_logging()


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class DatabaseConfig:
    type: str = "sqlite"
    path: str = "data/curated/financial_analytics.db"


@dataclass
class DataConfig:
    raw_path: str = "data/raw"
    staging_path: str = "data/staging"
    curated_path: str = "data/curated"
    output_path: str = "data/outputs"


@dataclass
class SyntheticConfig:
    n_months: int = 24
    start_date: str = "2024-01-01"
    regions: List[str] = field(default_factory=lambda: ["North", "South", "East", "West", "Central"])
    products: List[str] = field(
        default_factory=lambda: [
            "Personal Loans", "Auto Loans", "Mortgages", "Credit Cards", "Business Loans"
        ]
    )
    departments: List[str] = field(
        default_factory=lambda: [
            "Sales", "Operations", "Technology", "Finance", "Marketing", "HR", "Risk"
        ]
    )
    n_loan_records: int = 10000


@dataclass
class ScorecardModelConfig:
    base_score: int = 600
    base_odds: int = 50
    pdo: int = 20


@dataclass
class ModelConfig:
    test_size: float = 0.3
    random_state: int = 42
    scorecard: ScorecardModelConfig = field(default_factory=ScorecardModelConfig)


@dataclass
class ReportingConfig:
    board_pack_output: str = "reports/monthly_board_pack"
    financial_report_output: str = "reports/financial_report"


@dataclass
class ProjectConfig:
    name: str = "Financial Analytics and Risk Reporting System"
    version: str = "1.0.0"
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"


@dataclass
class Config:
    """Top-level typed configuration object."""
    project: ProjectConfig = field(default_factory=ProjectConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    data: DataConfig = field(default_factory=DataConfig)
    synthetic: SyntheticConfig = field(default_factory=SyntheticConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    metrics: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------
def _load_yaml(path: Path) -> Dict[str, Any]:
    """Read and parse a YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the file cannot be parsed.
    """
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(
    config_path: Optional[Path] = None,
    metric_path: Optional[Path] = None,
) -> Config:
    """Load and validate the application configuration.

    Args:
        config_path: Override path to config.yaml.
        metric_path: Override path to metric_definitions.yaml.

    Returns:
        Populated Config dataclass.
    """
    cfg_path = config_path or CONFIG_PATH
    met_path = metric_path or METRIC_DEFINITIONS_PATH

    raw_cfg = _load_yaml(cfg_path)
    logger.info("Loaded config from %s", cfg_path)

    metric_defs: Dict[str, Any] = {}
    if met_path.exists():
        raw_metrics = _load_yaml(met_path)
        metric_defs = raw_metrics.get("metrics", {})
        logger.info("Loaded %d metric definitions from %s", len(metric_defs), met_path)
    else:
        logger.warning("Metric definitions file not found: %s", met_path)

    # --- Project ---
    proj_raw = raw_cfg.get("project", {})
    project = ProjectConfig(
        name=proj_raw.get("name", ProjectConfig.name),
        version=proj_raw.get("version", ProjectConfig.version),
        start_date=proj_raw.get("start_date", ProjectConfig.start_date),
        end_date=proj_raw.get("end_date", ProjectConfig.end_date),
    )

    # --- Database ---
    db_raw = raw_cfg.get("database", {})
    database = DatabaseConfig(
        type=db_raw.get("type", "sqlite"),
        path=db_raw.get("path", "data/curated/financial_analytics.db"),
    )

    # --- Data ---
    data_raw = raw_cfg.get("data", {})
    data = DataConfig(
        raw_path=data_raw.get("raw_path", "data/raw"),
        staging_path=data_raw.get("staging_path", "data/staging"),
        curated_path=data_raw.get("curated_path", "data/curated"),
        output_path=data_raw.get("output_path", "data/outputs"),
    )

    # --- Synthetic ---
    syn_raw = raw_cfg.get("synthetic", {})
    synthetic = SyntheticConfig(
        n_months=syn_raw.get("n_months", 24),
        start_date=syn_raw.get("start_date", "2024-01-01"),
        regions=syn_raw.get("regions", SyntheticConfig.__dataclass_fields__["regions"].default_factory()),
        products=syn_raw.get("products", SyntheticConfig.__dataclass_fields__["products"].default_factory()),
        departments=syn_raw.get("departments", SyntheticConfig.__dataclass_fields__["departments"].default_factory()),
        n_loan_records=syn_raw.get("n_loan_records", 10000),
    )

    # --- Model ---
    mod_raw = raw_cfg.get("model", {})
    sc_raw = mod_raw.get("scorecard", {})
    scorecard = ScorecardModelConfig(
        base_score=sc_raw.get("base_score", 600),
        base_odds=sc_raw.get("base_odds", 50),
        pdo=sc_raw.get("pdo", 20),
    )
    model = ModelConfig(
        test_size=mod_raw.get("test_size", 0.3),
        random_state=mod_raw.get("random_state", 42),
        scorecard=scorecard,
    )

    # --- Reporting ---
    rep_raw = raw_cfg.get("reporting", {})
    reporting = ReportingConfig(
        board_pack_output=rep_raw.get("board_pack_output", "reports/monthly_board_pack"),
        financial_report_output=rep_raw.get("financial_report_output", "reports/financial_report"),
    )

    return Config(
        project=project,
        database=database,
        data=data,
        synthetic=synthetic,
        model=model,
        reporting=reporting,
        metrics=metric_defs,
    )


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def get_db_path(cfg: Optional[Config] = None) -> Path:
    """Return absolute path to the SQLite database file.

    Args:
        cfg: Config object. If None, loads from default config.yaml.

    Returns:
        Absolute Path to the database file.
    """
    if cfg is None:
        cfg = load_config()
    db_path = PROJECT_ROOT / cfg.database.path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_data_path(layer: str, cfg: Optional[Config] = None) -> Path:
    """Return absolute path for a data layer directory.

    Args:
        layer: One of 'raw', 'staging', 'curated', 'output'.
        cfg: Config object. If None, loads from default config.yaml.

    Returns:
        Absolute Path to the requested data directory.

    Raises:
        ValueError: If the layer name is not recognised.
    """
    if cfg is None:
        cfg = load_config()

    layer_map = {
        "raw": cfg.data.raw_path,
        "staging": cfg.data.staging_path,
        "curated": cfg.data.curated_path,
        "output": cfg.data.output_path,
    }
    if layer not in layer_map:
        raise ValueError(f"Unknown data layer '{layer}'. Choose from: {list(layer_map)}")

    path = PROJECT_ROOT / layer_map[layer]
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_path(cfg: Optional[Config] = None) -> Path:
    """Return absolute path to the data/outputs directory.

    Args:
        cfg: Config object. If None, loads from default config.yaml.

    Returns:
        Absolute Path to the outputs directory.
    """
    return get_data_path("output", cfg)


def get_report_path(report_type: str = "financial", cfg: Optional[Config] = None) -> Path:
    """Return absolute path for a reporting output directory.

    Args:
        report_type: 'board_pack' or 'financial'.
        cfg: Config object. If None, loads from default config.yaml.

    Returns:
        Absolute Path to the report directory.
    """
    if cfg is None:
        cfg = load_config()
    if report_type == "board_pack":
        path = PROJECT_ROOT / cfg.reporting.board_pack_output
    else:
        path = PROJECT_ROOT / cfg.reporting.financial_report_output
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_metric_definition(metric_name: str, cfg: Optional[Config] = None) -> Dict[str, Any]:
    """Return the definition dictionary for a named metric.

    Args:
        metric_name: Snake-case metric key (e.g. 'gross_margin').
        cfg: Config object. If None, loads from default config.yaml.

    Returns:
        Metric definition dictionary, or empty dict if not found.
    """
    if cfg is None:
        cfg = load_config()
    return cfg.metrics.get(metric_name, {})


# ---------------------------------------------------------------------------
# Module-level singleton (lazy)
# ---------------------------------------------------------------------------
_config_singleton: Optional[Config] = None


def get_config() -> Config:
    """Return the module-level singleton Config, loading it on first call."""
    global _config_singleton
    if _config_singleton is None:
        _config_singleton = load_config()
    return _config_singleton
