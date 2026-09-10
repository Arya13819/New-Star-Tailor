import { query, mutation, internalMutation } from './_generated/server'
import { v } from 'convex/values'
import { requireAdmin } from './lib/helpers'
import { serviceCategories } from './schema'

export const SEED_SERVICES: Array<{
  name: string
  nameHi: string
  category: (typeof serviceCategories)[number]
  defaultStitchingPrice: number
  description: string
  sortOrder: number
}> = [
  {
    name: 'Shirt Stitching',
    nameHi: 'शर्ट की सिलाई',
    category: 'regular',
    defaultStitchingPrice: 450,
    description: 'Formal or casual shirt, full or half sleeve.',
    sortOrder: 10,
  },
  {
    name: 'Trouser / Pant Stitching',
    nameHi: 'पैंट की सिलाई',
    category: 'regular',
    defaultStitchingPrice: 550,
    description: 'Formal trousers with pockets and proper finishing.',
    sortOrder: 20,
  },
  {
    name: 'Kurta Pyjama',
    nameHi: 'कुर्ता पजामा',
    category: 'regular',
    defaultStitchingPrice: 700,
    description: 'Traditional kurta with matching pyjama.',
    sortOrder: 30,
  },
  {
    name: 'Safari Suit',
    nameHi: 'सफारी सूट',
    category: 'regular',
    defaultStitchingPrice: 1600,
    description: 'Two-piece safari suit, fully stitched.',
    sortOrder: 40,
  },
  {
    name: 'Blazer / Coat',
    nameHi: 'ब्लेज़र / कोट',
    category: 'regular',
    defaultStitchingPrice: 2800,
    description: 'Lined blazer or coat with canvas front.',
    sortOrder: 50,
  },
  {
    name: 'Police Uniform Set',
    nameHi: 'पुलिस वर्दी सेट',
    category: 'police',
    defaultStitchingPrice: 1800,
    description: 'Khaki shirt and trouser as per state police pattern.',
    sortOrder: 60,
  },
  {
    name: 'Police Shirt Only',
    nameHi: 'पुलिस शर्ट',
    category: 'police',
    defaultStitchingPrice: 650,
    description: 'Regulation khaki shirt with epaulettes.',
    sortOrder: 70,
  },
  {
    name: 'CRPF Uniform Set',
    nameHi: 'सीआरपीएफ वर्दी सेट',
    category: 'crpf',
    defaultStitchingPrice: 2100,
    description: 'CRPF combat pattern shirt and trouser.',
    sortOrder: 80,
  },
  {
    name: 'Army Uniform Set',
    nameHi: 'सेना वर्दी सेट',
    category: 'army',
    defaultStitchingPrice: 2400,
    description: 'Indian Army disruptive pattern combat dress.',
    sortOrder: 90,
  },
  {
    name: 'Cheetah / US Pattern Uniform',
    nameHi: 'चीता (यूएस पैटर्न) वर्दी',
    category: 'army',
    defaultStitchingPrice: 2600,
    description: 'Cheetah force US disruptive pattern uniform set.',
    sortOrder: 100,
  },
  {
    name: 'Uniform Alteration',
    nameHi: 'वर्दी में फेरबदल',
    category: 'police',
    defaultStitchingPrice: 250,
    description: 'Resize or refit an existing uniform.',
    sortOrder: 110,
  },
  {
    name: 'General Alteration',
    nameHi: 'सामान्य फेरबदल',
    category: 'regular',
    defaultStitchingPrice: 150,
    description: 'Length, waist or fit adjustment on any garment.',
    sortOrder: 120,
  },
]

export const list = query({
  args: { includeInactive: v.optional(v.boolean()) },
  handler: async (ctx, { includeInactive }) => {
    const all = await ctx.db.query('services').collect()
    const filtered = includeInactive ? all : all.filter((s) => s.active)
    return filtered.sort(
      (a, b) => (a.sortOrder ?? 999) - (b.sortOrder ?? 999),
    )
  },
})

export const get = query({
  args: { id: v.id('services') },
  handler: async (ctx, { id }) => ctx.db.get(id),
})

export const create = mutation({
  args: {
    name: v.string(),
    nameHi: v.optional(v.string()),
    category: v.union(...serviceCategories.map((c) => v.literal(c))),
    defaultStitchingPrice: v.number(),
    description: v.optional(v.string()),
    sortOrder: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    await requireAdmin(ctx)
    return await ctx.db.insert('services', { ...args, active: true })
  },
})

export const update = mutation({
  args: {
    id: v.id('services'),
    name: v.optional(v.string()),
    nameHi: v.optional(v.string()),
    defaultStitchingPrice: v.optional(v.number()),
    description: v.optional(v.string()),
    active: v.optional(v.boolean()),
    sortOrder: v.optional(v.number()),
  },
  handler: async (ctx, { id, ...patch }) => {
    await requireAdmin(ctx)
    const clean = Object.fromEntries(
      Object.entries(patch).filter(([, val]) => val !== undefined),
    )
    await ctx.db.patch(id, clean)
  },
})

/** Public: seed the catalogue if empty. Safe to call repeatedly. */
export const seedIfEmpty = mutation({
  args: {},
  handler: async (ctx) => {
    const existing = await ctx.db.query('services').first()
    if (existing) return { seeded: 0 }
    for (const s of SEED_SERVICES) {
      await ctx.db.insert('services', { ...s, active: true })
    }
    return { seeded: SEED_SERVICES.length }
  },
})

export const seedInternal = internalMutation({
  args: {},
  handler: async (ctx) => {
    const existing = await ctx.db.query('services').first()
    if (existing) return
    for (const s of SEED_SERVICES) {
      await ctx.db.insert('services', { ...s, active: true })
    }
  },
})
