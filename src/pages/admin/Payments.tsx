import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery } from 'convex/react'
import { CheckIcon } from 'lucide-react'
import { api } from '@convex/api'
import { PageHeader } from '@/components/admin/PageHeader'
import { StatCard } from '@/components/admin/StatCard'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useI18n } from '@/i18n'
import { formatCurrency, formatDateTime } from '@/lib/format'
import { toast } from 'sonner'

export default function Payments() {
  const { t } = useI18n()
  const [tab, setTab] = useState<'all' | 'verified' | 'pending'>('all')
  const data = useQuery(api.payments.listAll, {
    status: tab === 'all' ? undefined : tab,
  })
  const verify = useMutation(api.payments.verify)

  return (
    <>
      <PageHeader title={t('payments.title')} />

      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {data === undefined ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full" />
          ))
        ) : (
          <>
            <StatCard
              label={t('payments.verifiedTotal')}
              value={formatCurrency(data.summary.verifiedTotal)}
              tone="success"
            />
            <StatCard
              label={t('payments.pendingTotal')}
              value={formatCurrency(data.summary.pendingTotal)}
              tone="warning"
            />
            <StatCard
              label={t('payments.byUpi')}
              value={formatCurrency(data.summary.byMethod.upi)}
            />
            <StatCard
              label={t('payments.byOnline')}
              value={formatCurrency(data.summary.byMethod.online)}
            />
          </>
        )}
      </div>

      <Tabs value={tab} onValueChange={(v) => setTab(v as typeof tab)} className="mb-4">
        <TabsList>
          <TabsTrigger value="all">{t('payments.all')}</TabsTrigger>
          <TabsTrigger value="verified">{t('payments.verified')}</TabsTrigger>
          <TabsTrigger value="pending">{t('payments.pending')}</TabsTrigger>
        </TabsList>
      </Tabs>

      {data === undefined ? (
        <Skeleton className="h-64 w-full" />
      ) : data.rows.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-sm text-muted-foreground">{t('payments.empty')}</p>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-muted-foreground">
                    <th className="p-3 font-medium">{t('payments.columnDate')}</th>
                    <th className="p-3 font-medium">{t('payments.columnOrder')}</th>
                    <th className="p-3 font-medium">{t('payments.columnCustomer')}</th>
                    <th className="p-3 font-medium">{t('payments.columnMethod')}</th>
                    <th className="p-3 text-right font-medium">
                      {t('payments.columnAmount')}
                    </th>
                    <th className="p-3 text-right font-medium">
                      {t('payments.columnStatus')}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {data.rows.map((p) => (
                    <tr key={p._id} className="border-b border-border/60">
                      <td className="p-3 whitespace-nowrap text-muted-foreground">
                        {formatDateTime(p._creationTime)}
                      </td>
                      <td className="p-3">
                        <Link
                          to={`/admin/orders/${p.orderId}`}
                          className="font-mono hover:text-gold"
                        >
                          {p.orderNumber}
                        </Link>
                      </td>
                      <td className="p-3">{p.customerName}</td>
                      <td className="p-3">{t(`paymentMethod.${p.method}`)}</td>
                      <td className="p-3 text-right font-medium">
                        {formatCurrency(p.amount)}
                      </td>
                      <td className="p-3">
                        <div className="flex items-center justify-end gap-2">
                          {p.status === 'verified' ? (
                            <Badge variant="success">
                              {t('payments.verified')}
                            </Badge>
                          ) : (
                            <>
                              <Badge variant="warning">
                                {t('payments.pending')}
                              </Badge>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={async () => {
                                  await verify({ paymentId: p._id })
                                  toast.success(t('payments.verifiedToast'))
                                }}
                              >
                                <CheckIcon className="size-3.5" />
                                {t('payments.verifyAction')}
                              </Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </>
  )
}
