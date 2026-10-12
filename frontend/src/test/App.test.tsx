import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';

describe('Axiom Observatory Frontend', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders navbar and dashboard header with initial metrics', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((url: any) => {
      if (typeof url === 'string' && url.includes('/api/stats')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            total_sessions: 3,
            total_symbols_analyzed: 14,
            total_absent_symbols: 2,
            category_counts: { UNRESOLVED_SYMBOL: 2, CFG_MERGE_EXPLOSION: 1 },
            target_os_counts: { linux: 2, windows: 1 },
          }),
        } as Response);
      }
      if (typeof url === 'string' && url.includes('/api/triage')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            items: [
              {
                id: 1,
                title_id: 'PPSA11386',
                title_name: '007 First Light',
                target_os: 'linux',
                category: 'UNRESOLVED_SYMBOL',
                confidence: 0.94,
                total_imports: 5,
                absent_imports: 1,
                stub_imports: 1,
                created_at: new Date().toISOString(),
              },
            ],
            total: 1,
          }),
        } as Response);
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    render(<App />);

    expect(screen.getByText('Axiom Observatory')).toBeInTheDocument();
    expect(screen.getByText('Observatory Status & Triage Dashboard')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('PPSA11386')).toBeInTheDocument();
      expect(screen.getByText('007 First Light')).toBeInTheDocument();
    });
  });

  it('switches to New Triage form when clicking + New Triage', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0 }),
    } as Response);

    render(<App />);

    const newTriageBtn = screen.getByRole('button', { name: /\+ New Triage Session/i });
    fireEvent.click(newTriageBtn);

    expect(screen.getByText('New Binary & Execution Stop Triage')).toBeInTheDocument();
    expect(screen.getByLabelText(/Title ID/i)).toBeInTheDocument();
  });

  it('submits a new triage and views the generated diagnosis report', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((_url: any, opts: any) => {
      if (opts?.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            id: 42,
            title_id: 'PPSA69420',
            title_name: 'ScreenTester5',
            target_os: 'windows',
            category: 'UNRESOLVED_SYMBOL',
            confidence: 0.92,
            root_cause: 'Missing sysctlbyname from libkernel.prx',
            mitigation: 'Implement POSIX sysctl emulation',
            raw_trace: 'FAIL: unresolved ELF import MhC53TKmjVA',
            total_imports: 1,
            absent_imports: 1,
            stub_imports: 0,
            created_at: new Date().toISOString(),
            symbols: [
              {
                id: 101,
                nid: 'MhC53TKmjVA',
                library: 'libkernel.prx',
                function_name: 'sysctlbyname',
                status: 'absent',
                caller_module: 'eboot.bin',
              },
            ],
            audit_events: [
              {
                id: 201,
                action: 'TRIAGE_ANALYZED',
                detail: 'Analyzed PPSA69420',
                created_at: new Date().toISOString(),
              },
            ],
          }),
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        json: async () => ({ items: [], total: 0 }),
      } as Response);
    });

    render(<App />);

    // Open form
    fireEvent.click(screen.getByRole('button', { name: /\+ New Triage Session/i }));

    // Click preset chip
    const presetBtn = screen.getByRole('button', { name: /ScreenTester5/i });
    fireEvent.click(presetBtn);

    // Submit form
    const submitBtn = screen.getByRole('button', { name: /Execute Triage & Diagnosis/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('Machine Learning Stop Classification')).toBeInTheDocument();
      expect(screen.getByText('Missing sysctlbyname from libkernel.prx')).toBeInTheDocument();
      expect(screen.getByText('sysctlbyname')).toBeInTheDocument();
    });
  });

  it('updates search filter when typing into search input', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ items: [], total: 0 }),
    } as Response);

    render(<App />);

    const searchInput = screen.getByPlaceholderText(/Search by Title ID/i) as HTMLInputElement;
    fireEvent.change(searchInput, { target: { value: 'PPSA11386' } });

    expect(searchInput.value).toBe('PPSA11386');
  });
});
