import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboardIcon,
  ScissorsIcon,
  UsersIcon,
  WalletIcon,
  BarChart3Icon,
  SettingsIcon,
  LogOutIcon,
  PlusIcon,
} from 'lucide-react'
import { useAuthActions } from '@convex-dev/auth/react'
import { Logo } from '@/components/Logo'
import { LanguageSwitcher } from '@/components/LanguageSwitcher'
import { ThemeToggle } from '@/components/ThemeToggle'
import { Button } from '@/components/ui/button'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'

export function AdminNav() {
  const { t } = useI18n()
  const navigate = useNavigate()
  const { signOut } = useAuthActions()

  const items = [
    { to: '/admin/dashboard', label: t('nav.dashboard'), icon: LayoutDashboardIcon },
    { to: '/admin/orders', label: t('nav.orders'), icon: ScissorsIcon },
    { to: '/admin/customers', label: t('nav.customers'), icon: UsersIcon },
    { to: '/admin/payments', label: t('nav.payments'), icon: WalletIcon },
    { to: '/admin/reports', label: t('nav.reports'), icon: BarChart3Icon },
    { to: '/admin/settings', label: t('nav.settings'), icon: SettingsIcon },
  ]

  async function handleSignOut() {
    await signOut()
    navigate('/auth')
  }

  return (
    <>
      {/* Desktop top bar */}
      <header className="sticky top-0 z-40 hidden border-b border-border bg-background/90 backdrop-blur md:block">
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-4">
          <NavLink to="/admin/dashboard">
            <Logo />
          </NavLink>
          <nav className="flex items-center gap-1">
            {items.map((it) => (
              <NavLink
                key={it.to}
                to={it.to}
                className={({ isActive }) =>
                  cn(
                    'inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-secondary text-foreground'
                      : 'text-muted-foreground hover:text-foreground',
                  )
                }
              >
                <it.icon className="size-4" />
                {it.label}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <Button asChild size="sm" variant="gold">
              <NavLink to="/admin/orders/new">
                <PlusIcon className="size-4" />
                {t('nav.newOrder')}
              </NavLink>
            </Button>
            <LanguageSwitcher />
            <ThemeToggle />
            <Button variant="ghost" size="icon" onClick={handleSignOut} aria-label={t('nav.signOut')}>
              <LogOutIcon className="size-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Mobile top bar */}
      <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-border bg-background/90 px-4 backdrop-blur md:hidden">
        <Logo />
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <ThemeToggle />
          <Button variant="ghost" size="icon" onClick={handleSignOut} aria-label={t('nav.signOut')}>
            <LogOutIcon className="size-4" />
          </Button>
        </div>
      </header>

      {/* Mobile bottom tabs */}
      <nav className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 border-t border-border bg-background/95 backdrop-blur md:hidden">
        {items.slice(0, 5).map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            className={({ isActive }) =>
              cn(
                'flex flex-col items-center gap-1 py-2 text-[11px] font-medium',
                isActive ? 'text-gold' : 'text-muted-foreground',
              )
            }
          >
            <it.icon className="size-5" />
            {it.label}
          </NavLink>
        ))}
      </nav>
    </>
  )
}
