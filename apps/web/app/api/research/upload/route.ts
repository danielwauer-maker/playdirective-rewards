import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { API_INTERNAL_URL } from "@/lib/backend";

export async function POST(request: NextRequest) {
  const store = await cookies();
  const token = store.get("pd_session")?.value;
  if (!token) return NextResponse.json({detail: "Authentication required"}, {status: 401});

  const formData = await request.formData();
  const response = await fetch(`${API_INTERNAL_URL}/v1/research/screenshots`, {
    method: "POST",
    headers: {Authorization: `Bearer ${token}`},
    body: formData,
    cache: "no-store",
  });
  const data = await response.json().catch(() => ({detail: "Upload failed"}));
  return NextResponse.json(data, {status: response.status});
}
