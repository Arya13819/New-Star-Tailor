import { Link } from 'react-router-dom'
import { useQuery } from 'convex/react'
import {
  ScissorsIcon,
  AlarmClockIcon,
  PackageCheckIcon,
  WalletIcon,
  IndianRupeeIcon,
  PlusIcon,
  UsersIcon,
  BarChart3Icon,
  ArrowRightIcon,
} from 'lucide-react'
import { api } from '@convex/api'
import { PageHeader } from '@/components/admin/PageHeader'
import { StatCard } from '@/components/admin/StatCard'
import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { useI18n } from '@/i18n'
import { formatCurrency } from '@/lib/format'

export default function Dashboard() {
  const { t } = useI18n()
  const counts = useQuery(api.orders.counts, {})
  const recent = useQuery(api.orders.recentForDashboard, {})
  const report = useQuery(api.reports.summary, {})
  const me = useQuery(api.users.me, {})

  const open = counts ? counts.new + counts.measurement + counts.ready : 0

  return (
    <>
      <PageHeader
        title={`${t('dashboard.greeting')}${me?.name ? `, ${me.name}` : ''}`}
        subtitle={t('dashboard.subtitle')}
        actions={
          <Button asChild variant="gold" size="sm">
            <Link to="/admin/orders/new">
              <PlusIcon className="size-4" />
              {t('nav.newOrder')}
            </Link>
          </Button>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {counts === undefined || report === undefined ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))
        ) : (
          <>
            <StatCard
              label={t('dashboard.openOrders')}
              value={open}
              icon={ScissorsIcon}
              hint={`${counts.new} ${t('status.newShort')} · ${counts.measurement} ${t('status.measurementShort')}`}
            />
            <StatCard
              label={t('dashboard.urgentOpen')}
              value={report.urgentOpen}
              icon={AlarmClockIcon}
              tone="warning"
            />
            <StatCard
              label={t('dashboard.readyForPickup')}
              value={counts.ready}
              icon={PackageCheckIcon}
              tone="gold"
            />
            <StatCard
              label={t('dashboard.outstanding')}
              value={formatCurrency(report.outstandingAllTime)}
              icon={WalletIcon}
            />
          </>
        )}
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>{t('dashboard.recentOrders')}</CardTitle>
            <Button asChild variant="ghost" size="sm">
              <Link to="/admin/orders">
                {t('common.viewAll')}
                <ArrowRightIcon className="size-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {recent === undefined ? (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-14 w-full" />
                ))}
              </div>
            ) : recent.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">
                {t('dashboard.noOrders')}
              </p>
            ) : (
              <ul className="divide-y divide-border">
                {recent.map((o) => (
                  <li key={o._id}>
                    <Link
                      to={`/admin/orders/${o._id}`}
                      className="flex items-center justify-between gap-3 py-3 hover:opacity-80"
                    >
                      <div className="min-w-0">
                        <p className="flex items-center gap-2 font-medium">
                          <span className="font-mono text-sm">{o.orderNumber}</span>
                          {o.priority === 'urgent' && (
                            <Badge variant="warning">{t('priority.urgent')}</Badge>
                          )}
                        </p>
                        <p className="truncate text-sm text-muted-foreground">
                          {o.customerName}
                        </p>
                      </div>
                      <div className="flex shrink-0 items-center gap-3">
                        <span className="hidden text-sm text-muted-foreground sm:block">
                          {o.balance > 0
                            ? t('orders.balanceDue', {
                                amount: formatCurrency(o.balance),
                              })
                            : t('orders.fullyPaid')}
                        </span>
                        <StatusBadge status={o.status} short />
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('dashboard.quickActions')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              { to: '/admin/orders/new', label: t('dashboard.newWalkIn'), icon: PlusIcon },
              { to: '/admin/customers', label: t('dashboard.findCustomer'), icon: UsersIcon },
              { to: '/admin/payments', label: t('dashboard.recordPayment'), icon: IndianRupeeIcon },
              { to: '/admin/reports', label: t('dashboard.viewReports'), icon: BarChart3Icon },
            ].map((a) => (
              <Button
                key={a.to}
                asChild
                variant="outline"
                className="w-full justify-start"
              >
                <Link to={a.to}>
                  <a.icon className="size-4" />
                  {a.label}
                </Link>
              </Button>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  )
}
