import { useI18n } from '@/i18n'
import { formatCurrency, formatDate } from '@/lib/format'
import { StitchDivider } from '@/components/StitchDivider'

type ReceiptData = {
  orderNumber: string
  createdAt: number
  promisedDate?: number | null
  priority: 'normal' | 'urgent'
  fabricSource: 'customer' | 'shop'
  fittingPreference?: string | null
  notes?: string | null
  customer: { name: string; mobile: string; address?: string | null } | null
  items: Array<{
    serviceName: string
    quantity: number
    stitchingPrice: number
    materialPrice: number
    lineTotal: number
  }>
  stitchingTotal: number
  materialTotal: number
  grandTotal: number
  paid: number
  balance: number
  payments: Array<{ amount: number; method: string; status: string; at: number }>
  shop: {
    name?: string
    address?: string
    phone?: string
    gstin?: string
  } | null
}

export function ReceiptView({ data }: { data: ReceiptData }) {
  const { t } = useI18n()
  const shop = data.shop ?? {}

  return (
    <div className="print-area mx-auto max-w-xl rounded-xl border border-border bg-white p-8 text-[#1b2a4a] shadow-warm">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-serif text-xl font-semibold">
            {shop.name ?? t('common.appName')}
          </h1>
          {shop.address && (
            <p className="mt-1 max-w-[15rem] text-xs text-[#6b6459]">{shop.address}</p>
          )}
          {shop.phone && <p className="text-xs text-[#6b6459]">{shop.phone}</p>}
          {shop.gstin && (
            <p className="text-xs text-[#6b6459]">GSTIN: {shop.gstin}</p>
          )}
        </div>
        <div className="text-right">
          <p className="text-[11px] tracking-[0.15em] text-[#c5993a] uppercase">
            {t('receipt.title')}
          </p>
          <p className="mt-1 font-serif text-lg font-semibold">{data.orderNumber}</p>
          <p className="text-xs text-[#6b6459]">{formatDate(data.createdAt)}</p>
        </div>
      </div>

      <StitchDivider className="my-5" />

      <div className="grid grid-cols-2 gap-4 text-xs">
        <div>
          <p className="tracking-[0.12em] text-[#c5993a] uppercase">
            {t('receipt.customer')}
          </p>
          <p className="mt-1 text-sm font-medium">{data.customer?.name ?? '—'}</p>
          {data.customer?.mobile && <p className="text-[#6b6459]">{data.customer.mobile}</p>}
          {data.customer?.address && (
            <p className="text-[#6b6459]">{data.customer.address}</p>
          )}
        </div>
        <div className="text-right">
          <p className="text-[#6b6459]">
            {t('receipt.fabricLabel')}:{' '}
            <span className="text-[#1b2a4a]">
              {t(`fabric.${data.fabricSource}Short`)}
            </span>
          </p>
          {data.fittingPreference && (
            <p className="text-[#6b6459]">
              {t('receipt.fittingLabel')}:{' '}
              <span className="text-[#1b2a4a]">
                {t(`fitting.${data.fittingPreference}`)}
              </span>
            </p>
          )}
          {data.promisedDate && (
            <p className="text-[#6b6459]">
              {t('track.promisedBy')}: {formatDate(data.promisedDate)}
            </p>
          )}
        </div>
      </div>

      <table className="mt-5 w-full text-xs">
        <thead>
          <tr className="border-b border-[#e4dfd6] text-left text-[#6b6459]">
            <th className="py-2 font-medium">{t('receipt.item')}</th>
            <th className="py-2 text-center font-medium">{t('common.quantity')}</th>
            <th className="py-2 text-right font-medium">{t('receipt.stitching')}</th>
            <th className="py-2 text-right font-medium">{t('receipt.material')}</th>
            <th className="py-2 text-right font-medium">{t('receipt.lineTotal')}</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map((it, i) => (
            <tr key={i} className="border-b border-[#f0ece4]">
              <td className="py-2">{it.serviceName}</td>
              <td className="py-2 text-center">{it.quantity}</td>
              <td className="py-2 text-right">{formatCurrency(it.stitchingPrice)}</td>
              <td className="py-2 text-right">
                {it.materialPrice > 0 ? formatCurrency(it.materialPrice) : '—'}
              </td>
              <td className="py-2 text-right font-medium">
                {formatCurrency(it.lineTotal)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-4 ml-auto w-56 space-y-1 text-xs">
        <div className="flex justify-between text-[#6b6459]">
          <span>{t('receipt.stitchingTotal')}</span>
          <span>{formatCurrency(data.stitchingTotal)}</span>
        </div>
        <div className="flex justify-between text-[#6b6459]">
          <span>{t('receipt.materialTotal')}</span>
          <span>{formatCurrency(data.materialTotal)}</span>
        </div>
        <div className="flex justify-between border-t border-[#e4dfd6] pt-1 text-sm font-semibold">
          <span>{t('receipt.grandTotal')}</span>
          <span>{formatCurrency(data.grandTotal)}</span>
        </div>
        <div className="flex justify-between text-[#3f7d54]">
          <span>{t('receipt.paid')}</span>
          <span>{formatCurrency(data.paid)}</span>
        </div>
        <div className="flex justify-between font-semibold">
          <span>{t('receipt.balance')}</span>
          <span>{formatCurrency(data.balance)}</span>
        </div>
      </div>

      {data.payments.length > 0 && (
        <div className="mt-5 text-xs">
          <p className="tracking-[0.12em] text-[#c5993a] uppercase">
            {t('receipt.payments')}
          </p>
          <ul className="mt-1 space-y-0.5 text-[#6b6459]">
            {data.payments.map((p, i) => (
              <li key={i} className="flex justify-between">
                <span>
                  {formatDate(p.at)} · {t(`paymentMethod.${p.method}`)}
                  {p.status === 'pending' ? ` (${t('orderDetail.pending')})` : ''}
                </span>
                <span>{formatCurrency(p.amount)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.notes && (
        <p className="mt-5 rounded-md bg-[#faf8f5] p-3 text-xs text-[#6b6459]">
          {data.notes}
        </p>
      )}

      <StitchDivider className="my-5" />
      <p className="text-center text-xs text-[#6b6459]">{t('receipt.thankYou')}</p>
    </div>
  )
}
