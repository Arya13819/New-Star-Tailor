import { useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useConvexAuth } from 'convex/react'
import { useAuthActions } from '@convex-dev/auth/react'
import { ArrowLeftIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Logo } from '@/components/Logo'
import { LanguageSwitcher } from '@/components/LanguageSwitcher'
import { useI18n } from '@/i18n'

export default function AuthPage() {
  const { t } = useI18n()
  const { isAuthenticated } = useConvexAuth()
  const { signIn } = useAuthActions()
  const location = useLocation()
  const from = (location.state as { from?: string } | null)?.from ?? '/admin/dashboard'

  const [step, setStep] = useState<'email' | 'code'>('email')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (isAuthenticated) return <Navigate to={from} replace />

  async function sendCode(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await signIn('resend-otp', { email })
      setStep('code')
    } catch {
      setError(t('common.somethingWrong'))
    } finally {
      setBusy(false)
    }
  }

  async function verify(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await signIn('resend-otp', { email, code })
      // On success, isAuthenticated flips and the Navigate above redirects.
    } catch {
      setError(t('auth.invalidCode'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex min-h-dvh flex-col gradient-hero">
      <div className="flex items-center justify-between p-4">
        <a href="/">
          <Logo />
        </a>
        <LanguageSwitcher />
      </div>

      <div className="flex flex-1 items-center justify-center px-4 pb-16">
        <div className="w-full max-w-sm rounded-xl border border-border bg-card p-8 shadow-warm">
          <h1 className="font-serif text-xl font-semibold">{t('auth.title')}</h1>
          <p className="mt-1.5 text-sm text-muted-foreground">
            {step === 'email'
              ? t('auth.subtitle')
              : t('auth.codeSent', { email })}
          </p>

          {step === 'email' ? (
            <form className="mt-6 space-y-4" onSubmit={sendCode}>
              <div>
                <Label htmlFor="email">{t('auth.emailLabel')}</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  className="mt-1.5"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={busy}>
                {busy ? t('common.loading') : t('auth.sendCode')}
              </Button>
            </form>
          ) : (
            <form className="mt-6 space-y-4" onSubmit={verify}>
              <div>
                <Label htmlFor="code">{t('auth.codeLabel')}</Label>
                <Input
                  id="code"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  className="mt-1.5 text-center text-lg tracking-[0.4em]"
                  maxLength={6}
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                  required
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={busy || code.length < 6}>
                {busy ? t('common.loading') : t('auth.verify')}
              </Button>
              <div className="flex items-center justify-between text-xs">
                <button
                  type="button"
                  className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground"
                  onClick={() => {
                    setStep('email')
                    setCode('')
                    setError(null)
                  }}
                >
                  <ArrowLeftIcon className="size-3" />
                  {t('auth.useDifferentEmail')}
                </button>
                <button
                  type="button"
                  className="text-muted-foreground hover:text-foreground"
                  onClick={() => void signIn('resend-otp', { email })}
                >
                  {t('auth.resend')}
                </button>
              </div>
            </form>
          )}

          <p className="mt-6 border-t border-border pt-4 text-xs text-muted-foreground">
            {t('auth.devHint')}
          </p>
        </div>
      </div>
    </div>
  )
}
