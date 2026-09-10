import { query, mutation } from './_generated/server'
import { v } from 'convex/values'
import { requireAdmin } from './lib/helpers'

export const DEFAULT_SHOP = {
  name: 'New Star Tailor',
  tagline: 'Expert tailoring and uniform specialists in Neemuch',
  phone: '+91 90000 00000',
  whatsapp: '919000000000',
  address: 'Main Road, Neemuch, Madhya Pradesh 458441',
  hours: 'Monday to Saturday, 10:00 AM – 8:00 PM',
  email: '',
  gstin: '',
}

export const getShop = query({
  args: {},
  handler: async (ctx) => {
    const row = await ctx.db
      .query('settings')
      .withIndex('by_key', (q) => q.eq('key', 'shop'))
      .first()
    return { ...DEFAULT_SHOP, ...(row?.value ?? {}) }
  },
})

export const all = query({
  args: {},
  handler: async (ctx) => {
    await requireAdmin(ctx)
    const rows = await ctx.db.query('settings').collect()
    const map: Record<string, unknown> = {}
    for (const r of rows) map[r.key] = r.value
    return {
      shop: { ...DEFAULT_SHOP, ...((map.shop as object) ?? {}) },
      orderSeq: typeof map.order_seq === 'number' ? map.order_seq : 0,
    }
  },
})

async function setKey(ctx: any, key: string, value: unknown) {
  const row = await ctx.db
    .query('settings')
    .withIndex('by_key', (q: any) => q.eq('key', key))
    .first()
  if (row) await ctx.db.patch(row._id, { value })
  else await ctx.db.insert('settings', { key, value })
}

export const updateShop = mutation({
  args: {
    name: v.optional(v.string()),
    tagline: v.optional(v.string()),
    phone: v.optional(v.string()),
    whatsapp: v.optional(v.string()),
    address: v.optional(v.string()),
    hours: v.optional(v.string()),
    email: v.optional(v.string()),
    gstin: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await requireAdmin(ctx)
    const row = await ctx.db
      .query('settings')
      .withIndex('by_key', (q) => q.eq('key', 'shop'))
      .first()
    const current = { ...DEFAULT_SHOP, ...(row?.value ?? {}) }
    const next = { ...current }
    for (const [k, val] of Object.entries(args)) {
      if (val !== undefined) (next as Record<string, unknown>)[k] = val
    }
    await setKey(ctx, 'shop', next)
    return next
  },
})
