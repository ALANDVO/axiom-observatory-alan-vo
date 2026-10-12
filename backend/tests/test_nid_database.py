from app.services.nid_database import lookup_by_nid, lookup_by_name, extract_symbols_from_trace

def test_lookup_by_nid():
    info = lookup_by_nid("MhC53TKmjVA")
    assert info is not None
    assert info["name"] == "sysctlbyname"
    assert info["library"] == "libkernel.prx"

def test_lookup_by_name():
    res = lookup_by_name("sceAudioOut2EnableChat")
    assert res is not None
    nid, info = res
    assert nid == "oiOi7vgPfAY"
    assert info["status"] == "stub"

def test_extract_symbols_from_trace():
    trace = "unresolved ELF import MhC53TKmjVA from libkernel.prx and sceSslGetCaList failed"
    symbols = extract_symbols_from_trace(trace)
    assert len(symbols) >= 2
    names = [s["function_name"] for s in symbols]
    assert "sysctlbyname" in names
    assert "sceSslGetCaList" in names
