"use client";

import { FormEvent, useState } from "react";

type M={label:string;reward:number;estimated_hours:number;estimated_spend:number;completion_probability:number;tracking_confidence:number};
const empty=():M=>({label:"",reward:0,estimated_hours:0,estimated_spend:0,completion_probability:.7,tracking_confidence:.9});

export default function AnalyzePage(){
  const [title,setTitle]=useState(""); const [provider,setProvider]=useState("freecash"); const [headline,setHeadline]=useState(0); const [deadline,setDeadline]=useState(30);
  const [milestones,setMilestones]=useState<M[]>([empty(),empty()]); const [loading,setLoading]=useState(false); const [result,setResult]=useState<any>(null); const [error,setError]=useState("");
  function patch(i:number,key:keyof M,value:string){setMilestones(x=>x.map((m,n)=>n===i?{...m,[key]:key==="label"?value:Number(value)}:m));}
  async function submit(e:FormEvent){e.preventDefault();setLoading(true);setError("");setResult(null);
    const body={provider,title,headline_reward:headline,deadline_days:deadline,currency:"EUR",milestones:milestones.map((m,i)=>({...m,position:i+1}))};
    const r=await fetch("/api/pd/offers",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const d=await r.json().catch(()=>({}));
    if(!r.ok)setError(d.detail||"Analysis failed.");else setResult(d);setLoading(false);
  }
  return <>
    <div className="pagehead"><div><div className="eyebrow">Decision engine</div><h1>Analyze an offer</h1><p className="muted">For the first SaaS version, enter milestone assumptions manually. Later screenshot ingestion can populate the same model automatically.</p></div></div>
    <form className="card form" onSubmit={submit}>
      <div className="row"><div className="field"><label>Offer / game title</label><input className="input" required value={title} onChange={e=>setTitle(e.target.value)} placeholder="e.g. Monopoly GO"/></div><div className="field"><label>Provider</label><select className="input" value={provider} onChange={e=>setProvider(e.target.value)}><option value="freecash">Freecash</option><option value="swagbucks">Swagbucks</option><option value="rewardxp">RewardXP</option><option value="other">Other</option></select></div></div>
      <div className="row"><div className="field"><label>Headline reward (€)</label><input className="input" type="number" min="0" step="0.01" value={headline} onChange={e=>setHeadline(Number(e.target.value))}/></div><div className="field"><label>Deadline (days)</label><input className="input" type="number" min="1" value={deadline} onChange={e=>setDeadline(Number(e.target.value))}/></div></div>
      <div><div className="eyebrow" style={{marginTop:10}}>Milestones</div><p className="muted">Probability and tracking confidence use values from 0 to 1.</p></div>
      {milestones.map((m,i)=><div className="milestone" key={i}>
        <div className="field"><label>Milestone {i+1}</label><input className="input" required value={m.label} onChange={e=>patch(i,"label",e.target.value)} placeholder="Reach level 20"/></div>
        <div className="field"><label>Reward €</label><input className="input" type="number" step="0.01" min="0" value={m.reward} onChange={e=>patch(i,"reward",e.target.value)}/></div>
        <div className="field"><label>Hours</label><input className="input" type="number" step="0.1" min="0" value={m.estimated_hours} onChange={e=>patch(i,"estimated_hours",e.target.value)}/></div>
        <div className="field"><label>Spend €</label><input className="input" type="number" step="0.01" min="0" value={m.estimated_spend} onChange={e=>patch(i,"estimated_spend",e.target.value)}/></div>
        <div className="field"><label>Completion</label><input className="input" type="number" step="0.05" min="0" max="1" value={m.completion_probability} onChange={e=>patch(i,"completion_probability",e.target.value)}/></div>
        <div className="field"><label>Tracking</label><input className="input" type="number" step="0.05" min="0" max="1" value={m.tracking_confidence} onChange={e=>patch(i,"tracking_confidence",e.target.value)}/></div>
        <button type="button" className="btn" onClick={()=>setMilestones(x=>x.filter((_,n)=>n!==i))} disabled={milestones.length===1}>×</button>
      </div>)}
      <div className="actions"><button type="button" className="btn" onClick={()=>setMilestones(x=>[...x,empty()])}>+ Add milestone</button><button className="btn primary" disabled={loading}>{loading?"Analyzing…":"Run PD analysis"}</button></div>
      {error&&<p className="error">{error}</p>}
    </form>
    {result?.analysis&&<div className="card" style={{marginTop:20}}><div className="eyebrow">Decision</div><div className="score">{result.analysis.pd_score}</div><h2 className={result.analysis.verdict==="START"?"good":result.analysis.verdict==="SKIP"?"bad":"warn"}>{result.analysis.verdict}</h2><div className="grid3"><div><div className="muted">Expected reward</div><div className="kpi">€{Number(result.analysis.expected_reward).toFixed(2)}</div></div><div><div className="muted">Expected spend</div><div className="kpi">€{Number(result.analysis.expected_spend).toFixed(2)}</div></div><div><div className="muted">Effective rate</div><div className="kpi">€{Number(result.analysis.effective_hourly_rate).toFixed(2)}/h</div></div></div><p className="muted">Recommended stop: {result.analysis.recommended_stop_position?`Milestone ${result.analysis.recommended_stop_position}`:"—"}. {result.analysis.explanation}</p></div>}
  </>
}
