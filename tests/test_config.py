"""
Behavior tests for config.yaml

Tests focus on real use cases:
- Config loads correctly
- All required sections exist for pipeline
- Data paths are valid
- Scoring weights are properly configured
"""

import os
import pytest
import yaml
from pathlib import Path


CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


@pytest.fixture
def config():
    """Load the config file"""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


class TestConfigLoads:
    """Behavior: Config file should load without errors"""

    def test_config_file_exists(self):
        """Config file should exist in project root"""
        assert CONFIG_PATH.exists(), f"Config not found at {CONFIG_PATH}"

    def test_config_parses_as_yaml(self, config):
        """Config should be valid YAML"""
        assert config is not None
        assert isinstance(config, dict)


class TestRequiredSections:
    """Behavior: All pipeline phases should have config sections"""

    def test_has_data_section(self, config):
        """Should have data paths configuration"""
        assert "data" in config
        assert "posts_file" in config["data"]
        assert "comments_file" in config["data"]
        assert "output_dir" in config["data"]

    def test_has_ticker_extraction_section(self, config):
        """Should have ticker extraction configuration"""
        assert "ticker_extraction" in config
        assert "min_confidence" in config["ticker_extraction"]
        assert "action_words" in config["ticker_extraction"]

    def test_has_prices_section(self, config):
        """Should have price data configuration"""
        assert "prices" in config
        assert "benchmark_ticker" in config["prices"]
        assert "forward_days" in config["prices"]

    def test_has_sentiment_section(self, config):
        """Should have sentiment classification configuration"""
        assert "sentiment" in config
        assert "model_name" in config["sentiment"]

    def test_has_first_mover_section(self, config):
        """Should have first-mover detection configuration"""
        assert "first_mover" in config
        assert "early_adopter_window_hours" in config["first_mover"]

    def test_has_aggregation_section(self, config):
        """Should have user aggregation configuration"""
        assert "aggregation" in config
        assert "min_mentions" in config["aggregation"]

    def test_has_scoring_section(self, config):
        """Should have credibility scoring configuration"""
        assert "scoring" in config
        assert "weights" in config["scoring"]


class TestDataPaths:
    """Behavior: Data file paths should be valid"""

    def test_posts_file_exists(self, config):
        """Posts file should exist at configured path"""
        path = os.path.expanduser(config["data"]["posts_file"])
        assert os.path.exists(path), f"Posts file not found: {path}"

    def test_comments_file_exists(self, config):
        """Comments file should exist at configured path"""
        path = os.path.expanduser(config["data"]["comments_file"])
        assert os.path.exists(path), f"Comments file not found: {path}"

    def test_paths_expand_tilde(self, config):
        """Paths with ~ should expand to home directory"""
        posts_path = config["data"]["posts_file"]
        expanded = os.path.expanduser(posts_path)
        assert "~" not in expanded
        assert expanded.startswith("/")


class TestScoringWeights:
    """Behavior: Scoring weights should be properly configured"""

    def test_weights_sum_to_one(self, config):
        """Scoring weights must sum to 1.0 for valid weighting"""
        weights = config["scoring"]["weights"]
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.001, f"Weights sum to {total}, should be 1.0"

    def test_all_weights_positive(self, config):
        """All weights should be positive"""
        weights = config["scoring"]["weights"]
        for name, value in weights.items():
            assert value > 0, f"Weight '{name}' is not positive: {value}"

    def test_has_expected_weight_categories(self, config):
        """Should have weights for key metrics"""
        weights = config["scoring"]["weights"]
        expected = ["mean_alpha", "win_rate", "first_mover_rate"]
        for key in expected:
            assert key in weights, f"Missing weight for '{key}'"


class TestPriceConfig:
    """Behavior: Price configuration should be sensible"""

    def test_benchmark_is_spy(self, config):
        """Should use SPY as benchmark (standard market benchmark)"""
        assert config["prices"]["benchmark_ticker"] == "SPY"

    def test_forward_days_is_reasonable(self, config):
        """Forward period should be reasonable (1-30 days)"""
        days = config["prices"]["forward_days"]
        assert 1 <= days <= 30, f"Forward days {days} seems unreasonable"
