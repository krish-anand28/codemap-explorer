import { X, Crosshair, Brain, Tag, FileCode, Hash } from 'lucide-react';
import { LANG_COLORS, COMPLEXITY_COLORS } from '../constants';

export default function SidePanel({ node, aiResult, loading, onClose }) {
  const isOpen = !!node;
  const lang = node?.data?.language || 'Unknown';
  const langColor = LANG_COLORS[lang] || LANG_COLORS.default;

  return (
    <div className={`side-panel ${isOpen ? 'open' : ''}`}>
      {isOpen && (
        <>
          <div className="side-panel-header">
            <div className="side-panel-title-group">
              <FileCode size={20} color="#a1a1aa" />
              <h2 className="side-panel-filename">{node.data.label}</h2>
              <span
                className="language-badge"
                style={{
                  backgroundColor: langColor + '22',
                  color: langColor,
                  borderColor: langColor + '44',
                }}
              >
                {lang}
              </span>
            </div>
            <button id="close-panel-btn" className="close-btn" onClick={onClose}>
              <X size={18} />
            </button>
          </div>

          <div className="side-panel-body">
            {loading ? (
              <div className="skeleton-container">
                <div className="skeleton-line" style={{ width: '90%' }} />
                <div className="skeleton-line" style={{ width: '70%' }} />
                <div className="skeleton-line" style={{ width: '80%' }} />
              </div>
            ) : aiResult ? (
              <div className="ai-results" style={{ animation: 'fadeIn 0.3s ease' }}>
                <div className="side-panel-section">
                  <div className="section-title">
                    <Brain size={14} />
                    <span>Summary</span>
                  </div>
                  <p className="section-content">{aiResult.summary}</p>
                </div>

                <div className="side-panel-section">
                  <div className="section-title">
                    <Crosshair size={14} />
                    <span>Purpose</span>
                  </div>
                  <p className="section-content">{aiResult.purpose}</p>
                </div>

                <div className="side-panel-section">
                  <div className="section-title">
                    <Tag size={14} />
                    <span>Complexity</span>
                  </div>
                  <span
                    className="complexity-badge"
                    style={{
                      backgroundColor: (COMPLEXITY_COLORS[aiResult.complexity] || '#71717a') + '22',
                      color: COMPLEXITY_COLORS[aiResult.complexity] || '#71717a',
                      borderColor: (COMPLEXITY_COLORS[aiResult.complexity] || '#71717a') + '44',
                    }}
                  >
                    {aiResult.complexity}
                  </span>
                </div>

                <div className="side-panel-section">
                  <div className="section-title">
                    <Hash size={14} />
                    <span>Key Concepts</span>
                  </div>
                  <div className="concepts-container">
                    {(aiResult.key_concepts || []).map((concept, i) => (
                      <span key={i} className="concept-tag">{concept}</span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="side-panel-empty">
                <p>Click "Analyze" to get AI insights</p>
              </div>
            )}
          </div>

          <div className="side-panel-footer">
            <span>Lines of Code: {node.data.lines_of_code}</span>
            <span>Size: {node.data.size_category}</span>
          </div>
        </>
      )}
    </div>
  );
}
