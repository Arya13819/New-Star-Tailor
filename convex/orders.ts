import { query, mutation } from './_generated/server'
import { v } from 'convex/values'
import type { Doc, Id } from './_generated/dataModel'
import {
  requireAdmin,
  formatOrderNumber,
  normaliseMobile,
  round2,
  verifiedPaidForOrder,
  pendingPaidForOrder,
} from './lib/helpers'
import { findOrCreateCustomer } from './customers'
import {
  orderStatuses,
  priorities,
  fabricSources,
  fittingPreferences,
  serviceCategories,
} from './schema'

const statusValidator = v.union(...orderStatuses.map((s) => v.literal(s)))
const fittingValidator = v.union(...fittingPreferences.map((p) => v.literal(p)))

async function nextOrderSeq(ctx: {
  db: any
}): Promise<number> {
  const row = await ctx.db
    .query('settings')
    .withIndex('by_key', (q: any) => q.eq('key', 'order_seq'))
    .first()
  const current = typeof row?.value === 'number' ? row.value : 0
  const next = current + 1
  if (row) {
    await ctx.db.patch(row._id, { value: next })
  } else {
    await ctx.db.insert('settings', { key: 'order_seq', value: next })
  }
  return next
}

const itemInput = v.object({
  serviceId: v.optional(v.id('services')),
  serviceName: v.string(),
  category: v.union(...serviceCategories.map((c) => v.literal(c))),
  stitchingPrice: v.number(),
  materialPrice: v.number(),
  quantity: v.number(),
})

export const create = mutation({
  args: {
    customerId: v.optional(v.id('customers')),
    newCustomer: v.optional(
      v.object({
        name: v.string(),
        mobile: v.string(),
        address: v.optional(v.string()),
      }),
    ),
    items: v.array(itemInput),
    fabricSource: v.union(...fabricSources.map((f) => v.literal(f))),
    priority: v.union(...priorities.map((p) => v.literal(p))),
    fittingPreference: v.optional(fittingValidator),
    notes: v.optional(v.string()),
    promisedDate: v.optional(v.number()),
    source: v.optional(v.union(v.literal('walk_in'), v.literal('online'))),
  },
  handler: async (ctx, args) => {
    const admin = await requireAdmin(ctx)

    if (args.items.length === 0) {
      throw new Error('Add at least one service to the order.')
    }

    let customerId = args.customerId
    if (!customerId) {
      if (!args.newCustomer) throw new Error('Select or create a customer first.')
      customerId = await findOrCreateCustomer(ctx, {
        ...args.newCustomer,
        createdBy: admin._id,
      })
    }

    const customer = await ctx.db.get(customerId)
    if (!customer) throw new Error('Customer not found.')

    // Current measurement version snapshot (may be null if none taken yet).
    const measurementDoc = await ctx.db
      .query('measurements')
      .withIndex('by_customer', (q) => q.eq('customerId', customerId))
      .first()
    const measurementVersionId = measurementDoc?.currentVersionId ?? undefined

    const shopProvidesCloth = args.fabricSource === 'shop'

    let stitchingTotal = 0
    let materialTotal = 0
    const normalisedItems = args.items.map((it) => {
      const qty = Math.max(1, Math.round(it.quantity))
      const stitching = round2(it.stitchingPrice)
      // Material only applies when the shop supplies the cloth.
      const material = shopProvidesCloth ? round2(it.materialPrice) : 0
      const lineTotal = round2((stitching + material) * qty)
      stitchingTotal += stitching * qty
      materialTotal += material * qty
      return { ...it, quantity: qty, stitchingPrice: stitching, materialPrice: material, lineTotal }
    })
    stitchingTotal = round2(stitchingTotal)
    materialTotal = round2(materialTotal)
    const grandTotal = round2(stitchingTotal + materialTotal)

    const seq = await nextOrderSeq(ctx)
    const orderNumber = formatOrderNumber(seq)

    const orderId = await ctx.db.insert('orders', {
      orderNumber,
      seq,
      customerId,
      measurementVersionId,
      status: 'new',
      priority: args.priority,
      fabricSource: args.fabricSource,
      fittingPreference: args.fittingPreference ?? customer.fittingPreference,
      notes: args.notes?.trim() || undefined,
      stitchingTotal,
      materialTotal,
      grandTotal,
      requiredAdvancePercent: shopProvidesCloth ? 100 : 50,
      promisedDate: args.promisedDate,
      source: args.source ?? 'walk_in',
      createdBy: admin._id,
    })

    for (const it of normalisedItems) {
      await ctx.db.insert('order_items', {
        orderId,
        serviceId: it.serviceId,
        serviceName: it.serviceName,
        category: it.category,
        stitchingPrice: it.stitchingPrice,
        materialPrice: it.materialPrice,
        quantity: it.quantity,
        lineTotal: it.lineTotal,
      })
    }

    return { orderId, orderNumber, grandTotal, requiredAdvancePercent: shopProvidesCloth ? 100 : 50 }
  },
})

