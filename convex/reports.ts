import { query } from './_generated/server'
import { v } from 'convex/values'
import { requireAdmin, round2 } from './lib/helpers'
import { serviceCategories } from './schema'

export const summary = query({
  args: {
    from: v.optional(v.number()),
    to: v.optional(v.number()),
  },
  handler: async (ctx, { from, to }) => {
    await requireAdmin(ctx)
    const start = from ?? 0
    const end = to ?? Date.now() + 1

    const allOrders = await ctx.db.query('orders').collect()
    const orders = allOrders.filter(
      (o) => o._creationTime >= start && o._creationTime <= end,
    )
    const orderIds = new Set(orders.map((o) => o._id))

    const allPayments = await ctx.db.query('payments').collect()
    const payments = allPayments.filter(
      (p) =>
        p.status === 'verified' &&
        p._creationTime >= start &&
        p._creationTime <= end,
    )

    const revenueCollected = round2(
      payments.reduce((s, p) => s + p.amount, 0),
    )
    const orderValue = round2(orders.reduce((s, o) => s + o.grandTotal, 0))
    const stitchingValue = round2(
      orders.reduce((s, o) => s + o.stitchingTotal, 0),
    )
    const materialValue = round2(orders.reduce((s, o) => s + o.materialTotal, 0))

    const byStatus: Record<string, number> = {
      new: 0,
      measurement: 0,
      ready: 0,
      delivered: 0,
    }
    for (const o of orders) byStatus[o.status] += 1

    // Category breakdown from order items within the window.
    const allItems = await ctx.db.query('order_items').collect()
    const items = allItems.filter((it) => orderIds.has(it.orderId))
    const byCategory: Record<string, { count: number; value: number }> = {}
    for (const c of serviceCategories) byCategory[c] = { count: 0, value: 0 }
    for (const it of items) {
      byCategory[it.category].count += it.quantity
      byCategory[it.category].value += it.lineTotal
    }

    const outstanding = round2(
      allOrders.reduce((s, o) => s + o.grandTotal, 0) -
        allPayments
          .filter((p) => p.status === 'verified')
          .reduce((s, p) => s + p.amount, 0),
    )

    return {
      window: { from: start, to: end },
      orderCount: orders.length,
      revenueCollected,
      orderValue,
      stitchingValue,
      materialValue,
      pendingVerification: round2(
        allPayments
          .filter((p) => p.status === 'pending')
          .reduce((s, p) => s + p.amount, 0),
      ),
      outstandingAllTime: outstanding,
      byStatus,
      byCategory: serviceCategories.map((c) => ({
        category: c,
        count: byCategory[c].count,
        value: round2(byCategory[c].value),
      })),
      urgentOpen: orders.filter(
        (o) => o.priority === 'urgent' && o.status !== 'delivered',
      ).length,
    }
  },
})
