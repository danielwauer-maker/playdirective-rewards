import { NextResponse } from "next/server";
import { backendFetch } from "@/lib/backend";

export async function POST() {
  await backendFetch("/v1/auth/logout", {method: "POST"}).catch(() => null);
  const response = NextResponse.json({status: "ok"});
  response.cookies.set("pd_session", "", {httpOnly: true, path: "/", maxAge: 0});
  return response;
}
