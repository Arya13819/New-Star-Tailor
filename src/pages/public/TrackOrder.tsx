import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from 'convex/react'
import { api } from '@convex/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Section, SectionHeader } from '@/components/public/Section'
import { StatusBadge } from '@/components/StatusBadge'
import { OrderStatusStepper } from '@/components/admin/OrderStatusStepper'
import { useI18n } from '@/i18n'
import { formatCurrency, formatDate } from '@/lib/format'

export default function TrackOrder() {
  const { t } = useI18n()
  const [orderNumber, setOrderNumber] = useState('')
  const [mobile, setMobile] = useState('')
  const [submitted, setSubmitted] = useState<{ orderNumber: string; mobile: string } | null>(null)

  const result = useQuery(
    api.orders.track,
    submitted ? submitted : 'skip',
  )

  const loading = submitted !== null && result === undefined

  return (
    <>
      <div className="gradient-hero">
        <Section className="py-14 md:py-16">
          <SectionHeader title={t('track.title')} subtitle={t('track.subtitle')} />
        </Section>
      </div>

      <Section className="max-w-2xl">
        <Card>
          <CardContent className="pt-6">
            <form
              className="grid gap-4 sm:grid-cols-2"
              onSubmit={(e) => {
                e.preventDefault()
                setSubmitted({ orderNumber: orderNumber.trim(), mobile: mobile.trim() })
              }}
            >
              <div className="sm:col-span-2">
                <Label htmlFor="ordno">{t('track.orderNumber')}</Label>
                <Input
                  id="ordno"
                  className="mt-1.5"
                  placeholder="NST-000123"
                  value={orderNumber}
                  onChange={(e) => setOrderNumber(e.target.value)}
                  required
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  {t('track.orderNumberHint')}
                </p>
              </div>
              <div className="sm:col-span-2">
                <Label htmlFor="mob">{t('common.mobile')}</Label>
                <Input
                  id="mob"
                  className="mt-1.5"
                  inputMode="numeric"
                  placeholder="9876543210"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  required
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  {t('track.mobileHint')}
                </p>
              </div>
              <div className="sm:col-span-2">
                <Button type="submit" disabled={loading} className="w-full sm:w-auto">
                  {loading ? t('common.loading') : t('track.checkStatus')}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {submitted && result && !result.found && (
          <p className="mt-6 rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
            {t('track.notFound')}
          </p>
        )}

        {submitted && result && result.found && (
          <Card className="mt-6">
            <CardContent className="space-y-6 pt-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="font-serif text-xl font-semibold">
                    {t('track.resultTitle', { number: result.orderNumber })}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {result.customerName}
                  </p>
                </div>
                <StatusBadge status={result.status} />
              </div>

              <div>
                <p className="section-label mb-3">{t('track.statusHeading')}</p>
                <OrderStatusStepper status={result.status} />
              </div>

              <dl className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
                <div>
                  <dt className="text-muted-foreground">{t('track.placedOn')}</dt>
                  <dd className="mt-0.5 font-medium">{formatDate(result.createdAt)}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">{t('track.promisedBy')}</dt>
                  <dd className="mt-0.5 font-medium">{formatDate(result.promisedDate)}</dd>
                </div>
                {result.deliveredAt && (
                  <div>
                    <dt className="text-muted-foreground">{t('track.deliveredOn')}</dt>
                    <dd className="mt-0.5 font-medium">{formatDate(result.deliveredAt)}</dd>
                  </div>
                )}
              </dl>

              <div>
                <p className="section-label mb-2">{t('track.items')}</p>
                <ul className="space-y-1 text-sm">
                  {result.items.map((it, i) => (
                    <li key={i} className="flex justify-between">
                      <span>{it.serviceName}</span>
                      <span className="text-muted-foreground">× {it.quantity}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="grid grid-cols-3 gap-4 rounded-lg bg-secondary/60 p-4 text-sm">
                <div>
                  <p className="text-muted-foreground">{t('track.amount')}</p>
                  <p className="mt-0.5 font-semibold">{formatCurrency(result.grandTotal)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">{t('track.paid')}</p>
                  <p className="mt-0.5 font-semibold text-success">
                    {formatCurrency(result.paid)}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">{t('track.balance')}</p>
                  <p className="mt-0.5 font-semibold text-foreground">
                    {formatCurrency(result.balance)}
                  </p>
                </div>
              </div>

              <Button asChild variant="outline" size="sm">
                <Link to={`/enquiry`}>{t('nav.enquiry')}</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </Section>
    </>
  )
}
