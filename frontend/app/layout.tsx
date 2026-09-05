import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SUSTAINA — Develop Without Destroying",
  description: "A sustainability intelligence & geospatial decision platform for India.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-graphite-950 text-earth-100 antialiased">{children}</body>
    </html>
  );
}
