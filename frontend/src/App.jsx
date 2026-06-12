import { useState, useCallback } from 'react';
import axios from 'axios';
import GraphCanvas from './components/GraphCanvas';
import SidePanel from './components/SidePanel';
import Toolbar from './components/Toolbar';

const API_BASE = 'http://localhost:8000';

function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [aiResult, setAiResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [repoPath, setRepoPath] = useState('');
  const [error, setError] = useState('');
  const [view, setView] = useState('input');

  const analyzeRepo = async () => {
    if (!repoPath.trim()) {
      setError('Please enter a repository path');
      return;
    }
    setError('');
    setAnalyzing(true);
    try {
      const response = await axios.post(`${API_BASE}/api/analyze`, {
        repo_path: repoPath.trim()
      });
      const data = response.data;

      const rfNodes = data.nodes.map(node => ({
        id: node.id,
        type: 'customNode',
        position: node.position,
        data: {
          label: node.label,
          lines_of_code: node.lines_of_code,
          size_category: node.size_category,
          language: node.language,
          file_id: node.id
        }
      }));

      const rfEdges = data.edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        animated: true,
        style: { stroke: '#7c3aed', strokeDasharray: '5 5' },
        markerEnd: { type: 'arrowclosed', color: '#7c3aed' }
      }));

      setNodes(rfNodes);
      setEdges(rfEdges);
      setView('graph');
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Failed to analyze repository';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleNodeSelect = useCallback(async (node) => {
    setSelectedNode(node);
    setAiResult(null);
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/explain`, {
        file_id: node.data.file_id
      });
      setAiResult(response.data);
    } catch (err) {
      setAiResult({
        summary: 'Failed to get AI explanation: ' + (err.response?.data?.detail || err.message),
        purpose: 'Error occurred',
        complexity: 'unknown',
        key_concepts: []
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const handleClosePanel = () => {
    setSelectedNode(null);
    setAiResult(null);
  };

  const handleReset = () => {
    setView('input');
    setNodes([]);
    setEdges([]);
    setSelectedNode(null);
    setAiResult(null);
    setRepoPath('');
    setError('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') analyzeRepo();
  };

  if (view === 'input') {
    return (
      <div className="app">
        <div className="input-screen">
          <div className="input-card">
            <div className="input-card-icon">◇</div>
            <h1>CodeMap Explorer</h1>
            <p>Visualize your codebase as an interactive dependency graph with AI-powered insights</p>
            <input
              id="repo-path-input"
              className="input-field"
              type="text"
              placeholder="Enter absolute path to your repository"
              value={repoPath}
              onChange={(e) => { setRepoPath(e.target.value); setError(''); }}
              onKeyDown={handleKeyDown}
            />
            <button
              id="analyze-btn"
              className="analyze-btn"
              onClick={analyzeRepo}
              disabled={analyzing}
            >
              {analyzing ? 'Analyzing...' : 'Analyze Repository'}
            </button>
            {error && <div className="error-message">⚠ {error}</div>}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="graph-view">
        <Toolbar
          nodeCount={nodes.length}
          edgeCount={edges.length}
          onReset={handleReset}
        />
        <div className="react-flow-wrapper">
          <GraphCanvas
            nodes={nodes}
            edges={edges}
            onNodeSelect={handleNodeSelect}
          />
        </div>
        <SidePanel
          node={selectedNode}
          aiResult={aiResult}
          loading={loading}
          onClose={handleClosePanel}
        />
      </div>
    </div>
  );
}

export default App;
