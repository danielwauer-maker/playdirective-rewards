import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import LogoutButton from "./LogoutButton";

export default async function AppLayout({children}:{children:React.ReactNode}){
  const store=await cookies();
  if(!store.get("pd_session")) redirect("/login");
  return <div className="shell">
    <aside className="sidebar">
      <div className="eyebrow" style={{margin:"0 10px 14px"}}>Workspace</div>
      <Link href="/app">Overview</Link>
      <Link href="/app/analyze">Analyze offer</Link>
      <Link href="/app/referrals">Referrals</Link>
      <Link href="/app/billing">Billing</Link>
      <div className="eyebrow" style={{margin:"18px 10px 8px"}}>Internal</div>
      <Link href="/app/research">Research import</Link>
      <LogoutButton />
    </aside>
    <section className="main">{children}</section>
  </div>
}
