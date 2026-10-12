import React, { useState } from 'react';
import { TriageCreatePayload } from '../api/client';

interface TriageFormProps {
  onSubmit: (payload: TriageCreatePayload) => Promise<void>;
  onCancel: () => void;
  isSubmitting: boolean;
}

const PRESETS = [
  {
    name: '007 First Light (Stop 1: NID sceSslGetCaList)',
    title_id: 'PPSA11386',
    title_name: '007 First Light',
    target_os: 'linux',
    raw_trace: 'loader: undefined symbol: qOn+wm28wmA (sceSslGetCaList); absent imports sceSslGetCaList, sceSslFreeCaList, sceNetShowNetstat',
  },
  {
    name: 'ScreenTester5 (libkernel sysctlbyname)',
    title_id: 'PPSA69420',
    title_name: 'ScreenTester5',
    target_os: 'windows',
    raw_trace: 'FAIL: unresolved ELF import MhC53TKmjVA from libkernel.prx (sysctlbyname)\nsceSystemServiceLaunchWebBrowser',
  },
  {
    name: 'Stray (CFG Merge Explosion)',
    title_id: 'PPSA02101',
    title_name: 'Stray',
    target_os: 'linux',
    raw_trace: 'CFG shared merge splitting exceeded budget: originalBlocks=125 currentBlocks=625 splitBudget=500 in MaskedSelectEliminator',
  },
  {
    name: 'Palworld (AudioChat NID oiOi7vgPfAY)',
    title_id: 'PPSA23126',
    title_name: 'Palworld',
    target_os: 'windows',
    raw_trace: 'FAIL: unresolved ELF import oiOi7vgPfAY from libSceAudioOut.prx (sceAudioOut2EnableChat)\nlibdiscord_partner_sdk.prx registry 0x8732B0',
  },
  {
    name: 'Intel UHD 770 (Hardware Feature Gap)',
    title_id: 'PPSA99005',
    title_name: 'ps5-opengl Showcase',
    target_os: 'windows',
    raw_trace: 'ShaderRecompiler::Recompile: SPIR-V module emission failed: 64-bit buffer atomics need shaderBufferInt64Atomics on host device',
  },
];

export const TriageForm: React.FC<TriageFormProps> = ({ onSubmit, onCancel, isSubmitting }) => {
  const [titleId, setTitleId] = useState('');
  const [titleName, setTitleName] = useState('');
  const [targetOs, setTargetOs] = useState('linux');
  const [rawTrace, setRawTrace] = useState('');
  const [error, setError] = useState<string | null>(null);

  const applyPreset = (preset: typeof PRESETS[0]) => {
    setTitleId(preset.title_id);
    setTitleName(preset.title_name);
    setTargetOs(preset.target_os);
    setRawTrace(preset.raw_trace);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!titleId.trim() || !titleName.trim() || !rawTrace.trim()) {
      setError('Please fill in Title ID, Title Name, and the Execution Trace.');
      return;
    }
    setError(null);
    try {
      await onSubmit({
        title_id: titleId.trim(),
        title_name: titleName.trim(),
        target_os: targetOs,
        raw_trace: rawTrace.trim(),
      });
    } catch (err: any) {
      setError(err.message || 'Failed to submit triage.');
    }
  };

  return (
    <div className="card form-container">
      <div className="card-header">
        <h3>New Binary & Execution Stop Triage</h3>
        <p className="subtitle">
          Submit an ELF / PRX import table snippet, shader compiler assertion, or crash log for ML root-cause analysis.
        </p>
      </div>

      <div className="preset-selector">
        <span className="preset-label">Quick Benchmark Presets:</span>
        <div className="preset-chips">
          {PRESETS.map((p) => (
            <button
              key={p.name}
              type="button"
              className="chip-btn"
              onClick={() => applyPreset(p)}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit} className="triage-form">
        <div className="form-row">
          <div className="form-group flex-1">
            <label htmlFor="titleId">Title ID (e.g. PPSA11386)</label>
            <input
              id="titleId"
              type="text"
              value={titleId}
              onChange={(e) => setTitleId(e.target.value)}
              placeholder="PPSA11386"
              required
            />
          </div>
          <div className="form-group flex-2">
            <label htmlFor="titleName">Title Name</label>
            <input
              id="titleName"
              type="text"
              value={titleName}
              onChange={(e) => setTitleName(e.target.value)}
              placeholder="Game or Homebrew Application Name"
              required
            />
          </div>
          <div className="form-group flex-1">
            <label htmlFor="targetOs">Target Host OS</label>
            <select
              id="targetOs"
              value={targetOs}
              onChange={(e) => setTargetOs(e.target.value)}
            >
              <option value="linux">Linux (Vulkan / Proton)</option>
              <option value="windows">Windows (Vulkan / MinGW)</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="rawTrace">Execution Trace / Recompiler Error Log</label>
          <textarea
            id="rawTrace"
            rows={6}
            value={rawTrace}
            onChange={(e) => setRawTrace(e.target.value)}
            placeholder="Paste log output, unresolved ELF imports, or recompiler assertion..."
            required
          />
        </div>

        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </button>
          <button type="submit" className="btn-primary" disabled={isSubmitting}>
            {isSubmitting ? 'Running ML Triage...' : 'Execute Triage & Diagnosis'}
          </button>
        </div>
      </form>
    </div>
  );
};
