import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import InspectionView from './components/InspectionView';
import DashboardView from './components/DashboardView';
import BlockchainAuditView from './components/BlockchainAuditView';
import CounterfeitView from './components/CounterfeitView';

export default function App() {
  const [activeTab, setActiveTab] = useState('inspect');
  const [stats, setStats] = useState(null);

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/stats');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        stats={stats}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'inspect' && (
          <InspectionView
            onInspectionComplete={fetchStats}
            onNavigateBlockchain={() => setActiveTab('blockchain')}
          />
        )}
        {activeTab === 'dashboard' && <DashboardView />}
        {activeTab === 'blockchain' && <BlockchainAuditView />}
        {activeTab === 'counterfeit' && <CounterfeitView />}
      </main>

      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 space-y-1">
          <p className="font-semibold text-slate-700">
            SmartMetrology • AI-Assisted Legal Metrology Compliance Inspection & Tamper-Evident Ledger
          </p>
          <p className="text-slate-400">
            Compliant with Legal Metrology (Packaged Commodities) Rules, 2011 • Built for Smart India Hackathon
          </p>
        </div>
      </footer>
    </div>
  );
}
