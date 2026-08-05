"use client";

import React, { useState, useCallback } from "react";
import abcjs from "abcjs";
import { ExerciseRequest } from "@/types/exercise";
import { generateExercise } from "@/lib/api";
import { ControlDashboard } from "@/components/ControlDashboard";
import { SheetMusicDisplay } from "@/components/SheetMusicDisplay";
import { AudioPlayer } from "@/components/AudioPlayer";
import { ErrorAlert } from "@/components/ErrorAlert";
import { Music, Headphones, BookOpen, Sparkles } from "lucide-react";

const INITIAL_DEMO_ABC = `X:1
T:Sight-Reading Practice (G Major Piano)
M:4/4
L:1/8
Q:1/4=110
K:G
G2 B2 d2 g2 | f2 d2 z2 G2 | c2 e2 d2 B2 | A4 G2 z2 |]`;

export default function SightReadingStudioPage() {
  const [params, setParams] = useState<ExerciseRequest>({
    difficulty: "intermediate",
    key_signature: "G",
    instrument: "piano",
    time_signature: "4/4",
    tempo: 110,
    bars: 4,
  });

  const [abcString, setAbcString] = useState<string>(INITIAL_DEMO_ABC);
  const [visualObj, setVisualObj] = useState<abcjs.TuneObject | null>(null);
  const [tokenUsage, setTokenUsage] = useState<number | undefined>(undefined);
  const [estimatedCostUsd, setEstimatedCostUsd] = useState<number | undefined>(undefined);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const response = await generateExercise(params);
      setAbcString(response.abc_notation);
      setTokenUsage(response.token_usage);
      setEstimatedCostUsd(response.estimated_cost_usd);
    } catch (err: any) {
      setErrorMsg(
        err?.message ||
          "Failed to connect to music composer service. Please check your network or try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleRenderSuccess = useCallback((obj: abcjs.TuneObject) => {
    setVisualObj(obj);
    setErrorMsg(null);
  }, []);

  const handleRenderError = useCallback((msg: string) => {
    setErrorMsg(msg);
  }, []);

  return (
    <div className="min-h-screen flex flex-col justify-between">
      {/* Top Header */}
      <header className="border-b border-white/10 bg-surface/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white shadow-glow">
              <Music className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-display font-bold tracking-tight text-white flex items-center gap-2">
                <span>AI Sight-Reading Studio</span>
                <span className="text-[10px] font-medium bg-primary/20 text-primary-light px-2 py-0.5 rounded-full border border-primary/30">
                  Interactive Practice
                </span>
              </h1>
              <p className="text-xs text-gray-400">
                Dynamic sight-reading practice for musicians &amp; educators
              </p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-5 text-xs font-medium text-gray-300">
            <div className="flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-primary-light" />
              <span>AI Composer</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Headphones className="w-4 h-4 text-accent" />
              <span>Web Audio Playback</span>
            </div>
            <div className="flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-purple-400" />
              <span>Vector Notation</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Studio Content */}
      <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 flex-1">
        {/* Banner Section */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <h2 className="text-3xl sm:text-4xl font-display font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-200 to-gray-400">
            Master Sight-Reading on Any Instrument
          </h2>
          <p className="text-sm sm:text-base text-gray-400">
            Dynamically compose custom musical sight-reading exercises tailored to your instrument, key signature,
            meter, and skill level—with real-time interactive audio playback.
          </p>
        </div>

        {/* Error Display */}
        <ErrorAlert message={errorMsg} onDismiss={() => setErrorMsg(null)} />

        {/* Studio Workspace Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls Panel */}
          <div className="lg:col-span-5">
            <ControlDashboard
              params={params}
              onChange={setParams}
              onGenerate={handleGenerate}
              isLoading={isLoading}
            />
          </div>

          {/* Notation & Audio Player Studio */}
          <div className="lg:col-span-7 space-y-6">
            <SheetMusicDisplay
              abcString={abcString}
              onRenderSuccess={handleRenderSuccess}
              onRenderError={handleRenderError}
              tokenUsage={tokenUsage}
              estimatedCostUsd={estimatedCostUsd}
            />

            <AudioPlayer visualObj={visualObj} tempo={params.tempo} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-surface/30 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-500">
          <div>
            &copy; {new Date().getFullYear()} AI Sight-Reading Studio. Built for musicians, students, and educators.
          </div>
          <div className="flex items-center gap-4 text-gray-400">
            <span>Dynamic Practice</span>
            <span>&bull;</span>
            <span>Interactive Notation</span>
            <span>&bull;</span>
            <span>Web Audio Synth</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