function decorate(order: Doc<'orders'>, paid: number, pending: number) {
  const balance = round2(order.grandTotal - paid)
  const requiredAdvance = round2(
    (order.stitchingTotal * order.requiredAdvancePercent) / 100 +
      order.materialTotal,
  )
  return {
    ...order,
    paid,
    pendingPaid: pending,
    balance,
    requiredAdvance,
    advanceMet: paid + 1e-6 >= requiredAdvance,
  }
}

export const list = query({
  args: {
    status: v.optional(statusValidator),
    search: v.optional(v.string()),
  },
  handler: async (ctx, { status, search }) => {
    await requireAdmin(ctx)
    let orders = status
      ? await ctx.db
          .query('orders')
          .withIndex('by_status', (q) => q.eq('status', status))
          .order('desc')
          .collect()
      : await ctx.db.query('orders').order('desc').collect()

    const term = (search ?? '').trim().toLowerCase()

    const rows = await Promise.all(
      orders.map(async (o) => {
        const customer = await ctx.db.get(o.customerId)
        const paid = await verifiedPaidForOrder(ctx, o._id)
        const pending = await pendingPaidForOrder(ctx, o._id)
        return {
          ...decorate(o, paid, pending),
          customerName: customer?.name ?? '—',
          customerMobile: customer?.mobile ?? '',
        }
      }),
    )

    if (!term) return rows
    const digits = normaliseMobile(term)
    return rows.filter(
      (r) =>
        r.orderNumber.toLowerCase().includes(term) ||
        r.customerName.toLowerCase().includes(term) ||
        (digits.length >= 3 && normaliseMobile(r.customerMobile).includes(digits)),
    )
  },
})

export const counts = query({
  args: {},
  handler: async (ctx) => {
    await requireAdmin(ctx)
    const all = await ctx.db.query('orders').collect()
    const byStatus = { new: 0, measurement: 0, ready: 0, delivered: 0 }
    for (const o of all) byStatus[o.status] += 1
    return {
      total: all.length,
      new: byStatus.new,
      measurement: byStatus.measurement,
      ready: byStatus.ready,
      delivered: byStatus.delivered,
    }
  },
})

export const get = query({
  args: { id: v.id('orders') },
  handler: async (ctx, { id }) => {
    await requireAdmin(ctx)
    const order = await ctx.db.get(id)
    if (!order) return null
    const customer = await ctx.db.get(order.customerId)
    const items = await ctx.db
      .query('order_items')
      .withIndex('by_order', (q) => q.eq('orderId', id))
      .collect()
    const payments = await ctx.db
      .query('payments')
      .withIndex('by_order', (q) => q.eq('orderId', id))
      .order('desc')
      .collect()
    const measurementVersion = order.measurementVersionId
      ? await ctx.db.get(order.measurementVersionId)
      : null
    const paid = await verifiedPaidForOrder(ctx, id)
    const pending = await pendingPaidForOrder(ctx, id)

    return {
      ...decorate(order, paid, pending),
      customer,
      items,
      payments,
      measurementVersion,
    }
  },
})

