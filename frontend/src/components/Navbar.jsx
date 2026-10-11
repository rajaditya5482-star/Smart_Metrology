import React from 'react';
import { Shield, ScanLine, BarChart3, Link as LinkIcon, QrCode, Sparkles } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, stats }) {
  const navItems = [
    { id: 'inspect', label: 'New Inspection', icon: ScanLine },
    { id: 'dashboard', label: 'Dashboard & Records', icon: BarChart3 },
    { id: 'blockchain', label: 'Blockchain Audit Lab', icon: LinkIcon },
    { id: 'counterfeit', label: 'Counterfeit Verifier', icon: QrCode },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Department Title */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('inspect')}>
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-white">SmartMetrology</span>
                <span className="bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs px-2 py-0.5 rounded-full font-medium">
                  v1.0 • SIH
                </span>
              </div>
              <p className="text-xs text-slate-400 font-normal hidden sm:block">
                Legal Metrology Compliance & Tamper-Evident Ledger
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Blockchain & Status Indicator */}
          <div className="hidden lg:flex items-center space-x-3">
            <div className="flex items-center space-x-2 bg-slate-800/80 border border-slate-700/60 rounded-full px-3 py-1 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300 font-mono">
                Ledger: {stats?.blocks_mined ?? 1} Blocks
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
