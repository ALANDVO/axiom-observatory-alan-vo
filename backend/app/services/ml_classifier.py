from typing import List, Tuple, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

TRAINING_DATASET: List[Tuple[str, str]] = [
    # UNRESOLVED_SYMBOL
    ("loader: undefined symbol: qOn+wm28wmA (sceSslGetCaList); absent imports sceSslGetCaList, sceSslFreeCaList", "UNRESOLVED_SYMBOL"),
    ("FAIL: unresolved ELF import MhC53TKmjVA from libkernel.prx (sysctlbyname)", "UNRESOLVED_SYMBOL"),
    ("FAIL: unresolved ELF import uEtgPWgPxOk from libScePosixForWebKit.prx (mkstemp)", "UNRESOLVED_SYMBOL"),
    ("FAIL: unresolved ELF import fLcU5G6Qrjs from libSceLibcInternal.prx (atoll)", "UNRESOLVED_SYMBOL"),
    ("Failed to load module: libs/libSceOpusDec.prx absent modules CreateEx Decode Destroy", "UNRESOLVED_SYMBOL"),
    ("FAIL: unresolved ELF import oiOi7vgPfAY from libSceAudioOut.prx (sceAudioOut2EnableChat)", "UNRESOLVED_SYMBOL"),
    ("undefined reference to pthread_set_name_np in libkernel loader symbol table", "UNRESOLVED_SYMBOL"),
    ("relocation error: symbol sceKernelAddWriteEvent not found in dynamic symbol table", "UNRESOLVED_SYMBOL"),

    # CFG_MERGE_EXPLOSION
    ("CFG shared merge splitting exceeded budget: originalBlocks=125 currentBlocks=625 splitBudget=500", "CFG_MERGE_EXPLOSION"),
    ("Shader preparation: masked-lane walk takes 150 to 400 s on Stray large pixel shaders in MaskedSelectEliminator", "CFG_MERGE_EXPLOSION"),
    ("GameThread timed out waiting for RenderThread after 120.00 secs in MaskedSelectEliminator::Eliminate", "CFG_MERGE_EXPLOSION"),
    ("CFG loop structurize pass exploded blocks exceeded branch limit in PrepareShader", "CFG_MERGE_EXPLOSION"),
    ("masked-lane walk implication loop: 56,190 walks, 1,233 M values visited, selects eliminated", "CFG_MERGE_EXPLOSION"),
    ("CFG shared merge splitting exceeded budget: originalBlocks=210 currentBlocks=940", "CFG_MERGE_EXPLOSION"),

    # ANCILLARY_REGISTER_REUSE
    ("ShaderRecompiler::Recompile: shader info collection failed: packed pixel ancillary input has an unsupported live use", "ANCILLARY_REGISTER_REUSE"),
    ("unsupported live use used by BitFieldUExtract 16 11, SelectU32 ancillary VGPR reused", "ANCILLARY_REGISTER_REUSE"),
    ("RDNA2 ancillary VGPR v4 reused as ordinary data register after v_bfe_u32 render target index", "ANCILLARY_REGISTER_REUSE"),
    ("ancillary input packing raw word passed to BitCastF32U32 and FPMad32 without Layer/SampleId extraction", "ANCILLARY_REGISTER_REUSE"),
    ("packed pixel ancillary word read whole after its VGPR is reused SelectU32 cond HelperInvocation", "ANCILLARY_REGISTER_REUSE"),

    # HARDWARE_FEATURE_GAP
    ("ShaderRecompiler::Recompile: SPIR-V module emission failed: 64-bit buffer atomics need shaderBufferInt64Atomics", "HARDWARE_FEATURE_GAP"),
    ("AGC: storage image access to depth/stencil surface 0x201a800000 is not implemented", "HARDWARE_FEATURE_GAP"),
    ("VideoOut: unsupported display pixel format 0xc001000622000000", "HARDWARE_FEATURE_GAP"),
    ("execution test agc_driver_vopc_compare failed on Intel UHD 770 NaN unordered compare", "HARDWARE_FEATURE_GAP"),
    ("device lacks support for bindless storage image tables or shaderBufferInt64Atomics feature flag", "HARDWARE_FEATURE_GAP"),
    ("VOP3 source modifiers are not implemented: v_cubeid_f32 v, v, -v, -v div:2 output denormals", "HARDWARE_FEATURE_GAP"),

    # RUNTIME_STUB_FAULT
    ("sceSharePlayInitialize: invalid argument (007 passes a null heap, size 0x1800)", "RUNTIME_STUB_FAULT"),
    ("int 0x42 trap (exit 139) after scePlayGoGetLocus on chunk 1 returns 0x80B2000C", "RUNTIME_STUB_FAULT"),
    ("hang, all threads asleep: loading thread waits inside synchronous APR submit for value written after submit", "RUNTIME_STUB_FAULT"),
    ("kernel thread panic: invalid mutex lock state during worker teardown", "RUNTIME_STUB_FAULT"),
    ("trap exit code 139 signal SIGSEGV in ampr_emu priority queue scheduler", "RUNTIME_STUB_FAULT"),
]

