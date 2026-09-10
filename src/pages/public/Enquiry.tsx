import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery } from 'convex/react'
import { CheckCircle2Icon, PlusIcon, Trash2Icon } from 'lucide-react'
import { api } from '@convex/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Section, SectionHeader } from '@/components/public/Section'
import { useI18n, useLocalized } from '@/i18n'
import { formatCurrency } from '@/lib/format'
import type { FabricSource } from '@/lib/constants'
import { toast } from 'sonner'

type Line = { serviceId: string; quantity: number }

export default function Enquiry() {
  const { t } = useI18n()
  const localized = useLocalized()
  const services = useQuery(api.services.list, {})
  const submit = useMutation(api.orders.submitOnline)

  const [name, setName] = useState('')
  const [mobile, setMobile] = useState('')
  const [address, setAddress] = useState('')
  const [message, setMessage] = useState('')

  const [lines, setLines] = useState<Line[]>([])
  const [fabric, setFabric] = useState<FabricSource>('customer')
  const [priority, setPriority] = useState<'normal' | 'urgent'>('normal')

  const [busy, setBusy] = useState(false)
  const [enquiryDone, setEnquiryDone] = useState(false)
  const [orderDone, setOrderDone] = useState<string | null>(null)

  const serviceMap = useMemo(
    () => new Map((services ?? []).map((s) => [s._id as string, s])),
    [services],
  )

  const estimate = lines.reduce((sum, l) => {
    const s = serviceMap.get(l.serviceId)
    return sum + (s ? s.defaultStitchingPrice * l.quantity : 0)
  }, 0)

  async function handleEnquiry(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    try {
      await submit({ name, mobile, address: address || undefined, message: message || undefined })
      setEnquiryDone(true)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    } finally {
      setBusy(false)
    }
  }

  async function handleOrder(e: React.FormEvent) {
    e.preventDefault()
    if (lines.length === 0) {
      toast.error(t('enquiry.addAtLeastOne'))
      return
    }
    setBusy(true)
    try {
      const items = lines.map((l) => {
        const s = serviceMap.get(l.serviceId)!
        return {
          serviceId: s._id,
          serviceName: s.name,
          category: s.category,
          stitchingPrice: s.defaultStitchingPrice,
          materialPrice: 0,
          quantity: l.quantity,
        }
      })
      const res = await submit({
        name,
        mobile,
        address: address || undefined,
        message: message || undefined,
        items,
        fabricSource: fabric,
        priority,
      })
      if (res.type === 'order') setOrderDone(res.orderNumber)
      else setEnquiryDone(true)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    } finally {
      setBusy(false)
    }
  }

  const detailFields = (
    <div className="grid gap-4 sm:grid-cols-2">
      <div>
        <Label htmlFor="n">{t('common.name')}</Label>
        <Input id="n" className="mt-1.5" value={name} onChange={(e) => setName(e.target.value)} required />
      </div>
      <div>
        <Label htmlFor="m">{t('common.mobile')}</Label>
        <Input
          id="m"
          className="mt-1.5"
          inputMode="numeric"
          value={mobile}
          onChange={(e) => setMobile(e.target.value)}
          required
        />
      </div>
      <div className="sm:col-span-2">
        <Label htmlFor="a">
          {t('common.address')}{' '}
          <span className="text-muted-foreground">({t('common.optional')})</span>
        </Label>
        <Input id="a" className="mt-1.5" value={address} onChange={(e) => setAddress(e.target.value)} />
      </div>
    </div>
  )

  if (orderDone) {
    return (
      <Section className="max-w-xl">
        <Card>
          <CardContent className="pt-8 pb-8 text-center">
            <CheckCircle2Icon className="mx-auto size-12 text-success" />
            <h2 className="mt-4 font-serif text-2xl font-semibold">
              {t('enquiry.orderPlaced')}
            </h2>
            <p className="mt-3 text-sm text-muted-foreground">
              {t('enquiry.orderPlacedBody', { number: orderDone })}
            </p>
            <div className="mt-4 rounded-lg bg-secondary p-4">
              <p className="font-serif text-2xl font-semibold tracking-wide">{orderDone}</p>
            </div>
            <Button asChild className="mt-6" variant="gold">
              <Link to="/track-order">{t('enquiry.trackThisOrder')}</Link>
            </Button>
          </CardContent>
        </Card>
      </Section>
    )
  }

  if (enquiryDone) {
    return (
      <Section className="max-w-xl">
        <Card>
          <CardContent className="pt-8 pb-8 text-center">
            <CheckCircle2Icon className="mx-auto size-12 text-success" />
            <p className="mt-4 text-sm text-muted-foreground">{t('enquiry.enquirySent')}</p>
            <Button asChild className="mt-6" variant="outline">
              <Link to="/">{t('nav.home')}</Link>
            </Button>
          </CardContent>
        </Card>
      </Section>
    )
  }

  return (
    <>
      <div className="gradient-hero">
        <Section className="py-14 md:py-16">
          <SectionHeader title={t('enquiry.title')} subtitle={t('enquiry.subtitle')} />
        </Section>
      </div>

      <Section className="max-w-2xl">
        <Tabs defaultValue="enquiry">
          <TabsList className="w-full">
            <TabsTrigger value="enquiry" className="flex-1">
              {t('enquiry.tabEnquiry')}
            </TabsTrigger>
            <TabsTrigger value="order" className="flex-1">
              {t('enquiry.tabOrder')}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="enquiry">
            <Card>
              <CardContent className="pt-6">
                <form className="space-y-5" onSubmit={handleEnquiry}>
                  <p className="section-label">{t('enquiry.yourDetails')}</p>
                  {detailFields}
                  <div>
                    <Label htmlFor="msg">{t('enquiry.messageLabel')}</Label>
                    <Textarea
                      id="msg"
                      className="mt-1.5"
                      rows={4}
                      placeholder={t('enquiry.messagePlaceholder')}
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                    />
                  </div>
                  <Button type="submit" disabled={busy}>
                    {busy ? t('common.saving') : t('enquiry.sendEnquiry')}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="order">
            <Card>
              <CardContent className="pt-6">
                <form className="space-y-5" onSubmit={handleOrder}>
                  <p className="section-label">{t('enquiry.yourDetails')}</p>
                  {detailFields}

                  <div>
                    <p className="section-label">{t('enquiry.pickServices')}</p>
                    <div className="mt-2 space-y-2">
                      {lines.map((line, idx) => (
                        <div key={idx} className="flex gap-2">
                          <Select
                            value={line.serviceId}
                            onValueChange={(val) =>
                              setLines((prev) =>
                                prev.map((l, i) => (i === idx ? { ...l, serviceId: val } : l)),
                              )
                            }
                          >
                            <SelectTrigger className="flex-1">
                              <SelectValue placeholder={t('enquiry.pickServices')} />
                            </SelectTrigger>
                            <SelectContent>
                              {(services ?? []).map((s) => (
                                <SelectItem key={s._id} value={s._id}>
                                  {localized(s, 'name')} — {formatCurrency(s.defaultStitchingPrice)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Input
                            type="number"
                            min={1}
                            className="w-20"
                            value={line.quantity}
                            onChange={(e) =>
                              setLines((prev) =>
                                prev.map((l, i) =>
                                  i === idx
                                    ? { ...l, quantity: Math.max(1, Number(e.target.value) || 1) }
                                    : l,
                                ),
                              )
                            }
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => setLines((prev) => prev.filter((_, i) => i !== idx))}
                          >
                            <Trash2Icon className="size-4" />
                          </Button>
                        </div>
                      ))}
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          setLines((prev) => [
                            ...prev,
                            { serviceId: services?.[0]?._id ?? '', quantity: 1 },
                          ])
                        }
                        disabled={!services || services.length === 0}
                      >
                        <PlusIcon className="size-4" />
                        {t('newOrder.addService')}
                      </Button>
                    </div>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <Label>{t('enquiry.fabricQuestion')}</Label>
                      <Select value={fabric} onValueChange={(v) => setFabric(v as FabricSource)}>
                        <SelectTrigger className="mt-1.5">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="customer">{t('fabric.customer')}</SelectItem>
                          <SelectItem value="shop">{t('fabric.shop')}</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>{t('enquiry.priorityQuestion')}</Label>
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
                  </div>

                  <div>
                    <Label htmlFor="omsg">
                      {t('enquiry.messageLabel')}{' '}
                      <span className="text-muted-foreground">({t('common.optional')})</span>
                    </Label>
                    <Textarea
                      id="omsg"
                      className="mt-1.5"
                      rows={3}
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                    />
                  </div>

                  {lines.length > 0 && (
                    <div className="flex items-center justify-between rounded-lg bg-secondary/60 p-4 text-sm">
                      <span className="text-muted-foreground">
                        {t('services.stitchingFrom')} ({t('services.materialSeparate')})
                      </span>
                      <span className="font-serif text-lg font-semibold">
                        {formatCurrency(estimate)}
                      </span>
                    </div>
                  )}

                  <Button type="submit" variant="gold" disabled={busy}>
                    {busy ? t('common.saving') : t('enquiry.placeOrder')}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </Section>
    </>
  )
}
