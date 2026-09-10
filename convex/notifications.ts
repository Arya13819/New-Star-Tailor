import { query, mutation } from './_generated/server'
import { v } from 'convex/values'
import { requireAdmin, normaliseMobile } from './lib/helpers'
import { notificationChannels } from './schema'

/**
 * Notification records are WhatsApp-ready: we store the exact message
 * and recipient now, and a future sender (WhatsApp Cloud API / SMS
 * gateway) just needs to pick up `scheduled` rows and mark them sent.
 */

export const list = query({
  args: {
    status: v.optional(
      v.union(v.literal('scheduled'), v.literal('sent'), v.literal('failed')),
    ),
  },
  handler: async (ctx, { status }) => {
    await requireAdmin(ctx)
    const rows = status
      ? await ctx.db
          .query('notifications')
          .withIndex('by_status', (q) => q.eq('status', status))
          .order('desc')
          .collect()
      : await ctx.db.query('notifications').order('desc').take(100)
    return await Promise.all(
      rows.map(async (n) => ({
        ...n,
        orderNumber: n.orderId
          ? (await ctx.db.get(n.orderId))?.orderNumber ?? null
          : null,
        customerName: n.customerId
          ? (await ctx.db.get(n.customerId))?.name ?? null
          : null,
      })),
    )
  },
})

export const create = mutation({
  args: {
    orderId: v.optional(v.id('orders')),
    customerId: v.optional(v.id('customers')),
    channel: v.optional(v.union(...notificationChannels.map((c) => v.literal(c)))),
    to: v.string(),
    template: v.string(),
    body: v.string(),
    scheduledFor: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    await requireAdmin(ctx)
    return await ctx.db.insert('notifications', {
      orderId: args.orderId,
      customerId: args.customerId,
      channel: args.channel ?? 'whatsapp',
      to: normaliseMobile(args.to),
      template: args.template,
      body: args.body,
      status: 'scheduled',
      scheduledFor: args.scheduledFor,
    })
  },
})

export const markSent = mutation({
  args: { id: v.id('notifications') },
  handler: async (ctx, { id }) => {
    await requireAdmin(ctx)
    await ctx.db.patch(id, { status: 'sent', sentAt: Date.now() })
  },
})

export const markFailed = mutation({
  args: { id: v.id('notifications'), error: v.string() },
  handler: async (ctx, { id, error }) => {
    await requireAdmin(ctx)
    await ctx.db.patch(id, { status: 'failed', error })
  },
})

export const remove = mutation({
  args: { id: v.id('notifications') },
  handler: async (ctx, { id }) => {
    await requireAdmin(ctx)
    await ctx.db.delete(id)
  },
})
