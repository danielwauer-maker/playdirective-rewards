import { NextRequest, NextResponse } from "next/server";
import { API_INTERNAL_URL } from "@/lib/backend";

export async function POST(request: NextRequest) {
  const body = await request.text();
  const response = await fetch(`${API_INTERNAL_URL}/v1/auth/redeem`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body,
    cache: "no-store",
  });
  const data = await response.json().catch(() => ({detail: "Sign-in failed"}));
  const result = NextResponse.json(data, {status: response.status});
  if (response.ok && data.access_token) {
    result.cookies.set("pd_session", data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 30,
    });
  }
  return result;
}
