import React, { useState, useEffect } from 'react';
import { 
  Upload, CheckCircle, AlertTriangle, XCircle, FileText, 
  ShieldCheck, ArrowRight, RefreshCw, Eye, Sparkles, AlertCircle,
  HelpCircle, ExternalLink, ScanLine
} from 'lucide-react';

export default function InspectionView({ onInspectionComplete, onNavigateBlockchain }) {
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState(null);
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  
  // Form state
  const [shopName, setShopName] = useState('Om Sai General Store');
  const [shopLocation, setShopLocation] = useState('Karol Bagh, New Delhi');
  const [sellingPrice, setSellingPrice] = useState('');
  const [inspectorId, setInspectorId] = useState('INSP-LM-DELHI-408');

  // Execution state
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [inspectionResult, setInspectionResult] = useState(null);
  const [activeImageTab, setActiveImageTab] = useState('annotated');

  // Fetch pre-bundled sample packages
  useEffect(() => {
    fetch('/api/samples')
      .then((res) => res.json())
      .then((data) => {
        setSamples(data);
        if (data.length > 0 && !selectedSample && !previewUrl) {
          // Pre-select first sample for instant demo
          handleSelectSample(data[0]);
        }
      })
      .catch((err) => console.error('Failed to load sample packages:', err));
  }, []);

  const handleSelectSample = (sample) => {
    setSelectedSample(sample);
    setFile(null);
    setPreviewUrl(sample.image_url);
    if (sample.default_selling_price) {
      setSellingPrice(sample.default_selling_price);
    } else {
      setSellingPrice('');
    }
    setInspectionResult(null);
  };

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      setSelectedSample(null);
      setPreviewUrl(URL.createObjectURL(uploadedFile));
      setInspectionResult(null);
    }
  };

  const handleRunInspection = async () => {
    if (!file && !selectedSample) {
      alert('Please upload an image or choose one of the sample packages.');
      return;
    }

    setIsLoading(true);
    setLoadingStep(1);

    const stepInterval = setInterval(() => {
      setLoadingStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 450);

    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    } else if (selectedSample) {
      formData.append('sample_filename', selectedSample.filename);
    }
    formData.append('shop_name', shopName);
    formData.append('shop_location', shopLocation);
    if (sellingPrice) {
      formData.append('selling_price', sellingPrice);
    }
    formData.append('inspector_id', inspectorId);

    try {
      const response = await fetch('/api/inspect', {
        method: 'POST',
        body: formData,
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Inspection failed');
      }

      const data = await response.json();
      setInspectionResult(data);
      if (onInspectionComplete) onInspectionComplete();
    } catch (err) {
      clearInterval(stepInterval);
      alert('Error during inspection: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const renderVerdictBadge = (verdict) => {
    if (verdict === 'PASS') {
      return (
        <div className="flex items-center space-x-2 bg-emerald-500 text-white px-4 py-2 rounded-xl shadow-lg shadow-emerald-500/20 font-bold text-lg">
          <CheckCircle className="w-6 h-6" />
          <span>PASS • COMPLIANT</span>
        </div>
      );
    } else if (verdict === 'FAIL') {
      return (
        <div className="flex items-center space-x-2 bg-rose-600 text-white px-4 py-2 rounded-xl shadow-lg shadow-rose-600/20 font-bold text-lg">
          <XCircle className="w-6 h-6" />
          <span>FAIL • VIOLATION DETECTED</span>
        </div>
      );
    } else {
      return (
        <div className="flex items-center space-x-2 bg-amber-500 text-white px-4 py-2 rounded-xl shadow-lg shadow-amber-500/20 font-bold text-lg">
          <AlertTriangle className="w-6 h-6" />
          <span>REVIEW • UNCERTAIN / BLURRY</span>
        </div>
      );
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Page Title & Subhead */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <span>Legal Metrology Compliance Inspector</span>
              <span className="text-xs font-semibold uppercase tracking-wider bg-blue-100 text-blue-800 px-2.5 py-1 rounded-md">
                Rules 2011
              </span>
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Upload or capture a packaged commodity label. The system extracts declarations via AI & OCR, checks statutory rules, and creates an immutable blockchain audit receipt.
            </p>
          </div>
          {inspectionResult && (
            <div className="flex items-center gap-3">
              <a
                href={inspectionResult.report_pdf_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-sm font-medium shadow transition"
              >
                <FileText className="w-4 h-4 text-rose-400" />
                <span>Download Official PDF Notice</span>
              </a>
            </div>
          )}
        </div>

        {/* 1-Click Test Scenarios Bar */}
        <div className="mt-6 pt-5 border-t border-slate-100">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              1-Click Presentation & Test Fixtures:
            </span>
            <span className="text-xs text-slate-400 hidden sm:inline">
              Click any scenario below to test instantly without uploading
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
            {samples.map((s) => {
              const isSelected = selectedSample?.id === s.id;
              const isPass = s.expected_verdict === 'PASS';
              const isFail = s.expected_verdict === 'FAIL';
              return (
                <button
                  key={s.id}
                  onClick={() => handleSelectSample(s)}
                  className={`p-2.5 rounded-xl border text-left transition-all relative overflow-hidden ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50/70 shadow-sm ring-2 ring-blue-500/20'
                      : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        isPass
                          ? 'bg-emerald-100 text-emerald-800'
                          : isFail
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {s.expected_verdict}
                    </span>
                    {isSelected && (
                      <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                    )}
                  </div>
                  <div className="text-xs font-semibold text-slate-800 line-clamp-1">
                    {s.name.split('(')[0].trim()}
                  </div>
                  <div className="text-[11px] text-slate-500 line-clamp-2 mt-0.5">
                    {s.description}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Inspection Workflow Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Image Ingest & Inspection Parameters */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center justify-between">
              <span>Packaging Photograph</span>
              {selectedSample && (
                <span className="text-xs text-blue-600 font-normal">
                  Preloaded Sample Active
                </span>
              )}
            </h2>

            {/* Image Preview Box / Drag and Drop */}
            <div className="relative group border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-xl overflow-hidden bg-slate-50 min-h-[220px] flex flex-col items-center justify-center p-3 text-center transition">
              {previewUrl ? (
                <div className="relative w-full h-[220px] flex items-center justify-center">
                  <img
                    src={previewUrl}
                    alt="Packaging preview"
                    className="max-h-full max-w-full object-contain rounded-lg shadow-sm"
                  />
                  <div className="absolute inset-0 bg-slate-900/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center rounded-lg">
                    <label className="cursor-pointer bg-white text-slate-800 px-3 py-1.5 rounded-lg text-xs font-medium shadow-md">
                      Change Photo
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={handleFileChange}
                      />
                    </label>
                  </div>
                </div>
              ) : (
                <label className="cursor-pointer flex flex-col items-center p-4 w-full">
                  <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                    <Upload className="w-6 h-6" />
                  </div>
                  <span className="text-sm font-medium text-slate-700">
                    Upload packaged commodity image
                  </span>
                  <span className="text-xs text-slate-400 mt-1">
                    Supports JPG, PNG, WEBP (Direct camera upload supported)
                  </span>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </label>
              )}
            </div>

            {/* Inspection Context Fields */}
            <div className="mt-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  Shop / Retail Establishment Name
                </label>
                <input
                  type="text"
                  value={shopName}
                  onChange={(e) => setShopName(e.target.value)}
                  className="w-full text-sm px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Metro Supermarket"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  Location / Zone
                </label>
                <input
                  type="text"
                  value={shopLocation}
                  onChange={(e) => setShopLocation(e.target.value)}
                  className="w-full text-sm px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. Connaught Place, New Delhi"
                />
              </div>

              <div className="bg-amber-50/60 border border-amber-200/80 rounded-xl p-3">
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-bold text-amber-900 flex items-center gap-1">
                    <span>Actual Selling Price Charged (₹)</span>
                    <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
                  </label>
                  <span className="text-[10px] text-amber-700 bg-amber-100/80 px-1.5 py-0.5 rounded font-medium">
                    Sec 36(1) Check
                  </span>
                </div>
                <input
                  type="number"
                  step="0.5"
                  value={sellingPrice}
                  onChange={(e) => setSellingPrice(e.target.value)}
                  className="w-full text-sm px-3 py-2 border border-amber-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-amber-500 font-semibold text-slate-800"
                  placeholder="Enter shop selling price to test overcharging"
                />
                <p className="text-[11px] text-amber-700/90 mt-1 leading-relaxed">
                  As noted in Section 10: An image alone cannot know the shopkeeper's price. Enter the price charged to test anti-overcharging compliance!
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  Inspector Credential ID
                </label>
                <input
                  type="text"
                  value={inspectorId}
                  onChange={(e) => setInspectorId(e.target.value)}
                  className="w-full text-sm px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 text-slate-600"
                />
              </div>

              <button
                onClick={handleRunInspection}
                disabled={isLoading}
                className={`w-full py-3 px-4 rounded-xl font-bold text-sm text-white shadow-lg flex items-center justify-center space-x-2 transition ${
                  isLoading
                    ? 'bg-blue-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/20'
                }`}
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Processing Pipeline...</span>
                  </>
                ) : (
                  <>
                    <ScanLine className="w-5 h-5" />
                    <span>Execute Legal Compliance Check</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Dynamic Pipeline Status & Inspection Results */}
        <div className="lg:col-span-8 space-y-6">
          {isLoading && (
            <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm flex flex-col items-center justify-center text-center min-h-[400px]">
              <div className="w-16 h-16 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mb-4 animate-bounce">
                <ScanLine className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">
                Running Legal Metrology Pipeline
              </h3>
              <p className="text-sm text-slate-500 max-w-md mb-6">
                Executing computer vision enhancement, RapidOCR neural inference, declaration parsing, and statutory rule evaluation.
              </p>

              {/* Progress Steps */}
              <div className="w-full max-w-md space-y-3 text-left">
                {[
                  '1. Computer Vision: CLAHE contrast enhancement & blur variance',
                  '2. Deep Learning OCR: Text detection & bounding coordinates',
                  '3. Information Structuring: Extracting MRP, Net Qty, Mfg details',
                  '4. Rule-Based Engine: Validating against Legal Metrology Rules 2011',
                  '5. Tamper-Proof Audit: Calculating SHA-256 fingerprint & mining block',
                ].map((step, idx) => {
                  const isDone = loadingStep > idx;
                  const isCurrent = loadingStep === idx;
                  return (
                    <div
                      key={idx}
                      className={`flex items-center space-x-3 text-xs font-medium p-2 rounded-lg transition ${
                        isDone
                          ? 'text-emerald-700 bg-emerald-50'
                          : isCurrent
                          ? 'text-blue-700 bg-blue-50 ring-1 ring-blue-400 font-semibold'
                          : 'text-slate-400 bg-slate-50'
                      }`}
                    >
                      {isDone ? (
                        <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                      ) : isCurrent ? (
                        <RefreshCw className="w-4 h-4 text-blue-600 animate-spin shrink-0" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                      )}
                      <span>{step}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {!isLoading && !inspectionResult && (
            <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-sm min-h-[400px] flex flex-col items-center justify-center">
              <div className="w-16 h-16 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mb-4">
                <ShieldCheck className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-1">
                Ready for Inspection
              </h3>
              <p className="text-sm text-slate-500 max-w-md">
                Select one of the pre-loaded packaging samples above or upload your own product photo, then click <b>Execute Legal Compliance Check</b>.
              </p>
            </div>
          )}

          {!isLoading && inspectionResult && (
            <div className="space-y-6">
              {/* Outcome Header Banner */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <span className="text-xs font-mono text-slate-400">
                      CASE ID: {inspectionResult.inspection_id}
                    </span>
                    <h2 className="text-xl font-bold text-slate-900">
                      Inspection Determination Summary
                    </h2>
                  </div>
                  {renderVerdictBadge(inspectionResult.verdict)}
                </div>

                {/* Violation Alerts or Pass Messages */}
                <div className="mt-4 pt-4 border-t border-slate-100">
                  {inspectionResult.verdict === 'PASS' && (
                    <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 p-4 rounded-xl flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-bold">
                          All Mandatory Legal Metrology Declarations Satisfied
                        </h4>
                        <p className="text-xs text-emerald-700 mt-0.5">
                          Maximum Retail Price with tax declaration, standard metric net quantity, manufacturer name & address, and packing date are compliant with Legal Metrology (Packaged Commodities) Rules, 2011.
                        </p>
                      </div>
                    </div>
                  )}

                  {inspectionResult.verdict === 'FAIL' && (
                    <div className="bg-rose-50 border border-rose-200 text-rose-900 p-4 rounded-xl space-y-2">
                      <div className="flex items-center gap-2 font-bold text-sm text-rose-800">
                        <XCircle className="w-5 h-5 text-rose-600 shrink-0" />
                        <span>Definite Compliance Violations Identified ({inspectionResult.violations.length}):</span>
                      </div>
                      <ul className="list-disc list-inside text-xs space-y-1 text-rose-800 pl-1">
                        {inspectionResult.violations.map((v, i) => (
                          <li key={i}>
                            <span className="font-semibold">{v.title}</span> ({v.rule}): {v.description}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {inspectionResult.verdict === 'REVIEW' && (
                    <div className="bg-amber-50 border border-amber-200 text-amber-900 p-4 rounded-xl space-y-2">
                      <div className="flex items-center gap-2 font-bold text-sm text-amber-800">
                        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                        <span>System Uncertainty — Sent for Human Inspector Review ({inspectionResult.review_reasons.length}):</span>
                      </div>
                      <ul className="list-disc list-inside text-xs space-y-1 text-amber-800 pl-1">
                        {inspectionResult.review_reasons.map((r, i) => (
                          <li key={i}>
                            <span className="font-semibold">{r.title}</span>: {r.description}
                          </li>
                        ))}
                      </ul>
                      <p className="text-[11px] text-amber-700 italic pt-1">
                        As detailed in Section 7 of the specification: The system avoids blindly making a final enforcement decision when packaging is curved or image quality is uncertain.
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Visual Evidence Card with Mode Switching */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    <Eye className="w-4 h-4 text-blue-600" />
                    <span>Computer Vision & Label Localization</span>
                  </h3>
                  {/* Mode Tabs */}
                  <div className="flex bg-slate-100 p-1 rounded-lg text-xs font-semibold">
                    <button
                      onClick={() => setActiveImageTab('annotated')}
                      className={`px-3 py-1 rounded-md transition ${
                        activeImageTab === 'annotated'
                          ? 'bg-white text-blue-600 shadow-sm'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      Detected Labels
                    </button>
                    <button
                      onClick={() => setActiveImageTab('enhanced')}
                      className={`px-3 py-1 rounded-md transition ${
                        activeImageTab === 'enhanced'
                          ? 'bg-white text-blue-600 shadow-sm'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      CV Enhanced
                    </button>
                    <button
                      onClick={() => setActiveImageTab('original')}
                      className={`px-3 py-1 rounded-md transition ${
                        activeImageTab === 'original'
                          ? 'bg-white text-blue-600 shadow-sm'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      Original
                    </button>
                  </div>
                </div>

                <div className="relative rounded-xl overflow-hidden bg-slate-900 flex items-center justify-center min-h-[300px] max-h-[420px] p-2">
                  <img
                    src={inspectionResult.images[activeImageTab]}
                    alt="Packaging inspection view"
                    className="max-h-[400px] w-auto object-contain rounded-lg shadow-inner"
                  />
                  <div className="absolute bottom-3 left-3 bg-slate-900/80 backdrop-blur-sm border border-slate-700/80 rounded-lg px-2.5 py-1 text-[11px] text-slate-300 font-mono flex items-center gap-3">
                    <span>Blur Var: {inspectionResult.cv_metrics.blur_variance}</span>
                    <span>OCR Conf: {Math.round(inspectionResult.ocr.mean_confidence * 100)}%</span>
                    <span>Lines: {inspectionResult.ocr.lines_detected}</span>
                  </div>
                </div>
              </div>

              {/* Extracted Declarations Table */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <h3 className="text-base font-bold text-slate-900 mb-4">
                  Extracted Statutory Declarations
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    {
                      label: 'Generic Commodity Name',
                      rule: 'Rule 6(1)(a)',
                      value: inspectionResult.extracted_data.product_name?.value || 'Not isolated',
                      status: inspectionResult.extracted_data.product_name?.status,
                    },
                    {
                      label: 'Maximum Retail Price (MRP)',
                      rule: 'Rule 6(1)(e)',
                      value: inspectionResult.extracted_data.mrp?.value
                        ? `₹ ${inspectionResult.extracted_data.mrp.value} (${
                            inspectionResult.extracted_data.mrp.inclusive_of_taxes
                              ? 'Incl. of all taxes'
                              : 'Taxes missing'
                          })`
                        : 'Missing / Unreadable',
                      status: inspectionResult.extracted_data.mrp?.status,
                    },
                    {
                      label: 'Net Quantity & Units',
                      rule: 'Rule 6(1)(b)',
                      value: inspectionResult.extracted_data.net_quantity?.value
                        ? `${inspectionResult.extracted_data.net_quantity.value} ${inspectionResult.extracted_data.net_quantity.unit}`
                        : 'Missing / Unreadable',
                      status: inspectionResult.extracted_data.net_quantity?.status,
                    },
                    {
                      label: 'Date of Mfg / Packing',
                      rule: 'Rule 6(1)(d)',
                      value: inspectionResult.extracted_data.mfg_date?.value || 'Missing / Unreadable',
                      status: inspectionResult.extracted_data.mfg_date?.status,
                    },
                    {
                      label: 'Manufacturer / Packer',
                      rule: 'Rule 6(1)(c)',
                      value: inspectionResult.extracted_data.manufacturer?.value || 'Missing / Unreadable',
                      status: inspectionResult.extracted_data.manufacturer?.status,
                    },
                    {
                      label: 'Consumer Grievance Cell',
                      rule: 'Rule 6(1)(n)',
                      value: inspectionResult.extracted_data.consumer_care?.value || 'Not found in current view',
                      status: inspectionResult.extracted_data.consumer_care?.status,
                    },
                  ].map((item, idx) => {
                    const isPresent = item.status === 'PRESENT';
                    return (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/70 space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold text-slate-500">
                            {item.label}
                          </span>
                          <span className="text-[10px] font-mono text-slate-400 bg-white border border-slate-200 px-1.5 py-0.5 rounded">
                            {item.rule}
                          </span>
                        </div>
                        <div className="text-sm font-bold text-slate-800 break-words">
                          {item.value}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Full Rule Checklist */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <h3 className="text-base font-bold text-slate-900 mb-4">
                  Rule-Based Compliance Engine Results
                </h3>
                <div className="space-y-3">
                  {inspectionResult.rule_results.map((r, i) => {
                    const isPass = r.status === 'PASS';
                    const isFail = r.status === 'FAIL';
                    return (
                      <div
                        key={i}
                        className={`p-3.5 rounded-xl border flex items-start justify-between gap-4 ${
                          isPass
                            ? 'border-emerald-200 bg-emerald-50/40'
                            : isFail
                            ? 'border-rose-200 bg-rose-50/40'
                            : 'border-amber-200 bg-amber-50/40'
                        }`}
                      >
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-mono font-bold text-slate-700">
                              {r.rule}
                            </span>
                            <span className="text-xs font-bold text-slate-900">
                              • {r.title}
                            </span>
                          </div>
                          <p className="text-xs text-slate-600">{r.details}</p>
                        </div>
                        <span
                          className={`text-xs font-bold px-2.5 py-1 rounded-md uppercase shrink-0 ${
                            isPass
                              ? 'bg-emerald-100 text-emerald-800'
                              : isFail
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {r.status}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Blockchain Evidence Receipt Card */}
              <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-lg space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                      <ShieldCheck className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h4 className="font-bold text-sm">
                        Blockchain Tamper-Evident Evidence Ledger
                      </h4>
                      <p className="text-xs text-slate-400">
                        Immutable cryptographic fingerprint recorded on-chain
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={onNavigateBlockchain}
                    className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-semibold transition"
                  >
                    <span>Inspect in Audit Lab</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
                  <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60">
                    <span className="text-slate-400 block text-[10px] uppercase font-sans font-semibold mb-1">
                      Block Height & Index
                    </span>
                    <span className="text-emerald-400 font-bold text-sm">
                      Block #{inspectionResult.blockchain.block_index}
                    </span>
                  </div>
                  <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 overflow-hidden">
                    <span className="text-slate-400 block text-[10px] uppercase font-sans font-semibold mb-1">
                      Block Hash
                    </span>
                    <span className="text-slate-200 truncate block">
                      {inspectionResult.blockchain.block_hash}
                    </span>
                  </div>
                  <div className="sm:col-span-2 bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 overflow-hidden">
                    <span className="text-slate-400 block text-[10px] uppercase font-sans font-semibold mb-1">
                      Canonical Inspection Evidence SHA-256 Digest
                    </span>
                    <span className="text-blue-400 truncate block font-bold">
                      {inspectionResult.blockchain.record_sha256}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
