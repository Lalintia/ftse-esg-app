/**
 * Server-side proxy for backend API calls.
 *
 * Injects X-API-Key from server env (never bundled to client).
 * nginx routes /api/proxy/* here; this strips the /proxy prefix and forwards
 * to the backend service at BACKEND_URL.
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://backend:8000';
const API_KEY = process.env.API_KEY ?? '';

async function proxy(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const backendPath = `/api/${path.join('/')}`;
  const url = new URL(backendPath, BACKEND_URL);

  // Forward query string
  req.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.set(key, value);
  });

  const headers = new Headers(req.headers);
  headers.delete('host');
  if (API_KEY) {
    headers.set('X-API-Key', API_KEY);
  }

  const upstream = await fetch(url.toString(), {
    method: req.method,
    headers,
    body: req.method !== 'GET' && req.method !== 'HEAD' ? req.body : undefined,
    // @ts-expect-error — Node.js fetch supports duplex for streaming
    duplex: 'half',
  });

  const responseHeaders = new Headers(upstream.headers);
  // Strip hop-by-hop headers
  responseHeaders.delete('transfer-encoding');

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
