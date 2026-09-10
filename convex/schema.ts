import { defineSchema, defineTable } from 'convex/server'
import { v } from 'convex/values'
import { authTables } from '@convex-dev/auth/server'

/**
 * NEW STAR TAILOR — database schema
 *
 * Design notes:
 * - Stitching and material charges are kept separate everywhere.
 * - Order items carry price *snapshots* so later price changes never
 *   rewrite the history of an existing order.
 * - Measurements are versioned: an order points at a specific
 *   measurement_version, so editing a customer's measurements later
 *   does not change what an old order was cut to.
 * - Balances are always derived server-side from verified payments.
 */

export const orderStatuses = ['new', 'measurement', 'ready', 'delivered'] as const
export const priorities = ['normal', 'urgent'] as const
export const fabricSources = ['customer', 'shop'] as const
export const fittingPreferences = ['slim', 'regular', 'relaxed'] as const
export const serviceCategories = ['regular', 'police', 'crpf', 'army'] as const
export const paymentMethods = ['cash', 'upi', 'online'] as const
export const paymentStatuses = ['pending', 'verified'] as const
export const notificationStatuses = ['scheduled', 'sent', 'failed'] as const
export const notificationChannels = ['whatsapp', 'sms'] as const

export default defineSchema({
  ...authTables,

  // users table is provided by authTables; we extend it with app fields.
  users: defineTable({
    name: v.optional(v.string()),
    email: v.optional(v.string()),
    phone: v.optional(v.string()),
    image: v.optional(v.string()),
    emailVerificationTime: v.optional(v.number()),
    phoneVerificationTime: v.optional(v.number()),
    isAnonymous: v.optional(v.boolean()),
    role: v.optional(v.union(v.literal('admin'), v.literal('customer'))),
  })
    .index('email', ['email'])
    .index('phone', ['phone']),

  customers: defineTable({
    name: v.string(),
    mobile: v.string(),
    address: v.optional(v.string()),
    notes: v.optional(v.string()),
    userId: v.optional(v.id('users')),
    fittingPreference: v.optional(
      v.union(...fittingPreferences.map((p) => v.literal(p))),
    ),
    createdBy: v.optional(v.id('users')),
  })
    .index('by_mobile', ['mobile'])
    .index('by_user', ['userId'])
    .searchIndex('search_name', { searchField: 'name' }),

  // Current measurement pointer for a customer (points at latest version).
  measurements: defineTable({
    customerId: v.id('customers'),
    currentVersionId: v.optional(v.id('measurement_versions')),
    updatedBy: v.optional(v.id('users')),
  }).index('by_customer', ['customerId']),

  // Immutable measurement snapshots.
  measurement_versions: defineTable({
    customerId: v.id('customers'),
    measurementId: v.id('measurements'),
    version: v.number(),
    // Free-form key/value cm values, e.g. { chest: 40, waist: 34, "pant_mori": 15 }
    values: v.record(v.string(), v.number()),
    notes: v.optional(v.string()),
    takenBy: v.optional(v.id('users')),
  })
    .index('by_customer', ['customerId'])
    .index('by_measurement', ['measurementId', 'version']),

  services: defineTable({
    name: v.string(),
    nameHi: v.optional(v.string()),
    category: v.union(...serviceCategories.map((c) => v.literal(c))),
    defaultStitchingPrice: v.number(),
    description: v.optional(v.string()),
    active: v.boolean(),
    sortOrder: v.optional(v.number()),
  }).index('by_category', ['category']),

  orders: defineTable({
    orderNumber: v.string(), // NST-000001
    seq: v.number(), // numeric sequence for ordering / generation
    customerId: v.id('customers'),
    measurementVersionId: v.optional(v.id('measurement_versions')),
    status: v.union(...orderStatuses.map((s) => v.literal(s))),
    priority: v.union(...priorities.map((p) => v.literal(p))),
    fabricSource: v.union(...fabricSources.map((f) => v.literal(f))),
    fittingPreference: v.optional(
      v.union(...fittingPreferences.map((p) => v.literal(p))),
    ),
    notes: v.optional(v.string()),
    // Price snapshots (whole order rollup, in INR).
    stitchingTotal: v.number(),
    materialTotal: v.number(),
    grandTotal: v.number(),
    // Advance rule captured at creation: 50 (customer cloth) or 100 (shop cloth).
    requiredAdvancePercent: v.number(),
    promisedDate: v.optional(v.number()),
    source: v.union(v.literal('walk_in'), v.literal('online')),
    createdBy: v.optional(v.id('users')),
    deliveredAt: v.optional(v.number()),
  })
    .index('by_seq', ['seq'])
    .index('by_status', ['status'])
    .index('by_customer', ['customerId'])
    .index('by_order_number', ['orderNumber']),

  order_items: defineTable({
    orderId: v.id('orders'),
    serviceId: v.optional(v.id('services')),
    serviceName: v.string(), // snapshot
    category: v.union(...serviceCategories.map((c) => v.literal(c))),
    stitchingPrice: v.number(), // per unit snapshot
    materialPrice: v.number(), // per unit snapshot (0 when customer brings cloth)
    quantity: v.number(),
    lineTotal: v.number(),
  }).index('by_order', ['orderId']),

  payments: defineTable({
    orderId: v.id('orders'),
    customerId: v.id('customers'),
    amount: v.number(),
    method: v.union(...paymentMethods.map((m) => v.literal(m))),
    status: v.union(...paymentStatuses.map((s) => v.literal(s))),
    transactionRef: v.optional(v.string()),
    note: v.optional(v.string()),
    recordedBy: v.optional(v.id('users')),
    verifiedBy: v.optional(v.id('users')),
    verifiedAt: v.optional(v.number()),
  })
    .index('by_order', ['orderId'])
    .index('by_customer', ['customerId'])
    .index('by_status', ['status']),

  // Webhook idempotency for online payment providers.
  payment_events: defineTable({
    provider: v.string(),
    eventId: v.string(),
    orderId: v.optional(v.id('orders')),
    paymentId: v.optional(v.id('payments')),
    raw: v.optional(v.string()),
    processedAt: v.number(),
  }).index('by_event', ['provider', 'eventId']),

  reference_images: defineTable({
    orderId: v.id('orders'),
    storageId: v.id('_storage'),
    caption: v.optional(v.string()),
    uploadedBy: v.optional(v.id('users')),
  }).index('by_order', ['orderId']),

  notifications: defineTable({
    orderId: v.optional(v.id('orders')),
    customerId: v.optional(v.id('customers')),
    channel: v.union(...notificationChannels.map((c) => v.literal(c))),
    to: v.string(),
    template: v.string(),
    body: v.string(),
    status: v.union(...notificationStatuses.map((s) => v.literal(s))),
    scheduledFor: v.optional(v.number()),
    sentAt: v.optional(v.number()),
    error: v.optional(v.string()),
  })
    .index('by_status', ['status'])
    .index('by_order', ['orderId']),

  settings: defineTable({
    key: v.string(),
    value: v.any(),
  }).index('by_key', ['key']),
})
