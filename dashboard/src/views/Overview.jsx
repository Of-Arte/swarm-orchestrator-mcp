import React from 'react';
import { Activity, ListChecks, Network, Clock } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import StatCard from '../components/StatCard';
import { useSwarmData } from '../hooks/useSwarmData';

const Overview = () => {
  const { data: status, loading, error } = useSwarmData('/status');
  
  // Placeholder data for chart until we have historical metrics
  const mockChartData = [
    { name: '10:00', load: 20 },
    { name: '10:05', load: 35 },
    { name: '10:10', load: 25 },
    { name: '10:15', load: 45 },
    { name: '10:20', load: 30 },
    { name: '10:25', load: 60 },
    { name: '10:30', load: 45 },
  ];

  if (loading) return <div className="page-content">Loading Swarm status...</div>;
  if (error) return <div className="page-content" style={{color: '#ef4444'}}>Error: {error}. Is specific polling active?</div>;

  return (
    <div className="page-content">
      <h1 className="gradient-text">Swarm Overview</h1>
      
      <div className="stats-grid">
        <StatCard 
          icon={Activity} 
          label="System Status" 
          value={status.status === 'online' ? 'Active' : 'Offline'} 
          color="#6366f1" 
          delay={0}
        />
        <StatCard 
          icon={ListChecks} 
          label="Tasks Completed" 
          value={status.tasks_completed} 
          color="#a855f7" 
          delay={0.1}
        />
        <StatCard 
          icon={Clock} 
          label="Pending Tasks" 
          value={Math.max(0, status.tasks_total - status.tasks_completed)} 
          color="#ec4899" 
          delay={0.2}
        />
         <StatCard 
          icon={Network} 
          label="Graph Nodes" 
          value={status.memory_nodes || 'N/A'} 
          color="#22d3ee" 
          delay={0.3}
        />
      </div>

      <div className="glass-panel dashboard-chart">
        <h2 style={{marginBottom: '20px'}}>System Load</h2>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <AreaChart data={mockChartData}>
              <defs>
                <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e2029', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Area type="monotone" dataKey="load" stroke="#6366f1" fillOpacity={1} fill="url(#colorLoad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Overview;
