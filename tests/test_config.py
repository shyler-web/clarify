def test_load_signal_weights_returns_six_signals():
    from paydown.config import load_signal_weights
    w = load_signal_weights()
    assert set(w) == {"cognitive_complexity", "size_cyclomatic", "churn",
                      "coupling", "intent_coverage", "ai_provenance"}
    assert sum(w.values()) == 1.0

def test_get_env_missing_key_raises_config_error():
    import os, pytest
    from paydown.config import get_env, ConfigError
    os.environ.pop("NEVER_SET_XYZ", None)
    with pytest.raises(ConfigError):
        get_env("NEVER_SET_XYZ")