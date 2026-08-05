"use client";

import React from "react";
import { DifficultyLevel, ExerciseRequest } from "@/types/exercise";
import { Sparkles, Sliders } from "lucide-react";

interface ControlDashboardProps {
  params: ExerciseRequest;
  onChange: (newParams: ExerciseRequest) => void;
  onGenerate: () => void;
  isLoading: boolean;
}

const DIFFICULTIES: DifficultyLevel[] = ["beginner", "intermediate", "advanced", "expert"];
const KEYS = ["C", "G", "F", "D", "Bb", "A", "Eb", "Am", "Em", "Dm"];
const INSTRUMENTS = ["piano", "violin", "flute", "saxophone", "guitar", "cello"];
const TIME_SIGNATURES = ["4/4", "3/4", "2/4", "6/8"];
const BAR_COUNTS = [4, 8, 12, 16];

export const ControlDashboard: React.FC<ControlDashboardProps> = ({
  params,
  onChange,
  onGenerate,
  isLoading,
}) => {
  const updateField = <K extends keyof ExerciseRequest>(key: K, value: ExerciseRequest[K]) => {
    onChange({ ...params, [key]: value });
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2 text-white">
          <Sliders className="w-5 h-5 text-primary-light" />
          Exercise Studio
        </h2>
        <span className="text-xs font-medium uppercase bg-primary/20 text-primary-light px-2.5 py-1 rounded-full border border-primary/30">
          AI Composer
        </span>
      </div>

      {/* Featured Full-Width Difficulty Selector */}
      <div>
        <label className="block text-xs font-medium uppercase tracking-wider text-gray-400 mb-2">
          Difficulty Level
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {DIFFICULTIES.map((level) => (
            <button
              key={level}
              type="button"
              onClick={() => updateField("difficulty", level)}
              className={`px-2.5 py-2.5 text-xs sm:text-sm font-semibold rounded-xl capitalize transition-all duration-200 border text-center truncate ${
                params.difficulty === level
                  ? "bg-primary text-white border-primary shadow-glow"
                  : "bg-surface-highlight/60 text-gray-300 border-white/5 hover:border-white/20 hover:text-white"
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      {/* Configuration Grid for remaining parameters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Key Signature */}
        <div>
          <label className="block text-xs font-medium uppercase tracking-wider text-gray-400 mb-2">
            Key Signature
          </label>
          <select
            value={params.key_signature}
            onChange={(e) => updateField("key_signature", e.target.value)}
            className="w-full bg-surface-highlight border border-white/10 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-primary transition-colors"
          >
            {KEYS.map((keySig) => (
              <option key={keySig} value={keySig}>
                Key of {keySig}
              </option>
            ))}
          </select>
        </div>

        {/* Instrument */}
        <div>
          <label className="block text-xs font-medium uppercase tracking-wider text-gray-400 mb-2">
            Instrument
          </label>
          <select
            value={params.instrument}
            onChange={(e) => updateField("instrument", e.target.value)}
            className="w-full bg-surface-highlight border border-white/10 rounded-lg px-3.5 py-2.5 text-sm text-white capitalize focus:outline-none focus:border-primary transition-colors"
          >
            {INSTRUMENTS.map((inst) => (
              <option key={inst} value={inst} className="capitalize">
                {inst}
              </option>
            ))}
          </select>
        </div>

        {/* Time Signature */}
        <div>
          <label className="block text-xs font-medium uppercase tracking-wider text-gray-400 mb-2">
            Time Signature
          </label>
          <select
            value={params.time_signature}
            onChange={(e) => updateField("time_signature", e.target.value)}
            className="w-full bg-surface-highlight border border-white/10 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-primary transition-colors"
          >
            {TIME_SIGNATURES.map((meter) => (
              <option key={meter} value={meter}>
                {meter}
              </option>
            ))}
          </select>
        </div>

        {/* Bar Count */}
        <div>
          <label className="block text-xs font-medium uppercase tracking-wider text-gray-400 mb-2">
            Measure Count (Bars)
          </label>
          <div className="grid grid-cols-4 gap-1.5">
            {BAR_COUNTS.map((bars) => (
              <button
                key={bars}
                type="button"
                onClick={() => updateField("bars", bars)}
                className={`py-2 text-xs font-semibold rounded-lg transition-all duration-200 border text-center ${
                  params.bars === bars
                    ? "bg-accent text-white border-accent shadow-glow-accent"
                    : "bg-surface-highlight/50 text-gray-300 border-white/5 hover:border-white/20"
                }`}
              >
                {bars}
              </button>
            ))}
          </div>
        </div>

        {/* Tempo Slider */}
        <div>
          <div className="flex justify-between text-xs font-medium uppercase tracking-wider text-gray-400 mb-2">
            <span>Tempo (BPM)</span>
            <span className="text-primary-light font-mono font-bold">{params.tempo} BPM</span>
          </div>
          <input
            type="range"
            min={60}
            max={180}
            step={5}
            value={params.tempo}
            onChange={(e) => updateField("tempo", Number(e.target.value))}
            className="w-full h-2 bg-surface-highlight rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>
      </div>

      <div className="pt-2">
        <button
          type="button"
          onClick={onGenerate}
          disabled={isLoading}
          className="w-full py-3.5 px-6 rounded-xl font-semibold text-white bg-gradient-to-r from-primary to-primary-light hover:from-primary-hover hover:to-primary shadow-glow transition-all duration-300 flex items-center justify-center gap-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Composing Musical Exercise...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              <span>Generate Sight-Reading Exercise</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
