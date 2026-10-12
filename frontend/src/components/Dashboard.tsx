import React from 'react';
import { StatsData, TriageSessionSummary } from '../api/client';

interface DashboardProps {
  stats: StatsData | null;
  sessions: TriageSessionSummary[];
  onSelectSession: (id: number) => void;
  onOpenNewTriage: () => void;
  searchTerm: string;
  onSearchChange: (val: string) => void;
  selectedCategory: string;
  onCategoryChange: (val: string) => void;
  isLoading: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({
  stats,
  sessions,
  onSelectSession,
  onOpenNewTriage,
  searchTerm,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  isLoading,
}) => {
  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h2>Observatory Status & Triage Dashboard</h2>
          <p className="subtitle">
            Automated binary dependency auditing and machine-learning execution stop triage.
          </p>
        </div>
        <button className="btn-primary" onClick={onOpenNewTriage}>
          + New Triage Session
        </button>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-label">Total Analyzed Sessions</span>
            <span className="stat-value">{stats.total_sessions}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Symbols Inspected</span>
            <span className="stat-value">{stats.total_symbols_analyzed}</span>
          </div>
          <div className="stat-card stat-alert">
            <span className="stat-label">Absent Symbols Flagged</span>
            <span className="stat-value">{stats.total_absent_symbols}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Target OS Distribution</span>
            <span className="stat-subtext">
              Linux: {stats.target_os_counts['linux'] || 0} | Windows: {stats.target_os_counts['windows'] || 0}
            </span>
          </div>
        </div>
      )}

      <div className="filters-bar">
        <input
          type="text"
          className="search-input"
          placeholder="Search by Title ID (e.g. PPSA11386) or name..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
        />
        <select
          className="select-filter"
          value={selectedCategory}
          onChange={(e) => onCategoryChange(e.target.value)}
        >
          <option value="">All Categories</option>
          <option value="UNRESOLVED_SYMBOL">Unresolved Symbol</option>
          <option value="CFG_MERGE_EXPLOSION">CFG Merge Explosion</option>
          <option value="ANCILLARY_REGISTER_REUSE">Ancillary Register Reuse</option>
          <option value="HARDWARE_FEATURE_GAP">Hardware Feature Gap</option>
          <option value="RUNTIME_STUB_FAULT">Runtime Stub Fault</option>
        </select>
      </div>

      <div className="sessions-table-wrapper">
        {isLoading ? (
          <div className="loading-state">Loading sessions...</div>
        ) : sessions.length === 0 ? (
          <div className="empty-state">
            <p>No triage sessions found matching criteria.</p>
            <button className="btn-secondary" onClick={onOpenNewTriage}>
              Create your first triage run
            </button>
          </div>
        ) : (
          <table className="sessions-table">
            <thead>
              <tr>
                <th>Title ID</th>
                <th>Title Name</th>
                <th>OS</th>
                <th>Category</th>
                <th>Confidence</th>
                <th>Symbols (Absent)</th>
                <th>Recorded</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((item) => (
                <tr key={item.id} onClick={() => onSelectSession(item.id)}>
                  <td className="mono font-bold">{item.title_id}</td>
                  <td>{item.title_name}</td>
                  <td>
                    <span className={`tag tag-${item.target_os}`}>{item.target_os}</span>
                  </td>
                  <td>
                    <span className={`badge badge-${item.category.toLowerCase()}`}>
                      {item.category.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td>{Math.round(item.confidence * 100)}%</td>
                  <td>
                    {item.total_imports} ({item.absent_imports})
                  </td>
                  <td className="text-muted">{new Date(item.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      className="btn-link"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectSession(item.id);
                      }}
                    >
                      View Report &rarr;
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
