import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, AlertOctagon, Link as LinkIcon, RefreshCw, 
  Database, Lock, CheckCircle2, XCircle, ArrowRight, ShieldAlert
} from 'lucide-react';

export default function BlockchainAuditView() {
  const [blocks, setBlocks] = useState([]);
  const [records, setRecords] = useState([]);
  const [selectedRecordId, setSelectedRecordId] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [tamperLoading, setTamperLoading] = useState(false);

  const fetchBlocksAndRecords = async () => {
    try {
      const [bRes, rRes] = await Promise.all([
        fetch('/api/blockchain/blocks'),
        fetch('/api/records')
      ]);
      const bData = await bRes.json();
      const rData = await rRes.json();
      setBlocks(bData);
      setRecords(rData);

      if (rData.length > 0 && !selectedRecordId) {
        setSelectedRecordId(rData[0].id);
        verifyRecord(rData[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch blockchain data:', err);
    }
  };

  useEffect(() => {
    fetchBlocksAndRecords();
  }, []);

  const verifyRecord = async (recordId) => {
    setIsVerifying(true);
    try {
      const res = await fetch(`/api/records/${recordId}/verify-tamper`, { method: 'POST' });
      const data = await res.json();
      setVerificationResult(data);
    } catch (err) {
      console.error('Verification failed:', err);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleSimulateTamper = async () => {
    if (!selectedRecordId) return;
    setTamperLoading(true);
    try {
      const res = await fetch(`/api/records/${selectedRecordId}/simulate-tamper`, { method: 'POST' });
      const data = await res.json();
      setVerificationResult(data);
      fetchBlocksAndRecords();
    } catch (err) {
      console.error('Tamper simulation failed:', err);
    } finally {
      setTamperLoading(false);
    }
  };

  const handleRevertTamper = async () => {
    if (!selectedRecordId) return;
    setTamperLoading(true);
    try {
      const res = await fetch(`/api/records/${selectedRecordId}/revert-tamper`, { method: 'POST' });
      const data = await res.json();
      setVerificationResult(data);
      fetchBlocksAndRecords();
    } catch (err) {
      console.error('Revert failed:', err);
    } finally {
      setTamperLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Top Banner: Conceptual Clarification as Required by Project Document */}
      <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white p-6 rounded-2xl shadow-md border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
              Section 11 & 12 Implementation
            </span>
            <h1 className="text-2xl font-bold tracking-tight">
              Blockchain Tamper-Evident Audit Layer
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl">
              Blockchain does not replace the database or check laws. It acts as an immutable cryptographic notary: storing SHA-256 digital fingerprints so any post-inspection database modification is immediately caught.
            </p>
          </div>
          <button
            onClick={fetchBlocksAndRecords}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium transition self-start"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh Ledger</span>
          </button>
        </div>

        {/* Database vs Blockchain Distinction Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 pt-6 border-t border-slate-800 text-xs">
          <div className="bg-slate-800/60 border border-slate-700/60 p-4 rounded-xl flex items-start gap-3">
            <Database className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-slate-100 text-sm block mb-1">
                Database (SQL / Detailed Storage)
              </span>
              <p className="text-slate-400 leading-relaxed">
                Stores high-resolution packaging images, full OCR transcripts, manufacturer addresses, shop information, and formatted inspection PDF documents.
              </p>
            </div>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/60 p-4 rounded-xl flex items-start gap-3">
            <Lock className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-slate-100 text-sm block mb-1">
                Blockchain (Tamper-Evident Ledger)
              </span>
              <p className="text-slate-400 leading-relaxed">
                Stores only cryptographic SHA-256 fingerprints and linked block headers. Makes evidence tamper-evident; if someone alters records in the database, the hash comparison fails.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Tamper Detection Demonstration Lab */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-indigo-600" />
              <span>Live Tampering Demonstration Lab</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Select an inspection record and test how the blockchain catches unauthorized database modifications.
            </p>
          </div>

          {/* Record Selector */}
          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold text-slate-600">Select Case:</label>
            <select
              value={selectedRecordId || ''}
              onChange={(e) => {
                const id = Number(e.target.value);
                setSelectedRecordId(id);
                verifyRecord(id);
              }}
              className="text-xs px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 font-mono font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {records.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.inspection_id} ({r.shop_name} • {r.verdict})
                </option>
              ))}
            </select>
          </div>
        </div>

        {verificationResult && (
          <div className="space-y-6">
            {/* Integrity Status Alert */}
            {verificationResult.is_valid ? (
              <div className="bg-emerald-50 border-2 border-emerald-300 rounded-xl p-5 flex items-start gap-4">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <h3 className="text-base font-bold text-emerald-900">
                    RECORD IS AUTHENTIC & UNTAMPERED
                  </h3>
                  <p className="text-xs text-emerald-700">
                    The active database values perfectly match the cryptographic SHA-256 fingerprint anchored on Block #{verificationResult.block_index}. No unauthorized alterations detected.
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-rose-50 border-2 border-rose-400 rounded-xl p-5 flex items-start gap-4 animate-pulse">
                <AlertOctagon className="w-8 h-8 text-rose-600 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <h3 className="text-base font-bold text-rose-900 flex items-center gap-2">
                    <span>CRITICAL WARNING: RECORD TAMPERING DETECTED!</span>
                  </h3>
                  <p className="text-xs text-rose-700 font-medium">
                    The recalculated hash of the active database record DOES NOT MATCH the immutable block hash on the blockchain! Someone modified the database after the inspection was finalized.
                  </p>
                </div>
              </div>
            )}

            {/* Cryptographic Comparison Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              {/* Recorded Blockchain Hash */}
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                <div className="flex items-center justify-between font-sans">
                  <span className="font-bold text-slate-700 flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-emerald-600" />
                    Immutable Blockchain Hash (Block #{verificationResult.block_index})
                  </span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">
                    TRUSTED SOURCE
                  </span>
                </div>
                <div className="bg-white p-3 rounded-lg border border-slate-200 text-slate-800 break-all select-all font-semibold">
                  {verificationResult.recorded_blockchain_data_hash}
                </div>
                <div className="text-[11px] text-slate-500 font-sans">
                  MRP at time of block creation: <b>₹{verificationResult.original_recorded_payload?.mrp}</b>
                </div>
              </div>

              {/* Recalculated Active DB Hash */}
              <div className={`p-4 rounded-xl border space-y-2 ${
                verificationResult.is_valid
                  ? 'border-slate-200 bg-slate-50'
                  : 'border-rose-300 bg-rose-50/70'
              }`}>
                <div className="flex items-center justify-between font-sans">
                  <span className="font-bold text-slate-700 flex items-center gap-1.5">
                    <Database className="w-3.5 h-3.5 text-blue-600" />
                    Active Database Recalculated Hash
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                    verificationResult.is_valid
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-rose-100 text-rose-800'
                  }`}>
                    {verificationResult.is_valid ? 'SYNCHRONIZED' : 'MISMATCH DETECTED'}
                  </span>
                </div>
                <div className={`p-3 rounded-lg border break-all select-all font-semibold ${
                  verificationResult.is_valid
                    ? 'bg-white border-slate-200 text-slate-800'
                    : 'bg-white border-rose-300 text-rose-700 font-bold'
                }`}>
                  {verificationResult.current_recalculated_hash}
                </div>
                <div className="text-[11px] text-slate-500 font-sans flex items-center justify-between">
                  <span>Current MRP in Database: <b className={!verificationResult.is_valid ? 'text-rose-600 underline font-bold' : ''}>₹{verificationResult.current_db_payload?.mrp}</b></span>
                  {!verificationResult.is_valid && (
                    <span className="text-rose-600 font-bold text-[10px]">Tampered!</span>
                  )}
                </div>
              </div>
            </div>

            {/* Demonstration Action Buttons */}
            <div className="pt-2 flex flex-wrap items-center gap-3">
              {verificationResult.is_valid ? (
                <button
                  onClick={handleSimulateTamper}
                  disabled={tamperLoading}
                  className="flex items-center gap-2 px-4 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow-md shadow-rose-600/20 transition"
                >
                  <AlertOctagon className="w-4 h-4" />
                  <span>Simulate Database Tampering (e.g. Alter MRP to ₹35)</span>
                </button>
              ) : (
                <button
                  onClick={handleRevertTamper}
                  disabled={tamperLoading}
                  className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/20 transition"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Revert Modification & Restore Integrity</span>
                </button>
              )}
              <span className="text-xs text-slate-400">
                Click to demonstrate live to evaluators how blockchain proves tampering.
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Blockchain Blocks Explorer */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <LinkIcon className="w-4 h-4 text-blue-600" />
          <span>Immutable Ledger Block Sequence</span>
        </h2>

        <div className="space-y-3">
          {blocks.map((block) => (
            <div
              key={block.index}
              className="border border-slate-200 rounded-xl p-4 bg-slate-50/60 hover:bg-slate-50 transition font-mono text-xs space-y-2"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 font-sans text-xs">
                <span className="font-bold text-slate-900 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                  <span>Block #{block.index}</span>
                  {block.index === 0 && (
                    <span className="bg-blue-100 text-blue-800 text-[10px] px-2 py-0.5 rounded font-semibold font-mono">
                      GENESIS
                    </span>
                  )}
                </span>
                <span className="text-slate-400 text-[11px]">
                  Timestamp: {block.timestamp}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
                <div className="truncate">
                  <span className="text-slate-400">Prev Hash: </span>
                  <span className="text-slate-600">{block.previous_hash}</span>
                </div>
                <div className="truncate">
                  <span className="text-slate-400">Current Hash: </span>
                  <span className="text-indigo-600 font-semibold">{block.current_hash}</span>
                </div>
                <div className="truncate md:col-span-2">
                  <span className="text-slate-400">Payload Data Hash: </span>
                  <span className="text-slate-800 font-semibold">{block.data_hash}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
