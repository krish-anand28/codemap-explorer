import { useCallback, useMemo, useEffect } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const LANG_COLORS = {
  Python: '#3b82f6',
  JavaScript: '#eab308',
  TypeScript: '#06b6d4',
  Java: '#ef4444',
  Go: '#14b8a6',
  Ruby: '#dc2626',
  Rust: '#f97316',
  'C': '#a855f7',
  'C++': '#a855f7',
  'C#': '#22c55e',
  PHP: '#8b5cf6',
  Swift: '#f97316',
  Kotlin: '#a855f7',
  HTML: '#f97316',
  CSS: '#3b82f6',
  SCSS: '#ec4899',
  Shell: '#22c55e',
  Markdown: '#71717a',
  JSON: '#eab308',
  YAML: '#ef4444',
};

const SIZE_COLORS = {
  small: '#10b981',
  medium: '#f59e0b',
  large: '#ef4444',
};

function CustomNode({ data, selected }) {
  const langColor = LANG_COLORS[data.language] || '#71717a';
  const sizeColor = SIZE_COLORS[data.size_category] || '#71717a';

  return (
    <div className={`custom-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Top} style={{ background: 'transparent', border: 'none' }} />
      <div className="node-header">
        <span className="node-icon" style={{ backgroundColor: langColor }} />
        <span className="node-filename">{data.label}</span>
      </div>
      <div className="node-meta">
        <span>{data.lines_of_code} LOC</span>
        <span className="node-lang-text" style={{ color: langColor }}>{data.language}</span>
      </div>
      <div className="node-size-bar" style={{ backgroundColor: sizeColor }} />
      <Handle type="source" position={Position.Bottom} style={{ background: 'transparent', border: 'none' }} />
    </div>
  );
}

export default function GraphCanvas({ nodes: initialNodes, edges: initialEdges, onNodeSelect }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const nodeTypes = useMemo(() => ({ customNode: CustomNode }), []);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const onNodeClick = useCallback((event, node) => {
    if (onNodeSelect) onNodeSelect(node);
  }, [onNodeSelect]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      nodeTypes={nodeTypes}
      fitView
      minZoom={0.1}
      maxZoom={2}
      defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
    >
      <Background color="#333" gap={20} size={1} variant="dots" />
      <Controls
        style={{ backgroundColor: '#1a1a2e', borderColor: '#2a2a3e' }}
      />
      <MiniMap
        nodeColor={(node) => LANG_COLORS[node.data?.language] || '#71717a'}
        maskColor="rgba(0, 0, 0, 0.7)"
        style={{ backgroundColor: '#12121a' }}
      />
    </ReactFlow>
  );
}
