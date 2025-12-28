# Kollect-It – AI Agent Working Rules

## Brand & Design

- Overall vibe: luxury, calm, collector-focused, similar to 1stDibs / Chairish.
- Color system: use the tokens from globals.css / tailwind.config.ts (ink, cream, gold, black). Avoid random new hex codes unless necessary.
- Typography: use the configured serif/sans families from Tailwind; no inline style fonts.
- Layout: prefer clean grids, good spacing, clear hierarchy. Mobile-first, then tablet, then desktop.

## Tech Stack

- Next.js 15 App Router (src/app).
- TypeScript everywhere.
- Prisma for database access (prisma/schema.prisma).
- Tailwind CSS for styling.
- Stripe for checkout.
- Resend for transactional email.
- ImageKit (or equivalent) for images.

## Coding Rules

- Keep components small, focused, and reusable.
- Prefer server components unless interactivity is needed.
- Use existing UI components in src/components/ui before creating new ones.
- Do not break existing imports or paths.
- Maintain or improve accessibility (semantic HTML, aria- attributes, skip links, focus states).

## Safety & Process

- Before making large changes:
  - Scan relevant files.
  - Explain the plan in plain English.
  - Wait for approval (from the user) before applying.
- When modifying multiple files:
  - Show a summary of file changes.
  - Avoid destructive changes (don't delete code unless obviously dead).
- Prefer incremental improvements over huge rewrites unless requested.

## Business Logic Priorities

- Phase 1: focus on:
  - Working checkout and orders
  - Solid product browsing and product detail pages
  - Clean header/footer and navigation
  - Functional admin product + order management
  - Complete legal and policy pages

- Phase 2: enhancements:
  - Advanced analytics and reports
  - Realtime features
  - Editorial content, blog, extra UX polish

---

## Phase 1 Task List

### Global UX
- [ ] Header & Footer consistency (nav structure, brand colors, mobile menu)
- [ ] Replace "Sell With Us" with "Consign" across the app
- [ ] Ensure all nav links work and point to correct pages

### Checkout & Orders
- [ ] Cart persistence per user/session
- [ ] Checkout form validation
- [ ] Stripe test mode integration
- [ ] Order creation in Prisma after successful payment
- [ ] Order confirmation email via Resend

### Product Pages
- [ ] Product detail page displays all info correctly
- [ ] Product images work (ImageKit integration)
- [ ] Add to cart functionality
- [ ] Related products / recommendations

### Admin
- [ ] Product approval queue functional
- [ ] Order management (view, update status)
- [ ] Basic dashboard metrics

### Legal & Policy Pages
- [ ] Privacy Policy
- [ ] Terms of Service
- [ ] Shipping & Returns
- [ ] Authentication Guarantee
- [ ] Cookie Policy

---

## Phase 2 Task List (Future)

- [ ] Advanced analytics dashboards
- [ ] Real-time order notifications
- [ ] Blog / editorial content
- [ ] Enhanced search with filters
- [ ] Customer reviews system
- [ ] Seller/consignor portal

