def test_debt_index_high_complexity_and_low_intent():
    from paydown.signals import debt_index, signal_a_complexity, signal_e_intent
    complex_src = "def a():\n  if x:\n    for i in y:\n      if z:\n        return 1\n"
    simple_src = "def b():\n    return 1\n"
    signals = {
        "cognitive_complexity": signal_a_complexity(complex_src),
        "size_cyclomatic": 0.9, "churn": 0.1, "coupling": 0.1,
        "intent_coverage": signal_e_intent(complex_src),
        "ai_provenance": 0.5,
    }
    w = {"cognitive_complexity": .30, "size_cyclomatic": .20, "churn": .15,
         "coupling": .15, "intent_coverage": .10, "ai_provenance": .10}
    hi = debt_index(signals, w, {})
    low_signals = dict(signals, cognitive_complexity=0.1, intent_coverage=0.9)
    lo = debt_index(low_signals, w, {})
    assert hi > lo

def test_signal_c_churn_empty_history_no_div_by_zero(tmp_path):
    from paydown.signals import signal_c_churn
    import subprocess
    # empty repo: no commits
    res = signal_c_churn(tmp_path)
    assert isinstance(res, dict)