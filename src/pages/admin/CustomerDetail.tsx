import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery } from 'convex/react'
import { ArrowLeftIcon, PencilIcon } from 'lucide-react'
import { api } from '@convex/api'
import type { Id } from '@convex/dataModel'
import { PageHeader } from '@/components/admin/PageHeader'
import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useI18n } from '@/i18n'
import { initials, formatCurrency, formatDate } from '@/lib/format'
import {
  MEASUREMENT_FIELDS,
  FITTING_PREFERENCES,
  type FittingPreference,
} from '@/lib/constants'
import { toast } from 'sonner'

export default function CustomerDetail() {
  const { t } = useI18n()
  const { customerId } = useParams<{ customerId: string }>()
  const id = customerId as Id<'customers'>

  const data = useQuery(api.customers.get, customerId ? { id } : 'skip')
  const orders = useQuery(
    api.customers.orderHistory,
    customerId ? { id } : 'skip',
  )
  const updateCustomer = useMutation(api.customers.update)
  const saveVersion = useMutation(api.measurements.saveVersion)

  const [editProfile, setEditProfile] = useState(false)
  const [profile, setProfile] = useState({
    name: '',
    mobile: '',
    address: '',
    fittingPreference: '' as FittingPreference | '',
  })

  const [editMeasure, setEditMeasure] = useState(false)
  const [values, setValues] = useState<Record<string, string>>({})
  const [measureNote, setMeasureNote] = useState('')
  const [savingMeasure, setSavingMeasure] = useState(false)

  useEffect(() => {
    if (data?.customer) {
      setProfile({
        name: data.customer.name,
        mobile: data.customer.mobile,
        address: data.customer.address ?? '',
        fittingPreference: data.customer.fittingPreference ?? '',
      })
    }
  }, [data?.customer])

  useEffect(() => {
    const current = data?.currentVersion?.values ?? {}
    setValues(
      Object.fromEntries(
        MEASUREMENT_FIELDS.map((f) => [
          f.key,
          current[f.key] != null ? String(current[f.key]) : '',
        ]),
      ),
    )
  }, [data?.currentVersion])

  if (data === undefined) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }
  if (data === null || !data.customer) {
    return (
      <Card className="p-10 text-center">
        <p className="text-sm text-muted-foreground">{t('customers.empty')}</p>
      </Card>
    )
  }

  const c = data.customer

  async function saveProfile() {
    try {
      await updateCustomer({
        id,
        name: profile.name,
        mobile: profile.mobile,
        address: profile.address,
        fittingPreference: profile.fittingPreference || undefined,
      })
      toast.success(t('customerDetail.profileSaved'))
      setEditProfile(false)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    }
  }

  async function saveMeasurements() {
    setSavingMeasure(true)
    try {
      const numeric: Record<string, number> = {}
      for (const [k, v] of Object.entries(values)) {
        const n = Number(v)
        if (v !== '' && !Number.isNaN(n) && n > 0) numeric[k] = n
      }
      await saveVersion({
        customerId: id,
        values: numeric,
        notes: measureNote || undefined,
      })
      toast.success(t('customerDetail.measurementsSaved'))
      setEditMeasure(false)
      setMeasureNote('')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    } finally {
      setSavingMeasure(false)
    }
  }

  const groups = [
    { key: 'upper' as const, label: t('customerDetail.upperBody') },
    { key: 'lower' as const, label: t('customerDetail.lowerBody') },
  ]

  return (
    <>
      <PageHeader
        title={c.name}
        subtitle={c.mobile}
        actions={
          <Button asChild variant="ghost" size="sm">
            <Link to="/admin/customers">
              <ArrowLeftIcon className="size-4" />
              {t('customerDetail.back')}
            </Link>
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[20rem_1fr]">
        {/* Profile */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle>{t('customerDetail.profile')}</CardTitle>
              {!editProfile && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setEditProfile(true)}
                >
                  <PencilIcon className="size-4" />
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {editProfile ? (
                <div className="space-y-3">
                  <div>
                    <Label>{t('common.name')}</Label>
                    <Input
                      className="mt-1"
                      value={profile.name}
                      onChange={(e) =>
                        setProfile({ ...profile, name: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <Label>{t('common.mobile')}</Label>
                    <Input
                      className="mt-1"
                      value={profile.mobile}
                      onChange={(e) =>
                        setProfile({ ...profile, mobile: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <Label>{t('common.address')}</Label>
                    <Textarea
                      className="mt-1"
                      rows={2}
                      value={profile.address}
                      onChange={(e) =>
                        setProfile({ ...profile, address: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <Label>{t('fitting.label')}</Label>
                    <Select
                      value={profile.fittingPreference || undefined}
                      onValueChange={(v) =>
                        setProfile({
                          ...profile,
                          fittingPreference: v as FittingPreference,
                        })
                      }
                    >
                      <SelectTrigger className="mt-1">
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
                  <div className="flex gap-2">
                    <Button size="sm" onClick={saveProfile}>
                      {t('common.save')}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setEditProfile(false)}
                    >
                      {t('common.cancel')}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-3">
                    <Avatar className="size-12">
                      <AvatarFallback>{initials(c.name)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium">{c.name}</p>
                      <p className="text-muted-foreground">{c.mobile}</p>
                    </div>
                  </div>
                  {c.address && (
                    <p className="text-muted-foreground">{c.address}</p>
                  )}
                  <p>
                    <span className="text-muted-foreground">
                      {t('fitting.label')}:{' '}
                    </span>
                    {c.fittingPreference
                      ? t(`fitting.${c.fittingPreference}`)
                      : '—'}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Measurement history */}
          <Card>
            <CardHeader>
              <CardTitle>{t('customerDetail.measurementHistory')}</CardTitle>
            </CardHeader>
            <CardContent>
              {data.versions.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  {t('customerDetail.noMeasurements')}
                </p>
              ) : (
                <ul className="space-y-2 text-sm">
                  {data.versions.map((v) => (
                    <li
                      key={v._id}
                      className="rounded-lg border border-border p-3"
                    >
                      <div className="flex items-center justify-between">
                        <Badge
                          variant={
                            v._id === data.currentVersion?._id ? 'gold' : 'outline'
                          }
                        >
                          {v._id === data.currentVersion?._id
                            ? t('customerDetail.currentVersion', { n: v.version })
                            : t('customerDetail.version', { n: v.version })}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatDate(v._creationTime)}
                        </span>
                      </div>
                      {v.notes && (
                        <p className="mt-1.5 text-xs text-muted-foreground">
                          {v.notes}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Measurements + orders */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle>{t('customerDetail.measurements')}</CardTitle>
              {!editMeasure ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setEditMeasure(true)}
                >
                  <PencilIcon className="size-4" />
                  {t('customerDetail.editMeasurements')}
                </Button>
              ) : (
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={saveMeasurements}
                    disabled={savingMeasure}
                  >
                    {savingMeasure
                      ? t('common.saving')
                      : t('customerDetail.saveMeasurements')}
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setEditMeasure(false)}
                  >
                    {t('common.cancel')}
                  </Button>
                </div>
              )}
            </CardHeader>
            <CardContent className="space-y-6">
              {data.currentVersion == null && !editMeasure && (
                <p className="text-sm text-muted-foreground">
                  {t('customerDetail.noMeasurements')}
                </p>
              )}
              {(data.currentVersion != null || editMeasure) &&
                groups.map((g) => (
                  <div key={g.key}>
                    <p className="section-label mb-3">{g.label}</p>
                    <div className="grid gap-x-6 gap-y-3 sm:grid-cols-2">
                      {MEASUREMENT_FIELDS.filter((f) => f.group === g.key).map(
                        (f) => (
                          <div
                            key={f.key}
                            className="flex items-center justify-between gap-3"
                          >
                            <Label className="text-sm text-muted-foreground">
                              {f.en}
                            </Label>
                            {editMeasure ? (
                              <Input
                                type="number"
                                className="h-8 w-24"
                                value={values[f.key] ?? ''}
                                onChange={(e) =>
                                  setValues((prev) => ({
                                    ...prev,
                                    [f.key]: e.target.value,
                                  }))
                                }
                              />
                            ) : (
                              <span className="text-sm font-medium">
                                {data.currentVersion?.values[f.key] != null
                                  ? `${data.currentVersion.values[f.key]} ${t('customerDetail.cm')}`
                                  : '—'}
                              </span>
                            )}
                          </div>
                        ),
                      )}
                    </div>
                  </div>
                ))}

              {editMeasure && (
                <div>
                  <Label>{t('customerDetail.measurementNote')}</Label>
                  <Textarea
                    className="mt-1"
                    rows={2}
                    value={measureNote}
                    onChange={(e) => setMeasureNote(e.target.value)}
                  />
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t('customerDetail.orderHistory')}</CardTitle>
            </CardHeader>
            <CardContent>
              {orders === undefined ? (
                <Skeleton className="h-24 w-full" />
              ) : orders.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  {t('customerDetail.noOrderHistory')}
                </p>
              ) : (
                <ul className="divide-y divide-border">
                  {orders.map((o) => (
                    <li key={o._id}>
                      <Link
                        to={`/admin/orders/${o._id}`}
                        className="flex items-center justify-between gap-3 py-3 hover:opacity-80"
                      >
                        <div>
                          <p className="font-mono text-sm font-medium">
                            {o.orderNumber}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {formatDate(o._creationTime)}
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-sm">
                            {formatCurrency(o.grandTotal)}
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
        </div>
      </div>
    </>
  )
}
