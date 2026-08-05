"use client";

import React, { useState, useRef, useEffect } from "react";
import abcjs from "abcjs";
import { Play, Square, Volume2, AlertCircle, Loader2 } from "lucide-react";

interface AudioPlayerProps {
  visualObj: abcjs.TuneObject | null;
  tempo: number;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ visualObj, tempo }) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [isInitializing, setIsInitializing] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const synthRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    // Stop playback if tune changes or component unmounts
    if (synthRef.current) {
      try {
        synthRef.current.stop();
      } catch {
        // ignore errors on unmount/reset
      }
    }
    setIsPlaying(false);
    setIsInitializing(false);
    setErrorMsg(null);
  }, [visualObj]);

  const getAudioContext = (): AudioContext => {
    if (!audioContextRef.current) {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      audioContextRef.current = new AudioContextClass();
    }
    return audioContextRef.current;
  };

  const handlePlayStop = async () => {
    if (!visualObj) return;

    // If currently playing, stop playback
    if (isPlaying && synthRef.current) {
      try {
        synthRef.current.stop();
      } catch {
        // ignore stop error
      }
      setIsPlaying(false);
      return;
    }

    try {
      setErrorMsg(null);
      setIsInitializing(true);

      if (!abcjs.synth.supportsAudio()) {
        setErrorMsg("Web Audio API is not supported in this browser.");
        setIsInitializing(false);
        return;
      }

      const audioContext = getAudioContext();
      if (audioContext.state === "suspended") {
        await audioContext.resume();
      }

      if (!synthRef.current) {
        synthRef.current = new abcjs.synth.CreateSynth();
      }

      // Initialize synth and bind onEnded so Play button resets when tune finishes
      await synthRef.current.init({
        audioContext: audioContext,
        visualObj: visualObj,
        onEnded: () => {
          setIsPlaying(false);
        },
      });

      await synthRef.current.prime();
      synthRef.current.start();
      setIsInitializing(false);
      setIsPlaying(true);
    } catch (err: any) {
      setErrorMsg(err?.message || "Audio synthesizer failed to play notation.");
      setIsInitializing(false);
      setIsPlaying(false);
    }
  };

  const handleStop = () => {
    if (synthRef.current && isPlaying) {
      try {
        synthRef.current.stop();
      } catch {
        // ignore
      }
      setIsPlaying(false);
    }
  };

  if (!visualObj) {
    return null;
  }

  return (
    <div className="glass-card p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="p-2.5 bg-primary/20 rounded-xl border border-primary/30 text-primary-light">
          <Volume2 className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-white">Interactive Audio Studio</h4>
          <p className="text-xs text-gray-400">
            Real-time Web Audio synthesis at{" "}
            <span className="text-primary-light font-mono font-medium">{tempo} BPM</span>
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
        <button
          type="button"
          onClick={handlePlayStop}
          disabled={isInitializing}
          className={`px-5 py-2.5 rounded-xl font-semibold text-xs flex items-center gap-2 transition-all duration-200 shadow-lg disabled:opacity-50 ${
            isPlaying
              ? "bg-amber-600 hover:bg-amber-700 text-white shadow-amber-900/30"
              : "bg-accent hover:bg-accent-hover text-white shadow-glow-accent"
          }`}
        >
          {isInitializing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading Audio Samples...</span>
            </>
          ) : isPlaying ? (
            <>
              <Square className="w-4 h-4" />
              <span>Pause Playback</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Play Exercise</span>
            </>
          )}
        </button>

        {isPlaying && (
          <button
            type="button"
            onClick={handleStop}
            className="p-2.5 rounded-xl bg-surface-highlight hover:bg-red-500/20 text-gray-300 hover:text-red-400 border border-white/10 transition-colors"
            title="Stop Playback"
          >
            <Square className="w-4 h-4" />
          </button>
        )}
      </div>

      {errorMsg && (
        <div className="w-full text-xs text-red-400 bg-red-950/30 border border-red-500/30 rounded-lg p-2.5 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}
    </div>
  );
};
