import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <section className="container hero">
        <div>
          <div className="eyebrow">Reward gaming decision intelligence</div>
          <h1>Know what is worth playing.</h1>
          <p>Analyze Freecash and other rewarded-game offers before you invest hours or money. PlayDirective estimates realistic earnings, time, in-app spend, completion probability and the milestone where you should stop.</p>
          <div className="actions">
            <Link href="/login" className="btn primary">Analyze an offer</Link>
            <Link href="/pricing" className="btn ghost">See pricing</Link>
          </div>
        </div>
        <div className="heroCard">
          <div className="eyebrow">Example decision</div>
          <div className="score">84</div>
          <h2>START</h2>
          <p className="muted">Do not chase the €482 headline reward. Based on the current milestones, your strongest expected outcome is around milestone 5.</p>
          <div className="grid3">
            <div><div className="muted">Expected net</div><div className="kpi">€76</div></div>
            <div><div className="muted">Active time</div><div className="kpi">16h</div></div>
            <div><div className="muted">Expected rate</div><div className="kpi">€4.75/h</div></div>
          </div>
        </div>
      </section>
      <section className="container section">
        <div className="eyebrow">How it works</div>
        <h2>Headline rewards are not decisions.</h2>
        <div className="grid3">
          <div className="card"><h3>1. Add the offer</h3><p className="muted">Enter its milestones, deadline and rewards. Screenshot ingestion can be layered on top without changing the decision model.</p></div>
          <div className="card"><h3>2. Model the outcome</h3><p className="muted">We combine expected reward, time, spend, completion probability and tracking confidence per milestone.</p></div>
          <div className="card"><h3>3. Get the action</h3><p className="muted">START, CAUTION or SKIP — plus the milestone where continuing stops making sense.</p></div>
        </div>
      </section>
      <footer><div className="container">PlayDirective Rewards · Independent decision intelligence for rewarded gaming.</div></footer>
    </main>
  );
}
