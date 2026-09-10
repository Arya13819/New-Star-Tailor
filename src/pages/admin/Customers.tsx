import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery } from 'convex/react'
import { SearchIcon, UserPlusIcon } from 'lucide-react'
import { api } from '@convex/api'
import { PageHeader } from '@/components/admin/PageHeader'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from '@/components/ui/dialog'
import { useI18n } from '@/i18n'
import { initials, relativeDay } from '@/lib/format'
import { toast } from 'sonner'

export default function Customers() {
  const { t } = useI18n()
  const [search, setSearch] = useState('')
  const customers = useQuery(api.customers.list, {
    search: search.trim() || undefined,
  })
  const create = useMutation(api.customers.create)

  const [form, setForm] = useState({ name: '', mobile: '', address: '' })
  const [saving, setSaving] = useState(false)
  const [open, setOpen] = useState(false)

  async function submit() {
    setSaving(true)
    try {
      await create({
        name: form.name,
        mobile: form.mobile,
        address: form.address || undefined,
      })
      toast.success(t('customers.created'))
      setForm({ name: '', mobile: '', address: '' })
      setOpen(false)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t('common.somethingWrong'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader
        title={t('customers.title')}
        actions={
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button variant="gold" size="sm">
                <UserPlusIcon className="size-4" />
                {t('customers.addCustomer')}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t('customers.newCustomerTitle')}</DialogTitle>
              </DialogHeader>
              <div className="space-y-3">
                <div>
                  <Label htmlFor="cn">{t('common.name')}</Label>
                  <Input
                    id="cn"
                    className="mt-1"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="cm">{t('common.mobile')}</Label>
                  <Input
                    id="cm"
                    inputMode="numeric"
                    className="mt-1"
                    value={form.mobile}
                    onChange={(e) => setForm({ ...form, mobile: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="ca">
                    {t('common.address')}{' '}
                    <span className="text-muted-foreground">
                      ({t('common.optional')})
                    </span>
                  </Label>
                  <Input
                    id="ca"
                    className="mt-1"
                    value={form.address}
                    onChange={(e) => setForm({ ...form, address: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="ghost">{t('common.cancel')}</Button>
                </DialogClose>
                <Button
                  onClick={submit}
                  disabled={
                    saving || !form.name.trim() || form.mobile.trim().length < 10
                  }
                >
                  {saving ? t('common.saving') : t('newOrder.saveCustomer')}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      <div className="relative mb-4 sm:w-80">
        <SearchIcon className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder={t('customers.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {customers === undefined ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : customers.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-sm text-muted-foreground">{t('customers.empty')}</p>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {customers.map((c) => (
            <Link
              key={c._id}
              to={`/admin/customers/${c._id}`}
              className="hover-gold flex items-center gap-3 rounded-xl border border-border bg-card p-4 shadow-warm"
            >
              <Avatar>
                <AvatarFallback>{initials(c.name)}</AvatarFallback>
              </Avatar>
              <div className="min-w-0">
                <p className="truncate font-medium">{c.name}</p>
                <p className="text-sm text-muted-foreground">{c.mobile}</p>
                <p className="text-xs text-muted-foreground">
                  {c.orderCount === 0
                    ? t('customers.noOrders')
                    : c.orderCount === 1
                      ? t('customers.oneOrder')
                      : t('customers.orders', { count: c.orderCount })}
                  {c.lastOrderAt
                    ? ` · ${t('customers.lastOrder', {
                        when: relativeDay(c.lastOrderAt),
                      })}`
                    : ''}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  )
}
