import { motion, useReducedMotion } from "framer-motion";

type Item = { name: string; caps: string[] };

type Category = {
  name: string;
  count: number;
  blurb: string;
  items: Item[];
  accent?: string;
};

const CATEGORIES: Category[] = [
  {
    name: "backbone",
    count: 4,
    blurb:
      "Continued-pretraining and ranking heads for MiniCPM-5, Llama 3.2, Qwen 2.5, and Pythia-1B.",
    items: [
      { name: "llama32", caps: ["distributable", "gpu", "teachable"] },
      { name: "minicpm5", caps: ["distributable", "gpu", "teachable"] },
      { name: "qwen25", caps: ["distributable", "gpu", "teachable"] },
      { name: "pythia1", caps: ["distributable", "gpu", "teachable"] },
    ],
  },
  {
    name: "catalogstore",
    count: 4,
    blurb:
      "Matmul, int4 AWQ, FAISS IVF, and RQ-VAE semantic-id stores — all gated by `h @ E.T`.",
    items: [
      { name: "matmulinmem", caps: ["distributable"] },
      { name: "matmulint4awq", caps: ["int4quantize", "distributable"] },
      { name: "faissivfstore", caps: ["distributable", "gpu"] },
      { name: "semanticids", caps: ["distributable"] },
    ],
  },
  {
    name: "reward",
    count: 5,
    blurb:
      "Long-term return, diversity bonus, novelty, content-type balance — and a composite that weighted-sums them.",
    items: [
      { name: "longtermreturn", caps: ["teachable"] },
      { name: "diversitybonus", caps: [] },
      { name: "noveltyreward", caps: [] },
      { name: "contenttypebalance", caps: [] },
      { name: "composite", caps: [] },
    ],
  },
  {
    name: "loss",
    count: 6,
    blurb:
      "Ranking-CE, L-max, calibration, reward-weighted, diversity-entropy — and `braidedloss` to combine them.",
    items: [
      { name: "rankingce", caps: [] },
      { name: "lmax", caps: [] },
      { name: "rewardweighted", caps: [] },
      { name: "diversityentropy", caps: [] },
      { name: "calibration", caps: [] },
      { name: "braidedloss", caps: ["composite"] },
    ],
  },
  {
    name: "eval",
    count: 7,
    blurb:
      "Offline ranking, calibration, diversity, replay, interleaving, baseline — plus a composite with bootstrap CI.",
    items: [
      { name: "offlineranking", caps: [] },
      { name: "calibration", caps: [] },
      { name: "diversity", caps: [] },
      { name: "replay", caps: [] },
      { name: "interleaving", caps: [] },
      { name: "baseline", caps: [] },
      { name: "composite", caps: [] },
    ],
  },
  {
    name: "drift",
    count: 4,
    blurb:
      "PSI, Kolmogorov-Smirnov, Jensen-Shannon divergence, and Page-Hinkley — all detectable from the registry.",
    items: [
      { name: "psi", caps: [] },
      { name: "ks", caps: [] },
      { name: "jsd", caps: [] },
      { name: "pagehinkley", caps: ["sequential"] },
    ],
  },
];

export function RegistryExplorer() {
  const reduce = useReducedMotion();

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {CATEGORIES.map((cat, idx) => (
        <motion.article
          key={cat.name}
          initial={false}
          whileInView={
            reduce
              ? undefined
              : { opacity: 1, y: 0 }
          }
          viewport={{ once: true, margin: "-60px" }}
          transition={{
            duration: 0.7,
            delay: idx * 0.05,
            ease: [0.16, 1, 0.3, 1],
          }}
          whileHover={
            reduce
              ? undefined
              : { y: -4, transition: { duration: 0.25, ease: "easeOut" } }
          }
          className="group card relative overflow-hidden p-6 transition-shadow duration-500 hover:shadow-[0_30px_60px_-30px_color-mix(in_oklab,var(--accent)_30%,transparent)]"
        >
          <header className="flex items-baseline justify-between">
            <h3
              className="font-mono text-[15px] font-semibold tracking-tight"
              style={{ color: "var(--fg)" }}
            >
              {cat.name}
            </h3>
            <span
              className="rounded-full px-2 py-0.5 font-mono text-[10.5px] uppercase tracking-[0.14em] ring-soft"
              style={{
                background:
                  "color-mix(in oklab, var(--accent) 12%, transparent)",
                color: "var(--accent)",
              }}
            >
              {cat.count} concretes
            </span>
          </header>

          <p className="mt-3 text-[13.5px] leading-[1.55] text-[var(--fg-muted)]">
            {cat.blurb}
          </p>

          <ul className="mt-5 space-y-1.5">
            {cat.items.map((it) => (
              <li
                key={it.name}
                className="flex items-center justify-between gap-3 rounded-md px-2 py-1 font-mono text-[12.5px] transition-colors hover:bg-[color-mix(in_oklab,var(--fg)_4%,transparent)]"
              >
                <span className="flex items-center gap-2 text-[var(--fg-soft)]">
                  <span className="h-1 w-1 rounded-full bg-[var(--accent)] opacity-60"></span>
                  {it.name}
                </span>
                {it.caps.length > 0 && (
                  <span className="truncate text-[10.5px] uppercase tracking-[0.12em] text-[var(--fg-muted)]">
                    {it.caps.join(" · ")}
                  </span>
                )}
              </li>
            ))}
          </ul>

          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-x-0 bottom-0 h-px"
            style={{
              background:
                "linear-gradient(90deg, transparent, color-mix(in oklab, var(--accent) 60%, transparent), transparent)",
              opacity: 0,
              transition: "opacity 400ms var(--ease-out-soft, ease)",
            }}
          />
          <style>{`
            .group:hover > div[aria-hidden="true"] { opacity: 1; }
          `}</style>
        </motion.article>
      ))}
    </div>
  );
}

export default RegistryExplorer;
