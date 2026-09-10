import { useMemo, useState } from 'react'
import { useQuery } from 'convex/react'
import {
  IndianRupeeIcon,
  ClipboardListIcon,
  WalletIcon,
  AlarmClockIcon,
} from 'lucide-react'
import { api } from '@convex/api'
import { PageHeader } from '@/components/admin/PageHeader'
import { StatCard } from '@/components/admin/StatCard'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'
import { formatCurrency } from '@/lib/format'
import { ORDER_STATUSES } from '@/lib/constants'

type RangeKey = 'today' | 'week' | 'month' | 'custom'

function rangeToWindow(key: RangeKey, from: string, to: string) {
  const now = new Date()
  if (key === 'today') {
    const start = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    return { from: start.getTime(), to: Date.now() }
  }
  if (key === 'week') {
    return { from: Date.now() - 7 * 24 * 60 * 60 * 1000, to: Date.now() }
  }
  if (key === 'month') {
    return { from: Date.now() - 30 * 24 * 60 * 60 * 1000, to: Date.now() }
  }
  return {
    from: from ? new Date(from).getTime() : undefined,
    to: to ? new Date(to).getTime() + 24 * 60 * 60 * 1000 : undefined,
  }
}

export default function Reports() {
  const { t } = useI18n()
  const [range, setRange] = useState<RangeKey>('month')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')

  const win = useMemo(() => rangeToWindow(range, from, to), [range, from, to])
  const report = useQuery(api.reports.summary, win)

  const maxCategoryValue = report
    ? Math.max(1, ...report.byCategory.map((c) => c.value))
    : 1
  const maxStatus = report
    ? Math.max(1, ...Object.values(report.byStatus))
    : 1

  return (
    <>
      <PageHeader title={t('reports.title')} />

      <div className="mb-6 flex flex-wrap items-center gap-2">
        {(['today', 'week', 'month', 'custom'] as RangeKey[]).map((k) => (
          <Button
            key={k}
            size="sm"
            variant={range === k ? 'default' : 'outline'}
            onClick={() => setRange(k)}
          >
            {k === 'today'
              ? t('common.today')
              : k === 'week'
                ? t('common.thisWeek')
                : k === 'month'
                  ? t('common.thisMonth')
                  : t('common.custom')}
          </Button>
        ))}
        {range === 'custom' && (
          <div className="flex items-center gap-2">
            <Input
              type="date"
              className="w-40"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
            />
            <span className="text-sm text-muted-foreground">{t('common.to')}</span>
            <Input
              type="date"
              className="w-40"
              value={to}
              onChange={(e) => setTo(e.target.value)}
            />
          </div>
        )}
      </div>

      {report === undefined ? (
        <div className="space-y-4">
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Revenue hero */}
          <Card className="overflow-hidden">
            <CardContent className="gradient-navy p-8 text-white">
              <p className="text-xs tracking-[0.15em] text-gold uppercase">
                {t('reports.revenueCollected')}
              </p>
              <p className="mt-2 font-serif text-4xl font-semibold">
                {formatCurrency(report.revenueCollected)}
              </p>
              <p className="mt-1 text-sm text-white/70">
                {report.orderCount} {t('nav.orders').toLowerCase()} ·{' '}
                {t('reports.inSelectedRange')}
              </p>
              <div className="mt-6 flex flex-wrap gap-6 text-sm">
                <div>
                  <p className="text-white/60">{t('reports.stitchingValue')}</p>
                  <p className="font-medium">
                    {formatCurrency(report.stitchingValue)}
                  </p>
                </div>
                <div>
                  <p className="text-white/60">{t('reports.materialValue')}</p>
                  <p className="font-medium">
                    {formatCurrency(report.materialValue)}
                  </p>
                </div>
                <div>
                  <p className="text-white/60">{t('reports.orderValue')}</p>
                  <p className="font-medium">
                    {formatCurrency(report.orderValue)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label={t('reports.orderValue')}
              value={formatCurrency(report.orderValue)}
              icon={ClipboardListIcon}
            />
            <StatCard
              label={t('reports.outstanding')}
              value={formatCurrency(report.outstandingAllTime)}
              icon={WalletIcon}
            />
            <StatCard
              label={t('reports.pendingVerification')}
              value={formatCurrency(report.pendingVerification)}
              icon={IndianRupeeIcon}
              tone="warning"
            />
            <StatCard
              label={t('reports.urgentOpen')}
              value={report.urgentOpen}
              icon={AlarmClockIcon}
              tone="warning"
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Orders by status */}
            <Card>
              <CardHeader>
                <CardTitle>{t('reports.ordersByStatus')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {ORDER_STATUSES.map((s) => (
                  <div key={s}>
                    <div className="mb-1 flex justify-between text-sm">
                      <span>{t(`status.${s}`)}</span>
                      <span className="font-medium">{report.byStatus[s]}</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-secondary">
                      <div
                        className="h-full rounded-full bg-navy dark:bg-gold"
                        style={{
                          width: `${(report.byStatus[s] / maxStatus) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Category breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>{t('reports.categoryBreakdown')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {report.byCategory.every((c) => c.count === 0) ? (
                  <p className="text-sm text-muted-foreground">
                    {t('reports.noData')}
                  </p>
                ) : (
                  report.byCategory.map((c) => (
                    <div key={c.category}>
                      <div className="mb-1 flex items-baseline justify-between text-sm">
                        <span>{t(`category.${c.category}`)}</span>
                        <span className="font-medium">
                          {formatCurrency(c.value)}
                        </span>
                      </div>
                      <div className="h-3 overflow-hidden rounded-full bg-secondary">
                        <div
                          className={cn('h-full rounded-full gradient-gold')}
                          style={{
                            width: `${(c.value / maxCategoryValue) * 100}%`,
                          }}
                        />
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {t('reports.categoryItems', { count: c.count })}
                      </p>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </>
  )
}
