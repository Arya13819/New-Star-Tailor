import { useParams } from 'react-router-dom'
import { useQuery } from 'convex/react'
import { PrinterIcon } from 'lucide-react'
import { api } from '@convex/api'
import type { Id } from '@convex/dataModel'
import { Button } from '@/components/ui/button'
import { ReceiptView } from '@/components/ReceiptView'
import { Logo } from '@/components/Logo'
import { LanguageSwitcher } from '@/components/LanguageSwitcher'
import { useI18n } from '@/i18n'

export default function Receipt() {
  const { t } = useI18n()
  const { orderId } = useParams<{ orderId: string }>()
  const data = useQuery(
    api.orders.receipt,
    orderId ? { id: orderId as Id<'orders'> } : 'skip',
  )

  return (
    <div className="min-h-dvh bg-linen py-8">
      <div className="mx-auto max-w-xl px-4">
        <div className="no-print mb-6 flex items-center justify-between">
          <Logo />
          <LanguageSwitcher />
        </div>

        {data === undefined && (
          <p className="text-center text-sm text-muted-foreground">
            {t('common.loading')}
          </p>
        )}

        {data === null && (
          <p className="rounded-lg border border-border bg-card p-6 text-center text-sm text-muted-foreground">
            {t('receipt.notFound')}
          </p>
        )}

        {data && (
          <>
            <ReceiptView data={data} />
            <div className="no-print mt-6 flex justify-center">
              <Button onClick={() => window.print()} variant="gold">
                <PrinterIcon className="size-4" />
                {t('receipt.printReceipt')}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
