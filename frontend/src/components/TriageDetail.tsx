import React from 'react';
import { TriageSessionDetail } from '../api/client';

interface TriageDetailProps {
  session: TriageSessionDetail;
  onBack: () => void;
  onExport: () => void;
}

export const TriageDetail: React.FC<TriageDetailProps> = ({ session, onBack, onExport }) => {
  return (
    <div className="detail-container">
      <div className="detail-header">
        <button className="btn-secondary" onClick={onBack}>
          &larr; Back to Dashboard
        </button>
        <div className="detail-header-actions">
          <button className="btn-primary" onClick={onExport}>
            Export Report (JSON)
          </button>
        </div>
      </div>

      <div className="card title-meta-card">
        <div className="title-meta-grid">
          <div>
            <span className="meta-label">Title ID</span>
            <h2 className="mono">{session.title_id}</h2>
          </div>
          <div>
            <span className="meta-label">Title Name</span>
            <h2>{session.title_name}</h2>
          </div>
          <div>
            <span className="meta-label">Target Architecture</span>
            <span className={`tag tag-${session.target_os}`}>{session.target_os}</span>
          </div>
          <div>
            <span className="meta-label">Analyzed Date</span>
            <span>{new Date(session.created_at).toLocaleString()}</span>
          </div>
        </div>
      </div>

      <div className="card diagnosis-card">
        <div className="diagnosis-header">
          <span className="diagnosis-label">Machine Learning Stop Classification</span>
          <span className={`badge badge-large badge-${session.category.toLowerCase()}`}>
            {session.category.replace(/_/g, ' ')}
          </span>
        </div>

        <div className="confidence-section">
          <div className="confidence-bar-wrapper">
            <div
              className="confidence-bar"
              style={{ width: `${Math.round(session.confidence * 100)}%` }}
            />
          </div>
          <span className="confidence-text">
            Confidence: {Math.round(session.confidence * 100)}%
          </span>
        </div>

        <div className="diagnosis-body">
          <div className="diagnosis-block">
            <h4>Root Cause Analysis</h4>
            <p>{session.root_cause}</p>
          </div>
          <div className="diagnosis-block block-mitigation">
            <h4>Recommended Mitigation / Compiler Flags</h4>
            <p>{session.mitigation}</p>
          </div>
        </div>
      </div>

      <div className="card symbols-card">
        <h3>Symbol & Import Table Audit ({session.symbols.length} detected)</h3>
        {session.symbols.length === 0 ? (
          <p className="text-muted">No explicit NIDs or symbols parsed in this log snippet.</p>
        ) : (
          <table className="symbols-table">
            <thead>
              <tr>
                <th>NID</th>
                <th>Target Library</th>
                <th>Resolved Symbol Name</th>
                <th>Status</th>
                <th>Caller Module</th>
              </tr>
            </thead>
            <tbody>
              {session.symbols.map((sym) => (
                <tr key={sym.id}>
                  <td className="mono">{sym.nid}</td>
                  <td>{sym.library}</td>
                  <td className="mono font-bold">{sym.function_name}</td>
                  <td>
                    <span className={`badge-sym badge-sym-${sym.status}`}>
                      {sym.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="mono text-muted">{sym.caller_module}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card trace-card">
        <h3>Raw Execution Trace</h3>
        <pre className="trace-box">{session.raw_trace}</pre>
      </div>

      <div className="card audit-card">
        <h3>Audit Log History</h3>
        <ul className="audit-list">
          {session.audit_events.map((evt) => (
            <li key={evt.id}>
              <span className="mono audit-action">[{evt.action}]</span>{' '}
              <span className="audit-detail">{evt.detail}</span>{' '}
              <span className="text-muted">({new Date(evt.created_at).toLocaleTimeString()})</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
