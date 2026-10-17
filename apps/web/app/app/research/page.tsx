"use client";

import { FormEvent, useMemo, useState } from "react";

type Milestone = {
  label: string;
  reward: number;
  milestone_type: string;
  purchase_amount: number | null;
  notes: string;
};

const emptyMilestone = (): Milestone => ({
  label: "",
  reward: 0,
  milestone_type: "progress",
  purchase_amount: null,
  notes: "",
});

export default function ResearchImportPage(){
  const [file,setFile]=useState<File|null>(null);
  const [preview,setPreview]=useState<string>("");
  const [screenshotId,setScreenshotId]=useState<number|null>(null);
  const [uploadState,setUploadState]=useState("");
  const [provider,setProvider]=useState("freecash");
  const [gameName,setGameName]=useState("");
  const [platform,setPlatform]=useState("ios");
  const [country,setCountry]=useState("DE");
  const [currency,setCurrency]=useState("EUR");
  const [headlineReward,setHeadlineReward]=useState(0);
  const [deadlineDays,setDeadlineDays]=useState<number|"">(30);
  const [sourceNote,setSourceNote]=useState("");
  const [milestones,setMilestones]=useState<Milestone[]>([emptyMilestone(),emptyMilestone()]);
  const [saving,setSaving]=useState(false);
  const [message,setMessage]=useState("");
  const [error,setError]=useState("");

  const totalMilestoneReward=useMemo(()=>milestones.reduce((sum,m)=>sum+(Number(m.reward)||0),0),[milestones]);

  function chooseFile(next:File|null){
    setFile(next); setScreenshotId(null); setUploadState(""); setMessage(""); setError("");
    if(preview) URL.revokeObjectURL(preview);
    setPreview(next?URL.createObjectURL(next):"");
  }

  async function upload(){
    if(!file){setError("Choose a screenshot first.");return;}
    setError("");setUploadState("Uploading…");
    const form=new FormData(); form.append("file",file);
    const r=await fetch("/api/research/upload",{method:"POST",body:form});
    const d=await r.json().catch(()=>({}));
    if(!r.ok){setError(d.detail||"Upload failed.");setUploadState("");return;}
    setScreenshotId(d.screenshot.id); setUploadState(d.duplicate?"Already uploaded — using existing screenshot.":"Screenshot uploaded.");
  }

  function patch(i:number,key:keyof Milestone,value:string){
    setMilestones(xs=>xs.map((m,n)=>n===i?{
      ...m,
      [key]:key==="reward"?Number(value):key==="purchase_amount"?(value===""?null:Number(value)):value,
    }:m));
  }

  async function save(e:FormEvent){
    e.preventDefault(); setError("");setMessage("");setSaving(true);
    const body={
      screenshot_id:screenshotId,
      provider,
      game_name:gameName,
      platform:platform||null,
      country:country||null,
      currency,
      headline_reward:headlineReward,
      deadline_days:deadlineDays===""?null:Number(deadlineDays),
      source_note:sourceNote||null,
      milestones:milestones.map((m,i)=>({...m,position:i+1,notes:m.notes||null})),
    };
    const r=await fetch("/api/pd/research/snapshots",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    const d=await r.json().catch(()=>({}));
    if(!r.ok){setError(d.detail||"Could not save snapshot.");setSaving(false);return;}
    setMessage(`Snapshot #${d.id} saved for ${d.game_name}.`); setSaving(false);
  }

  return <>
    <div className="pagehead"><div><div className="eyebrow">Admin research</div><h1>Import Freecash offer</h1><p className="muted">Upload what you actually see in the app, then verify the fields manually. This creates a dated market snapshot for our shared intelligence layer.</p></div></div>

    <div className="row" style={{alignItems:"start"}}>
      <div className="card">
        <div className="eyebrow">1 · Evidence</div>
        <h2>Screenshot</h2>
        <input className="input" type="file" accept="image/png,image/jpeg,image/webp" onChange={e=>chooseFile(e.target.files?.[0]||null)}/>
        {preview&&<img src={preview} alt="Screenshot preview" style={{width:"100%",marginTop:16,borderRadius:14,border:"1px solid var(--line)"}}/>}
        <div className="actions"><button type="button" className="btn primary" onClick={upload} disabled={!file}>Upload screenshot</button></div>
        {uploadState&&<p className="success">{uploadState}</p>}
        <p className="muted" style={{fontSize:13}}>The screenshot is stored only in the research storage volume. A SHA-256 fingerprint prevents accidental duplicate uploads.</p>
      </div>

      <form className="card form" onSubmit={save}>
        <div className="eyebrow">2 · Verify offer</div>
        <div className="row"><div className="field"><label>Provider</label><input className="input" value={provider} onChange={e=>setProvider(e.target.value)}/></div><div className="field"><label>Game</label><input className="input" required value={gameName} onChange={e=>setGameName(e.target.value)} placeholder="e.g. Monopoly GO"/></div></div>
        <div className="row"><div className="field"><label>Platform</label><select className="input" value={platform} onChange={e=>setPlatform(e.target.value)}><option value="ios">iOS</option><option value="android">Android</option><option value="web">Web</option><option value="">Unknown</option></select></div><div className="field"><label>Country</label><input className="input" maxLength={2} value={country} onChange={e=>setCountry(e.target.value.toUpperCase())}/></div></div>
        <div className="row"><div className="field"><label>Headline reward</label><input className="input" type="number" min="0" step="0.01" value={headlineReward} onChange={e=>setHeadlineReward(Number(e.target.value))}/></div><div className="field"><label>Deadline days</label><input className="input" type="number" min="1" value={deadlineDays} onChange={e=>setDeadlineDays(e.target.value===""?"":Number(e.target.value))}/></div></div>
        <div className="row"><div className="field"><label>Currency</label><input className="input" maxLength={3} value={currency} onChange={e=>setCurrency(e.target.value.toUpperCase())}/></div><div className="field"><label>Milestone total</label><input className="input" readOnly value={`${totalMilestoneReward.toFixed(2)} ${currency}`}/></div></div>
        <div className="field"><label>Research note</label><textarea className="input" value={sourceNote} onChange={e=>setSourceNote(e.target.value)} placeholder="Anything unusual about this offer, bonus window, visible terms, etc."/></div>

        <div><div className="eyebrow">3 · Milestones</div><p className="muted">Enter only what is visible in the offer. Do not estimate playtime here — this table is market evidence, not prediction data.</p></div>
        {milestones.map((m,i)=><div key={i} className="card" style={{padding:14}}>
          <div className="row"><div className="field"><label>Milestone {i+1}</label><input className="input" required value={m.label} onChange={e=>patch(i,"label",e.target.value)} placeholder="Reach Board 35"/></div><div className="field"><label>Reward</label><input className="input" type="number" step="0.01" min="0" value={m.reward} onChange={e=>patch(i,"reward",e.target.value)}/></div></div>
          <div className="row"><div className="field"><label>Type</label><select className="input" value={m.milestone_type} onChange={e=>patch(i,"milestone_type",e.target.value)}><option value="progress">Progress</option><option value="purchase">Purchase</option><option value="install">Install</option><option value="retention">Retention</option><option value="other">Other</option></select></div><div className="field"><label>Purchase amount (if applicable)</label><input className="input" type="number" step="0.01" min="0" value={m.purchase_amount??""} onChange={e=>patch(i,"purchase_amount",e.target.value)}/></div></div>
          <div className="field"><label>Note</label><input className="input" value={m.notes} onChange={e=>patch(i,"notes",e.target.value)}/></div>
          <button type="button" className="btn" onClick={()=>setMilestones(xs=>xs.filter((_,n)=>n!==i))} disabled={milestones.length===1}>Remove</button>
        </div>)}
        <div className="actions"><button type="button" className="btn" onClick={()=>setMilestones(xs=>[...xs,emptyMilestone()])}>+ Add milestone</button><button className="btn primary" disabled={saving}>{saving?"Saving…":"Save verified snapshot"}</button></div>
        {message&&<p className="success">{message}</p>}{error&&<p className="error">{error}</p>}
      </form>
    </div>
  </>
}
