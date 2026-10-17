"use client";

import { FormEvent, useEffect, useState } from "react";

export default function LoginPage(){
  const [ref,setRef]=useState("");
  const [plan,setPlan]=useState("");
  const [email,setEmail]=useState("");
  const [loading,setLoading]=useState(false);
  const [message,setMessage]=useState("");
  const [error,setError]=useState("");

  useEffect(()=>{
    const params=new URLSearchParams(window.location.search);
    setRef(params.get("ref")||"");
    setPlan(params.get("plan")||"");
  },[]);

  async function submit(e:FormEvent){
    e.preventDefault(); setLoading(true); setMessage(""); setError("");
    const r=await fetch("/api/auth/magic-link",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email,referral_code:ref||null})});
    const data=await r.json().catch(()=>({}));
    if(!r.ok)setError(data.detail||"Could not send sign-in link."); else setMessage(data.message||"Check your email.");
    setLoading(false);
  }

  return <main className="container section" style={{maxWidth:620}}>
    <div className="card">
      <div className="eyebrow">Passwordless access</div>
      <h1 style={{fontSize:46,letterSpacing:"-.055em",marginBottom:8}}>Sign in to PlayDirective Rewards</h1>
      <p className="muted">Enter your email. We will send a secure, single-use sign-in link. No password to remember.</p>
      {ref&&<div className="notice" style={{marginBottom:16}}>Referral code <strong>{ref}</strong> will be attached if this is a new account.</div>}
      {plan&&<div className="notice" style={{marginBottom:16}}>After sign-in, you can activate the <strong>{plan.toUpperCase()}</strong> plan from Billing.</div>}
      <form className="form" onSubmit={submit}>
        <div className="field"><label>Email</label><input className="input" type="email" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com"/></div>
        <button className="btn primary" disabled={loading}>{loading?"Sending…":"Email me a sign-in link"}</button>
      </form>
      {message&&<p className="success">{message}</p>}{error&&<p className="error">{error}</p>}
    </div>
  </main>
}
