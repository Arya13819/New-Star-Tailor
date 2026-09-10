import { query, mutation } from './_generated/server'
import { v } from 'convex/values'
import {
  requireAdmin,
  round2,
  verifiedPaidForOrder,
} from './lib/helpers'
import { paymentMethods } from './schema'

const methodValidator = v.union(...paymentMethods.map((m) => v.literal(m)))

export const forOrder = query({
  args: { orderId: v.id('orders') },
  handler: async (ctx, { orderId }) => {
    await requireAdmin(ctx)
    const order = await ctx.db.get(orderId)
    if (!order) return null
    const payments = await ctx.db
      .query('payments')
      .withIndex('by_order', (q) => q.eq('orderId', orderId))
      .order('desc')
      .collect()
    const verified = round2(
      payments.filter((p) => p.status === 'verified').reduce((s, p) => s + p.amount, 0),
    )
    const pending = round2(
      payments.filter((p) => p.status === 'pending').reduce((s, p) => s + p.amount, 0),
    )
    const requiredAdvance = round2(
      (order.stitchingTotal * order.requiredAdvancePercent) / 100 + order.materialTotal,
    )
    return {
      payments,
      verified,
      pending,
      balance: round2(order.grandTotal - verified),
      grandTotal: order.grandTotal,
      requiredAdvance,
      requiredAdvancePercent: order.requiredAdvancePercent,
      advanceMet: verified + 1e-6 >= requiredAdvance,
    }
  },
})

export const record = mutation({
  args: {
    orderId: v.id('orders'),
    amount: v.number(),
    method: methodValidator,
    transactionRef: v.optional(v.string()),
    note: v.optional(v.string()),
    // Cash/UPI collected at the counter is verified immediately; online
    // is left pending until the webhook / manual check confirms it.
    markVerified: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const admin = await requireAdmin(ctx)
    const order = await ctx.db.get(args.orderId)
    if (!order) throw new Error('Order not found.')

    const amount = round2(args.amount)
    if (!(amount > 0)) throw new Error('Enter an amount greater than zero.')

    const alreadyPaid = await verifiedPaidForOrder(ctx, args.orderId)
    if (amount - (order.grandTotal - alreadyPaid) > 0.5) {
      throw new Error(
        `That is more than the outstanding balance (₹${round2(
          order.grandTotal - alreadyPaid,
        )}).`,
      )
    }

    const verified =
      args.markVerified ?? (args.method === 'cash' || args.method === 'upi')

    return await ctx.db.insert('payments', {
      orderId: args.orderId,
      customerId: order.customerId,
      amount,
      method: args.method,
      status: verified ? 'verified' : 'pending',
      transactionRef: args.transactionRef?.trim() || undefined,
      note: args.note?.trim() || undefined,
      recordedBy: admin._id,
      verifiedBy: verified ? admin._id : undefined,
      verifiedAt: verified ? Date.now() : undefined,
    })
  },
})

export const verify = mutation({
  args: { paymentId: v.id('payments') },
  handler: async (ctx, { paymentId }) => {
    const admin = await requireAdmin(ctx)
    const payment = await ctx.db.get(paymentId)
    if (!payment) throw new Error('Payment not found.')
    if (payment.status === 'verified') return
    await ctx.db.patch(paymentId, {
      status: 'verified',
      verifiedBy: admin._id,
      verifiedAt: Date.now(),
    })
  },
})

export const remove = mutation({
  args: { paymentId: v.id('payments') },
  handler: async (ctx, { paymentId }) => {
    await requireAdmin(ctx)
    await ctx.db.delete(paymentId)
  },
})

export const listAll = query({
  args: {
    status: v.optional(v.union(v.literal('pending'), v.literal('verified'))),
  },
  handler: async (ctx, { status }) => {
    await requireAdmin(ctx)
    const payments = status
      ? await ctx.db
          .query('payments')
          .withIndex('by_status', (q) => q.eq('status', status))
          .order('desc')
          .collect()
      : await ctx.db.query('payments').order('desc').collect()

    const rows = await Promise.all(
      payments.map(async (p) => {
        const order = await ctx.db.get(p.orderId)
        const customer = await ctx.db.get(p.customerId)
        return {
          ...p,
          orderNumber: order?.orderNumber ?? '—',
          customerName: customer?.name ?? '—',
        }
      }),
    )

    const verifiedTotal = round2(
      payments.filter((p) => p.status === 'verified').reduce((s, p) => s + p.amount, 0),
    )
    const pendingTotal = round2(
      payments.filter((p) => p.status === 'pending').reduce((s, p) => s + p.amount, 0),
    )
    const byMethod: Record<string, number> = { cash: 0, upi: 0, online: 0 }
    for (const p of payments) {
      if (p.status === 'verified') byMethod[p.method] += p.amount
    }

    return {
      rows,
      summary: {
        verifiedTotal,
        pendingTotal,
        count: payments.length,
        byMethod: {
          cash: round2(byMethod.cash),
          upi: round2(byMethod.upi),
          online: round2(byMethod.online),
        },
      },
    }
  },
})
