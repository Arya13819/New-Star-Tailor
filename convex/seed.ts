import { mutation } from './_generated/server'
import type { Id } from './_generated/dataModel'
import { requireAdmin, formatOrderNumber, round2 } from './lib/helpers'
import { SEED_SERVICES } from './services'
import { MEASUREMENT_FIELDS } from './measurements'
import { DEFAULT_SHOP } from './settings'

const DAY = 24 * 60 * 60 * 1000

const CUSTOMERS = [
  { name: 'Ramesh Prajapat', mobile: '9827011001', address: 'Bagana Road, Neemuch' },
  { name: 'Sunil Verma', mobile: '9827011002', address: 'Station Road, Neemuch' },
  { name: 'Imran Sheikh', mobile: '9827011003', address: 'Ghantaghar, Neemuch' },
  { name: 'Pooja Rathore', mobile: '9827011004', address: 'Vikas Nagar, Neemuch' },
  { name: 'Constable Mahesh Solanki', mobile: '9827011005', address: 'Police Line, Neemuch' },
  { name: 'Deepak Nagda', mobile: '9827011006', address: 'Mahavir Nagar, Neemuch' },
  { name: 'Farhan Qureshi', mobile: '9827011007', address: 'Sarafa Bazaar, Neemuch' },
  { name: 'Head Constable Lokesh Dhakad', mobile: '9827011008', address: 'CRPF Camp Road, Neemuch' },
]

function sampleMeasurements(seed: number): Record<string, number> {
  const out: Record<string, number> = {}
  for (const f of MEASUREMENT_FIELDS) {
    const base: Record<string, number> = {
      length: 74, shoulder: 46, chest: 102, stomach: 96, seat: 104,
      sleeve_length: 62, sleeve_loose: 42, neck: 40, front_cross: 40, back_cross: 44,
      pant_length: 100, waist: 84, hip: 102, thigh: 62, knee: 44, pant_mori: 38, crotch: 27,
    }
    out[f.key] = round2((base[f.key] ?? 40) + ((seed * 7) % 9) - 4)
  }
  return out
}

