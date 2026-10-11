import React, { useState, useEffect } from 'react';
import { 
  BarChart3, CheckCircle2, XCircle, AlertTriangle, 
  FileText, Search, ShieldCheck, ArrowUpRight, Filter
} from 'lucide-react';

export default function DashboardView({ onSelectRecord }) {
  const [records, setRecords] = useState([]);
  const [stats, setStats] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterVerdict, setFilterVerdict] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [rRes, sRes] = await Promise.all([
        fetch('/api/records'),
        fetch('/api/stats')
      ]);
      const rData = await rRes.json();
      const sData = await sRes.json();
      setRecords(rData);
      setStats(sData);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredRecords = records.filter((r) => {
    const matchesSearch =
      r.inspection_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.shop_name && r.shop_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (r.inspector_id && r.inspector_id.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesFilter = filterVerdict === 'ALL' || r.verdict === filterVerdict;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-8 pb-12">
      {/* Top Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Legal Metrology Inspection Analytics
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Live statutory enforcement statistics, compliance ratios, and historical case logs.
            </p>
          </div>
          <button
            onClick={fetchData}
            className="px-3.5 py-2 border border-slate-200 hover:bg-slate-50 rounded-lg text-xs font-semibold text-slate-700 transition"
          >
            Refresh Analytics
          </button>
        </div>

        {/* Metric Cards */}
        {stats && (
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mt-6 pt-6 border-t border-slate-100">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <span className="text-xs font-semibold text-slate-500 block">
                Total Inspections
              </span>
              <span className="text-2xl font-extrabold text-slate-900 mt-1 block">
                {stats.total_inspections}
              </span>
              <span className="text-[11px] text-slate-400">All registered cases</span>
            </div>

            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200/80">
              <span className="text-xs font-semibold text-emerald-800 block flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Compliant (PASS)</span>
              </span>
              <span className="text-2xl font-extrabold text-emerald-900 mt-1 block">
                {stats.passed}
              </span>
              <span className="text-[11px] text-emerald-700">No violations found</span>
            </div>

            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200/80">
              <span className="text-xs font-semibold text-rose-800 block flex items-center gap-1">
                <XCircle className="w-3.5 h-3.5" />
                <span>Violations (FAIL)</span>
              </span>
              <span className="text-2xl font-extrabold text-rose-900 mt-1 block">
                {stats.failed}
              </span>
              <span className="text-[11px] text-rose-700">Actionable infractions</span>
            </div>

            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200/80">
              <span className="text-xs font-semibold text-amber-800 block flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Under Review</span>
              </span>
              <span className="text-2xl font-extrabold text-amber-900 mt-1 block">
                {stats.review}
              </span>
              <span className="text-[11px] text-amber-700">Unclear / blurry OCR</span>
            </div>

            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200/80">
              <span className="text-xs font-semibold text-blue-800 block">
                Compliance Rate
              </span>
              <span className="text-2xl font-extrabold text-blue-900 mt-1 block">
                {stats.compliance_rate}%
              </span>
              <span className="text-[11px] text-blue-700">Passing percentage</span>
            </div>
          </div>
        )}
      </div>

      {/* Top Violations Chart & Overview */}
      {stats && stats.top_violations && stats.top_violations.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <h2 className="text-base font-bold text-slate-900 mb-4">
            Most Frequent Legal Metrology Infractions
          </h2>
          <div className="space-y-3">
            {stats.top_violations.map((v, i) => (
              <div key={i} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-700">
                  <span>{v.title}</span>
                  <span className="font-mono text-rose-600">{v.count} occurrences</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-rose-500 h-2 rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.min(100, (v.count / stats.total_inspections) * 100)}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Historical Records Table */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h2 className="text-base font-bold text-slate-900">
            Inspection Case History Log ({filteredRecords.length})
          </h2>

          <div className="flex items-center gap-3">
            {/* Search Input */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search case, shop, officer..."
                className="text-xs pl-9 pr-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 w-48 sm:w-64"
              />
            </div>

            {/* Verdict Filter */}
            <select
              value={filterVerdict}
              onChange={(e) => setFilterVerdict(e.target.value)}
              className="text-xs px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="PASS">PASS Only</option>
              <option value="FAIL">FAIL Only</option>
              <option value="REVIEW">REVIEW Only</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Photo</th>
                <th className="py-3 px-4">Inspection ID</th>
                <th className="py-3 px-4">Date & Time</th>
                <th className="py-3 px-4">Shop Name</th>
                <th className="py-3 px-4">Declared MRP</th>
                <th className="py-3 px-4">Net Qty</th>
                <th className="py-3 px-4">Verdict</th>
                <th className="py-3 px-4">Ledger Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredRecords.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50/70 transition">
                  <td className="py-2.5 px-4">
                    {r.thumbnail ? (
                      <img
                        src={r.thumbnail}
                        alt="Product"
                        className="w-10 h-10 object-cover rounded-md border border-slate-200"
                      />
                    ) : (
                      <div className="w-10 h-10 bg-slate-100 rounded-md" />
                    )}
                  </td>
                  <td className="py-2.5 px-4 font-mono font-bold text-slate-900">
                    {r.inspection_id}
                  </td>
                  <td className="py-2.5 px-4 whitespace-nowrap text-slate-500">
                    {new Date(r.timestamp).toLocaleString()}
                  </td>
                  <td className="py-2.5 px-4 font-medium text-slate-800">
                    {r.shop_name || 'N/A'}
                  </td>
                  <td className="py-2.5 px-4 font-semibold text-slate-900">
                    {r.mrp ? `₹${r.mrp}` : '—'}
                  </td>
                  <td className="py-2.5 px-4 text-slate-600">
                    {r.net_quantity || '—'}
                  </td>
                  <td className="py-2.5 px-4">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                        r.verdict === 'PASS'
                          ? 'bg-emerald-100 text-emerald-800'
                          : r.verdict === 'FAIL'
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {r.verdict}
                    </span>
                  </td>
                  <td className="py-2.5 px-4">
                    {r.is_tampered ? (
                      <span className="text-[10px] font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-200 flex items-center gap-1 w-max">
                        <XCircle className="w-3 h-3" />
                        <span>TAMPERED</span>
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex items-center gap-1 w-max">
                        <ShieldCheck className="w-3 h-3" />
                        <span>Block #{r.block_index}</span>
                      </span>
                    )}
                  </td>
                  <td className="py-2.5 px-4 text-right">
                    <a
                      href={`/api/reports/${r.id}/pdf`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-semibold"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>PDF</span>
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredRecords.length === 0 && (
            <div className="p-8 text-center text-slate-400 text-xs">
              No matching inspection records found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
