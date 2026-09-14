import { useEffect, useState } from "react";
import { useReducedMotion } from "framer-motion";

type Line =
  | { kind: "prompt"; text: string }
  | { kind: "out"; text: string; tone?: "muted" | "accent" | "warn" }
  | { kind: "blank" };

const script: Line[] = [
  { kind: "prompt", text: "python -m braid list" },
  {
    kind: "out",
    text: "[backbone] (4)",
    tone: "accent",
  },
  {
    kind: "out",
    text: "  llama32      caps: distributable,gpu,observable,teachable",
  },
  {
    kind: "out",
    text: "  minicpm5     caps: distributable,gpu,observable,teachable",
  },
  {
    kind: "out",
    text: "  qwen25       caps: distributable,gpu,observable,teachable",
  },
  { kind: "out", text: "[catalogstore] (4)", tone: "accent" },
  {
    kind: "out",
    text: "  matmulinmem   caps: distributable,observable",
  },
  {
    kind: "out",
    text: "  faissivfstore caps: distributable,gpu,observable",
  },
  { kind: "blank" },
  { kind: "prompt", text: "python -m braid dryrun --config configs/train/phase2.yaml" },
  { kind: "out", text: "{", tone: "muted" },
  {
    kind: "out",
    text: '  "wouldinstantiate": [',
  },
  {
    kind: "out",
    text: '    { "category": "backbone",     "name": "minicpm5" },',
    tone: "accent",
  },
  {
    kind: "out",
    text: '    { "category": "catalogstore", "name": "matmulinmem" },',
    tone: "accent",
  },
  {
    kind: "out",
    text: '    { "category": "loss",         "name": "braidedloss" },',
    tone: "accent",
  },
  {
    kind: "out",
    text: '    { "category": "rewards",      "name": "composite"   }',
    tone: "accent",
  },
  { kind: "out", text: "  ]", tone: "muted" },
  { kind: "out", text: "}", tone: "muted" },
  { kind: "blank" },
  { kind: "prompt", text: "python -m braid conformance" },
  {
    kind: "out",
    text: "131 / 147 real-pass   ·   16 skipped   ·   ✓ fail-fast",
    tone: "accent",
  },
];

function colorFor(tone: Line extends { tone?: infer T } ? T : never) {
  switch (tone) {
    case "accent":
      return "text-[var(--accent)]";
    case "warn":
      return "text-[var(--color-ember-500)]";
    case "muted":
      return "text-[var(--fg-muted)]";
    default:
      return "text-[var(--fg-soft)]";
  }
}

export function Terminal() {
  const reduce = useReducedMotion();
  const [shown, setShown] = useState<number>(reduce ? script.length : 0);
  const [typing, setTyping] = useState<string>("");

  useEffect(() => {
    if (reduce) {
      setShown(script.length);
      return;
    }
    let mounted = true;
    let i = 0;
    let charIdx = 0;
    let typingId: number | undefined;

    const next = () => {
      if (!mounted) return;
      if (i >= script.length) return;
      const line = script[i];
      if (line.kind === "blank") {
        setShown(i + 1);
        i++;
        typingId = window.setTimeout(next, 80);
        return;
      }
      if (line.kind === "out") {
        setShown(i);
        i++;
        typingId = window.setTimeout(next, 32);
        return;
      }
      // prompt — type char by char
      charIdx = 0;
      setTyping("");
      const type = () => {
        if (!mounted) return;
        charIdx++;
        setTyping(line.text.slice(0, charIdx));
        if (charIdx >= line.text.length) {
          setShown(i + 1);
          setTyping("");
          i++;
          typingId = window.setTimeout(next, 260);
        } else {
          typingId = window.setTimeout(type, 14 + Math.random() * 16);
        }
      };
      type();
    };

    const startId = window.setTimeout(next, 500);
    return () => {
      mounted = false;
      if (typingId) clearTimeout(typingId);
      clearTimeout(startId);
    };
  }, []);

  return (
    <div
      className="animate-fade-up relative"
      style={{ animationDuration: "900ms" }}
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -inset-x-12 -inset-y-10 -z-10 rounded-[40px] glow-blur"
        style={{
          background:
            "radial-gradient(60% 50% at 50% 30%, color-mix(in oklab, var(--accent) 35%, transparent), transparent 70%)",
        }}
      ></div>

      <div
        className="card relative overflow-hidden"
        style={{
          background:
            "linear-gradient(180deg, var(--bg-elev) 0%, color-mix(in oklab, var(--bg-elev) 92%, var(--accent-soft)) 100%)",
        }}
      >
        <div class="flex items-center justify-between border-b border-[var(--line-soft)] px-4 py-3">
          <div class="flex items-center gap-1.5">
            <span class="h-2.5 w-2.5 rounded-full bg-[#FF5F57]/80"></span>
            <span class="h-2.5 w-2.5 rounded-full bg-[#FEBC2E]/80"></span>
            <span class="h-2.5 w-2.5 rounded-full bg-[#28C840]/80"></span>
          </div>
          <div class="font-mono text-[11px] tracking-wide text-[var(--fg-muted)]">
            ~/braid — zsh
          </div>
          <div class="flex items-center gap-2 text-[10px] uppercase tracking-[0.16em] text-[var(--fg-muted)]">
            <span class="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--accent)]"></span>
            live
          </div>
        </div>

        <pre
          className="font-mono text-[12.5px] leading-[1.65] md:text-[13px]"
          style={{ padding: "1.1rem 1.25rem 1.4rem" }}
        >
          <code>
            {script.slice(0, shown).map((line, idx) => {
              if (line.kind === "blank")
                return <div key={idx} class="h-[0.6em]"></div>;
              if (line.kind === "out")
                return (
                  <div key={idx} class={colorFor(line.tone)}>
                    {line.text}
                  </div>
                );
              // prompt
              return (
                <div key={idx} class="flex items-center gap-2 text-[var(--fg)]">
                  <span class="text-[var(--accent)]">›</span>
                  <span>{line.text}</span>
                </div>
              );
            })}
            {typing && (
              <div class="flex items-center gap-2 text-[var(--fg)]">
                <span class="text-[var(--accent)]">›</span>
                <span>{typing}</span>
                <span class="ml-0.5 inline-block h-[1.1em] w-[6px] translate-y-[1px] animate-pulse bg-[var(--fg-soft)]"></span>
              </div>
            )}
            {shown === script.length && (
              <div class="mt-1 flex items-center gap-2 text-[var(--fg-soft)]">
                <span class="text-[var(--accent)]">›</span>
                <span class="inline-block h-[1.1em] w-[7px] animate-pulse bg-[var(--accent)]"></span>
              </div>
            )}
          </code>
        </pre>
      </div>
    </div>
  );
}

export default Terminal;
