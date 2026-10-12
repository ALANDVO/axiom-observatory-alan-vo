from app.services.ml_classifier import classifier

def test_classifier_predict_unresolved_symbol():
    result = classifier.predict("undefined symbol: qOn+wm28wmA in libkernel")
    assert result["category"] == "UNRESOLVED_SYMBOL"
    assert result["confidence"] > 0.4
    assert "class_probabilities" in result

def test_classifier_predict_cfg_merge():
    result = classifier.predict("CFG shared merge splitting exceeded budget: originalBlocks=125")
    assert result["category"] == "CFG_MERGE_EXPLOSION"
    assert "split budget" in result["mitigation"].lower()

def test_classifier_predict_ancillary():
    result = classifier.predict("packed pixel ancillary input has an unsupported live use BitFieldUExtract")
    assert result["category"] == "ANCILLARY_REGISTER_REUSE"
    assert "ancillary" in result["root_cause"].lower()

def test_classifier_predict_hardware_gap():
    result = classifier.predict("SPIR-V module emission failed: 64-bit buffer atomics need shaderBufferInt64Atomics")
    assert result["category"] == "HARDWARE_FEATURE_GAP"

def test_classifier_evaluation():
    eval_metrics = classifier.evaluate()
    assert eval_metrics["accuracy"] >= 0.8
    assert eval_metrics["macro_f1"] >= 0.7
    assert len(eval_metrics["classes"]) == 5
