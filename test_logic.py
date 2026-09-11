from logic_engine import KnowledgeBase

def test_inference_engine():
    kb = KnowledgeBase()
    kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
    kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

    # Test 1: Deduce SafeToEngage only
    kb.clear_facts()
    kb.tell_fact('TargetVisible')
    kb.tell_fact('HasDust')
    kb.forward_chain()
    
    assert 'SafeToEngage' in kb.facts, "Failed: SafeToEngage not deduced!"
    assert 'Retreat' not in kb.facts, "Failed: Retreat falsely deduced!"
    print("Test 1 Passed.")

    # Test 2: Chained deduction leading to Retreat
    kb.clear_facts()
    kb.tell_fact('TargetVisible')
    kb.tell_fact('HasDust')
    kb.tell_fact('BloodseekerMissing')
    kb.forward_chain()
    
    assert 'SafeToEngage' in kb.facts, "Failed: SafeToEngage not deduced!"
    assert 'Retreat' in kb.facts, "Failed: Retreat not deduced!"
    print("Test 2 Passed.")

if __name__ == "__main__":
    test_inference_engine()