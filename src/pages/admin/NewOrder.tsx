import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from 'convex/react'
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  CheckCircle2Icon,
  CheckIcon,
  PlusIcon,
  PrinterIcon,
  SearchIcon,
  Trash2Icon,
  UserPlusIcon,
} from 'lucide-react'
import { api } from '@convex/api'
import type { Id } from '@convex/dataModel'
import { PageHeader } from '@/components/admin/PageHeader'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useI18n, useLocalized } from '@/i18n'
import { cn } from '@/lib/utils'
import { formatCurrency } from '@/lib/format'
import {
  FITTING_PREFERENCES,
  type FabricSource,
  type FittingPreference,
} from '@/lib/constants'
import { toast } from 'sonner'

type ItemRow = {
  key: string
  serviceId: Id<'services'> | ''
  serviceName: string
  category: 'regular' | 'police' | 'crpf' | 'army'
  stitchingPrice: number
  materialPrice: number
  quantity: number
}

type SelectedCustomer = { _id: Id<'customers'>; name: string; mobile: string }

export default function NewOrder() {
  const { t } = useI18n()
  const localized = useLocalized()
  const navigate = useNavigate()

  const services = useQuery(api.services.list, {})
  const seedServices = useMutation(api.services.seedIfEmpty)
  const createCustomer = useMutation(api.customers.create)
  const createOrder = useMutation(api.orders.create)

  const seededRef = useRef(false)
  useEffect(() => {
    if (services && services.length === 0 && !seededRef.current) {
      seededRef.current = true
      seedServices({}).catch(() => undefined)
    }
  }, [services, seedServices])

  const [step, setStep] = useState(1)

  // Step 1 — customer
  const [search, setSearch] = useState('')
  const results = useQuery(
    api.customers.quickSearch,
    search.trim().length >= 2 ? { term: search.trim() } : 'skip',
  )
  const [selected, setSelected] = useState<SelectedCustomer | null>(null)
  const [showNewForm, setShowNewForm] = useState(false)
  const [nc, setNc] = useState({ name: '', mobile: '', address: '' })
  const [savingCustomer, setSavingCustomer] = useState(false)

  // Step 2 — items
  const [items, setItems] = useState<ItemRow[]>([])

  // Step 3 — options
  const [fabricSource, setFabricSource] = useState<FabricSource>('customer')
  const [priority, setPriority] = useState<'normal' | 'urgent'>('normal')
  const [fitting, setFitting] = useState<FittingPreference | ''>('')
  const [promisedDate, setPromisedDate] = useState('')
  const [notes, setNotes] = useState('')

  const [creating, setCreating] = useState(false)
  const [success, setSuccess] = useState<{ orderId: Id<'orders'>; orderNumber: string } | null>(null)

  const shopCloth = fabricSource === 'shop'

  const totals = useMemo(() => {
    let stitching = 0
    let material = 0
    for (const it of items) {
      stitching += it.stitchingPrice * it.quantity
      material += (shopCloth ? it.materialPrice : 0) * it.quantity
    }
    const grand = stitching + material
    const advance = shopCloth ? grand : stitching * 0.5
    return { stitching, material, grand, advance }
  }, [items, shopCloth])

  function addItem() {
    const first = services?.[0]
    setItems((prev) => [
      ...prev,
      {
        key: crypto.randomUUID(),
        serviceId: first?._id ?? '',
        serviceName: first?.name ?? '',
        category: first?.category ?? 'regular',
        stitchingPrice: first?.defaultStitchingPrice ?? 0,
        materialPrice: 0,
        quantity: 1,
      },
    ])
  }

  function updateItemService(key: string, serviceId: Id<'services'>) {
    const svc = services?.find((s) => s._id === serviceId)
    if (!svc) return
    setItems((prev) =>
      prev.map((it) =>
        it.key === key
          ? {
              ...it,
              serviceId,
              serviceName: svc.name,
              category: svc.category,
              stitchingPrice: svc.defaultStitchingPrice,
            }
          : it,
      ),
    )
  }

  async function saveCustomer() {
    setSavingCustomer(true)
    try {
      const id = await createCustomer({
        name: nc.name,
        mobile: nc.mobile,
        address: nc.address || undefined,
      })
      setSelected({ _id: id, name: nc.name, mobile: nc.mobile })
      setShowNewForm(false)
      setNc({ name: '', mobile: '', address: '' })
      toast.success(t('newOrder.customerSaved'))
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    } finally {
      setSavingCustomer(false)
    }
  }

  async function submit() {
    if (!selected || items.length === 0) return
    setCreating(true)
    try {
      const res = await createOrder({
        customerId: selected._id,
        items: items.map((it) => ({
          serviceId: it.serviceId || undefined,
          serviceName: it.serviceName,
          category: it.category,
          stitchingPrice: it.stitchingPrice,
          materialPrice: it.materialPrice,
          quantity: it.quantity,
        })),
        fabricSource,
        priority,
        fittingPreference: fitting || undefined,
        notes: notes || undefined,
        promisedDate: promisedDate ? new Date(promisedDate).getTime() : undefined,
        source: 'walk_in',
      })
      setSuccess({ orderId: res.orderId, orderNumber: res.orderNumber })
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    } finally {
      setCreating(false)
    }
  }

  if (success) {
    return (
      <div className="mx-auto max-w-lg py-6">
        <Card>
          <CardContent className="pt-8 pb-8 text-center">
            <CheckCircle2Icon className="mx-auto size-12 text-success" />
            <h2 className="mt-4 font-serif text-2xl font-semibold">
              {t('newOrder.successTitle')}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {t('newOrder.successBody')}
            </p>
            <div className="mt-4 rounded-lg bg-secondary p-4">
              <p className="font-serif text-3xl font-semibold tracking-wide">
                {success.orderNumber}
              </p>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              {t('newOrder.successHint')}
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              <Button asChild variant="gold">
                <Link to={`/admin/orders/${success.orderId}`}>
                  {t('newOrder.viewOrder')}
                </Link>
              </Button>
              <Button asChild variant="outline">
                <Link to={`/receipt/${success.orderId}`} target="_blank">
                  <PrinterIcon className="size-4" />
                  {t('newOrder.printReceipt')}
                </Link>
              </Button>
              <Button
                variant="ghost"
                onClick={() => {
                  setSuccess(null)
                  setStep(1)
                  setSelected(null)
                  setItems([])
                  setNotes('')
                  setPromisedDate('')
                }}
              >
                {t('newOrder.anotherOrder')}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const steps = [t('newOrder.step1'), t('newOrder.step2'), t('newOrder.step3')]
  const canNext =
    (step === 1 && selected) || (step === 2 && items.length > 0) || step === 3

  return (
    <>
      <PageHeader
        title={t('newOrder.title')}
        actions={
          <Button asChild variant="ghost" size="sm">
            <Link to="/admin/orders">
              <ArrowLeftIcon className="size-4" />
              {t('orders.title')}
            </Link>
          </Button>
        }
      />

      {/* Stepper */}
      <ol className="mb-6 flex items-center gap-2">
        {steps.map((label, i) => {
          const n = i + 1
          return (
            <li key={label} className="flex flex-1 items-center gap-2">
              <button
                type="button"
                onClick={() => n < step && setStep(n)}
                className={cn(
                  'flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium',
                  n === step && 'bg-primary text-primary-foreground',
                  n < step && 'bg-success/15 text-success',
                  n > step && 'text-muted-foreground',
                )}
              >
                <span className="inline-flex size-5 items-center justify-center rounded-full border text-xs">
                  {n < step ? <CheckIcon className="size-3" /> : n}
                </span>
                <span className="hidden sm:inline">{label}</span>
              </button>
              {i < steps.length - 1 && (
                <span className="h-px flex-1 bg-border" />
              )}
            </li>
          )
        })}
      </ol>

      {/* Step 1 */}
      {step === 1 && (
        <Card>
          <CardContent className="space-y-5 pt-6">
            <h2 className="font-serif text-lg font-semibold">
              {t('newOrder.step1Title')}
            </h2>

            {selected ? (
              <div className="flex items-center justify-between rounded-lg border border-gold/40 bg-gold/5 p-4">
                <div>
                  <p className="text-xs text-muted-foreground">
                    {t('newOrder.selectedCustomer')}
                  </p>
                  <p className="font-medium">{selected.name}</p>
                  <p className="text-sm text-muted-foreground">{selected.mobile}</p>
                </div>
                <Button variant="outline" size="sm" onClick={() => setSelected(null)}>
                  {t('newOrder.changeCustomer')}
                </Button>
              </div>
            ) : (
              <>
                <div className="relative">
                  <SearchIcon className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    className="pl-9"
                    placeholder={t('newOrder.searchCustomer')}
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>

                {search.trim().length >= 2 && (
                  <div className="space-y-1">
                    {(results ?? []).map((c) => (
                      <button
                        key={c._id}
                        type="button"
                        onClick={() =>
                          setSelected({ _id: c._id, name: c.name, mobile: c.mobile })
                        }
                        className="flex w-full items-center justify-between rounded-lg border border-border bg-card p-3 text-left hover:border-gold"
                      >
                        <span className="font-medium">{c.name}</span>
                        <span className="text-sm text-muted-foreground">
                          {c.mobile}
                        </span>
                      </button>
                    ))}
                    {results && results.length === 0 && (
                      <p className="text-sm text-muted-foreground">
                        {t('newOrder.noMatches')}
                      </p>
                    )}
                  </div>
                )}

                {showNewForm ? (
                  <div className="space-y-3 rounded-lg border border-border p-4">
                    <p className="section-label">{t('newOrder.addNewCustomer')}</p>
                    <div className="grid gap-3 sm:grid-cols-2">
                      <div>
                        <Label htmlFor="ncn">{t('common.name')}</Label>
                        <Input
                          id="ncn"
                          className="mt-1.5"
                          value={nc.name}
                          onChange={(e) => setNc({ ...nc, name: e.target.value })}
                        />
                      </div>
                      <div>
                        <Label htmlFor="ncm">{t('common.mobile')}</Label>
                        <Input
                          id="ncm"
                          inputMode="numeric"
                          className="mt-1.5"
                          value={nc.mobile}
                          onChange={(e) => setNc({ ...nc, mobile: e.target.value })}
                        />
                      </div>
                      <div className="sm:col-span-2">
                        <Label htmlFor="nca">
                          {t('common.address')}{' '}
                          <span className="text-muted-foreground">
                            ({t('common.optional')})
                          </span>
                        </Label>
                        <Input
                          id="nca"
                          className="mt-1.5"
                          value={nc.address}
                          onChange={(e) => setNc({ ...nc, address: e.target.value })}
                        />
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={saveCustomer}
                        disabled={
                          savingCustomer || !nc.name.trim() || nc.mobile.trim().length < 10
                        }
                      >
                        {savingCustomer ? t('common.saving') : t('newOrder.saveCustomer')}
                      </Button>
                      <Button
                        variant="ghost"
                        onClick={() => setShowNewForm(false)}
                      >
                        {t('common.cancel')}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <Button variant="outline" onClick={() => setShowNewForm(true)}>
                    <UserPlusIcon className="size-4" />
                    {t('newOrder.addNewCustomer')}
                  </Button>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 2 */}
      {step === 2 && (
        <Card>
          <CardContent className="space-y-4 pt-6">
            <h2 className="font-serif text-lg font-semibold">
              {t('newOrder.step2Title')}
            </h2>

            {items.length === 0 && (
              <p className="text-sm text-muted-foreground">{t('newOrder.noItems')}</p>
            )}

            <div className="space-y-3">
              {items.map((it) => (
                <div
                  key={it.key}
                  className="rounded-lg border border-border p-4"
                >
                  <div className="flex items-start gap-2">
                    <Select
                      value={it.serviceId || undefined}
                      onValueChange={(v) =>
                        updateItemService(it.key, v as Id<'services'>)
                      }
                    >
                      <SelectTrigger className="flex-1">
                        <SelectValue placeholder={t('newOrder.addService')} />
                      </SelectTrigger>
                      <SelectContent>
                        {(services ?? []).map((s) => (
                          <SelectItem key={s._id} value={s._id}>
                            {localized(s, 'name')}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() =>
                        setItems((prev) => prev.filter((x) => x.key !== it.key))
                      }
                    >
                      <Trash2Icon className="size-4" />
                    </Button>
                  </div>

                  <div className="mt-3 grid gap-3 sm:grid-cols-3">
                    <div>
                      <Label className="text-xs">
                        {t('newOrder.stitchingPrice')}
                      </Label>
                      <Input
                        type="number"
                        min={0}
                        className="mt-1"
                        value={it.stitchingPrice}
                        onChange={(e) =>
                          setItems((prev) =>
                            prev.map((x) =>
                              x.key === it.key
                                ? { ...x, stitchingPrice: Number(e.target.value) || 0 }
                                : x,
                            ),
                          )
                        }
                      />
                    </div>
                    <div>
                      <Label className="text-xs">
                        {t('newOrder.materialPrice')}
                      </Label>
                      <Input
                        type="number"
                        min={0}
                        className="mt-1"
                        disabled={!shopCloth}
                        value={it.materialPrice}
                        onChange={(e) =>
                          setItems((prev) =>
                            prev.map((x) =>
                              x.key === it.key
                                ? { ...x, materialPrice: Number(e.target.value) || 0 }
                                : x,
                            ),
                          )
                        }
                      />
                    </div>
                    <div>
                      <Label className="text-xs">{t('common.quantity')}</Label>
                      <Input
                        type="number"
                        min={1}
                        className="mt-1"
                        value={it.quantity}
                        onChange={(e) =>
                          setItems((prev) =>
                            prev.map((x) =>
                              x.key === it.key
                                ? {
                                    ...x,
                                    quantity: Math.max(1, Number(e.target.value) || 1),
                                  }
                                : x,
                            ),
                          )
                        }
                      />
                    </div>
                  </div>
                  <p className="mt-2 text-right text-sm text-muted-foreground">
                    {t('newOrder.lineTotal')}:{' '}
                    <span className="font-medium text-foreground">
                      {formatCurrency(
                        (it.stitchingPrice + (shopCloth ? it.materialPrice : 0)) *
                          it.quantity,
                      )}
                    </span>
                  </p>
                </div>
              ))}
            </div>

            {!shopCloth && items.length > 0 && (
              <p className="text-xs text-muted-foreground">
                {t('newOrder.materialNoteCustomer')}
              </p>
            )}

            <Button
              variant="outline"
              onClick={addItem}
              disabled={!services || services.length === 0}
            >
              <PlusIcon className="size-4" />
              {t('newOrder.addService')}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Step 3 */}
      {step === 3 && (
        <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <h2 className="font-serif text-lg font-semibold">
                {t('newOrder.step3Title')}
              </h2>

              <div>
                <Label>{t('newOrder.fabricSource')}</Label>
                <Select
                  value={fabricSource}
                  onValueChange={(v) => setFabricSource(v as FabricSource)}
                >
                  <SelectTrigger className="mt-1.5">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="customer">{t('fabric.customer')}</SelectItem>
                    <SelectItem value="shop">{t('fabric.shop')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>{t('newOrder.priority')}</Label>
                  <Select
                    value={priority}
                    onValueChange={(v) => setPriority(v as 'normal' | 'urgent')}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="normal">{t('priority.normal')}</SelectItem>
                      <SelectItem value="urgent">{t('priority.urgent')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>{t('newOrder.fitting')}</Label>
                  <Select
                    value={fitting || undefined}
                    onValueChange={(v) => setFitting(v as FittingPreference)}
                  >
                    <SelectTrigger className="mt-1.5">
                      <SelectValue placeholder={t('common.none')} />
                    </SelectTrigger>
                    <SelectContent>
                      {FITTING_PREFERENCES.map((f) => (
                        <SelectItem key={f} value={f}>
                          {t(`fitting.${f}`)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="pd">{t('newOrder.promisedDate')}</Label>
                <Input
                  id="pd"
                  type="date"
                  className="mt-1.5"
                  value={promisedDate}
                  onChange={(e) => setPromisedDate(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="on">{t('newOrder.orderNotes')}</Label>
                <Textarea
                  id="on"
                  rows={3}
                  className="mt-1.5"
                  placeholder={t('newOrder.notesPlaceholder')}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          <Card className="h-fit">
            <CardContent className="space-y-3 pt-6 text-sm">
              <p className="section-label">{t('newOrder.summary')}</p>
              <div className="flex justify-between">
                <span className="text-muted-foreground">{selected?.name}</span>
                <span>{selected?.mobile}</span>
              </div>
              <ul className="space-y-1 border-y border-border py-2">
                {items.map((it) => (
                  <li key={it.key} className="flex justify-between">
                    <span className="truncate">
                      {it.serviceName} × {it.quantity}
                    </span>
                    <span>
                      {formatCurrency(
                        (it.stitchingPrice + (shopCloth ? it.materialPrice : 0)) *
                          it.quantity,
                      )}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="flex justify-between text-muted-foreground">
                <span>{t('newOrder.lineTotal')} ({t('receipt.stitching')})</span>
                <span>{formatCurrency(totals.stitching)}</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>{t('receipt.material')}</span>
                <span>{formatCurrency(totals.material)}</span>
              </div>
              <div className="flex justify-between font-semibold">
                <span>{t('receipt.grandTotal')}</span>
                <span>{formatCurrency(totals.grand)}</span>
              </div>
              <div className="rounded-lg bg-gold/10 p-3">
                <p className="text-xs text-muted-foreground">
                  {shopCloth
                    ? t('newOrder.advanceRule100')
                    : t('newOrder.advanceRule50')}
                </p>
                <p className="mt-1 flex justify-between font-medium">
                  <span>{t('newOrder.advanceDue')}</span>
                  <span>{formatCurrency(totals.advance)}</span>
                </p>
              </div>
              <Button
                variant="gold"
                className="w-full"
                onClick={submit}
                disabled={creating}
              >
                {creating ? t('newOrder.creating') : t('newOrder.createOrder')}
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Wizard nav */}
      <div className="mt-6 flex justify-between">
        <Button
          variant="ghost"
          onClick={() => (step === 1 ? navigate('/admin/orders') : setStep(step - 1))}
        >
          <ArrowLeftIcon className="size-4" />
          {t('common.back')}
        </Button>
        {step < 3 && (
          <Button onClick={() => setStep(step + 1)} disabled={!canNext}>
            {t('common.next')}
            <ArrowRightIcon className="size-4" />
          </Button>
        )}
      </div>
    </>
  )
}
