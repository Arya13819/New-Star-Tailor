import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'

export function LanguageSwitcher({ className }: { className?: string }) {
  const { lang, setLang } = useI18n()
  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full border border-border bg-card p-0.5 text-xs font-medium',
        className,
      )}
      role="group"
      aria-label="Language"
    >
      <button
        type="button"
        onClick={() => setLang('en')}
        className={cn(
          'rounded-full px-2.5 py-1 transition-colors',
          lang === 'en'
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:text-foreground',
        )}
      >
        EN
      </button>
      <button
        type="button"
        onClick={() => setLang('hi')}
        className={cn(
          'rounded-full px-2.5 py-1 transition-colors',
          lang === 'hi'
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:text-foreground',
        )}
      >
        हिन्दी
      </button>
    </div>
  )
}
