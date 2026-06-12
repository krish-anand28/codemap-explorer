import { RotateCcw, FileCode, ArrowRight } from 'lucide-react';

export default function Toolbar({ nodeCount, edgeCount, onReset }) {
  return (
    <div className="toolbar">
      <div className="toolbar-left">
        <span className="toolbar-logo">◇ CodeMap Explorer</span>
      </div>
      <div className="toolbar-center">
        <span className="toolbar-stats">
          <FileCode size={14} />
          {nodeCount} files
          <span className="toolbar-stats-divider">·</span>
          <ArrowRight size={14} />
          {edgeCount} dependencies
        </span>
      </div>
      <div className="toolbar-right">
        <button id="change-repo-btn" className="toolbar-btn" onClick={onReset}>
          <RotateCcw size={14} />
          Change Repository
        </button>
      </div>
    </div>
  );
}
