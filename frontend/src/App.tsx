import { useState, useEffect, useCallback } from 'react';
import {
  StatsData,
  TriageSessionSummary,
  TriageSessionDetail,
  fetchStats,
  listTriageSessions,
  getTriageSession,
  createTriageSession,
  exportTriageSession,
  TriageCreatePayload,
} from './api/client';
import { Dashboard } from './components/Dashboard';
import { TriageForm } from './components/TriageForm';
import { TriageDetail } from './components/TriageDetail';
import './App.css';

export function App() {
  const [view, setView] = useState<'dashboard' | 'form' | 'detail'>('dashboard');
  const [stats, setStats] = useState<StatsData | null>(null);
  const [sessions, setSessions] = useState<TriageSessionSummary[]>([]);
  const [selectedSession, setSelectedSession] = useState<TriageSessionDetail | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [notification, setNotification] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [statsRes, sessionsRes] = await Promise.all([
        fetchStats().catch(() => null),
        listTriageSessions(1, 50, searchTerm, selectedCategory).catch(() => ({ items: [], total: 0 })),
      ]);
      if (statsRes) setStats(statsRes);
      setSessions(sessionsRes.items);
    } catch (err: any) {
      setNotification({ msg: err.message || 'Error loading dashboard data', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, selectedCategory]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSelectSession = async (id: number) => {
    try {
      setIsLoading(true);
      const detail = await getTriageSession(id);
      setSelectedSession(detail);
      setView('detail');
    } catch (err: any) {
      setNotification({ msg: err.message || 'Failed to fetch session detail', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSession = async (payload: TriageCreatePayload) => {
    setIsSubmitting(true);
    try {
      const created = await createTriageSession(payload);
      setSelectedSession(created);
      setView('detail');
      setNotification({ msg: `Triage complete for ${created.title_id}!`, type: 'success' });
      await loadData();
    } catch (err: any) {
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleExport = async () => {
    if (!selectedSession) return;
    try {
      const exportData = await exportTriageSession(selectedSession.id);
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `axiom-triage-${selectedSession.title_id}-${selectedSession.id}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setNotification({ msg: 'Export failed: ' + err.message, type: 'error' });
    }
  };

  return (
    <div className="app-layout">
      <header className="app-navbar">
        <div className="brand" onClick={() => setView('dashboard')}>
          <div className="brand-logo">AX</div>
          <div className="brand-text">
            <h1>Axiom Observatory</h1>
            <span className="brand-tagline">Binary Translation & Recompiler ML Triage</span>
          </div>
        </div>
        <div className="navbar-actions">
          <button
            className={`nav-btn ${view === 'dashboard' ? 'nav-active' : ''}`}
            onClick={() => setView('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`nav-btn ${view === 'form' ? 'nav-active' : ''}`}
            onClick={() => setView('form')}
          >
            + New Triage
          </button>
        </div>
      </header>

      {notification && (
        <div className={`notification toast-${notification.type}`}>
          <span>{notification.msg}</span>
          <button className="toast-close" onClick={() => setNotification(null)}>
            &times;
          </button>
        </div>
      )}

      <main className="app-main">
        {view === 'dashboard' && (
          <Dashboard
            stats={stats}
            sessions={sessions}
            onSelectSession={handleSelectSession}
            onOpenNewTriage={() => setView('form')}
            searchTerm={searchTerm}
            onSearchChange={setSearchTerm}
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            isLoading={isLoading}
          />
        )}

        {view === 'form' && (
          <TriageForm
            onSubmit={handleCreateSession}
            onCancel={() => setView('dashboard')}
            isSubmitting={isSubmitting}
          />
        )}

        {view === 'detail' && selectedSession && (
          <TriageDetail
            session={selectedSession}
            onBack={() => setView('dashboard')}
            onExport={handleExport}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>Axiom Observatory — Alan Vo &lt;alanvo@gmail.com&gt;</p>
      </footer>
    </div>
  );
}

export default App;
