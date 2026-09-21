# quality-checks

    import quality_checks as Q
    problems  = Q.price_check(text, Q.offer_block(bank_text, offer), offer)
    problems += Q.unfilled_check(text)
    problems += Q.read_check_block(check_step_output)
    Q.hold("copy", problems, run_dir)        # writes check.json; raises Q.Held if anything failed

`python3 test_quality_checks.py` — 6 tests. See CLAUDE.md.
