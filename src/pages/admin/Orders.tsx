import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from 'convex/react'
import { PlusIcon, SearchIcon } from 'lucide-react'
import { api } from '@convex/api'
import { PageHeader } from '@/components/admin/PageHeader'
import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useI18n } from '@/i18n'
import { formatCurrency, formatDate } from '@/lib/format'
import { ORDER_STATUSES, type OrderStatus } from '@/lib/constants'

export default function Orders() {
  const { t } = useI18n()
  const [tab, setTab] = useState<'all' | OrderStatus>('all')
  const [search, setSearch] = useState('')

  const counts = useQuery(api.orders.counts, {})
  const orders = useQuery(api.orders.list, {
    status: tab === 'all' ? undefined : tab,
    search: search.trim() || undefined,
  })

  return (
    <>
      <PageHeader
        title={t('orders.title')}
        actions={
          <Button asChild variant="gold" size="sm">
            <Link to="/admin/orders/new">
              <PlusIcon className="size-4" />
              {t('orders.newOrder')}
            </Link>
          </Button>
        }
      />

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Tabs value={tab} onValueChange={(v) => setTab(v as typeof tab)}>
          <TabsList>
            <TabsTrigger value="all">
              {t('common.all')}
              {counts && (
                <Badge variant="secondary" className="ml-1.5">
                  {counts.total}
                </Badge>
              )}
            </TabsTrigger>
            {ORDER_STATUSES.map((s) => (
              <TabsTrigger key={s} value={s}>
                {t(`status.${s}Short`)}
                {counts && (
                  <Badge variant="secondary" className="ml-1.5">
                    {counts[s]}
                  </Badge>
                )}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>

        <div className="relative sm:w-72">
          <SearchIcon className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder={t('orders.searchPlaceholder')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {orders === undefined ? (
        <div className="space-y-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      ) : orders.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-sm text-muted-foreground">{t('orders.empty')}</p>
        </Card>
      ) : (
        <div className="space-y-2">
          {orders.map((o) => (
            <Link
              key={o._id}
              to={`/admin/orders/${o._id}`}
              className="hover-gold flex flex-col gap-3 rounded-xl border border-border bg-card p-4 shadow-warm sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="flex items-start gap-3">
                <div>
                  <p className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-sm font-semibold">
                      {o.orderNumber}
                    </span>
                    {o.priority === 'urgent' && (
                      <Badge variant="warning">{t('priority.urgent')}</Badge>
                    )}
                    <Badge variant="outline">
                      {o.source === 'online' ? t('orders.online') : t('orders.walkIn')}
                    </Badge>
                    <Badge variant="outline">
                      {t(`fabric.${o.fabricSource}Short`)}
                    </Badge>
                  </p>
                  <p className="mt-1 text-sm font-medium">{o.customerName}</p>
                  <p className="text-xs text-muted-foreground">
                    {t('orders.placed')} {formatDate(o._creationTime)}
                    {o.customerMobile ? ` · ${o.customerMobile}` : ''}
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between gap-4 sm:flex-col sm:items-end">
                <StatusBadge status={o.status} short />
                <div className="text-right">
                  <p className="text-sm font-semibold">
                    {formatCurrency(o.grandTotal)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {o.balance > 0
                      ? t('orders.balanceDue', { amount: formatCurrency(o.balance) })
                      : t('orders.fullyPaid')}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  )
}
