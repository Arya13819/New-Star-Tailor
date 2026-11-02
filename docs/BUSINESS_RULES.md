# Business Rules — single source of truth

Derived from the master prompt (v1.0) plus the owner's clarifications.
If code and this document disagree, this document wins — raise it.

## Shop
- **Name:** New Star Tailor
- **Address:** Old UCO Bank Gully, Near Patel Plaza, Tagore Marg, Neemuch, Madhya Pradesh, India
- **Phone:** 9424035393
- Scope: **men's tailoring only** (the general store is out of scope).

## Services & categories
Categories: `SHIRT`, `PANT`, `POLICE`, `CRPF`, `ARMY`.

| Service | Category | Stitching price |
|---|---|---|
| Shirt | SHIRT | **not set yet** — owner to provide |
| Pant | PANT | **not set yet** — owner to provide |
| Shirt + Pant Combo | SHIRT | ₹550 |
| Police Khaaki | POLICE | ₹700 |
| CRPF Khaaki | CRPF | ₹700 |
| CRPF Cheetah | CRPF | ₹700 |
| CRPF Khaaki Dangri | CRPF | **not set yet** — owner to provide |
| Army Pattern | ARMY | **not set yet** — owner to provide |
| Cheetah US Pattern | **ARMY** | ₹850 |

- All prices are **stitching / labour only**. Cloth is always separate.
- Prices are **configurable by the admin** (Settings). Changing a price affects **new orders only** — existing orders keep the price captured on their items.
- Services with an unset price are seeded inactive / flagged until the owner enters a price.

## Cloth / material
```
Stitching charges + Material charges = Final total
```
- **Customer provides cloth** → material = ₹0 → total = stitching.
- **Shop provides cloth** → material entered **manually** per item → total = stitching + material.
- Material is **never** auto-assumed and **never** folded into the stitching rate.

## Urgent orders
- An order can be marked `URGENT`.
- Urgent price is **entered manually by the admin per order**. There is **no percentage or formula**.

## Advance payment (compulsory)
- **Customer provides cloth** → minimum advance = **50% of stitching subtotal**.
- **Shop provides cloth** → required = **100% of the grand total** (stitching + material).
- **v1 behaviour: warn, do not block.** An order is still confirmed and gets its NST number even if the advance is short; it is flagged "advance not received" on the order, dashboard and pending list. (Switchable to hard-block later via a settings flag.)

## Payments
- Methods: `CASH`, `UPI`, `ONLINE`.
- Cash / UPI recorded by the admin are **verified** immediately.
- Online payments are **PENDING** until a provider webhook (or manual admin check) verifies them. **No fake verification, ever.**
- **Partial payments allowed.** Every payment is a separate row; nothing is overwritten.
- Balance is computed **server-side**: `grand_total − Σ(verified payments)`. Frontend totals are never trusted.
- Money uses `DECIMAL` / `Decimal` only — never floating point.
- **No udhaar / credit system.** An unpaid balance is just that order's remaining balance.

## Order numbers
- Format `NST-0001`, zero-padded to **4 digits** (owner's call, 2026-09-18 —
  was 6), auto-incrementing. This is a minimum width, not a cap: order #10000
  still prints in full as `NST-10000`, so it never needs code changes to
  "widen" later — only `Config.ORDER_NUMBER_PAD` would change, and only to
  alter how many leading zeros a low number shows.
- Generated **server-side**, atomically. Never generated on the frontend.
- Assigned when an order is confirmed (walk-in: on create; complete online order: on submit). Enquiries get no number until converted to an order.

## Order status
`NEW → MEASUREMENT → READY → DELIVERED`
- Changed **manually** by the admin. No automatic transitions in v1.

## Delivery
- Normal: **10–15 days** after confirmation.
- Customer may **request** a date; admin **confirms** the final date.

## Measurements
- Unit: **inches**.
- Shirt: Length, Chest, Shoulder, Sleeves, Neck.
- Pant: Length, Waist, Hips, Mori (pant end).
- Police / CRPF / Army use the same base fields for now; schema must allow uniform-specific fields later.
- Fitting: `LOOSE`, `NORMAL`, `SLIM`. Plus allowance, fitting preference, special notes, alteration notes.
- **Versioned.** Editing a customer's measurements creates a new version. Old orders keep the exact version they were made with (referenced per order item).
- No family-wide measurement profile — every person has their own measurements.

## Customers
- Fields: Name, Mobile, Address.
- **Mobile is NOT unique.** Two people (e.g. family members) can share a mobile and remain separate customer profiles.
- A customer profile may be linked to a login account (`user_id`), or not (walk-ins created by the admin).
- **Known gap (flag before Phase 11):** if a walk-in customer later self-registers a portal account with the *same* mobile number, registration creates a brand-new `Customer` profile rather than linking to their existing walk-in history — their old orders won't show in the portal. Deliberately not auto-linked by mobile alone (a recycled SIM could otherwise let a stranger inherit someone else's order history); needs an explicit "claim my history" flow with a real identity check if the owner wants this solved.

## Self-submitted measurements (online)
- Optional. If the customer enters their own measurements, they must see and accept an acknowledgement that **they are responsible for the accuracy** and the shop is not liable for measurement-related issues from self-submitted values.
- The acknowledgement (and timestamp) is stored on the order.

## Reference images
- Customer may upload one or more: `jpg`, `jpeg`, `png`, `webp` only.
- Validated by extension **and** content (Pillow), size-capped, stored with a random filename outside the web root, served only to authorised users.

## Notifications (architecture now, sending later)
Types: Order Confirmation, Order Ready, Delivery Reminder, Payment Reminder, New Enquiry (shop-facing).
- Channel: **plain SMS only** (owner's explicit choice, 2026-09-21) — never WhatsApp, to avoid the Meta Business verification process. An Indian SMS gateway still needs a DLT-registered sender ID and pre-approved templates before sending works.
- Customer-facing messages (order confirmation, order ready, payment reminder) go in Hinglish by default, or Hindi if the customer's own portal account has set that language preference — never the admin's UI language at the moment the message happens to be queued.
- A new public enquiry also queues a message to the shop's own number, so it isn't missed by only checking `/admin/enquiries`.
- **Payment reminders** start **7 days after delivery** if a balance remains, then follow a configurable policy until paid. Duplicates prevented via a unique dedupe key.
- The system never claims a message was sent unless the provider confirmed it. If messaging is not configured, that state is shown plainly.

## Online payment provider
- Abstracted behind an interface: `create_payment`, `verify_payment`, `handle_webhook`, `refund_payment`.
- Default provider `manual` = staff-verified, no external calls.
- Webhook endpoint exists but is inert until a real provider + credentials are configured. `payment_events` has a `UNIQUE(provider, event_id)` constraint so a duplicate webhook can never create a duplicate payment.

## Roles
- **ADMIN** — the shop operator (one primary user; elder family member). Mobile-first, large controls, search-led, bilingual.
- **CUSTOMER** — registers with **mobile + password**, sees own orders / measurements / payment history only. Strict data isolation.

## Languages
- English + Hindi, switchable. All user-facing text goes through translation catalogs (Flask-Babel).

## Auditability
- Timestamps on order creation, payment creation, payment verification, status changes, delivery, notification events.
- Lightweight `audit_logs` table for status and payment changes.

## Explicitly out of scope for v1
Inventory, cloth stock, employees, payroll, accounting, multi-branch, loyalty, coupons, appointment booking, advanced alteration workflow, badge/insignia management, detailed uniform-specific measurements, native Android app. Architecture stays extensible for them.
