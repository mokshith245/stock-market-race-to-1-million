"""
Behavior tests for requirements.txt

Tests focus on real use cases:
- All required packages are importable
- Key functionality is available
"""

import pytest


class TestDataProcessingImports:
    """Behavior: Data processing packages should be importable"""

    def test_pandas_imports(self):
        """pandas is needed for data manipulation"""
        import pandas as pd
        assert hasattr(pd, 'DataFrame')

    def test_numpy_imports(self):
        """numpy is needed for numerical operations"""
        import numpy as np
        assert hasattr(np, 'array')

    def test_pyarrow_imports(self):
        """pyarrow is needed for parquet file support"""
        import pyarrow
        assert hasattr(pyarrow, 'parquet')


class TestPriceDataImports:
    """Behavior: Price data packages should be importable"""

    def test_yfinance_imports(self):
        """yfinance is needed to download stock prices"""
        import yfinance as yf
        assert hasattr(yf, 'download')


class TestNLPImports:
    """Behavior: NLP packages should be importable"""

    def test_spacy_imports(self):
        """spacy is needed for NER in ticker extraction"""
        import spacy
        assert hasattr(spacy, 'load')

    def test_transformers_imports(self):
        """transformers is needed for FinBERT sentiment"""
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        assert AutoTokenizer is not None
        assert AutoModelForSequenceClassification is not None

    def test_torch_imports(self):
        """torch is needed as transformers backend"""
        import torch
        assert hasattr(torch, 'tensor')


class TestFileHandlingImports:
    """Behavior: File handling packages should be importable"""

    def test_zstandard_imports(self):
        """zstandard is needed for .zst file decompression"""
        import zstandard
        assert hasattr(zstandard, 'ZstdDecompressor')

    def test_orjson_imports(self):
        """orjson is needed for fast JSON parsing"""
        import orjson
        assert hasattr(orjson, 'loads')

    def test_pyyaml_imports(self):
        """pyyaml is needed for config loading"""
        import yaml
        assert hasattr(yaml, 'safe_load')


class TestUtilityImports:
    """Behavior: Utility packages should be importable"""

    def test_tqdm_imports(self):
        """tqdm is needed for progress bars"""
        from tqdm import tqdm
        assert tqdm is not None

    def test_pytest_imports(self):
        """pytest is needed for testing"""
        import pytest
        assert hasattr(pytest, 'fixture')
