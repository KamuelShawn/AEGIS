"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-graphite-950 px-6">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 left-1/2 h-[600px] w-[900px] -translate-x-1/2 rounded-full bg-sustaina-green/10 blur-3xl" />
        <div className="absolute bottom-0 right-0 h-[400px] w-[500px] rounded-full bg-sustaina-blue/10 blur-3xl" />
      </div>

      <motion.p
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="mb-6 text-xs uppercase tracking-[0.3em] text-earth-300/60"
      >
        SUSTAINA · Sustainability Intelligence &amp; Geospatial Decision Platform
      </motion.p>

      <motion.h1
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, delay: 0.15 }}
        className="max-w-4xl text-center text-5xl font-extrabold leading-[1.05] tracking-tight md:text-7xl"
      >
        DEVELOP WITHOUT
        <br />
        DESTROYING
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, delay: 0.35 }}
        className="mt-6 max-w-xl text-center text-lg text-earth-300/80"
      >
        Understand the land. Predict the future. Build responsibly.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, delay: 0.55 }}
        className="mt-12 flex gap-4"
      >
        <Link
          href="/explore"
          className="rounded-md bg-sustaina-green px-7 py-3 text-sm font-semibold text-graphite-950 transition hover:brightness-110"
        >
          Enter the Platform
        </Link>
        <Link
          href="/explore?region=bandipur"
          className="rounded-md border border-graphite-600 px-7 py-3 text-sm font-semibold text-earth-100 transition hover:border-earth-300/40"
        >
          View Bandipur Case Study
        </Link>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.2, delay: 1 }}
        className="mt-20 grid grid-cols-1 gap-8 text-center text-sm text-earth-300/60 sm:grid-cols-4"
      >
        {["Environment", "Resources", "Infrastructure", "Decision"].map((label, i) => (
          <div key={label} className="flex flex-col items-center gap-2">
            <span className="text-xs uppercase tracking-widest">{String(i + 1).padStart(2, "0")}</span>
            <span className="text-earth-200/80">{label}</span>
          </div>
        ))}
      </motion.div>
    </main>
  );
}
