import { useEffect, useRef, useState } from "react";
import { motion, useReducedMotion, type Variants } from "framer-motion";
import clsx from "clsx";

type Props = {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  y?: number;
  as?: "div" | "section" | "article" | "header" | "li" | "ul";
};

const variants: Variants = {
  hidden: { opacity: 0, y: 22, filter: "blur(6px)" },
  show: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] },
  },
};

export function Reveal({
  children,
  className,
  delay = 0,
  y = 22,
  as = "div",
}: Props) {
  const reduce = useReducedMotion();
  const Tag = motion[as] as typeof motion.div;
  if (reduce) {
    return <Tag className={className}>{children}</Tag>;
  }
  return (
    <Tag
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.8, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </Tag>
  );
}

type StaggerProps = {
  children: React.ReactNode;
  className?: string;
  step?: number;
  start?: number;
  as?: "div" | "ul" | "ol" | "section";
};

export function Stagger({
  children,
  className,
  step = 0.06,
  start = 0,
  as = "div",
}: StaggerProps) {
  const reduce = useReducedMotion();
  const Tag = motion[as] as typeof motion.div;
  const container: Variants = {
    hidden: {},
    show: { transition: { staggerChildren: step, delayChildren: start } },
  };
  if (reduce) return <Tag className={className}>{children}</Tag>;
  return (
    <Tag
      className={className}
      variants={container}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: "-80px" }}
    >
      {children}
    </Tag>
  );
}

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 18 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] },
  },
};

export function StaggerItem({
  children,
  className,
  as = "div",
}: {
  children: React.ReactNode;
  className?: string;
  as?: "div" | "li" | "article";
}) {
  const reduce = useReducedMotion();
  const Tag = motion[as] as typeof motion.div;
  if (reduce) return <Tag className={className}>{children}</Tag>;
  return (
    <Tag className={className} variants={itemVariants}>
      {children}
    </Tag>
  );
}

export function MagneticHover({
  children,
  className,
  strength = 8,
}: {
  children: React.ReactNode;
  className?: string;
  strength?: number;
}) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const el = ref.current;
    if (!el || reduce) return;
    const onMove = (e: MouseEvent) => {
      const r = el.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width - 0.5) * strength;
      const y = ((e.clientY - r.top) / r.height - 0.5) * strength;
      setPos({ x, y });
    };
    const onLeave = () => setPos({ x: 0, y: 0 });
    el.addEventListener("mousemove", onMove);
    el.addEventListener("mouseleave", onLeave);
    return () => {
      el.removeEventListener("mousemove", onMove);
      el.removeEventListener("mouseleave", onLeave);
    };
  }, [strength, reduce]);

  return (
    <div
      ref={ref}
      className={clsx("transition-transform duration-300 will-change-transform", className)}
      style={{ transform: `translate3d(${pos.x}px, ${pos.y}px, 0)` }}
    >
      {children}
    </div>
  );
}