export const loadDemoData = mutation({
  args: {},
  handler: async (ctx) => {
    await requireAdmin(ctx)

    const existingOrders = await ctx.db.query('orders').first()
    if (existingOrders) {
      return { ok: false, message: 'Demo data not loaded — orders already exist.' }
    }

    // --- Shop settings ---
    const shopRow = await ctx.db
      .query('settings')
      .withIndex('by_key', (q) => q.eq('key', 'shop'))
      .first()
    if (!shopRow) {
      await ctx.db.insert('settings', {
        key: 'shop',
        value: {
          ...DEFAULT_SHOP,
          phone: '+91 94250 12345',
          whatsapp: '919425012345',
          email: 'newstartailor.neemuch@gmail.com',
        },
      })
    }

    // --- Services ---
    let services = await ctx.db.query('services').collect()
    if (services.length === 0) {
      for (const s of SEED_SERVICES) {
        await ctx.db.insert('services', { ...s, active: true })
      }
      services = await ctx.db.query('services').collect()
    }
    const svc = (name: string) => services.find((s) => s.name === name)!

    // --- Customers + measurements ---
    const customerIds: Id<'customers'>[] = []
    for (let i = 0; i < CUSTOMERS.length; i++) {
      const c = CUSTOMERS[i]
      const customerId = await ctx.db.insert('customers', {
        name: c.name,
        mobile: c.mobile,
        address: c.address,
        fittingPreference: i % 3 === 0 ? 'slim' : i % 3 === 1 ? 'regular' : 'relaxed',
      })
      const measurementId = await ctx.db.insert('measurements', { customerId })
      const v1 = await ctx.db.insert('measurement_versions', {
        customerId,
        measurementId,
        version: 1,
        values: sampleMeasurements(i + 1),
        notes: 'Initial measurements taken in shop.',
      })
      let currentVersionId = v1
      // A couple of repeat customers get a second measurement version.
      if (i === 0 || i === 4) {
        const v2 = await ctx.db.insert('measurement_versions', {
          customerId,
          measurementId,
          version: 2,
          values: sampleMeasurements(i + 5),
          notes: 'Re-measured — customer requested a slightly looser fit.',
        })
        currentVersionId = v2
      }
      await ctx.db.patch(measurementId, { currentVersionId })
      customerIds.push(customerId)
    }

    const currentVersionFor = async (customerId: Id<'customers'>) => {
      const m = await ctx.db
        .query('measurements')
        .withIndex('by_customer', (q) => q.eq('customerId', customerId))
        .first()
      return m?.currentVersionId
    }

    // --- Order sequence counter ---
    let seq = 0
    const bumpSeq = async () => {
      seq += 1
      const row = await ctx.db
        .query('settings')
        .withIndex('by_key', (q) => q.eq('key', 'order_seq'))
        .first()
      if (row) await ctx.db.patch(row._id, { value: seq })
      else await ctx.db.insert('settings', { key: 'order_seq', value: seq })
      return seq
    }

    type OrderPlan = {
      customer: number
      items: Array<{ name: string; qty: number; material: number }>
      status: 'new' | 'measurement' | 'ready' | 'delivered'
      priority: 'normal' | 'urgent'
      fabric: 'customer' | 'shop'
      source: 'walk_in' | 'online'
      ageDays: number
      pay: Array<{ pct: number; method: 'cash' | 'upi' | 'online'; status: 'verified' | 'pending' }>
    }

    const plans: OrderPlan[] = [
      // 4 delivered
      { customer: 0, items: [{ name: 'Shirt Stitching', qty: 2, material: 0 }, { name: 'Trouser / Pant Stitching', qty: 2, material: 0 }], status: 'delivered', priority: 'normal', fabric: 'customer', source: 'walk_in', ageDays: 26, pay: [{ pct: 50, method: 'cash', status: 'verified' }, { pct: 50, method: 'upi', status: 'verified' }] },
      { customer: 1, items: [{ name: 'Safari Suit', qty: 1, material: 900 }], status: 'delivered', priority: 'normal', fabric: 'shop', source: 'walk_in', ageDays: 22, pay: [{ pct: 100, method: 'cash', status: 'verified' }] },
      { customer: 4, items: [{ name: 'Police Uniform Set', qty: 2, material: 0 }], status: 'delivered', priority: 'urgent', fabric: 'customer', source: 'walk_in', ageDays: 18, pay: [{ pct: 50, method: 'upi', status: 'verified' }, { pct: 50, method: 'cash', status: 'verified' }] },
      { customer: 7, items: [{ name: 'CRPF Uniform Set', qty: 1, material: 0 }, { name: 'Uniform Alteration', qty: 2, material: 0 }], status: 'delivered', priority: 'normal', fabric: 'customer', source: 'walk_in', ageDays: 12, pay: [{ pct: 100, method: 'online', status: 'verified' }] },
      // 3 new
      { customer: 2, items: [{ name: 'Kurta Pyjama', qty: 1, material: 0 }], status: 'new', priority: 'normal', fabric: 'customer', source: 'walk_in', ageDays: 1, pay: [] },
      { customer: 3, items: [{ name: 'Blazer / Coat', qty: 1, material: 1800 }], status: 'new', priority: 'normal', fabric: 'shop', source: 'online', ageDays: 0, pay: [{ pct: 40, method: 'online', status: 'pending' }] },
      { customer: 5, items: [{ name: 'Shirt Stitching', qty: 3, material: 0 }], status: 'new', priority: 'urgent', fabric: 'customer', source: 'walk_in', ageDays: 0, pay: [{ pct: 50, method: 'cash', status: 'verified' }] },
      // 3 measurement
      { customer: 0, items: [{ name: 'Trouser / Pant Stitching', qty: 2, material: 0 }], status: 'measurement', priority: 'normal', fabric: 'customer', source: 'walk_in', ageDays: 3, pay: [{ pct: 50, method: 'upi', status: 'verified' }] },
      { customer: 6, items: [{ name: 'Safari Suit', qty: 1, material: 850 }, { name: 'Shirt Stitching', qty: 2, material: 320 }], status: 'measurement', priority: 'normal', fabric: 'shop', source: 'walk_in', ageDays: 4, pay: [{ pct: 100, method: 'upi', status: 'verified' }] },
      { customer: 4, items: [{ name: 'Cheetah / US Pattern Uniform', qty: 1, material: 0 }], status: 'measurement', priority: 'urgent', fabric: 'customer', source: 'walk_in', ageDays: 2, pay: [{ pct: 50, method: 'cash', status: 'verified' }] },
      // 2 ready
      { customer: 1, items: [{ name: 'Shirt Stitching', qty: 2, material: 0 }, { name: 'General Alteration', qty: 1, material: 0 }], status: 'ready', priority: 'normal', fabric: 'customer', source: 'walk_in', ageDays: 7, pay: [{ pct: 50, method: 'cash', status: 'verified' }] },
      { customer: 3, items: [{ name: 'Police Shirt Only', qty: 3, material: 0 }], status: 'ready', priority: 'normal', fabric: 'customer', source: 'online', ageDays: 6, pay: [{ pct: 50, method: 'online', status: 'verified' }] },
    ]

    let created = 0
    for (const plan of plans) {
      const customerId = customerIds[plan.customer]
      const shopCloth = plan.fabric === 'shop'
      let stitchingTotal = 0
      let materialTotal = 0
      const items = plan.items.map((it) => {
        const s = svc(it.name)
        const stitching = s.defaultStitchingPrice
        const material = shopCloth ? it.material : 0
        stitchingTotal += stitching * it.qty
        materialTotal += material * it.qty
        return {
          serviceId: s._id,
          serviceName: s.name,
          category: s.category,
          stitchingPrice: stitching,
          materialPrice: material,
          quantity: it.qty,
          lineTotal: round2((stitching + material) * it.qty),
        }
      })
      stitchingTotal = round2(stitchingTotal)
      materialTotal = round2(materialTotal)
      const grandTotal = round2(stitchingTotal + materialTotal)
      const createdAt = Date.now() - plan.ageDays * DAY

      const s = await bumpSeq()
      const orderId = await ctx.db.insert('orders', {
        orderNumber: formatOrderNumber(s),
        seq: s,
        customerId,
        measurementVersionId: await currentVersionFor(customerId),
        status: plan.status,
        priority: plan.priority,
        fabricSource: plan.fabric,
        fittingPreference: 'regular',
        notes: plan.source === 'online' ? 'Placed online — confirmed by phone.' : undefined,
        stitchingTotal,
        materialTotal,
        grandTotal,
        requiredAdvancePercent: shopCloth ? 100 : 50,
        promisedDate: createdAt + (plan.priority === 'urgent' ? 3 : 8) * DAY,
        source: plan.source,
        deliveredAt: plan.status === 'delivered' ? createdAt + 8 * DAY : undefined,
      })

      for (const it of items) {
        await ctx.db.insert('order_items', { orderId, ...it })
      }

      for (const p of plan.pay) {
        const amount = round2((grandTotal * p.pct) / 100)
        await ctx.db.insert('payments', {
          orderId,
          customerId,
          amount,
          method: p.method,
          status: p.status,
          transactionRef:
            p.method === 'upi'
              ? `UPI${s}${p.pct}`
              : p.method === 'online'
                ? `pay_${s}${p.pct}${Math.floor(Math.random() * 1000)}`
                : undefined,
          note: p.pct >= 100 ? 'Full payment' : p.pct >= 50 ? 'Advance' : 'Part payment',
          verifiedAt: p.status === 'verified' ? createdAt + DAY : undefined,
        })
      }

      if (plan.status === 'ready') {
        await ctx.db.insert('notifications', {
          orderId,
          customerId,
          channel: 'whatsapp',
          to: CUSTOMERS[plan.customer].mobile,
          template: 'order_ready',
          body: `Namaste! Your order ${formatOrderNumber(s)} is ready for pickup at New Star Tailor.`,
          status: 'scheduled',
        })
      }
      created += 1
    }

    return {
      ok: true,
      message: `Loaded ${customerIds.length} customers and ${created} orders.`,
      customers: customerIds.length,
      orders: created,
    }
  },
})

export const clearAll = mutation({
  args: {},
  handler: async (ctx) => {
    await requireAdmin(ctx)
    for (const table of [
      'payments',
      'order_items',
      'orders',
      'reference_images',
      'notifications',
      'measurement_versions',
      'measurements',
      'customers',
    ] as const) {
      const rows = await ctx.db.query(table).collect()
      for (const r of rows) await ctx.db.delete(r._id)
    }
    const seqRow = await ctx.db
      .query('settings')
      .withIndex('by_key', (q) => q.eq('key', 'order_seq'))
      .first()
    if (seqRow) await ctx.db.delete(seqRow._id)
    return { ok: true, message: 'All customer, order and payment data cleared.' }
  },
})
