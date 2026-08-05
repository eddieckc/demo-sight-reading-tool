"use client";

import React, { useEffect, useRef, useState } from "react";
import abcjs from "abcjs";
import { Music2, Code, Copy, Check, Download, FileCode, Printer } from "lucide-react";

interface SheetMusicDisplayProps {
  abcString: string;
  onRenderSuccess?: (visualObj: abcjs.TuneObject) => void;
  onRenderError?: (errorMsg: string) => void;
  tokenUsage?: number;
  estimatedCostUsd?: number;
}

export const SheetMusicDisplay: React.FC<SheetMusicDisplayProps> = ({
  abcString,
  onRenderSuccess,
  onRenderError,
  tokenUsage,
  estimatedCostUsd,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hasRendered, setHasRendered] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  // Keep stable callback refs to prevent useEffect infinite re-render loops
  const onRenderSuccessRef = useRef(onRenderSuccess);
  const onRenderErrorRef = useRef(onRenderError);

  useEffect(() => {
    onRenderSuccessRef.current = onRenderSuccess;
    onRenderErrorRef.current = onRenderError;
  }, [onRenderSuccess, onRenderError]);

  useEffect(() => {
    if (!containerRef.current || !abcString.trim()) {
      setHasRendered(false);
      return;
    }

    try {
      const visualObjs = abcjs.renderAbc(containerRef.current, abcString, {
        responsive: "resize",
        add_classes: true,
        paddingtop: 25,
        paddingbottom: 25,
        paddingleft: 20,
        paddingright: 20,
        scale: 1.2,
        staffwidth: 740,
        format: {
          gchordfont: "Inter 12",
          vocalfont: "Inter 12",
        },
      });

      if (visualObjs && visualObjs.length > 0) {
        setHasRendered(true);
        onRenderSuccessRef.current?.(visualObjs[0]);
      } else {
        setHasRendered(false);
        onRenderErrorRef.current?.("No musical notation could be parsed from the string.");
      }
    } catch (err: any) {
      setHasRendered(false);
      onRenderErrorRef.current?.(err?.message || "Error rendering sheet music.");
    }
  }, [abcString]);

  const handleCopyAbc = () => {
    if (!abcString) return;
    navigator.clipboard.writeText(abcString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportAbc = () => {
    if (!abcString.trim()) return;
    const blob = new Blob([abcString], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sight_reading_exercise_${Date.now()}.abc`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExportSvg = () => {
    const svgEl = containerRef.current?.querySelector("svg");
    if (!svgEl) return;
    const serializer = new XMLSerializer();
    let source = serializer.serializeToString(svgEl);
    if (!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
      source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
    }
    source = '<?xml version="1.0" standalone="no"?>\r\n' + source;
    const blob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sight_reading_score_${Date.now()}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePrintScore = () => {
    const svgEl = containerRef.current?.querySelector("svg");
    if (!svgEl) return;
    const printWindow = window.open("", "_blank");
    if (!printWindow) return;
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>AI Sight-Reading Score</title>
        <style>
          @media print {
            body { margin: 0; padding: 20px; }
          }
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 40px; text-align: center; background: white; color: black; }
          .score-header { margin-bottom: 24px; }
          .score-header h1 { font-size: 24px; margin: 0 0 8px 0; font-weight: 700; }
          .score-header p { font-size: 14px; color: #555; margin: 0; }
          .score-container { max-width: 850px; margin: 0 auto; }
          svg { width: 100%; height: auto; }
        </style>
      </head>
      <body>
        <div class="score-header">
          <h1>AI Sight-Reading Studio Score</h1>
          <p>Generated via Google ADK Composer Engine</p>
        </div>
        <div class="score-container">
          ${svgEl.outerHTML}
        </div>
        <script>
          window.onload = () => {
            setTimeout(() => {
              window.print();
            }, 300);
          };
        </script>
      </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <div className="glass-card p-6 space-y-6">
      {/* Top Header with Export Toolbar */}
      <div className="flex items-center justify-between border-b border-white/10 pb-3 flex-wrap gap-3">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-300 flex items-center gap-2">
          <Music2 className="w-4 h-4 text-primary-light" />
          Sheet Music Score
        </h3>

        <div className="flex items-center gap-2 flex-wrap">
          {tokenUsage !== undefined && tokenUsage > 0 && (
            <span
              className="text-xs text-purple-300 font-mono font-medium bg-purple-950/40 border border-purple-500/30 px-3 py-1 rounded-full shadow-sm"
              title="Total Gemini AI tokens consumed and estimated generation cost"
            >
              {tokenUsage.toLocaleString()} tokens
              {estimatedCostUsd !== undefined ? ` • $${estimatedCostUsd.toFixed(6)}` : ""}
            </span>
          )}

          {hasRendered && (
            <div className="flex items-center gap-1.5 bg-surface/80 border border-white/10 rounded-lg p-1 shadow-sm">
              <button
                onClick={handleExportAbc}
                type="button"
                className="flex items-center gap-1 text-xs text-gray-300 hover:text-white hover:bg-white/10 px-2.5 py-1 rounded-md transition-colors cursor-pointer font-medium"
                title="Download raw ABC notation (.abc file)"
              >
                <Download className="w-3.5 h-3.5 text-primary-light" />
                <span>.ABC</span>
              </button>

              <button
                onClick={handleExportSvg}
                type="button"
                className="flex items-center gap-1 text-xs text-gray-300 hover:text-white hover:bg-white/10 px-2.5 py-1 rounded-md transition-colors cursor-pointer font-medium"
                title="Download scalable vector sheet music (.svg image)"
              >
                <FileCode className="w-3.5 h-3.5 text-accent" />
                <span>.SVG</span>
              </button>

              <button
                onClick={handlePrintScore}
                type="button"
                className="flex items-center gap-1 text-xs text-gray-300 hover:text-white hover:bg-white/10 px-2.5 py-1 rounded-md transition-colors cursor-pointer font-medium"
                title="Print sheet music or Save as PDF"
              >
                <Printer className="w-3.5 h-3.5 text-purple-400" />
                <span>Print / PDF</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Rendered Sheet Music Score SVG */}
      <div className="abc-score-card min-h-[220px] flex items-center justify-center overflow-x-auto">
        <div
          ref={containerRef}
          className="w-full"
          id="abc-sheet-container"
        />

        {!abcString.trim() && (
          <div className="text-center py-12 text-gray-400 space-y-2">
            <Music2 className="w-10 h-10 mx-auto text-gray-600 animate-pulse" />
            <p className="text-sm font-medium">No sheet music generated yet.</p>
            <p className="text-xs text-gray-500">
              Configure parameters above and click &quot;Generate Sight-Reading Exercise&quot; to begin.
            </p>
          </div>
        )}
      </div>

      {/* Raw ABC Notation Code View (Always Visible) */}
      <div className="space-y-2 pt-2">
        <div className="flex items-center justify-between border-b border-white/10 pb-2">
          <span className="text-xs font-semibold text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
            <Code className="w-3.5 h-3.5 text-purple-400" />
            Raw ABC Notation Code
          </span>

          <button
            onClick={handleCopyAbc}
            type="button"
            className="flex items-center gap-1.5 text-xs text-gray-300 hover:text-white bg-white/5 hover:bg-white/10 px-2.5 py-1 rounded-lg border border-white/10 transition-colors cursor-pointer"
            title="Copy raw ABC notation to clipboard"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-green-400" />
            ) : (
              <Copy className="w-3.5 h-3.5 text-gray-400" />
            )}
            <span>{copied ? "Copied!" : "Copy ABC"}</span>
          </button>
        </div>

        <div className="bg-black/60 border border-white/10 rounded-xl p-4 overflow-x-auto shadow-inner">
          <pre className="whitespace-pre font-mono text-xs text-purple-200 leading-relaxed">
            {abcString || "// No ABC notation present"}
          </pre>
        </div>
      </div>
    </div>
  );
};
