import type { MutationCtx, QueryCtx } from '../_generated/server'
import { getAuthUserId } from '@convex-dev/auth/server'
import type { Doc, Id } from '../_generated/dataModel'

export async function getCurrentUser(
  ctx: QueryCtx | MutationCtx,
): Promise<Doc<'users'> | null> {
  const userId = await getAuthUserId(ctx)
  if (!userId) return null
  return await ctx.db.get(userId)
}

export async function requireUser(
  ctx: QueryCtx | MutationCtx,
): Promise<Doc<'users'>> {
  const user = await getCurrentUser(ctx)
  if (!user) throw new Error('You must be signed in to do that.')
  return user
}

export async function requireAdmin(
  ctx: QueryCtx | MutationCtx,
): Promise<Doc<'users'>> {
  const user = await requireUser(ctx)
  if (user.role !== 'admin') {
    throw new Error('This action is only available to shop staff.')
  }
  return user
}

/** NST-000001 style order number from a numeric sequence. */
export function formatOrderNumber(seq: number): string {
  return `NST-${String(seq).padStart(6, '0')}`
}

/** Normalise an Indian mobile number for comparison (last 10 digits). */
export function normaliseMobile(input: string): string {
  return input.replace(/\D/g, '').slice(-10)
}

export function round2(n: number): number {
  return Math.round((n + Number.EPSILON) * 100) / 100
}

/**
 * Sum of *verified* payments for an order. Pending / online-unconfirmed
 * payments never count toward the balance.
 */
export async function verifiedPaidForOrder(
  ctx: QueryCtx | MutationCtx,
  orderId: Id<'orders'>,
): Promise<number> {
  const payments = await ctx.db
    .query('payments')
    .withIndex('by_order', (q) => q.eq('orderId', orderId))
    .collect()
  return round2(
    payments
      .filter((p) => p.status === 'verified')
      .reduce((sum, p) => sum + p.amount, 0),
  )
}

export async function pendingPaidForOrder(
  ctx: QueryCtx | MutationCtx,
  orderId: Id<'orders'>,
): Promise<number> {
  const payments = await ctx.db
    .query('payments')
    .withIndex('by_order', (q) => q.eq('orderId', orderId))
    .collect()
  return round2(
    payments
      .filter((p) => p.status === 'pending')
      .reduce((sum, p) => sum + p.amount, 0),
  )
}