/** PUBLIC: track an order by number + last 4/full mobile digits. */
export const track = query({
  args: { orderNumber: v.string(), mobile: v.string() },
  handler: async (ctx, { orderNumber, mobile }) => {
    const num = orderNumber.trim().toUpperCase().replace(/\s+/g, '')
    const order = await ctx.db
      .query('orders')
      .withIndex('by_order_number', (q) => q.eq('orderNumber', num))
      .first()
    if (!order) return { found: false as const }

    const customer = await ctx.db.get(order.customerId)
    const given = normaliseMobile(mobile)
    const actual = normaliseMobile(customer?.mobile ?? '')
    const matches =
      given.length >= 4 &&
      (actual === given || actual.endsWith(given))
    if (!matches) return { found: false as const }

    const items = await ctx.db
      .query('order_items')
      .withIndex('by_order', (q) => q.eq('orderId', order._id))
      .collect()
    const paid = await verifiedPaidForOrder(ctx, order._id)

    return {
      found: true as const,
      orderNumber: order.orderNumber,
      status: order.status,
      priority: order.priority,
      fabricSource: order.fabricSource,
      createdAt: order._creationTime,
      promisedDate: order.promisedDate,
      deliveredAt: order.deliveredAt,
      customerName: customer?.name ?? '',
      items: items.map((i) => ({
        serviceName: i.serviceName,
        quantity: i.quantity,
      })),
      grandTotal: order.grandTotal,
      paid,
      balance: round2(order.grandTotal - paid),
    }
  },
})

/** PUBLIC receipt view. Needs the id only (link is shareable but unguessable). */
export const receipt = query({
  args: { id: v.id('orders') },
  handler: async (ctx, { id }) => {
    const order = await ctx.db.get(id)
    if (!order) return null
    const customer = await ctx.db.get(order.customerId)
    const items = await ctx.db
      .query('order_items')
      .withIndex('by_order', (q) => q.eq('orderId', id))
      .collect()
    const payments = await ctx.db
      .query('payments')
      .withIndex('by_order', (q) => q.eq('orderId', id))
      .order('asc')
      .collect()
    const settings = await ctx.db.query('settings').collect()
    const shop = settings.find((s) => s.key === 'shop')?.value ?? null
    const paid = round2(
      payments
        .filter((p) => p.status === 'verified')
        .reduce((s, p) => s + p.amount, 0),
    )

    return {
      orderNumber: order.orderNumber,
      status: order.status,
      createdAt: order._creationTime,
      promisedDate: order.promisedDate,
      priority: order.priority,
      fabricSource: order.fabricSource,
      fittingPreference: order.fittingPreference ?? null,
      notes: order.notes ?? null,
      customer: customer
        ? { name: customer.name, mobile: customer.mobile, address: customer.address ?? null }
        : null,
      items: items.map((i) => ({
        serviceName: i.serviceName,
        quantity: i.quantity,
        stitchingPrice: i.stitchingPrice,
        materialPrice: i.materialPrice,
        lineTotal: i.lineTotal,
      })),
      stitchingTotal: order.stitchingTotal,
      materialTotal: order.materialTotal,
      grandTotal: order.grandTotal,
      paid,
      balance: round2(order.grandTotal - paid),
      payments: payments.map((p) => ({
        amount: p.amount,
        method: p.method,
        status: p.status,
        at: p._creationTime,
      })),
      shop,
    }
  },
})

export const updateStatus = mutation({
  args: { id: v.id('orders'), status: statusValidator },
  handler: async (ctx, { id, status }) => {
    await requireAdmin(ctx)
    const order = await ctx.db.get(id)
    if (!order) throw new Error('Order not found.')
    await ctx.db.patch(id, {
      status,
      deliveredAt: status === 'delivered' ? Date.now() : undefined,
    })
  },
})

export const updateDetails = mutation({
  args: {
    id: v.id('orders'),
    priority: v.optional(v.union(...priorities.map((p) => v.literal(p)))),
    fittingPreference: v.optional(fittingValidator),
    notes: v.optional(v.string()),
    promisedDate: v.optional(v.number()),
  },
  handler: async (ctx, { id, ...patch }) => {
    await requireAdmin(ctx)
    const clean = Object.fromEntries(
      Object.entries(patch).filter(([, val]) => val !== undefined),
    )
    await ctx.db.patch(id, clean)
  },
})

export const recentForDashboard = query({
  args: {},
  handler: async (ctx) => {
    await requireAdmin(ctx)
    const orders = await ctx.db.query('orders').order('desc').take(8)
    return await Promise.all(
      orders.map(async (o) => {
        const customer = await ctx.db.get(o.customerId)
        const paid = await verifiedPaidForOrder(ctx, o._id)
        return {
          ...o,
          customerName: customer?.name ?? '—',
          balance: round2(o.grandTotal - paid),
        }
      }),
    )
  },
})

