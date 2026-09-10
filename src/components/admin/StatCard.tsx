import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = 'default',
}: {
  label: string
  value: string | number
  hint?: string
  icon?: LucideIcon
  tone?: 'default' | 'gold' | 'success' | 'warning'
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-warm">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
          {label}
        </p>
        {Icon && (
          <span
            className={cn(
              'inline-flex size-8 items-center justify-center rounded-full',
              tone === 'gold' && 'bg-gold/12 text-gold',
              tone === 'success' && 'bg-success/12 text-success',
              tone === 'warning' && 'bg-warning/15 text-warning',
              tone === 'default' && 'bg-secondary text-muted-foreground',
            )}
          >
            <Icon className="size-4" />
          </span>
        )}
      </div>
      <p className="mt-3 font-serif text-2xl font-semibold">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}
