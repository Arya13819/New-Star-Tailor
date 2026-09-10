import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { MenuIcon, XIcon } from 'lucide-react'
import { Logo } from '@/components/Logo'
import { LanguageSwitcher } from '@/components/LanguageSwitcher'
import { ThemeToggle } from '@/components/ThemeToggle'
import { Button } from '@/components/ui/button'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'

export function PublicHeader() {
  const { t } = useI18n()
  const [open, setOpen] = useState(false)

  const links = [
    { to: '/', label: t('nav.home'), end: true },
    { to: '/services', label: t('nav.services') },
    { to: '/track-order', label: t('nav.trackOrder') },
    { to: '/enquiry', label: t('nav.enquiry') },
  ]

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/85 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link to="/" onClick={() => setOpen(false)}>
          <Logo />
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) =>
                cn(
                  'rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'text-foreground'
                    : 'text-muted-foreground hover:text-foreground',
                )
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <LanguageSwitcher />
          <ThemeToggle />
          <Button asChild size="sm" variant="gold">
            <Link to="/enquiry">{t('nav.enquiry')}</Link>
          </Button>
        </div>

        <button
          type="button"
          className="inline-flex size-9 items-center justify-center rounded-md text-foreground md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Menu"
        >
          {open ? <XIcon className="size-5" /> : <MenuIcon className="size-5" />}
        </button>
      </div>

      {open && (
        <div className="border-t border-border bg-background md:hidden">
          <nav className="mx-auto flex max-w-6xl flex-col px-4 py-2">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  cn(
                    'rounded-md px-3 py-2.5 text-sm font-medium',
                    isActive
                      ? 'bg-secondary text-foreground'
                      : 'text-muted-foreground',
                  )
                }
              >
                {l.label}
              </NavLink>
            ))}
            <div className="flex items-center justify-between px-3 py-3">
              <LanguageSwitcher />
              <ThemeToggle />
            </div>
          </nav>
        </div>
      )}
    </header>
  )
}
