import type { Metadata } from "metadata";
import "./globals.css";

export const metadata = {
  title: "AI Sight-Reading Studio | GCP Cloud-Native Edition",
  description:
    "Generate, render, and synthesize playable musical sight-reading exercises using Google Gemini on Vertex AI and Cloud Run.",
  keywords: ["sight-reading", "music notation", "abcjs", "gemini", "vertex ai", "gcp", "cloud run"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-gray-100 flex flex-col font-sans">
        {children}
      </body>
    </html>
  );
}
