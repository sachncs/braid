# braid — product site

The marketing site for [braid](https://github.com/sachncs/braid). Built with
[Astro](https://astro.build/) + [React](https://react.dev/) +
[Tailwind CSS v4](https://tailwindcss.com/) + [Framer Motion](https://motion.dev/).

The site is intentionally **not** rendered from project docs or markdown — every
section is hand-authored to feel like a real product launch page.

## Develop

```bash
cd site
npm install
npm run dev          # http://localhost:4321/braid
```

## Build

```bash
npm run build        # output → site/dist/
npm run preview      # preview the production build
```

The build output (`site/dist/`) is what GitHub Pages serves at
`https://sachncs.github.io/braid/`.

## Deploy

Pushing to `master` triggers `.github/workflows/pages.yml`, which builds
`site/` and deploys `site/dist/` to GitHub Pages.

## Stack

| Tool | Why |
| --- | --- |
| **Astro 5** | Static-first, island architecture, View Transitions built-in. |
| **React 18** | Islands for interactive bits (terminal animation, registry explorer, theme toggle). |
| **Tailwind CSS v4** | CSS-first design tokens via `@theme`. |
| **Framer Motion** | Scroll-reveal animations on React islands, with full `prefers-reduced-motion` respect. |
| **Inter + JetBrains Mono** | Self-hosted via `@fontsource-variable/*`. |

## File map

```
site/
├── astro.config.mjs        ← base: '/braid', output: 'static', vite tailwind plugin
├── package.json
├── public/
│   ├── favicon.svg
│   └── og.svg              ← Open Graph image
└── src/
    ├── assets/logo.svg
    ├── components/         ← Nav, Hero, Terminal, Stats, Marquee,
    │                         FeatureGrid, Architecture, CodeShowcase,
    │                         Registry, UseCases, CTA, Footer, Reveal
    ├── layouts/Base.astro
    ├── pages/index.astro
    └── styles/global.css   ← design tokens, base styles, components
```

## Conventions

- Headlines use `font-weight: 600` with tight tracking — never `font-black`.
- Color tokens are CSS custom properties on `:root` / `html.dark`. Components
  consume `var(--fg)`, `var(--fg-muted)`, `var(--accent)`, etc.
- Light + dark theme are equal citizens. Default follows
  `prefers-color-scheme`; the toggle persists in `localStorage`.
- Every motion is gated on `prefers-reduced-motion`.
