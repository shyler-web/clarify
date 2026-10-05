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

def test_signal_a_complexity_orders_complex_over_trivial():
    from paydown.signals import signal_a_complexity
    complex_src = "def a():\n  if x:\n    for i in y:\n      if z:\n        return 1\n"
    simple_src = "def b():\n    return 1\n"
    assert signal_a_complexity(complex_src) > signal_a_complexity(simple_src)
    assert signal_a_complexity(simple_src) >= 0.0

def test_signal_b_size_orders_long_over_short():
    from paydown.signals import signal_b_size
    long_src = "def f():\n" + "\n".join(f"    x{i} = {i}" for i in range(60)) + "\n"
    short_src = "def g():\n    return 1\n"
    assert signal_b_size(long_src) > signal_b_size(short_src)

def test_signal_e_intent_orders_documented_over_undocumented():
    from paydown.signals import signal_e_intent
    documented_src = ('def a():\n    """Docstring."""\n    return 1\n'
                      '\ndef b():\n    """Docstring."""\n    return 2\n')
    undocumented_src = "def a():\n    return 1\n\ndef b():\n    return 2\n"
    assert signal_e_intent(documented_src) > signal_e_intent(undocumented_src)
    assert signal_e_intent(documented_src) >= 0.0

def test_signal_f_provenance_sane_and_orders():
    from paydown.signals import signal_f_provenance
    high_src = "x = 1\nx = 1\nx = 1\ny = 2\n"          # duplication, no comments
    low_src = "# a comment\nx = 1\ny = 2\n"            # commented, no duplication
    assert signal_f_provenance(high_src) > signal_f_provenance(low_src)
    assert signal_f_provenance(low_src) >= 0.0

def test_signal_d_coupling_incoming_deps_score_higher(tmp_path):
    from pathlib import Path
    from paydown.repo import analyze_repo
    from paydown.signals import signal_d_coupling
    p = tmp_path / "proj"
    p.mkdir(parents=True)
    (p / "a.py").write_text("def f():\n    return 1\n")
    (p / "b.py").write_text("from a import f\n")
    (p / "c.py").write_text("def g():\n    return 2\n")
    res = signal_d_coupling(analyze_repo(p))
    a_key = str(p / "a.py")
    c_key = str(p / "c.py")
    assert res[a_key] > res[c_key]
    assert all(v >= 0.0 for v in res.values())

def test_debt_index_real_thresholds_ordering():
    from paydown.config import load_signal_weights, load_thresholds
    from paydown.signals import debt_index, signal_a_complexity, signal_e_intent
    complex_src = "def a():\n  if x:\n    for i in y:\n      if z:\n        return 1\n"
    signals = {
        "cognitive_complexity": signal_a_complexity(complex_src),
        "size_cyclomatic": 0.9, "churn": 0.1, "coupling": 0.1,
        "intent_coverage": signal_e_intent(complex_src),
        "ai_provenance": 0.5,
    }
    w = load_signal_weights()
    thr = load_thresholds()["generic"]
    hi = debt_index(signals, w, thr)
    low_signals = dict(signals, cognitive_complexity=0.1, intent_coverage=0.9)
    lo = debt_index(low_signals, w, thr)
    assert hi > lo