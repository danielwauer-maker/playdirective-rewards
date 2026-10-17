"use client";

import { useEffect, useState } from "react";

export default function BillingPage(){
  const [status,setStatus]=useState<any>(null); const [error,setError]=useState(""); const [busy,setBusy]=useState("");
  async function refresh(){const r=await fetch("/api/pd/billing/status");const d=await r.json().catch(()=>({}));if(r.ok)setStatus(d);else setError(d.detail||"Could not load billing.");}
  useEffect(()=>{refresh();},[]);
  async function checkout(plan_id:string){setBusy(plan_id);setError("");const r=await fetch("/api/pd/billing/checkout",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({plan_id})});const d=await r.json().catch(()=>({}));if(r.ok&&d.url)location.href=d.url;else setError(d.detail||"Checkout unavailable.");setBusy("");}
  async function portal(){setBusy("portal");const r=await fetch("/api/pd/billing/portal",{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"});const d=await r.json().catch(()=>({}));if(r.ok&&d.url)location.href=d.url;else setError(d.detail||"Billing portal unavailable.");setBusy("");}
  return <>
    <div className="pagehead"><div><div className="eyebrow">Subscription</div><h1>Billing</h1><p className="muted">Stripe handles payment details. PlayDirective stores subscription state and entitlements, not card numbers.</p></div></div>
    <div className="cards"><div className="card"><div className="muted">Current plan</div><div className="kpi">{status?.plan_id?.toUpperCase()||"…"}</div></div><div className="card"><div className="muted">Status</div><div className="kpi">{status?.status||"…"}</div></div><div className="card"><div className="muted">Renewal</div><div className="kpi" style={{fontSize:20}}>{status?.current_period_end?new Date(status.current_period_end).toLocaleDateString():"—"}</div></div></div>
    <div className="pricing">
      <div className="card"><div className="eyebrow">Free</div><div className="price">€0</div><p className="muted">Basic workspace and limited analyses.</p></div>
      <div className="card" style={{borderColor:"var(--accent)"}}><div className="eyebrow">Pro</div><div className="price">€4.99<small>/month</small></div><button className="btn primary" onClick={()=>checkout("pro")} disabled={!!busy}>{busy==="pro"?"Opening…":"Upgrade to Pro"}</button></div>
      <div className="card"><div className="eyebrow">Max</div><div className="price">€9.99<small>/month</small></div><button className="btn" onClick={()=>checkout("max")} disabled={!!busy}>{busy==="max"?"Opening…":"Upgrade to Max"}</button></div>
    </div>
    {status?.stripe_customer&&<div className="actions"><button className="btn" onClick={portal} disabled={!!busy}>Manage payment & subscription in Stripe</button></div>}
    {error&&<p className="error">{error}</p>}
  </>
}
