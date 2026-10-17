import Link from "next/link";
import { redirect } from "next/navigation";
import { backendFetch } from "@/lib/backend";

export default async function DashboardPage(){
  const [meRes,offersRes,refRes]=await Promise.all([
    backendFetch("/v1/auth/me"),backendFetch("/v1/offers"),backendFetch("/v1/referrals")
  ]);
  if(meRes.status===401) redirect("/login");
  const me=await meRes.json();
  const offers=offersRes.ok?(await offersRes.json()).items:[];
  const refs=refRes.ok?await refRes.json():{credit_balance_cents:0,referrals:[]};
  const best=offers.reduce((acc:any,x:any)=>(x.analysis?.pd_score||0)>(acc?.analysis?.pd_score||0)?x:acc,null);
  return <>
    <div className="pagehead"><div><div className="eyebrow">Your decision workspace</div><h1>Welcome back</h1><p className="muted">{me.email} · {String(me.plan||"free").toUpperCase()}</p></div><Link href="/app/analyze" className="btn primary">Analyze new offer</Link></div>
    <div className="cards">
      <div className="card"><div className="muted">Offers analyzed</div><div className="kpi">{offers.length}</div></div>
      <div className="card"><div className="muted">Best current PD Score</div><div className="kpi">{best?.analysis?.pd_score??"—"}</div></div>
      <div className="card"><div className="muted">Referral credit</div><div className="kpi">€{((refs.credit_balance_cents||0)/100).toFixed(2)}</div></div>
    </div>
    <div className="card" style={{marginTop:20}}><div className="pagehead"><div><div className="eyebrow">History</div><h2 style={{margin:"5px 0 0"}}>Your analyzed offers</h2></div></div>
      {offers.length===0?<p className="muted">No analyses yet. Add your first offer to start building your personal decision history.</p>:
      <div style={{overflowX:"auto"}}><table className="table"><thead><tr><th>Offer</th><th>Provider</th><th>Score</th><th>Verdict</th><th>Expected €/h</th><th>Stop</th></tr></thead><tbody>
        {offers.map((o:any)=><tr key={o.id}><td>{o.title}</td><td>{o.provider}</td><td className="good"><strong>{o.analysis?.pd_score??"—"}</strong></td><td>{o.analysis?.verdict??"—"}</td><td>€{Number(o.analysis?.effective_hourly_rate||0).toFixed(2)}</td><td>{o.analysis?.recommended_stop_position?`Milestone ${o.analysis.recommended_stop_position}`:"—"}</td></tr>)}
      </tbody></table></div>}
    </div>
  </>
}
