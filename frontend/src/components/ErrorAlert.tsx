"use client";

import React from "react";
import { AlertTriangle, X } from "lucide-react";

interface ErrorAlertProps {
  message: string | null;
  onDismiss?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, onDismiss }) => {
  if (!message) return null;

  return (
    <div className="glass-card bg-red-950/40 border-red-500/40 p-4 rounded-xl flex items-start justify-between gap-3 text-red-200 animate-fadeIn">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-red-300">
            System Alert
          </h4>
          <p className="text-sm">{message}</p>
        </div>
      </div>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="text-gray-400 hover:text-white transition-colors"
          aria-label="Dismiss Alert"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
