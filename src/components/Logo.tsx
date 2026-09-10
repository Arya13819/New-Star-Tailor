import { cn } from '@/lib/utils'
import { useI18n } from '@/i18n'

export function Logo({
  className,
  showText = true,
  tone = 'navy',
}: {
  className?: string
  showText?: boolean
  tone?: 'navy' | 'light'
}) {
  const { t } = useI18n()
  return (
    <span className={cn('inline-flex items-center gap-2.5', className)}>
      <svg
        viewBox="0 0 64 64"
        className="size-8 shrink-0"
        aria-hidden="true"
      >
        <rect
          width="64"
          height="64"
          rx="14"
          className={tone === 'light' ? 'fill-white/10' : 'fill-primary'}
        />
        <path
          d="M32 12l4.6 9.3 10.3 1.5-7.4 7.3 1.7 10.2L32 45.6l-9.2 4.7 1.7-10.2-7.4-7.3 10.3-1.5z"
          className="fill-gold"
        />
        <circle
          cx="32"
          cy="32"
          r="3"
          className={tone === 'light' ? 'fill-navy' : 'fill-primary'}
        />
      </svg>
      {showText && (
        <span
          className={cn(
            'font-serif text-base leading-tight font-semibold tracking-tight',
            tone === 'light' ? 'text-white' : 'text-foreground',
          )}
        >
          {t('common.appName')}
        </span>
      )}
    </span>
  )
}
