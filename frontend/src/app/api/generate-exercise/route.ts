import { NextRequest, NextResponse } from "next/server";

// Server-side backend URL (evaluated at runtime inside Cloud Run container)
const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.INTERNAL_BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "http://localhost:8080";

/**
 * Fetches Google Cloud IAM ID Token from the instance metadata server
 * when running inside GCP (Cloud Run) to authenticate service-to-service calls.
 */
async function getGcpAuthHeaders(audience: string): Promise<Record<string, string>> {
  try {
    const metadataUrl = `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=${encodeURIComponent(
      audience
    )}`;
    const tokenRes = await fetch(metadataUrl, {
      headers: { "Metadata-Flavor": "Google" },
      signal: AbortSignal.timeout(1000), // Fast fallback if running locally
    });
    if (tokenRes.ok) {
      const idToken = await tokenRes.text();
      return { Authorization: `Bearer ${idToken.trim()}` };
    }
  } catch {
    // Running locally or non-GCP environment
  }
  return {};
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const cleanBackendUrl = BACKEND_URL.replace(/\/$/, "");
    const targetUrl = `${cleanBackendUrl}/api/generate-exercise`;

    const authHeaders = await getGcpAuthHeaders(cleanBackendUrl);

    const backendResponse = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders,
      },
      body: JSON.stringify(body),
    });

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(data, { status: backendResponse.status });
    }

    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error("[Next.js Internal API Proxy Error]:", error);
    return NextResponse.json(
      { error: error?.message || "Failed to reach backend composer service." },
      { status: 502 }
    );
  }
}
