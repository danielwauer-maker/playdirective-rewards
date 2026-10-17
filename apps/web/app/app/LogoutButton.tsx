"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LogoutButton(){
  const router=useRouter();
  const [busy,setBusy]=useState(false);
  async function logout(){
    setBusy(true);
    await fetch("/api/auth/logout",{method:"POST"}).catch(()=>null);
    router.replace("/login");
    router.refresh();
  }
  return <button className="btn" style={{width:"100%",marginTop:18}} onClick={logout} disabled={busy}>{busy?"Signing out…":"Sign out"}</button>;
}
