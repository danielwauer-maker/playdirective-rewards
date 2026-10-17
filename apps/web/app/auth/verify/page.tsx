"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function VerifyPage(){
  const params=useSearchParams(); const router=useRouter();
  const [status,setStatus]=useState("Verifying your secure link…");
  useEffect(()=>{
    const token=params.get("token");
    if(!token){setStatus("Missing sign-in token.");return;}
    (async()=>{
      const r=await fetch("/api/auth/redeem",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token})});
      const d=await r.json().catch(()=>({}));
      if(!r.ok){setStatus(d.detail||"This link is invalid or expired.");return;}
      setStatus("Signed in. Opening your workspace…");
      router.replace("/app"); router.refresh();
    })();
  },[params,router]);
  return <main className="container section" style={{maxWidth:620}}><div className="card"><div className="eyebrow">Secure sign-in</div><h1>Almost there</h1><p className="muted">{status}</p></div></main>
}