export const attachReferenceImage = mutation({
  args: { orderId: v.id('orders'), storageId: v.id('_storage'), caption: v.optional(v.string()) },
  handler: async (ctx, { orderId, storageId, caption }) => {
    const admin = await requireAdmin(ctx)
    await ctx.db.insert('reference_images', {
      orderId,
      storageId,
      caption,
      uploadedBy: admin._id,
    })
  },
})

export const generateUploadUrl = mutation({
  args: {},
  handler: async (ctx) => {
    await requireAdmin(ctx)
    return await ctx.storage.generateUploadUrl()
  },
})

export const referenceImages = query({
  args: { orderId: v.id('orders') },
  handler: async (ctx, { orderId }) => {
    await requireAdmin(ctx)
    const rows = await ctx.db
      .query('reference_images')
      .withIndex('by_order', (q) => q.eq('orderId', orderId))
      .collect()
    return await Promise.all(
      rows.map(async (r) => ({
        ...r,
        url: await ctx.storage.getUrl(r.storageId),
      })),
    )
  },
})

/** PUBLIC online order / enquiry submission. */
export const submitOnline = mutation({
  args: {
    name: v.string(),
    mobile: v.string(),
    address: v.optional(v.string()),
    message: v.optional(v.string()),
    items: v.optional(v.array(itemInput)),
    fabricSource: v.optional(v.union(...fabricSources.map((f) => v.literal(f)))),
    priority: v.optional(v.union(...priorities.map((p) => v.literal(p)))),
  },
  handler: async (ctx, args) => {
    const mobile = normaliseMobile(args.mobile)
    if (mobile.length !== 10) throw new Error('Please enter a valid 10-digit mobile number.')

    const customerId = await findOrCreateCustomer(ctx, {
      name: args.name,
      mobile,
      address: args.address,
    })

    // Enquiry with no items -> just a notification record for staff to follow up.
    if (!args.items || args.items.length === 0) {
      await ctx.db.insert('notifications', {
        customerId,
        channel: 'whatsapp',
        to: mobile,
        template: 'enquiry',
        body: args.message?.trim() || 'New enquiry submitted online.',
        status: 'scheduled',
      })
      return { type: 'enquiry' as const }
    }

    const shopProvidesCloth = (args.fabricSource ?? 'customer') === 'shop'
    let stitchingTotal = 0
    let materialTotal = 0
    const items = args.items.map((it) => {
      const qty = Math.max(1, Math.round(it.quantity))
      const stitching = round2(it.stitchingPrice)
      const material = shopProvidesCloth ? round2(it.materialPrice) : 0
      stitchingTotal += stitching * qty
      materialTotal += material * qty
      return { ...it, quantity: qty, stitchingPrice: stitching, materialPrice: material, lineTotal: round2((stitching + material) * qty) }
    })
    stitchingTotal = round2(stitchingTotal)
    materialTotal = round2(materialTotal)
    const grandTotal = round2(stitchingTotal + materialTotal)

    const seq = await nextOrderSeq(ctx)
    const orderNumber = formatOrderNumber(seq)
    const orderId = await ctx.db.insert('orders', {
      orderNumber,
      seq,
      customerId,
      status: 'new',
      priority: args.priority ?? 'normal',
      fabricSource: args.fabricSource ?? 'customer',
      notes: args.message?.trim() || undefined,
      stitchingTotal,
      materialTotal,
      grandTotal,
      requiredAdvancePercent: shopProvidesCloth ? 100 : 50,
      source: 'online',
    })
    for (const it of items) {
      await ctx.db.insert('order_items', {
        orderId,
        serviceId: it.serviceId,
        serviceName: it.serviceName,
        category: it.category,
        stitchingPrice: it.stitchingPrice,
        materialPrice: it.materialPrice,
        quantity: it.quantity,
        lineTotal: it.lineTotal,
      })
    }
    await ctx.db.insert('notifications', {
      orderId,
      customerId,
      channel: 'whatsapp',
      to: mobile,
      template: 'online_order_received',
      body: `We received your online order ${orderNumber}. We will call you shortly to confirm measurements.`,
      status: 'scheduled',
    })
    return { type: 'order' as const, orderId: orderId as Id<'orders'>, orderNumber }
  },
})
