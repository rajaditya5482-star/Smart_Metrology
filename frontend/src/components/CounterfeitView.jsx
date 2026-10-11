import React, { useState, useEffect } from 'react';
import { 
  QrCode, ShieldAlert, CheckCircle2, XCircle, AlertTriangle, 
  Building2, PlusCircle, RefreshCw, Copy, Store
} from 'lucide-react';

export default function CounterfeitView() {
  const [batches, setBatches] = useState([]);
  const [serialInput, setSerialInput] = useState('ABC001');
  const [shopName, setShopName] = useState('Om Sai General Store (Delhi)');
  const [scanResult, setScanResult] = useState(null);
  const [isScanning, setIsScanning] = useState(false);

  // New batch form
  const [newBatchId, setNewBatchId] = useState('');
  const [newProduct, setNewProduct] = useState('');
  const [newMfr, setNewMfr] = useState('');
  const [newMrp, setNewMrp] = useState('');
  const [newPrefix, setNewPrefix] = useState('BRD');

  const fetchBatches = async () => {
    try {
      const res = await fetch('/api/counterfeit/batches');
      const data = await res.json();
      setBatches(data);
    } catch (err) {
      console.error('Failed to load batches:', err);
    }
  };

  useEffect(() => {
    fetchBatches();
  }, []);

  const handleVerifySerial = async () => {
    if (!serialInput.trim()) return;
    setIsScanning(true);
    try {
      const formData = new FormData();
      formData.append('serial_id', serialInput.trim());
      formData.append('shop_name', shopName);

      const res = await fetch('/api/counterfeit/verify', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setScanResult(data);
      fetchBatches(); // Refresh scan count in table
    } catch (err) {
      console.error('Verification failed:', err);
    } finally {
      setIsScanning(false);
    }
  };

  const handleRegisterBatch = async (e) => {
    e.preventDefault();
    if (!newBatchId || !newProduct || !newMfr || !newMrp) {
      alert('Please fill all required fields');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('batch_id', newBatchId);
      formData.append('product_name', newProduct);
      formData.append('manufacturer_name', newMfr);
      formData.append('mrp', newMrp);
      formData.append('unit_count', '8');
      formData.append('prefix', newPrefix);

      const res = await fetch('/api/counterfeit/register', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.error) {
        alert(data.error);
      } else {
        alert(`Batch registered successfully with serials: ${data.serials_sample.join(', ')}...`);
        setNewBatchId('');
        setNewProduct('');
        setNewMfr('');
        setNewMrp('');
        fetchBatches();
      }
    } catch (err) {
      console.error('Registration failed:', err);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Important Architecture Clarification (Sections 13-15) */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
            <QrCode className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-purple-600">
              Extension Module • Sections 13–15
            </span>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight mt-0.5">
              Serialized Product Identity & Duplicate Scan Verification
            </h1>
            <p className="text-sm text-slate-600 mt-1 max-w-3xl leading-relaxed">
              <b>Important Architectural Boundary:</b> An image-based AI alone cannot guarantee a product is genuine if a counterfeiter physically duplicates an identical label. True authentication requires manufacturers to register serialized unique unit IDs before distribution, allowing inspectors to flag clone attacks when the same ID appears across multiple shops.
            </p>
          </div>
        </div>
      </div>

      {/* Grid: Inspector Serial Scanner & Duplicate Detector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Inspector Verification Simulator */}
        <div className="lg:col-span-6 space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Store className="w-4 h-4 text-blue-600" />
              <span>Shop Inspection Serial ID Scanner</span>
            </h2>
            <p className="text-xs text-slate-500">
              Simulate an inspector scanning a QR/barcode serial ID at a physical retail store.
            </p>

            <div className="space-y-3 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  Serial ID on Physical Unit
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={serialInput}
                    onChange={(e) => setSerialInput(e.target.value.toUpperCase())}
                    placeholder="e.g. ABC001"
                    className="w-full text-sm font-mono px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 font-bold"
                  />
                  <button
                    onClick={handleVerifySerial}
                    disabled={isScanning}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-bold shrink-0 transition shadow-sm"
                  >
                    {isScanning ? 'Checking...' : 'Verify ID'}
                  </button>
                </div>
              </div>

              {/* Quick Sample Serial Chips */}
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="text-slate-400 font-medium text-[11px]">Try ID:</span>
                <button
                  onClick={() => setSerialInput('ABC001')}
                  className="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded font-mono text-[11px] font-semibold text-slate-700"
                >
                  ABC001 (Genuine)
                </button>
                <button
                  onClick={() => setSerialInput('ABC002')}
                  className="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded font-mono text-[11px] font-semibold text-slate-700"
                >
                  ABC002 (Genuine)
                </button>
                <button
                  onClick={() => setSerialInput('FAKE999')}
                  className="px-2 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded font-mono text-[11px] font-semibold border border-rose-200"
                >
                  FAKE999 (Unregistered)
                </button>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  Inspected Retail Store Location
                </label>
                <input
                  type="text"
                  value={shopName}
                  onChange={(e) => setShopName(e.target.value)}
                  className="w-full text-sm px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              {/* Duplicate Simulation Helper */}
              <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl text-xs space-y-1.5">
                <span className="font-bold text-slate-700 block">
                  How to Demonstrate Duplicate Clone Detection:
                </span>
                <ol className="list-decimal list-inside text-slate-600 space-y-1 text-[11px]">
                  <li>Scan <b>ABC001</b> at <i>"Om Sai General Store (Delhi)"</i> → Confirmed Genuine.</li>
                  <li>Now change store to <i>"Gupta Grocery (Mumbai)"</i> and scan <b>ABC001</b> again.</li>
                  <li>The system immediately flags a <b>Duplicate Clone Alert</b> because the same physical unit cannot exist in two stores simultaneously!</li>
                </ol>
              </div>
            </div>

            {/* Scan Outcome Card */}
            {scanResult && (
              <div className="pt-2">
                {scanResult.verdict === 'VERIFIED_AUTHENTIC' && (
                  <div className="bg-emerald-50 border-2 border-emerald-300 rounded-xl p-4 flex items-start gap-3">
                    <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
                    <div className="space-y-1">
                      <h4 className="text-sm font-bold text-emerald-900">
                        GENUINE UNIT VERIFIED
                      </h4>
                      <p className="text-xs text-emerald-700">
                        {scanResult.message}
                      </p>
                      <div className="text-[11px] text-emerald-800 font-mono pt-1">
                        Product: {scanResult.product_name} • Mfr: {scanResult.manufacturer}
                      </div>
                    </div>
                  </div>
                )}

                {scanResult.verdict === 'DUPLICATE_SUSPICIOUS' && (
                  <div className="bg-rose-50 border-2 border-rose-400 rounded-xl p-4 flex items-start gap-3 animate-pulse">
                    <ShieldAlert className="w-6 h-6 text-rose-600 shrink-0 mt-0.5" />
                    <div className="space-y-1">
                      <h4 className="text-sm font-bold text-rose-900">
                        CRITICAL: DUPLICATE SERIAL CLONE DETECTED!
                      </h4>
                      <p className="text-xs text-rose-700 font-medium">
                        {scanResult.message}
                      </p>
                      <div className="text-[11px] text-rose-800 pt-1 font-mono">
                        Previous Scan: {scanResult.previous_shop} • Current Scan: {scanResult.current_shop}
                      </div>
                    </div>
                  </div>
                )}

                {scanResult.verdict === 'SUSPICIOUS_UNREGISTERED' && (
                  <div className="bg-amber-50 border-2 border-amber-300 rounded-xl p-4 flex items-start gap-3">
                    <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
                    <div className="space-y-1">
                      <h4 className="text-sm font-bold text-amber-900">
                        UNREGISTERED SERIAL ID
                      </h4>
                      <p className="text-xs text-amber-700">
                        {scanResult.message}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right: Manufacturer Registration Form */}
        <div className="lg:col-span-6 space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-purple-600" />
              <span>Manufacturer Batch & Serial Registration</span>
            </h2>
            <p className="text-xs text-slate-500">
              Legitimate manufacturers register batches and generate serialized unit IDs prior to shop delivery.
            </p>

            <form onSubmit={handleRegisterBatch} className="space-y-3 pt-2 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-600 mb-1">
                    Batch Identifier
                  </label>
                  <input
                    type="text"
                    value={newBatchId}
                    onChange={(e) => setNewBatchId(e.target.value)}
                    placeholder="e.g. B2026-10"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-600 mb-1">
                    Serial Prefix (3 letters)
                  </label>
                  <input
                    type="text"
                    maxLength={4}
                    value={newPrefix}
                    onChange={(e) => setNewPrefix(e.target.value.toUpperCase())}
                    placeholder="e.g. ROY"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg uppercase font-mono font-bold"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-600 mb-1">
                  Product Commodity Name
                </label>
                <input
                  type="text"
                  value={newProduct}
                  onChange={(e) => setNewProduct(e.target.value)}
                  placeholder="e.g. Royale Butter Cookies 500g"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-600 mb-1">
                    Manufacturer Entity
                  </label>
                  <input
                    type="text"
                    value={newMfr}
                    onChange={(e) => setNewMfr(e.target.value)}
                    placeholder="e.g. Royale Foods India Ltd"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-600 mb-1">
                    Maximum Retail Price (₹)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={newMrp}
                    onChange={(e) => setNewMrp(e.target.value)}
                    placeholder="e.g. 50"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-bold transition flex items-center justify-center gap-2"
              >
                <PlusCircle className="w-4 h-4 text-purple-400" />
                <span>Register Batch & Issue Serialized IDs</span>
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Registered Batches and Units Table */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900">
            Registered Manufacturer Batches & Tracked Serials
          </h2>
          <button
            onClick={fetchBatches}
            className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 font-semibold"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>

        <div className="space-y-4">
          {batches.map((b) => (
            <div
              key={b.batch_id}
              className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200/80 pb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-sm">
                      {b.product_name}
                    </span>
                    <span className="font-mono text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded font-bold">
                      Batch {b.batch_id}
                    </span>
                  </div>
                  <span className="text-xs text-slate-500">
                    {b.manufacturer_name} • MRP: ₹{b.mrp}
                  </span>
                </div>
                <span className="text-xs text-slate-400">
                  Total Units Issued: {b.total_units}
                </span>
              </div>

              {/* Serials Chips */}
              <div className="flex flex-wrap gap-2">
                {b.serials.map((s) => {
                  const isDuplicate = s.status === 'DUPLICATE_SUSPICIOUS';
                  const isScanned = s.scan_count > 0;
                  return (
                    <button
                      key={s.serial_id}
                      onClick={() => setSerialInput(s.serial_id)}
                      className={`text-xs font-mono px-2.5 py-1 rounded-md border flex items-center gap-1.5 transition ${
                        isDuplicate
                          ? 'border-rose-300 bg-rose-50 text-rose-800 font-bold'
                          : isScanned
                          ? 'border-emerald-300 bg-emerald-50 text-emerald-800'
                          : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                      }`}
                    >
                      <span>{s.serial_id}</span>
                      <span className="text-[10px] text-slate-400">
                        ({s.scan_count} scans)
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
