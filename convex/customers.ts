import { query, mutation } from './_generated/server'
import { v } from 'convex/values'
import type { Id } from './_generated/dataModel'
import {
  requireAdmin,
  normaliseMobile,
  verifiedPaidForOrder,
  round2,
} from './lib/helpers'
import { fittingPreferences } from './schema'

const fittingValidator = v.union(
  ...fittingPreferences.map((p) => v.literal(p)),
)

export const list = query({
  args: { search: v.optional(v.string()) },
  handler: async (ctx, { search }) => {
    await requireAdmin(ctx)
    const term = (search ?? '').trim()

    let customers
    if (term.length > 0) {
      const digits = normaliseMobile(term)
      if (digits.length >= 4) {
        const all = await ctx.db.query('customers').collect()
        customers = all.filter((c) => normaliseMobile(c.mobile).includes(digits))
      } else {
        customers = await ctx.db
          .query('customers')
          .withSearchIndex('search_name', (q) => q.search('name', term))
          .take(50)
      }
    } else {
      customers = await ctx.db.query('customers').order('desc').take(100)
    }

    return await Promise.all(
      customers.map(async (c) => {
        const orders = await ctx.db
          .query('orders')
          .withIndex('by_customer', (q) => q.eq('customerId', c._id))
          .collect()
        return {
          ...c,
          orderCount: orders.length,
          lastOrderAt: orders.length
            ? Math.max(...orders.map((o) => o._creationTime))
            : null,
        }
      }),
    )
  },
})

export const get = query({
  args: { id: v.id('customers') },
  handler: async (ctx, { id }) => {
    await requireAdmin(ctx)
    const customer = await ctx.db.get(id)
    if (!customer) return null

    const measurementDoc = await ctx.db
      .query('measurements')
      .withIndex('by_customer', (q) => q.eq('customerId', id))
      .first()

    const versions = await ctx.db
      .query('measurement_versions')
      .withIndex('by_customer', (q) => q.eq('customerId', id))
      .collect()
    versions.sort((a, b) => b.version - a.version)

    const currentVersion = measurementDoc?.currentVersionId
      ? versions.find((x) => x._id === measurementDoc.currentVersionId) ?? null
      : versions[0] ?? null

    return { customer, currentVersion, versions }
  },
})

export const orderHistory = query({
  args: { id: v.id('customers') },
  handler: async (ctx, { id }) => {
    await requireAdmin(ctx)
    const orders = await ctx.db
      .query('orders')
      .withIndex('by_customer', (q) => q.eq('customerId', id))
      .order('desc')
      .collect()
    return await Promise.all(
      orders.map(async (o) => {
        const paid = await verifiedPaidForOrder(ctx, o._id)
        return { ...o, paid, balance: round2(o.grandTotal - paid) }
      }),
    )
  },
})

export const paymentHistory = query({
  args: { id: v.id('customers') },
  handler: async (ctx, { id }) => {
    await requireAdmin(ctx)
    const payments = await ctx.db
      .query('payments')
      .withIndex('by_customer', (q) => q.eq('customerId', id))
      .order('desc')
      .collect()
    return await Promise.all(
      payments.map(async (p) => {
        const order = await ctx.db.get(p.orderId)
        return { ...p, orderNumber: order?.orderNumber ?? '—' }
      }),
    )
  },
})

/** Search used by the New Order wizard (returns light rows). */
export const quickSearch = query({
  args: { term: v.string() },
  handler: async (ctx, { term }) => {
    await requireAdmin(ctx)
    const t = term.trim()
    if (t.length < 2) return []
    const digits = normaliseMobile(t)
    if (digits.length >= 4) {
      const all = await ctx.db.query('customers').collect()
      return all
        .filter((c) => normaliseMobile(c.mobile).includes(digits))
        .slice(0, 10)
    }
    return await ctx.db
      .query('customers')
      .withSearchIndex('search_name', (q) => q.search('name', t))
      .take(10)
  },
})

export const create = mutation({
  args: {
    name: v.string(),
    mobile: v.string(),
    address: v.optional(v.string()),
    notes: v.optional(v.string()),
    fittingPreference: v.optional(fittingValidator),
  },
  handler: async (ctx, args) => {
    const admin = await requireAdmin(ctx)
    const mobile = normaliseMobile(args.mobile)
    if (mobile.length !== 10) {
      throw new Error('Please enter a valid 10-digit mobile number.')
    }
    const existing = (await ctx.db.query('customers').collect()).find(
      (c) => normaliseMobile(c.mobile) === mobile,
    )
    if (existing) {
      throw new Error(
        `A customer with this mobile already exists: ${existing.name}.`,
      )
    }
    const customerId = await ctx.db.insert('customers', {
      name: args.name.trim(),
      mobile,
      address: args.address?.trim() || undefined,
      notes: args.notes?.trim() || undefined,
      fittingPreference: args.fittingPreference,
      createdBy: admin._id,
    })
    await ctx.db.insert('measurements', {
      customerId,
      updatedBy: admin._id,
    })
    return customerId
  },
})

export const update = mutation({
  args: {
    id: v.id('customers'),
    name: v.optional(v.string()),
    mobile: v.optional(v.string()),
    address: v.optional(v.string()),
    notes: v.optional(v.string()),
    fittingPreference: v.optional(fittingValidator),
  },
  handler: async (ctx, { id, ...patch }) => {
    await requireAdmin(ctx)
    const clean: Record<string, unknown> = {}
    if (patch.name !== undefined) clean.name = patch.name.trim()
    if (patch.mobile !== undefined) {
      const m = normaliseMobile(patch.mobile)
      if (m.length !== 10) throw new Error('Please enter a valid 10-digit mobile number.')
      clean.mobile = m
    }
    if (patch.address !== undefined) clean.address = patch.address.trim() || undefined
    if (patch.notes !== undefined) clean.notes = patch.notes.trim() || undefined
    if (patch.fittingPreference !== undefined)
      clean.fittingPreference = patch.fittingPreference
    await ctx.db.patch(id, clean)
  },
})

/** Internal helper reused by orders + seed: find-or-create by mobile. */
export async function findOrCreateCustomer(
  ctx: { db: any },
  input: { name: string; mobile: string; address?: string; createdBy?: Id<'users'> },
): Promise<Id<'customers'>> {
  const mobile = normaliseMobile(input.mobile)
  const all = await ctx.db.query('customers').collect()
  const existing = all.find((c: any) => normaliseMobile(c.mobile) === mobile)
  if (existing) return existing._id
  const customerId = await ctx.db.insert('customers', {
    name: input.name.trim(),
    mobile,
    address: input.address?.trim() || undefined,
    createdBy: input.createdBy,
  })
  await ctx.db.insert('measurements', { customerId, updatedBy: input.createdBy })
  return customerId
}
