import React, { useState } from 'react';
import { useSwarmData } from '../hooks/useSwarmData';
import TaskCard from '../components/TaskCard';
import { Filter } from 'lucide-react';

const TaskBoard = () => {
  const { data: tasks, loading, error } = useSwarmData('/tasks', 3000);
  const [filter, setFilter] = useState('ALL');

  if (loading) return <div className="page-content">Loading tasks...</div>;
  if (error) return <div className="page-content">Error loading tasks: {error}</div>;

  const filteredTasks = tasks ? tasks.filter(t => {
    if (filter === 'ALL') return true;
    return t.status === filter;
  }) : [];

  return (
    <div className="page-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h1 className="gradient-text" style={{margin: 0}}>Task Board</h1>
        
        <div className="glass-panel" style={{ padding: '8px', display: 'flex', gap: '8px', borderRadius: '12px' }}>
          {['ALL', 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED'].map(status => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              style={{
                background: filter === status ? 'rgba(255,255,255,0.1)' : 'transparent',
                border: 'none',
                color: filter === status ? '#fff' : 'var(--text-secondary)',
                padding: '8px 16px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '0.9rem',
                transition: 'all 0.2s'
              }}
            >
              {status === 'ALL' ? 'All Tasks' : status}
            </button>
          ))}
        </div>
      </div>

      {filteredTasks.length === 0 ? (
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <p>No tasks found with status: {filter}</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px' }}>
          {filteredTasks.map(task => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskBoard;
