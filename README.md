# New Star Tailor

A full-stack web app for **New Star Tailor**, a tailoring shop in Neemuch, Madhya Pradesh.
It has public customer-facing pages and a protected admin panel for shop staff.

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, shadcn-style UI, React Router v7, Motion
- **Backend:** Convex (database + serverless functions)
- **Auth:** Convex Auth with email one-time-password (staff only)
- **Bilingual:** English + Hindi, language preference saved locally

## Getting started

```bash
npm install

# 1. Provision a Convex deployment. Follow the prompts (creates .env.local
#    with VITE_CONVEX_URL and generates convex/_generated).
npx convex dev

# 2. In a second terminal, start the web app.
npm run dev
```

Open the app, go to `/auth`, and sign in with any email. **The first account to
sign in becomes the shop admin.** Every later account starts with no access and
must be promoted from **Settings → Staff access**.

Without an email provider configured, the 6-digit sign-in code is printed to the
`npx convex dev` logs.

### Optional: real sign-in emails

```bash
npx convex env set AUTH_RESEND_KEY re_xxxxxxxx
npx convex env set AUTH_EMAIL_FROM "New Star Tailor <orders@yourdomain.com>"
```

### Demo data

Sign in, then open **Settings → Demo data → Load demo data** for 8 customers and
12 orders across every status, with cash / UPI / online payments.

## Routes

| Public | Admin (requires staff access) |
| --- | --- |
| `/` landing | `/admin/dashboard` |
| `/services` catalogue & pricing | `/admin/orders`, `/admin/orders/new`, `/admin/orders/:id` |
| `/track-order` order number + mobile | `/admin/customers`, `/admin/customers/:id` |
| `/enquiry` enquiry or online order | `/admin/payments` |
| `/receipt/:orderId` printable receipt | `/admin/reports` |
| `/auth` staff sign-in | `/admin/settings` |

## Key business rules

- Stitching and material charges are tracked separately everywhere.
- Advance required: 50% of stitching when the customer brings cloth, 100% when the shop provides it.
- Order items store price snapshots — changing a service price never rewrites old orders.
- Measurements are versioned; an order keeps the measurement version it was created with.
- Order numbers are `NST-000001`, auto-incrementing.
- Balances are computed server-side from **verified** payments only.

## Project layout

```
convex/            Backend schema + functions
  schema.ts        Tables, indexes, validators
  auth.ts          Convex Auth (email OTP), role assignment
  orders.ts        Order creation, numbering, tracking, receipts
  payments.ts      Partial payments, verification, advance rules
  ...
src/
  i18n/            English + Hindi dictionaries
  components/ui/   shadcn-style primitives
  pages/public/    Landing, Services, TrackOrder, Enquiry, Receipt
  pages/admin/     Dashboard, Orders, NewOrder, OrderDetail, Customers, ...
```

## Notes

- `convex/_generated/` is committed so the app typechecks before the first
  `npx convex dev`; that command regenerates it in place.
- `@auth/core` carries an advisory pinned by `@convex-dev/auth`'s peer range.
  This app uses email OTP only (no OAuth), so the OAuth-cookie issues do not
  apply; upgrade when `@convex-dev/auth` widens the range.
