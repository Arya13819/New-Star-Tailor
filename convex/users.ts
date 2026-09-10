import { query, mutation } from './_generated/server'
import { v } from 'convex/values'
import { getCurrentUser, requireAdmin } from './lib/helpers'

export const me = query({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx)
    if (!user) return null
    return {
      _id: user._id,
      name: user.name ?? null,
      email: user.email ?? null,
      role: user.role ?? 'customer',
    }
  },
})

export const listStaff = query({
  args: {},
  handler: async (ctx) => {
    await requireAdmin(ctx)
    const users = await ctx.db.query('users').collect()
    return users
      .map((u) => ({
        _id: u._id,
        name: u.name ?? null,
        email: u.email ?? null,
        role: u.role ?? 'customer',
        createdAt: u._creationTime,
      }))
      .sort((a, b) => a.createdAt - b.createdAt)
  },
})

export const setRole = mutation({
  args: {
    userId: v.id('users'),
    role: v.union(v.literal('admin'), v.literal('customer')),
  },
  handler: async (ctx, { userId, role }) => {
    const admin = await requireAdmin(ctx)
    if (userId === admin._id && role !== 'admin') {
      throw new Error('You cannot remove your own admin access.')
    }
    await ctx.db.patch(userId, { role })
  },
})
