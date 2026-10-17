import Link from "next/link";

const plans = [
  {name:"Free", price:"€0", desc:"Try the decision engine", features:["5 offer analyses / month","Personal workspace","Basic PD Score","Referral program"], cta:"Start free", href:"/login"},
  {name:"Pro", price:"€4.99", desc:"For active reward gamers", features:["Unlimited manual analyses","Milestone exit recommendations","Full earnings & spend model","Offer history","Referral credits on billing"], cta:"Choose Pro", href:"/login?plan=pro", featured:true},
  {name:"Max", price:"€9.99", desc:"For power users", features:["Everything in Pro","Advanced comparisons","Priority intelligence features","Future cross-provider optimizer","Extended history & insights"], cta:"Choose Max", href:"/login?plan=max"},
];

export default function PricingPage(){
  return <main className="container section">
    <div className="eyebrow">Simple consumer pricing</div>
    <h1 style={{fontSize:56,letterSpacing:"-.06em",marginBottom:8}}>Spend less time on bad offers.</h1>
    <p className="muted" style={{fontSize:18,maxWidth:720}}>Start free. Upgrade when PlayDirective is saving you more time and money than it costs. Launch pricing can be changed through Stripe without changing the product architecture.</p>
    <div className="pricing">
      {plans.map(p=><div key={p.name} className="card" style={p.featured?{borderColor:"var(--accent)"}:undefined}>
        <div className="eyebrow">{p.name}</div><div className="price">{p.price}<small>/month</small></div><p className="muted">{p.desc}</p>
        <ul className="list">{p.features.map(f=><li key={f}>{f}</li>)}</ul>
        <Link href={p.href} className={`btn ${p.featured?"primary":""}`} style={{display:"inline-block",marginTop:12}}>{p.cta}</Link>
      </div>)}
    </div>
    <div className="notice" style={{marginTop:22}}>Referral launch default: earn account credit when a referred user becomes a qualified paying customer. Exact reward values are configuration-driven.</div>
  </main>
}
