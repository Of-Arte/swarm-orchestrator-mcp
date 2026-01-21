import React, { useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { useSwarmData } from '../hooks/useSwarmData';
import { ZoomIn, ZoomOut, Maximize } from 'lucide-react';

const KnowledgeGraph = () => {
  const { data, loading, error } = useSwarmData('/graph', 0); // Load once
  const graphRef = useRef();
  const [containerDimensions, setDimensions] = useState({ width: 800, height: 600 });
  const containerRef = useRef(null);

  useEffect(() => {
    const updateDims = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };

    window.addEventListener('resize', updateDims);
    updateDims();
    
    return () => window.removeEventListener('resize', updateDims);
  }, []);

  const getNodeColor = (node) => {
    switch (node.type) {
      case 'file': return '#3b82f6';   // Blue
      case 'class': return '#22c55e';  // Green
      case 'function': return '#f97316'; // Orange
      default: return '#94a3b8';
    }
  };

  const getNodeVal = (node) => {
    switch (node.type) {
      case 'file': return 8;
      case 'class': return 5;
      case 'function': return 3;
      default: return 3;
    }
  };

  if (loading) return <div className="page-content">Loading Knowledge Graph...</div>;
  if (error) return <div className="page-content">Error: {error}</div>;

  return (
    <div className="page-content" style={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
            <h1 className="gradient-text" style={{margin: 0}}>AI Knowledge Base</h1>
            <p style={{color: 'var(--text-secondary)', margin: '4px 0 0 0', fontSize: '0.9rem'}}>Semantic Map of Memories & Concepts</p>
        </div>
        <div style={{ display: 'flex', gap: '16px', fontSize: '0.9rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span style={{width: 10, height: 10, borderRadius: '50%', background: '#3b82f6'}}></span> Concept</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span style={{width: 10, height: 10, borderRadius: '50%', background: '#22c55e'}}></span> Entity</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span style={{width: 10, height: 10, borderRadius: '50%', background: '#f97316'}}></span> Relation</span>
        </div>
      </div>

      <div className="glass-panel graph-container" ref={containerRef} style={{ flex: 1, padding: 0, overflow: 'hidden', position: 'relative' }}>
         <ForceGraph2D
            ref={graphRef}
            width={containerDimensions.width}
            height={containerDimensions.height}
            graphData={data || { nodes: [], links: [] }}
            nodeLabel="name"
            nodeColor={getNodeColor}
            nodeVal={getNodeVal}
            linkColor={() => 'rgba(255,255,255,0.2)'}
            backgroundColor="rgba(0,0,0,0)"
            d3AlphaDecay={0.05}     // Slower decay = cleaner layout over time
            d3VelocityDecay={0.3}   // Lower friction
            onNodeClick={node => {
              graphRef.current.centerAt(node.x, node.y, 1000);
              graphRef.current.zoom(4, 2000);
            }}
          />
          
          <div style={{ position: 'absolute', bottom: 20, right: 20, display: 'flex', flexDirection: 'column', gap: 8 }}>
            <button className="glass-panel" style={{ padding: 8, cursor: 'pointer' }} onClick={() => graphRef.current.zoomIn()}>
              <ZoomIn size={20} />
            </button>
            <button className="glass-panel" style={{ padding: 8, cursor: 'pointer' }} onClick={() => graphRef.current.zoomOut()}>
              <ZoomOut size={20} />
            </button>
            <button className="glass-panel" style={{ padding: 8, cursor: 'pointer' }} onClick={() => graphRef.current.zoomToFit()}>
              <Maximize size={20} />
            </button>
          </div>
      </div>
    </div>
  );
};

export default KnowledgeGraph;
