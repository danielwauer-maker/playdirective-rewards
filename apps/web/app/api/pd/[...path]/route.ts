import { NextRequest, NextResponse } from "next/server";
import { backendFetch } from "@/lib/backend";

type Ctx = {params: Promise<{path: string[]}>};

async function proxy(request: NextRequest, context: Ctx) {
  const {path} = await context.params;
  const suffix = path.join("/");
  const search = request.nextUrl.search || "";
  const method = request.method;
  const body = ["GET", "HEAD"].includes(method) ? undefined : await request.text();
  const response = await backendFetch(`/v1/${suffix}${search}`, {method, body});
  const text = await response.text();
  return new NextResponse(text, {
    status: response.status,
    headers: {"Content-Type": response.headers.get("Content-Type") || "application/json"},
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
