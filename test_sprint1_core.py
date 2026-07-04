# test_sprint1_core.py
import pytest
from ai.exercise_config import get_exercise_config, EXERCISE_REGISTRY

def test_exercise_config_schema():
    for ex_key, config in EXERCISE_REGISTRY.items():
        assert "id" in config, f"{ex_key} missing distinct asset ID"
        assert "landmarks" in config, f"{ex_key} missing dependency tracking"
        assert "features" in config, f"{ex_key} missing feature bindings"
        assert "predictor_type" in config, f"{ex_key} missing predictor type configuration"

def test_invalid_exercise_lookup():
    with pytest.raises(KeyError):
        get_exercise_config("INVALID_EXERCISE_NAME")

print("✅ Sprint 1 - Day 1 Core Layout Checks Passed.")