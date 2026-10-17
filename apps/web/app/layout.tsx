import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "PlayDirective Rewards — Reward Gaming Decision Intelligence",
  description: "Know which rewarded-game offers are worth your time before you play.",
};

export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return (
    <html lang="en">
      <body>
        <div className="container nav">
          <Link href="/" className="brand">PlayDirective <span>Rewards</span></Link>
          <nav className="navlinks">
            <Link href="/pricing">Pricing</Link>
            <Link href="/login">Sign in</Link>
            <Link href="/app" className="btn primary">Open app</Link>
          </nav>
        </div>
        {children}
      </body>
    </html>
  );
}
