import { useState } from "react";
import { motion } from "framer-motion";
import {
  Map,
  Sparkles,
  Hotel,
  Megaphone,
  Users,
  Settings,
  Globe,
  LogOut,
  LayoutDashboard,
  Plus,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { fadeUp, pageVariants, staggerContainer } from "@/lib/motion";

const nav = [
  { icon: LayoutDashboard, label: "Overview", active: true },
  { icon: Map, label: "Trips" },
  { icon: Sparkles, label: "Creative" },
  { icon: Hotel, label: "Sourcing" },
  { icon: Megaphone, label: "Publishing" },
  { icon: Users, label: "Leads" },
  { icon: Settings, label: "Settings" },
];

const modules = [
  { icon: Map, title: "Trip Builder", desc: "Generate a day-by-day itinerary with AI.", phase: "Phase 1" },
  { icon: Sparkles, title: "Creative Studio", desc: "Posters, captions and brochures.", phase: "Phase 1" },
  { icon: Users, title: "Leads & CRM", desc: "Capture leads and auto-followup.", phase: "Phase 2" },
  { icon: Hotel, title: "Sourcing", desc: "Reach out to hotels & transport.", phase: "Phase 3" },
  { icon: Megaphone, title: "Publishing", desc: "Schedule Instagram posts.", phase: "Phase 3" },
];

export function Dashboard() {
  const { user, tenant, logout } = useAuth();
  const [active, setActive] = useState("Overview");

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex min-h-screen bg-[#f7f9fc] text-[var(--color-ink)]"
    >
      {/* Sidebar */}
      <aside className="hidden w-64 shrink-0 flex-col border-r border-black/5 bg-white px-4 py-6 md:flex">
        <div className="mb-8 flex items-center gap-2 px-2 font-semibold">
          <Globe className="h-6 w-6 text-[var(--color-ocean-500)]" />
          TravelOS
        </div>
        <nav className="flex-1 space-y-1">
          {nav.map((item) => {
            const isActive = item.label === active;
            return (
              <button
                key={item.label}
                onClick={() => setActive(item.label)}
                className="relative flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-black/60 transition hover:text-black"
              >
                {isActive && (
                  <motion.div
                    layoutId="nav-active"
                    className="absolute inset-0 rounded-xl bg-[var(--color-ocean-50)]"
                  />
                )}
                <item.icon
                  className={`relative h-4.5 w-4.5 ${isActive ? "text-[var(--color-ocean-600)]" : ""}`}
                />
                <span className={`relative ${isActive ? "text-[var(--color-ocean-600)]" : ""}`}>
                  {item.label}
                </span>
              </button>
            );
          })}
        </nav>
        <button
          onClick={logout}
          className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-black/50 transition hover:bg-black/5 hover:text-black"
        >
          <LogOut className="h-4 w-4" /> Log out
        </button>
      </aside>

      {/* Main */}
      <main className="flex-1 px-6 py-8 sm:px-10">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-sm text-black/50">{tenant?.name}</p>
            <h1 className="text-2xl font-bold">
              Welcome back, {user?.full_name?.split(" ")[0]} 👋
            </h1>
          </div>
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-[var(--color-teal-400)] to-[var(--color-ocean-500)] font-semibold text-white">
            {user?.full_name?.[0]?.toUpperCase()}
          </div>
        </header>

        {/* Quick stats */}
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="mb-10 grid grid-cols-2 gap-4 lg:grid-cols-4"
        >
          {[
            { label: "Active trips", value: "0" },
            { label: "New leads", value: "0" },
            { label: "Pending approvals", value: "0" },
            { label: "Deals closed", value: "0" },
          ].map((s) => (
            <motion.div
              key={s.label}
              variants={fadeUp}
              className="rounded-2xl border border-black/5 bg-white p-5"
            >
              <p className="text-sm text-black/50">{s.label}</p>
              <p className="mt-1 text-3xl font-bold">{s.value}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Module cards */}
        <h2 className="mb-4 text-lg font-semibold">Your workspace</h2>
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
        >
          {modules.map((m) => (
            <motion.div
              key={m.title}
              variants={fadeUp}
              whileHover={{ y: -4 }}
              className="group rounded-2xl border border-black/5 bg-white p-6 transition hover:shadow-lg hover:shadow-black/5"
            >
              <div className="mb-4 flex items-center justify-between">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--color-ocean-50)]">
                  <m.icon className="h-5 w-5 text-[var(--color-ocean-600)]" />
                </div>
                <span className="rounded-full bg-black/5 px-2.5 py-1 text-xs font-medium text-black/50">
                  {m.phase}
                </span>
              </div>
              <h3 className="font-semibold">{m.title}</h3>
              <p className="mt-1 text-sm text-black/55">{m.desc}</p>
              <button className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-[var(--color-ocean-600)] opacity-0 transition group-hover:opacity-100">
                <Plus className="h-4 w-4" /> Coming soon
              </button>
            </motion.div>
          ))}
        </motion.div>
      </main>
    </motion.div>
  );
}
