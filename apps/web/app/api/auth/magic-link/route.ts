import { NextRequest, NextResponse } from "next/server";
import { API_INTERNAL_URL } from "@/lib/backend";

export async function POST(request: NextRequest) {
  const body = await request.text();
  const response = await fetch(`${API_INTERNAL_URL}/v1/auth/magic-link`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body,
    cache: "no-store",
  });
  const data = await response.json().catch(() => ({detail: "Request failed"}));
  return NextResponse.json(data, {status: response.status});
}
