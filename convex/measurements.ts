import { query, mutation } from './_generated/server'
import { v } from 'convex/values'
import type { Id } from './_generated/dataModel'
import { requireAdmin } from './lib/helpers'

/**
 * Standard measurement fields we prompt for, in display order.
 * Values are stored as a free-form record so extra fields are allowed.
 */
export const MEASUREMENT_FIELDS: Array<{
  key: string
  en: string
  hi: string
  group: 'upper' | 'lower'
}> = [
  { key: 'length', en: 'Length', hi: 'लंबाई', group: 'upper' },
  { key: 'shoulder', en: 'Shoulder', hi: 'कंधा', group: 'upper' },
  { key: 'chest', en: 'Chest', hi: 'छाती', group: 'upper' },
  { key: 'stomach', en: 'Stomach', hi: 'पेट', group: 'upper' },
  { key: 'seat', en: 'Seat / Hip', hi: 'कमर के नीचे (हिप)', group: 'upper' },
  { key: 'sleeve_length', en: 'Sleeve Length', hi: 'आस्तीन की लंबाई', group: 'upper' },
  { key: 'sleeve_loose', en: 'Sleeve (loose)', hi: 'आस्तीन (ढीली)', group: 'upper' },
  { key: 'neck', en: 'Neck / Collar', hi: 'कॉलर', group: 'upper' },
  { key: 'front_cross', en: 'Front Cross', hi: 'आगे की चौड़ाई', group: 'upper' },
  { key: 'back_cross', en: 'Back Cross', hi: 'पीछे की चौड़ाई', group: 'upper' },
  { key: 'pant_length', en: 'Pant Length', hi: 'पैंट की लंबाई', group: 'lower' },
  { key: 'waist', en: 'Waist', hi: 'कमर', group: 'lower' },
  { key: 'hip', en: 'Hip', hi: 'हिप', group: 'lower' },
  { key: 'thigh', en: 'Thigh', hi: 'जांघ', group: 'lower' },
  { key: 'knee', en: 'Knee', hi: 'घुटना', group: 'lower' },
  { key: 'pant_mori', en: 'Bottom (Mori)', hi: 'मोरी (पैंट का खुला हिस्सा)', group: 'lower' },
  { key: 'crotch', en: 'Crotch / Rise', hi: 'राइज़', group: 'lower' },
]

export const forCustomer = query({
  args: { customerId: v.id('customers') },
  handler: async (ctx, { customerId }) => {
    await requireAdmin(ctx)
    const doc = await ctx.db
      .query('measurements')
      .withIndex('by_customer', (q) => q.eq('customerId', customerId))
      .first()
    const versions = await ctx.db
      .query('measurement_versions')
      .withIndex('by_customer', (q) => q.eq('customerId', customerId))
      .collect()
    versions.sort((a, b) => b.version - a.version)
    const current = doc?.currentVersionId
      ? versions.find((x) => x._id === doc.currentVersionId) ?? versions[0] ?? null
      : versions[0] ?? null
    return { current, versions }
  },
})

export const getVersion = query({
  args: { versionId: v.id('measurement_versions') },
  handler: async (ctx, { versionId }) => {
    await requireAdmin(ctx)
    return await ctx.db.get(versionId)
  },
})

/**
 * Save a new immutable measurement version and point the customer's
 * measurement record at it. Existing orders keep their old version.
 */
export const saveVersion = mutation({
  args: {
    customerId: v.id('customers'),
    values: v.record(v.string(), v.number()),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, { customerId, values, notes }) => {
    const admin = await requireAdmin(ctx)

    let measurementDoc = await ctx.db
      .query('measurements')
      .withIndex('by_customer', (q) => q.eq('customerId', customerId))
      .first()

    let measurementId: Id<'measurements'>
    if (!measurementDoc) {
      measurementId = await ctx.db.insert('measurements', {
        customerId,
        updatedBy: admin._id,
      })
    } else {
      measurementId = measurementDoc._id
    }

    const existing = await ctx.db
      .query('measurement_versions')
      .withIndex('by_customer', (q) => q.eq('customerId', customerId))
      .collect()
    const nextVersion =
      existing.reduce((max, x) => Math.max(max, x.version), 0) + 1

    const cleanValues = Object.fromEntries(
      Object.entries(values).filter(
        ([, val]) => typeof val === 'number' && !Number.isNaN(val) && val > 0,
      ),
    )

    const versionId = await ctx.db.insert('measurement_versions', {
      customerId,
      measurementId,
      version: nextVersion,
      values: cleanValues,
      notes: notes?.trim() || undefined,
      takenBy: admin._id,
    })

    await ctx.db.patch(measurementId, {
      currentVersionId: versionId,
      updatedBy: admin._id,
    })

    return { versionId, version: nextVersion }
  },
})
