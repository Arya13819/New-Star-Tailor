import { CheckIcon } from 'lucide-react'
import { ORDER_STATUSES, type OrderStatus } from '@/lib/constants'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'

export function OrderStatusStepper({ status }: { status: OrderStatus }) {
  const { t } = useI18n()
  const currentIndex = ORDER_STATUSES.indexOf(status)

  return (
    <ol className="flex flex-col gap-0 sm:flex-row sm:items-start sm:gap-0">
      {ORDER_STATUSES.map((s, i) => {
        const done = i < currentIndex
        const active = i === currentIndex
        return (
          <li
            key={s}
            className="flex flex-1 items-center gap-3 sm:flex-col sm:items-center sm:text-center"
          >
            <div className="flex items-center sm:w-full sm:flex-col">
              <span
                className={cn(
                  'inline-flex size-8 shrink-0 items-center justify-center rounded-full border text-xs font-semibold',
                  done && 'border-success bg-success text-white',
                  active && 'border-gold bg-gold/15 text-gold',
                  !done && !active && 'border-border bg-card text-muted-foreground',
                )}
              >
                {done ? <CheckIcon className="size-4" /> : i + 1}
              </span>
            </div>
            <div className="pb-4 sm:pb-0 sm:pt-2">
              <p
                className={cn(
                  'text-xs font-medium',
                  active ? 'text-foreground' : 'text-muted-foreground',
                )}
              >
                {t(`status.${s}`)}
              </p>
            </div>
          </li>
        )
      })}
    </ol>
  )
}
