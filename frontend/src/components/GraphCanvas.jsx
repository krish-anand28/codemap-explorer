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
import { LANG_COLORS, SIZE_COLORS } from '../constants';

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
