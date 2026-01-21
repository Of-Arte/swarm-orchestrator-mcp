import React, { useState, useEffect } from 'react';
import { Route, Link, useLocation } from 'wouter';
import { LayoutDashboard, Database, Network, ListChecks, Settings as SettingsIcon, Activity, Book } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './styles/design_system.css';
import './App.css';

import Overview from './views/Overview';
import TaskBoard from './views/TaskBoard';
import KnowledgeGraph from './views/KnowledgeGraph';
import DocsPage from './views/DocsPage';
import Memory from './views/Memory';
import Settings from './views/Settings';

import { useSwarmData } from './hooks/useSwarmData';

function App() {
  const [location] = useLocation();
  const { data: status } = useSwarmData('/status');
  const isDemo = status?.status === 'demo';

  return (
    <div className="app-container">
      {/* Sidebar */}
      <nav className="glass-panel side-nav">
        <div className="nav-logo">
          <div className="logo-icon glass-panel">S</div>
          <div style={{display: 'flex', flexDirection: 'column'}}>
            <span className="logo-text">SWARM</span>
            {isDemo && <span style={{fontSize: '0.7rem', color: '#f59e0b', fontWeight: 'bold'}}>DEMO MODE</span>}
          </div>
        </div>
        
        <ul className="nav-links">
          <li>
            <Link href="/">
              <a className={location === '/' ? 'active' : ''}>
                <LayoutDashboard size={20} />
                <span>Overview</span>
              </a>
            </Link>
          </li>
          <li>
            <Link href="/tasks">
              <a className={location === '/tasks' ? 'active' : ''}>
                <ListChecks size={20} />
                <span>Task Board</span>
              </a>
            </Link>
          </li>
          <li>
            <Link href="/graph">
              <a className={location === '/graph' ? 'active' : ''}>
                <Network size={20} />
                <span>AI Knowledge Base</span>
              </a>
            </Link>
          </li>
          <li>
            <Link href="/memory">
              <a className={location === '/memory' ? 'active' : ''}>
                <Database size={20} />
                <span>Memory</span>
              </a>
            </Link>
          </li>
          <li>
            <Link href="/docs">
              <a className={location === '/docs' ? 'active' : ''}>
                <Book size={20} />
                <span>Documentation</span>
              </a>
            </Link>
          </li>
        </ul>

        <div className="nav-footer">
          <Link href="/settings">
            <a className={location === '/settings' ? 'active' : ''}>
              <SettingsIcon size={20} />
              <span>Settings</span>
            </a>
          </Link>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-viewport">
        <AnimatePresence mode="wait">
          <motion.div
            key={location}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            style={{ height: '100%' }}
          >
            <Route path="/" component={Overview} />
            <Route path="/graph" component={KnowledgeGraph} />
            <Route path="/tasks" component={TaskBoard} />
            <Route path="/docs" component={DocsPage} />
            <Route path="/memory" component={Memory} />
            <Route path="/settings" component={Settings} />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
