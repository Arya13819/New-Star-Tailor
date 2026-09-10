import { mutation } from './_generated/server'
import { SEED_SERVICES } from './services'

/**
 * Standalone service-catalogue seeder.
 *
 * The public Services / New Order pages call `services.seedIfEmpty`
 * automatically when they find no services; this mutation is the
 * manual equivalent you can run from the Convex dashboard.
 */
export const run = mutation({
  args: {},
  handler: async (ctx) => {
    const existing = await ctx.db.query('services').first()
    if (existing) return { seeded: 0, message: 'Services already present.' }
    for (const s of SEED_SERVICES) {
      await ctx.db.insert('services', { ...s, active: true })
    }
    return { seeded: SEED_SERVICES.length, message: 'Service catalogue seeded.' }
  },
})
