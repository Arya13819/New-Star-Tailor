import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery } from 'convex/react'
import {
  ArrowLeftIcon,
  CheckIcon,
  CopyIcon,
  PrinterIcon,
  Trash2Icon,
} from 'lucide-react'
import { api } from '@convex/api'
import type { Id } from '@convex/dataModel'
import { PageHeader } from '@/components/admin/PageHeader'
import { OrderStatusStepper } from '@/components/admin/OrderStatusStepper'
import { StatusBadge } from '@/components/StatusBadge'
import { ReceiptView } from '@/components/ReceiptView'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'
import { formatCurrency, formatDate, formatDateTime } from '@/lib/format'
import { MEASUREMENT_FIELDS, type PaymentMethod } from '@/lib/constants'
import { toast } from 'sonner'

export default function OrderDetail() {
  const { t } = useI18n()
  const { orderId } = useParams<{ orderId: string }>()
  const id = orderId as Id<'orders'>

  const order = useQuery(api.orders.get, orderId ? { id } : 'skip')
  const updateStatus = useMutation(api.orders.updateStatus)
  const recordPayment = useMutation(api.payments.record)
  const verifyPayment = useMutation(api.payments.verify)
  const removePayment = useMutation(api.payments.remove)
  const updateDetails = useMutation(api.orders.updateDetails)

  const [amount, setAmount] = useState('')
  const [method, setMethod] = useState<PaymentMethod>('cash')
  const [ref, setRef] = useState('')
  const [markVerified, setMarkVerified] = useState(true)
  const [savingPayment, setSavingPayment] = useState(false)

  if (order === undefined) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (order === null) {
    return (
      <Card className="p-10 text-center">
        <p className="text-sm text-muted-foreground">{t('orders.empty')}</p>
        <Button asChild variant="outline" className="mt-4">
          <Link to="/admin/orders">{t('orderDetail.backToOrders')}</Link>
        </Button>
      </Card>
    )
  }

  const receiptUrl = `${window.location.origin}/receipt/${order._id}`

  async function setStatus(status: 'new' | 'measurement' | 'ready' | 'delivered') {
    try {
      await updateStatus({ id, status })
      toast.success(t('orderDetail.statusUpdated'))
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    }
  }

  async function addPayment(e: React.FormEvent) {
    e.preventDefault()
    setSavingPayment(true)
    try {
      await recordPayment({
        orderId: id,
        amount: Number(amount),
        method,
        transactionRef: ref || undefined,
        markVerified,
      })
      setAmount('')
      setRef('')
      toast.success(t('orderDetail.paymentRecorded'))
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    } finally {
      setSavingPayment(false)
    }
  }

  const advancePct = order.requiredAdvance
    ? Math.min(100, Math.round((order.paid / order.requiredAdvance) * 100))
    : 100

  const infoRows: Array<{ label: string; value: string }> = [
    { label: t('orderDetail.placedOn'), value: formatDate(order._creationTime) },
    { label: t('orderDetail.promisedDate'), value: formatDate(order.promisedDate) },
    { label: t('orderDetail.priority'), value: t(`priority.${order.priority}`) },
    {
      label: t('orderDetail.fabric'),
      value: t(`fabric.${order.fabricSource}Short`),
    },
    {
      label: t('orderDetail.fitting'),
      value: order.fittingPreference
        ? t(`fitting.${order.fittingPreference}`)
        : '—',
    },
    {
      label: t('orderDetail.source'),
      value: order.source === 'online' ? t('orders.online') : t('orders.walkIn'),
    },
  ]

  return (
    <>
      <PageHeader
        title={`${t('orderDetail.order')} ${order.orderNumber}`}
        subtitle={order.customer?.name}
        actions={
          <Button asChild variant="ghost" size="sm">
            <Link to="/admin/orders">
              <ArrowLeftIcon className="size-4" />
              {t('orderDetail.backToOrders')}
            </Link>
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_22rem]">
        <div className="space-y-6">
          {/* Status */}
          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle>{t('orderDetail.updateStatus')}</CardTitle>
              <StatusBadge status={order.status} />
            </CardHeader>
            <CardContent className="space-y-5">
              <OrderStatusStepper status={order.status} />
              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  disabled={order.status === 'measurement'}
                  onClick={() => setStatus('measurement')}
                >
                  {t('orderDetail.markMeasurement')}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={order.status === 'ready'}
                  onClick={() => setStatus('ready')}
                >
                  {t('orderDetail.markReady')}
                </Button>
                <Button
                  size="sm"
                  variant="gold"
                  disabled={order.status === 'delivered'}
                  onClick={() => setStatus('delivered')}
                >
                  {t('orderDetail.markDelivered')}
                </Button>
                {order.status !== 'new' && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setStatus('new')}
                  >
                    {t('orderDetail.reopenOrder')}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Info grid */}
          <Card>
            <CardContent className="pt-6">
              <dl className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
                {infoRows.map((r) => (
                  <div key={r.label}>
                    <dt className="text-muted-foreground">{r.label}</dt>
                    <dd className="mt-0.5 font-medium">{r.value}</dd>
                  </div>
                ))}
              </dl>
              <div className="mt-4">
                <Label htmlFor="promised" className="text-xs">
                  {t('orderDetail.setPromised')}
                </Label>
                <Input
                  id="promised"
                  type="date"
                  className="mt-1 w-48"
                  defaultValue={
                    order.promisedDate
                      ? new Date(order.promisedDate).toISOString().slice(0, 10)
                      : ''
                  }
                  onChange={(e) =>
                    e.target.value &&
                    updateDetails({
                      id,
                      promisedDate: new Date(e.target.value).getTime(),
                    })
                  }
                />
              </div>
              {order.notes ? (
                <p className="mt-4 rounded-md bg-secondary/60 p-3 text-sm">
                  {order.notes}
                </p>
              ) : (
                <p className="mt-4 text-sm text-muted-foreground">
                  {t('orderDetail.noNotes')}
                </p>
              )}
            </CardContent>
          </Card>

          {/* Items */}
          <Card>
            <CardHeader>
              <CardTitle>{t('orderDetail.items')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-muted-foreground">
                      <th className="py-2 font-medium">{t('receipt.item')}</th>
                      <th className="py-2 text-center font-medium">
                        {t('common.quantity')}
                      </th>
                      <th className="py-2 text-right font-medium">
                        {t('receipt.stitching')}
                      </th>
                      <th className="py-2 text-right font-medium">
                        {t('receipt.material')}
                      </th>
                      <th className="py-2 text-right font-medium">
                        {t('common.total')}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {order.items.map((it) => (
                      <tr key={it._id} className="border-b border-border/60">
                        <td className="py-2">{it.serviceName}</td>
                        <td className="py-2 text-center">{it.quantity}</td>
                        <td className="py-2 text-right">
                          {formatCurrency(it.stitchingPrice)}
                        </td>
                        <td className="py-2 text-right">
                          {it.materialPrice > 0
                            ? formatCurrency(it.materialPrice)
                            : '—'}
                        </td>
                        <td className="py-2 text-right font-medium">
                          {formatCurrency(it.lineTotal)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Measurements */}
          <Card>
            <CardHeader>
              <CardTitle>{t('orderDetail.measurementUsed')}</CardTitle>
            </CardHeader>
            <CardContent>
              {order.measurementVersion ? (
                <>
                  <Badge variant="gold" className="mb-3">
                    {t('orderDetail.measurementVersion', {
                      n: order.measurementVersion.version,
                    })}
                  </Badge>
                  <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-3">
                    {MEASUREMENT_FIELDS.filter(
                      (f) => order.measurementVersion?.values[f.key] != null,
                    ).map((f) => (
                      <div key={f.key} className="flex justify-between">
                        <dt className="text-muted-foreground">{f.en}</dt>
                        <dd className="font-medium">
                          {order.measurementVersion?.values[f.key]}
                        </dd>
                      </div>
                    ))}
                  </dl>
                </>
              ) : (
                <p className="text-sm text-muted-foreground">
                  {t('orderDetail.noMeasurement')}
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right column: financials + payments + receipt */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t('orderDetail.financials')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <Row label={t('orderDetail.stitchingTotal')} value={order.stitchingTotal} />
              <Row label={t('orderDetail.materialTotal')} value={order.materialTotal} />
              <div className="flex justify-between border-t border-border pt-2 font-semibold">
                <span>{t('orderDetail.grandTotal')}</span>
                <span>{formatCurrency(order.grandTotal)}</span>
              </div>
              <Row
                label={t('orderDetail.paidVerified')}
                value={order.paid}
                tone="success"
              />
              {order.pendingPaid > 0 && (
                <Row
                  label={t('orderDetail.pendingVerification')}
                  value={order.pendingPaid}
                  tone="muted"
                />
              )}
              <div className="flex justify-between font-semibold">
                <span>{t('orderDetail.balanceDue')}</span>
                <span>{formatCurrency(order.balance)}</span>
              </div>

              <div className="!mt-4 rounded-lg bg-secondary/60 p-3">
                <p className="flex justify-between text-xs text-muted-foreground">
                  <span>{t('orderDetail.requiredAdvance')}</span>
                  <span>{formatCurrency(order.requiredAdvance)}</span>
                </p>
                <Progress value={advancePct} className="mt-2" />
                <p
                  className={cn(
                    'mt-2 text-xs font-medium',
                    order.advanceMet ? 'text-success' : 'text-warning',
                  )}
                >
                  {order.advanceMet
                    ? t('orderDetail.advanceMet')
                    : t('orderDetail.advanceShort', {
                        amount: formatCurrency(
                          Math.max(0, order.requiredAdvance - order.paid),
                        ),
                      })}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Record payment */}
          <Card>
            <CardHeader>
              <CardTitle>{t('orderDetail.recordPayment')}</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-3" onSubmit={addPayment}>
                <div>
                  <Label htmlFor="amt">{t('orderDetail.amount')}</Label>
                  <Input
                    id="amt"
                    type="number"
                    min={1}
                    className="mt-1"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Label>{t('orderDetail.method')}</Label>
                  <Select
                    value={method}
                    onValueChange={(v) => {
                      setMethod(v as PaymentMethod)
                      setMarkVerified(v !== 'online')
                    }}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="cash">{t('paymentMethod.cash')}</SelectItem>
                      <SelectItem value="upi">{t('paymentMethod.upi')}</SelectItem>
                      <SelectItem value="online">
                        {t('paymentMethod.online')}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                {method !== 'cash' && (
                  <div>
                    <Label htmlFor="ref">{t('orderDetail.reference')}</Label>
                    <Input
                      id="ref"
                      className="mt-1"
                      placeholder={t('orderDetail.referenceHint')}
                      value={ref}
                      onChange={(e) => setRef(e.target.value)}
                    />
                  </div>
                )}
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={markVerified}
                    onChange={(e) => setMarkVerified(e.target.checked)}
                    className="size-4 rounded border-input"
                  />
                  {t('orderDetail.markVerified')}
                </label>
                <Button
                  type="submit"
                  className="w-full"
                  disabled={savingPayment || !amount}
                >
                  {t('orderDetail.addPayment')}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Payment history */}
          <Card>
            <CardHeader>
              <CardTitle>{t('orderDetail.paymentHistory')}</CardTitle>
            </CardHeader>
            <CardContent>
              {order.payments.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  {t('orderDetail.noPayments')}
                </p>
              ) : (
                <ul className="space-y-2">
                  {order.payments.map((p) => (
                    <li
                      key={p._id}
                      className="flex items-center justify-between gap-2 rounded-lg border border-border p-3 text-sm"
                    >
                      <div>
                        <p className="font-medium">{formatCurrency(p.amount)}</p>
                        <p className="text-xs text-muted-foreground">
                          {t(`paymentMethod.${p.method}`)} ·{' '}
                          {formatDateTime(p._creationTime)}
                        </p>
                      </div>
                      <div className="flex items-center gap-1">
                        {p.status === 'verified' ? (
                          <Badge variant="success">
                            {t('orderDetail.verified')}
                          </Badge>
                        ) : (
                          <>
                            <Badge variant="warning">
                              {t('orderDetail.pending')}
                            </Badge>
                            <Button
                              size="icon"
                              variant="ghost"
                              className="size-7"
                              onClick={() => verifyPayment({ paymentId: p._id })}
                            >
                              <CheckIcon className="size-4" />
                            </Button>
                          </>
                        )}
                        <Button
                          size="icon"
                          variant="ghost"
                          className="size-7 text-destructive"
                          onClick={() => removePayment({ paymentId: p._id })}
                        >
                          <Trash2Icon className="size-4" />
                        </Button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          {/* Receipt */}
          <Card>
            <CardHeader>
              <CardTitle>{t('orderDetail.receipt')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline" className="w-full">
                    <PrinterIcon className="size-4" />
                    {t('orderDetail.viewReceipt')}
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader className="no-print">
                    <DialogTitle>{t('receipt.title')}</DialogTitle>
                  </DialogHeader>
                  <ReceiptModalBody id={order._id} receiptUrl={receiptUrl} />
                </DialogContent>
              </Dialog>
              <Button
                variant="ghost"
                className="w-full"
                onClick={() => {
                  navigator.clipboard.writeText(receiptUrl)
                  toast.success(t('orderDetail.receiptLinkCopied'))
                }}
              >
                <CopyIcon className="size-4" />
                {t('orderDetail.copyReceiptLink')}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}

function Row({
  label,
  value,
  tone,
}: {
  label: string
  value: number
  tone?: 'success' | 'muted'
}) {
  return (
    <div className="flex justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span
        className={cn(
          tone === 'success' && 'text-success',
          tone === 'muted' && 'text-muted-foreground',
        )}
      >
        {formatCurrency(value)}
      </span>
    </div>
  )
}

function ReceiptModalBody({
  id,
  receiptUrl,
}: {
  id: Id<'orders'>
  receiptUrl: string
}) {
  const { t } = useI18n()
  const data = useQuery(api.orders.receipt, { id })
  if (data === undefined)
    return <p className="text-sm text-muted-foreground">{t('common.loading')}</p>
  if (data === null)
    return (
      <p className="text-sm text-muted-foreground">{t('receipt.notFound')}</p>
    )
  return (
    <div>
      <ReceiptView data={data} />
      <div className="no-print mt-4 flex flex-wrap justify-center gap-2">
        <Button variant="gold" onClick={() => window.print()}>
          <PrinterIcon className="size-4" />
          {t('receipt.printReceipt')}
        </Button>
        <Button variant="outline" asChild>
          <a href={receiptUrl} target="_blank" rel="noreferrer">
            {t('orderDetail.viewReceipt')}
          </a>
        </Button>
        <Button
          variant="ghost"
          onClick={() => {
            navigator.clipboard.writeText(receiptUrl)
            toast.success(t('orderDetail.receiptLinkCopied'))
          }}
        >
          <CopyIcon className="size-4" />
          {t('orderDetail.copyReceiptLink')}
        </Button>
      </div>
    </div>
  )
}
