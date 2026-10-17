import { backendFetch } from "@/lib/backend";

export default async function ReferralsPage(){
  const res=await backendFetch("/v1/referrals");
  const data=res.ok?await res.json():{referral_code:"—",referral_path:"",credit_balance_cents:0,referrals:[]};
  const origin=process.env.NEXT_PUBLIC_ORIGIN||"http://localhost:3000";
  const link=`${origin}${data.referral_path||""}`;
  return <>
    <div className="pagehead"><div><div className="eyebrow">Referral program</div><h1>Invite friends. Earn credit.</h1><p className="muted">A referral is attributed when a new user signs up through your link. Credit is released only after the referred user makes a qualifying successful payment.</p></div></div>
    <div className="cards">
      <div className="card"><div className="muted">Your code</div><div className="kpi">{data.referral_code}</div></div>
      <div className="card"><div className="muted">Account credit</div><div className="kpi">€{((data.credit_balance_cents||0)/100).toFixed(2)}</div></div>
      <div className="card"><div className="muted">Invited users</div><div className="kpi">{data.referrals?.length||0}</div></div>
    </div>
    <div className="card" style={{marginTop:20}}><div className="eyebrow">Your referral link</div><div className="row" style={{marginTop:10}}><input className="input" readOnly value={link}/><div className="notice">Share this link. Self-referrals and duplicate attribution are blocked by the account model.</div></div></div>
    <div className="card" style={{marginTop:20}}><h2>Referral activity</h2>{!data.referrals?.length?<p className="muted">No referrals yet.</p>:<div style={{overflowX:"auto"}}><table className="table"><thead><tr><th>User</th><th>Status</th><th>Joined</th><th>Rewarded</th></tr></thead><tbody>{data.referrals.map((r:any)=><tr key={r.id}><td>{r.email||"—"}</td><td><span className="pill">{r.status}</span></td><td>{new Date(r.created_at).toLocaleDateString()}</td><td>{r.rewarded_at?new Date(r.rewarded_at).toLocaleDateString():"—"}</td></tr>)}</tbody></table></div>}</div>
  </>
}
