export interface SymbolRecord {
  id: number;
  nid: string;
  library: string;
  function_name: string;
  status: string;
  caller_module: string;
}

export interface AuditEvent {
  id: number;
  action: string;
  detail: string;
  created_at: string;
}

export interface TriageSessionSummary {
  id: number;
  title_id: string;
  title_name: string;
  target_os: string;
  category: string;
  confidence: number;
  total_imports: number;
  absent_imports: number;
  stub_imports: number;
  walk_complexity_score?: number;
  complexity_risk?: string;
  created_at: string;
}

export interface TriageSessionDetail {
  id: number;
  title_id: string;
  title_name: string;
  target_os: string;
  category: string;
  confidence: number;
  root_cause: string;
  mitigation: string;
  raw_trace: string;
  total_imports: number;
  absent_imports: number;
  stub_imports: number;
  created_at: string;
  symbols: SymbolRecord[];
  audit_events: AuditEvent[];
  profiler_counters?: Record<string, number | null>;
  walk_complexity_score?: number;
  complexity_risk?: string;
}

export interface StatsData {
  total_sessions: number;
  total_symbols_analyzed: number;
  total_absent_symbols: number;
  category_counts: Record<string, number>;
  complexity_risk_counts?: Record<string, number>;
  target_os_counts: Record<string, number>;
}

export interface TriageCreatePayload {
  title_id: string;
  title_name: string;
  target_os: string;
  raw_trace: string;
}

const API_BASE = '/api';

export async function fetchStats(): Promise<StatsData> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error(`Failed to fetch stats: ${res.statusText}`);
  return res.json();
}

export async function listTriageSessions(page = 1, pageSize = 20, search?: string, category?: string): Promise<{ items: TriageSessionSummary[]; total: number }> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (search) params.append('search', search);
  if (category) params.append('category', category);

  const res = await fetch(`${API_BASE}/triage?${params.toString()}`);
  if (!res.ok) throw new Error(`Failed to list triage sessions: ${res.statusText}`);
  return res.json();
}

export async function getTriageSession(id: number): Promise<TriageSessionDetail> {
  const res = await fetch(`${API_BASE}/triage/${id}`);
  if (!res.ok) throw new Error(`Failed to get triage session ${id}: ${res.statusText}`);
  return res.json();
}

export async function createTriageSession(payload: TriageCreatePayload): Promise<TriageSessionDetail> {
  const res = await fetch(`${API_BASE}/triage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create triage session: ${res.statusText}`);
  }
  return res.json();
}

export async function exportTriageSession(id: number): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/triage/${id}/export`);
  if (!res.ok) throw new Error(`Failed to export triage session: ${res.statusText}`);
  return res.json();
}
