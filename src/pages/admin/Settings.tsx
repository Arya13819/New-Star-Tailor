import { useEffect, useState } from 'react'
import { useMutation, useQuery } from 'convex/react'
import { DatabaseIcon, Trash2Icon } from 'lucide-react'
import { api } from '@convex/api'
import type { Id } from '@convex/dataModel'
import { PageHeader } from '@/components/admin/PageHeader'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useI18n, useLocalized } from '@/i18n'
import { toast } from 'sonner'

export default function Settings() {
  const { t } = useI18n()
  const localized = useLocalized()

  const settings = useQuery(api.settings.all, {})
  const services = useQuery(api.services.list, { includeInactive: true })
  const staff = useQuery(api.users.listStaff, {})
  const me = useQuery(api.users.me, {})

  const updateShop = useMutation(api.settings.updateShop)
  const updateService = useMutation(api.services.update)
  const setRole = useMutation(api.users.setRole)
  const loadDemo = useMutation(api.seed.loadDemoData)
  const clearAll = useMutation(api.seed.clearAll)

  const [shop, setShop] = useState({
    name: '',
    tagline: '',
    phone: '',
    whatsapp: '',
    address: '',
    hours: '',
    email: '',
    gstin: '',
  })
  const [savingShop, setSavingShop] = useState(false)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (settings?.shop) {
      setShop({
        name: settings.shop.name ?? '',
        tagline: settings.shop.tagline ?? '',
        phone: settings.shop.phone ?? '',
        whatsapp: settings.shop.whatsapp ?? '',
        address: settings.shop.address ?? '',
        hours: settings.shop.hours ?? '',
        email: settings.shop.email ?? '',
        gstin: settings.shop.gstin ?? '',
      })
    }
  }, [settings?.shop])

  async function saveShop() {
    setSavingShop(true)
    try {
      await updateShop(shop)
      toast.success(t('settings.shopSaved'))
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    } finally {
      setSavingShop(false)
    }
  }

  const shopFields: Array<{ key: keyof typeof shop; label: string }> = [
    { key: 'name', label: t('settings.shopName') },
    { key: 'tagline', label: t('settings.tagline') },
    { key: 'phone', label: t('settings.phone') },
    { key: 'whatsapp', label: t('settings.whatsapp') },
    { key: 'address', label: t('settings.address') },
    { key: 'hours', label: t('settings.hours') },
    { key: 'email', label: t('settings.email') },
    { key: 'gstin', label: t('settings.gstin') },
  ]

  return (
    <>
      <PageHeader title={t('settings.title')} />

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Shop info */}
        <Card>
          <CardHeader>
            <CardTitle>{t('settings.shopInfo')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {settings === undefined ? (
              <Skeleton className="h-64 w-full" />
            ) : (
              <>
                {shopFields.map((f) => (
                  <div key={f.key}>
                    <Label htmlFor={f.key}>{f.label}</Label>
                    <Input
                      id={f.key}
                      className="mt-1"
                      value={shop[f.key]}
                      onChange={(e) =>
                        setShop({ ...shop, [f.key]: e.target.value })
                      }
                    />
                  </div>
                ))}
                <Button onClick={saveShop} disabled={savingShop}>
                  {savingShop ? t('common.saving') : t('settings.saveShop')}
                </Button>
              </>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          {/* Demo data */}
          <Card>
            <CardHeader>
              <CardTitle>{t('settings.demoData')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                {t('settings.demoDataHint')}
              </p>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="gold"
                  disabled={busy}
                  onClick={async () => {
                    setBusy(true)
                    try {
                      const res = await loadDemo({})
                      toast[res.ok ? 'success' : 'error'](res.message)
                    } finally {
                      setBusy(false)
                    }
                  }}
                >
                  <DatabaseIcon className="size-4" />
                  {t('settings.loadDemoData')}
                </Button>
                <Button
                  variant="outline"
                  disabled={busy}
                  className="text-destructive"
                  onClick={async () => {
                    if (!window.confirm(t('settings.clearDataConfirm'))) return
                    setBusy(true)
                    try {
                      const res = await clearAll({})
                      toast.success(res.message)
                    } finally {
                      setBusy(false)
                    }
                  }}
                >
                  <Trash2Icon className="size-4" />
                  {t('settings.clearData')}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Staff */}
          <Card>
            <CardHeader>
              <CardTitle>{t('settings.staff')}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-muted-foreground">
                {t('settings.staffHint')}
              </p>
              {staff === undefined ? (
                <Skeleton className="h-24 w-full" />
              ) : (
                <ul className="space-y-2">
                  {staff.map((u) => (
                    <li
                      key={u._id}
                      className="flex items-center justify-between gap-2 rounded-lg border border-border p-3 text-sm"
                    >
                      <div className="min-w-0">
                        <p className="truncate font-medium">
                          {u.name || u.email || u._id}
                        </p>
                        {u.email && u.name && (
                          <p className="truncate text-xs text-muted-foreground">
                            {u.email}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={u.role === 'admin' ? 'gold' : 'outline'}
                        >
                          {u.role === 'admin'
                            ? t('settings.roleAdmin')
                            : t('settings.roleCustomer')}
                        </Badge>
                        {u._id !== me?._id && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              setRole({
                                userId: u._id as Id<'users'>,
                                role: u.role === 'admin' ? 'customer' : 'admin',
                              })
                            }
                          >
                            {u.role === 'admin'
                              ? t('settings.removeAdmin')
                              : t('settings.makeAdmin')}
                          </Button>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Service prices */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>{t('settings.servicePrices')}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-muted-foreground">
              {t('settings.servicePricesHint')}
            </p>
            {services === undefined ? (
              <Skeleton className="h-64 w-full" />
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {services.map((s) => (
                  <div
                    key={s._id}
                    className="flex items-center justify-between gap-3 rounded-lg border border-border p-3"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">
                        {localized(s, 'name')}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {t(`category.${s.category}`)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="relative">
                        <span className="absolute top-1/2 left-2 -translate-y-1/2 text-xs text-muted-foreground">
                          ₹
                        </span>
                        <Input
                          type="number"
                          className="h-8 w-24 pl-5 text-right"
                          defaultValue={s.defaultStitchingPrice}
                          onBlur={(e) => {
                            const val = Number(e.target.value)
                            if (val >= 0 && val !== s.defaultStitchingPrice) {
                              updateService({
                                id: s._id,
                                defaultStitchingPrice: val,
                              }).then(() => toast.success(t('settings.priceUpdated')))
                            }
                          }}
                        />
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() =>
                          updateService({ id: s._id, active: !s.active })
                        }
                      >
                        {s.active
                          ? t('settings.active')
                          : t('settings.inactive')}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {settings && (
        <p className="mt-6 text-center text-xs text-muted-foreground">
          {t('common.appName')} · last order number NST-
          {String(settings.orderSeq).padStart(6, '0')}
        </p>
      )}
    </>
  )
}
