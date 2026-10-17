import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({status: "ok"});
  response.cookies.set("pd_session", "", {httpOnly: true, path: "/", maxAge: 0});
  return response;
}