# Evaluation test split
BENCHMARK_TESTSET: List[Tuple[str, str]] = [
    ("unresolved ELF import cG3t15OK4Ow from libkernel.prx", "UNRESOLVED_SYMBOL"),
    ("CFG shared merge splitting exceeded budget: originalBlocks=300 currentBlocks=1500 splitBudget=600", "CFG_MERGE_EXPLOSION"),
    ("shader info collection failed: packed pixel ancillary input has an unsupported live use (BitFieldUExtract)", "ANCILLARY_REGISTER_REUSE"),
    ("SPIR-V module emission failed: 64-bit buffer atomics need shaderBufferInt64Atomics on host device", "HARDWARE_FEATURE_GAP"),
    ("sceSharePlayInitialize returned error invalid argument on zero buffer pointer", "RUNTIME_STUB_FAULT"),
    ("loader: undefined symbol: MhC53TKmjVA in libkernel", "UNRESOLVED_SYMBOL"),
    ("MaskedSelectEliminator took 300 seconds; render thread timed out waiting for shader recompile", "CFG_MERGE_EXPLOSION"),
    ("storage image access to depth/stencil surface 0x201a800000 failed in AGC driver", "HARDWARE_FEATURE_GAP"),
    ("int 0x42 trap signal 139 in playgo chunk reader locus", "RUNTIME_STUB_FAULT"),
]

class StopClassifier:
    def __init__(self):
        self.pipeline: Pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, lowercase=True)),
            ("clf", LogisticRegression(C=5.0, max_iter=200, random_state=42))
        ])
        self._fit()

    def _fit(self):
        X = [item[0] for item in TRAINING_DATASET]
        y = [item[1] for item in TRAINING_DATASET]
        self.pipeline.fit(X, y)

    def predict(self, trace_text: str) -> Dict[str, Any]:
        probs = self.pipeline.predict_proba([trace_text])[0]
        classes = self.pipeline.classes_
        best_idx = int(np.argmax(probs))
        predicted_category = str(classes[best_idx])
        confidence = float(probs[best_idx])

        # Generate rule-informed root cause & mitigations based on category
        root_causes = {
            "UNRESOLVED_SYMBOL": "Executable or dynamic module imports unresolved PlayStation NID symbols absent from target runtime.",
            "CFG_MERGE_EXPLOSION": "Control Flow Graph structurization exceeded splitting budget or masked-lane optimization walk depth.",
            "ANCILLARY_REGISTER_REUSE": "RDNA2 packed pixel ancillary VGPR reused as standard data register before all lane bit fields were extracted.",
            "HARDWARE_FEATURE_GAP": "Host GPU or Vulkan driver lacks hardware feature capability (e.g. 64-bit atomics, depth-stencil storage).",
            "RUNTIME_STUB_FAULT": "Runtime stub received unhandled parameters or asynchronous thread queue synchronization deadlocked."
        }

        mitigations = {
            "UNRESOLVED_SYMBOL": "Implement stub or full POSIX adapter in corresponding PRX module (e.g. libkernel or libSce*).",
            "CFG_MERGE_EXPLOSION": "Increase CFG split budget via --recompiler-split-budget or enable pass-level masked-select visitor capping.",
            "ANCILLARY_REGISTER_REUSE": "Synthesize unmodelled ancillary VGPR bitfields from draw state builtins (SampleId, Layer, PrimitiveId).",
            "HARDWARE_FEATURE_GAP": "Enable software emulation fallback for missing Vulkan extension or remap surface layout formats.",
            "RUNTIME_STUB_FAULT": "Provide non-null dummy structures for initialization calls and implement async FIFO submission workers."
        }

        return {
            "category": predicted_category,
            "confidence": round(confidence, 4),
            "root_cause": root_causes.get(predicted_category, "Unknown execution stop pattern."),
            "mitigation": mitigations.get(predicted_category, "Inspect host debug logs and trace registers."),
            "class_probabilities": {str(cls_name): round(float(prob), 4) for cls_name, prob in zip(classes, probs)}
        }

    def evaluate(self) -> Dict[str, Any]:
        X_test = [item[0] for item in BENCHMARK_TESTSET]
        y_test = [item[1] for item in BENCHMARK_TESTSET]

        y_pred = self.pipeline.predict(X_test)
        accuracy = float(accuracy_score(y_test, y_pred))
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)

        sample_predictions = []
        for text, actual, pred in zip(X_test, y_test, y_pred):
            sample_predictions.append({
                "trace_snippet": text[:60] + "..." if len(text) > 60 else text,
                "expected": actual,
                "predicted": pred,
                "correct": actual == pred
            })

        return {
            "total_samples": len(y_test),
            "accuracy": round(accuracy, 4),
            "macro_precision": round(float(precision), 4),
            "macro_recall": round(float(recall), 4),
            "macro_f1": round(float(f1), 4),
            "classes": list(self.pipeline.classes_),
            "sample_predictions": sample_predictions
        }

classifier = StopClassifier()
