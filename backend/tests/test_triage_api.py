def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "axiom-observatory"

def test_initial_stats_empty(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 0
    assert data["total_symbols_analyzed"] == 0

def test_create_triage_unresolved_symbol(client):
    payload = {
        "title_id": "PPSA11386",
        "title_name": "007 First Light",
        "target_os": "linux",
        "raw_trace": "loader: undefined symbol: qOn+wm28wmA (sceSslGetCaList); absent imports sceSslGetCaList"
    }
    response = client.post("/api/triage", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title_id"] == "PPSA11386"
    assert data["category"] == "UNRESOLVED_SYMBOL"
    assert data["confidence"] > 0.5
    assert len(data["symbols"]) >= 1
    assert any(s["nid"] == "qOn+wm28wmA" for s in data["symbols"])
    assert len(data["audit_events"]) == 1

def test_create_triage_cfg_explosion(client):
    payload = {
        "title_id": "PPSA02101",
        "title_name": "Stray",
        "target_os": "linux",
        "raw_trace": "CFG shared merge splitting exceeded budget: originalBlocks=125 currentBlocks=625 splitBudget=500"
    }
    response = client.post("/api/triage", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "CFG_MERGE_EXPLOSION"
    assert "Control Flow" in data["root_cause"]

def test_create_triage_ancillary_hazard(client):
    payload = {
        "title_id": "PPSA02100",
        "title_name": "Stray UE4",
        "target_os": "linux",
        "raw_trace": "ShaderRecompiler::Recompile: shader info collection failed: packed pixel ancillary input has an unsupported live use (BitFieldUExtract 16 11, SelectU32)"
    }
    response = client.post("/api/triage", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "ANCILLARY_REGISTER_REUSE"

def test_create_triage_hardware_gap(client):
    payload = {
        "title_id": "PPSA99005",
        "title_name": "ps5-opengl",
        "target_os": "windows",
        "raw_trace": "SPIR-V module emission failed: 64-bit buffer atomics need shaderBufferInt64Atomics on host device"
    }
    response = client.post("/api/triage", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "HARDWARE_FEATURE_GAP"

def test_get_triage_detail(client):
    create_res = client.post("/api/triage", json={
        "title_id": "PPSA69420",
        "title_name": "ScreenTester5",
        "target_os": "windows",
        "raw_trace": "FAIL: unresolved ELF import MhC53TKmjVA from libkernel.prx (sysctlbyname)"
    })
    session_id = create_res.json()["id"]

    get_res = client.get(f"/api/triage/{session_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == session_id
    assert data["title_id"] == "PPSA69420"
    assert len(data["symbols"]) >= 1

def test_get_triage_not_found(client):
    res = client.get("/api/triage/999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_export_triage_json(client):
    create_res = client.post("/api/triage", json={
        "title_id": "PPSA99039",
        "title_name": "EVO-PLAYER-PS5",
        "target_os": "linux",
        "raw_trace": "FAIL: unresolved ELF import fLcU5G6Qrjs from libSceLibcInternal.prx"
    })
    session_id = create_res.json()["id"]

    export_res = client.get(f"/api/triage/{session_id}/export")
    assert export_res.status_code == 200
    data = export_res.json()
    assert data["export_version"] == "1.0.0"
    assert data["session"]["title_id"] == "PPSA99039"
    assert "symbols" in data["session"]

def test_export_triage_not_found(client):
    res = client.get("/api/triage/999999/export")
    assert res.status_code == 404

def test_list_triage_with_pagination_and_filter(client):
    for i in range(3):
        client.post("/api/triage", json={
            "title_id": f"PPSA0000{i}",
            "title_name": f"Game Title {i}",
            "target_os": "linux",
            "raw_trace": f"CFG shared merge splitting exceeded budget: originalBlocks={i} currentBlocks=500"
        })

    list_res = client.get("/api/triage?page=1&page_size=2")
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] >= 3
    assert len(data["items"]) == 2

    filter_res = client.get("/api/triage?search=Game Title 1")
    assert filter_res.status_code == 200
    filtered = filter_res.json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["title_name"] == "Game Title 1"

def test_validation_errors(client):
    bad_res = client.post("/api/triage", json={
        "title_id": "P",
        "title_name": "A",
        "raw_trace": "x"
    })
    assert bad_res.status_code == 422

def test_stats_aggregation(client):
    client.post("/api/triage", json={
        "title_id": "PPSA02101",
        "title_name": "Stray",
        "target_os": "linux",
        "raw_trace": "CFG shared merge splitting exceeded budget: originalBlocks=125 currentBlocks=625"
    })
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_sessions"] > 0
    assert "CFG_MERGE_EXPLOSION" in data["category_counts"]

def test_nid_lookup_endpoints(client):
    res1 = client.get("/api/nid/lookup?nid=MhC53TKmjVA")
    assert res1.status_code == 200
    assert res1.json()["function_name"] == "sysctlbyname"

    res2 = client.get("/api/nid/lookup?name=sceSslGetCaList")
    assert res2.status_code == 200
    assert res2.json()["nid"] == "qOn+wm28wmA"

    res3 = client.get("/api/nid/lookup?nid=nonexistent_nid")
    assert res3.status_code == 404

    res4 = client.get("/api/nid/lookup")
    assert res4.status_code == 400

def test_ml_evaluate_endpoint(client):
    res = client.post("/api/ml/evaluate")
    assert res.status_code == 200
    data = res.json()
    assert data["total_samples"] > 0
    assert data["accuracy"] > 0.7

def test_profiler_counters_flows_through_create_get_export(client):
    """Stray masked-lane trace (#3504): counters persist + surface end-to-end."""
    trace = (
        "masked-lane walk implication loop: 56,190 walks, "
        "1,233 M values visited, selects eliminated"
    )
    create_res = client.post("/api/triage", json={
        "title_id": "PPSA02101",
        "title_name": "Stray",
        "target_os": "linux",
        "raw_trace": trace,
    })
    assert create_res.status_code == 200
    data = create_res.json()
    assert data["category"] == "CFG_MERGE_EXPLOSION"
    assert data["complexity_risk"] == "critical"
    assert data["walk_complexity_score"] >= 0.85
    assert data["profiler_counters"]["walks"] == 56190.0
    assert data["profiler_counters"]["values_visited"] == 1_233_000_000.0
    assert any(a["action"] == "PROFILER_WALK_ANALYZED" for a in data["audit_events"])

    session_id = data["id"]
    detail = client.get(f"/api/triage/{session_id}").json()
    assert detail["complexity_risk"] == "critical"
    assert detail["profiler_counters"]["walks"] == 56190.0

    exported = client.get(f"/api/triage/{session_id}/export").json()
    assert exported["session"]["complexity_risk"] == "critical"
    assert exported["session"]["profiler_counters"]["walks"] == 56190.0


def test_non_profiler_trace_has_no_risk(client):
    res = client.post("/api/triage", json={
        "title_id": "PPSA11386",
        "title_name": "007 First Light",
        "target_os": "linux",
        "raw_trace": "loader: undefined symbol: qOn+wm28wmA (sceSslGetCaList)",
    })
    data = res.json()
    assert data["complexity_risk"] == "none"
    assert data["walk_complexity_score"] == 0.0
    assert all(v is None for v in data["profiler_counters"].values())
