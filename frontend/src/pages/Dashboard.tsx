import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { listParameters, getParameter, setParameter, deleteParameter, updateParameter } from '../api/params';
import { logout } from '../api/auth';
import type { Parameter } from '../types';
import { Eye, EyeOff, Trash2, Plus, Lock, Unlock, LogOut, X, Edit2, Check, Search } from 'lucide-react';


const Dashboard = () => {
  const [params, setParams] = useState<Parameter[]>([]);
  const [revealedValues, setRevealedValues] = useState<Record<string, string>>({});
  const [loadingValues, setLoadingValues] = useState<Record<string, boolean>>({});
  const [newParam, setNewParam] = useState({ name: '', app: 'default', value: '' });
  const [isNewApp, setIsNewApp] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const [editingParam, setEditingParam] = useState<{ name: string, app: string } | null>(null);
  const [editValue, setEditValue] = useState('');
  const [updatingValues, setUpdatingValues] = useState<Record<string, boolean>>({});

  const [searchName, setSearchName] = useState('');
  const [filterApp, setFilterApp] = useState('');
  const [allApps, setAllApps] = useState<string[]>(['default']);

  const navigate = useNavigate();

  const uniqueApps = allApps;

  const fetchParams = useCallback(async () => {
    try {
      const data = await listParameters(filterApp || undefined, searchName || undefined);
      setParams(data);

      const newApps = Array.from(new Set(data.map((p: Parameter) => p.app)));
      setAllApps(prev => {
        const combined = new Set([...prev, ...newApps]);
        return Array.from(combined).sort();
      });

      // Update default app if current one is not in the list and we're not adding a new one
      const apps = Array.from(new Set(data.map((p: Parameter) => p.app))).sort();
      if (apps.length > 0 && !isNewApp && !apps.includes(newParam.app)) {
        setNewParam(prev => ({ ...prev, app: apps[0] }));
      }
    } catch (err) {
      console.error('Failed to fetch parameters', err);
      setError('Failed to load parameters.');
    } finally {
      setLoading(false);
    }
  }, [isNewApp, newParam.app, filterApp, searchName]);

  useEffect(() => {
    fetchParams();
  }, [fetchParams]);

  const handleReveal = async (name: string, app: string) => {
    if (revealedValues[name]) {
      const updated = { ...revealedValues };
      delete updated[name];
      setRevealedValues(updated);
      return;
    }

    setLoadingValues({ ...loadingValues, [name]: true });
    try {
      const data = await getParameter(name, app);
      setRevealedValues({ ...revealedValues, [name]: data.value });
    } catch (err) {
      console.error('Failed to reveal parameter', err);
    } finally {
      setLoadingValues({ ...loadingValues, [name]: false });
    }
  };

  const handleAddParam = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await setParameter(newParam);
      const nextApp = isNewApp ? newParam.app : (newParam.app || 'default');
      setNewParam({ name: '', app: nextApp, value: '' });
      setIsNewApp(false);
      fetchParams();
    } catch (err: unknown) {
      // @ts-expect-error - err is unknown but we expect axios structure
      setError(err.response?.data?.detail || 'Failed to add parameter.');
    }
  };

  const handleDelete = async (name: string, app: string) => {
    if (window.confirm(`Are you sure you want to delete ${name}?`)) {
      try {
        await deleteParameter(name, app);
        fetchParams();
        const updatedRevealed = { ...revealedValues };
        delete updatedRevealed[name];
        setRevealedValues(updatedRevealed);
      } catch (err) {
        console.error('Failed to delete parameter', err);
      }
    }
  };

  const handleEditClick = (name: string, app: string) => {
    setEditingParam({ name, app });
    setEditValue('');
  };

  const handleCancelEdit = () => {
    setEditingParam(null);
    setEditValue('');
  };

  const handleUpdateSubmit = async (e: React.FormEvent, name: string, app: string) => {
    e.preventDefault();
    if (!editValue) return;

    setUpdatingValues({ ...updatingValues, [`${app}-${name}`]: true });
    try {
      await updateParameter(name, editValue, app);
      setEditingParam(null);
      setEditValue('');

      if (revealedValues[name]) {
        const updated = { ...revealedValues };
        delete updated[name];
        setRevealedValues(updated);
      }

      fetchParams();
    } catch (err) {
      console.error('Failed to update parameter', err);
      alert('Failed to update parameter');
    } finally {
      setUpdatingValues({ ...updatingValues, [`${app}-${name}`]: false });
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Secure Vault Dashboard</h1>
        <button onClick={handleLogout} className="logout-btn">
          <LogOut size={18} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          Logout
        </button>
      </div>

      <div className="add-param-form">
        <h3><Plus size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} /> Store New Parameter</h3>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleAddParam} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr auto', gap: '1rem', alignItems: 'end' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>App Name</label>
            {!isNewApp ? (
              <select
                value={newParam.app}
                onChange={(e) => {
                  if (e.target.value === '@@new@@') {
                    setIsNewApp(true);
                    setNewParam({ ...newParam, app: '' });
                  } else {
                    setNewParam({ ...newParam, app: e.target.value });
                  }
                }}
                required
              >
                {uniqueApps.map(app => (
                  <option key={app} value={app}>{app}</option>
                ))}
                <option value="@@new@@">+ Add New App...</option>
              </select>
            ) : (
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  placeholder="New app name"
                  value={newParam.app}
                  onChange={(e) => setNewParam({ ...newParam, app: e.target.value })}
                  required
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => {
                    setIsNewApp(false);
                    setNewParam({ ...newParam, app: uniqueApps[0] });
                  }}
                  style={{
                    position: 'absolute',
                    right: '10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: 'var(--text-muted)',
                    display: 'flex',
                    alignItems: 'center',
                    padding: 0
                  }}
                  title="Cancel"
                >
                  <X size={14} />
                </button>
              </div>
            )}
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Key Name</label>
            <input
              type="text"
              placeholder="e.g. API_KEY"
              value={newParam.name}
              onChange={(e) => setNewParam({ ...newParam, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Secret Value</label>
            <input
              type="password"
              placeholder="Enter sensitive value"
              value={newParam.value}
              onChange={(e) => setNewParam({ ...newParam, value: e.target.value })}
              required
            />
          </div>
          <button type="submit" className="btn" style={{ padding: '0.75rem 1.5rem' }}>Store</button>
        </form>
      </div>

      <h2>Your Protected Parameters</h2>

      <div className="filter-bar">
        <div className="search-container">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Search parameters by name..."
            value={searchName}
            onChange={(e) => setSearchName(e.target.value)}
          />
        </div>
        <select
          value={filterApp}
          onChange={(e) => setFilterApp(e.target.value)}
          className="app-filter-select"
        >
          <option value="">All Applications</option>
          {allApps.map(app => (
            <option key={app} value={app}>{app}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <p>Loading your secure vault...</p>
      ) : params.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', border: '1px dashed var(--border-color)', borderRadius: '8px' }}>
          <Lock size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
          <p style={{ color: 'var(--text-muted)' }}>No parameters stored in your vault yet.</p>
        </div>
      ) : (
        <div className="params-grid">
          {params.map((param) => (
            <div key={`${param.app}-${param.name}`} className="param-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div className="param-name">{param.name}</div>
                  <div className="param-app">{param.app}</div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    onClick={() => handleEditClick(param.name, param.app)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                    title="Edit parameter"
                  >
                    <Edit2 size={16} />
                  </button>
                  <button
                    onClick={() => handleDelete(param.name, param.app)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                    title="Delete parameter"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>

              {editingParam?.name === param.name && editingParam?.app === param.app ? (
                <form
                  onSubmit={(e) => handleUpdateSubmit(e, param.name, param.app)}
                  style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}
                >
                  <input
                    type="password"
                    placeholder="New secret value"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    required
                    autoFocus
                    style={{ flex: 1, padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-color)' }}
                  />
                  <button
                    type="submit"
                    className="btn"
                    disabled={updatingValues[`${param.app}-${param.name}`]}
                    style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                    title="Save"
                  >
                    {updatingValues[`${param.app}-${param.name}`] ? '...' : <Check size={16} />}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleCancelEdit}
                    style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                    title="Cancel"
                  >
                    <X size={16} />
                  </button>
                </form>
              ) : (
                <div className="param-reveal">
                  <button
                    className={`btn ${revealedValues[param.name] ? 'btn-secondary' : ''}`}
                    onClick={() => handleReveal(param.name, param.app)}
                    disabled={loadingValues[param.name]}
                  >
                    {loadingValues[param.name] ? 'Decrypting...' : (
                      <>
                        {revealedValues[param.name] ? <EyeOff size={16} /> : <Eye size={16} />}
                        <span style={{ marginLeft: '8px' }}>
                          {revealedValues[param.name] ? 'Hide Value' : 'Reveal Value'}
                        </span>
                      </>
                    )}
                  </button>
                  {revealedValues[param.name] && (
                    <div className="value-box">
                      <Unlock size={14} style={{ marginRight: '8px' }} />
                      {revealedValues[param.name]}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
