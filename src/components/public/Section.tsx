import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

export function Section({
  children,
  className,
  id,
}: {
  children: ReactNode
  className?: string
  id?: string
}) {
  return (
    <section id={id} className={cn('mx-auto max-w-6xl px-4 py-16 md:py-20', className)}>
      {children}
    </section>
  )
}

export function SectionHeader({
  kicker,
  title,
  subtitle,
  align = 'left',
}: {
  kicker?: string
  title: string
  subtitle?: string
  align?: 'left' | 'center'
}) {
  return (
    <div className={cn('max-w-2xl', align === 'center' && 'mx-auto text-center')}>
      {kicker && <p className="section-label">{kicker}</p>}
      <h2 className="mt-2 font-serif text-2xl font-semibold text-foreground md:text-3xl">
        {title}
      </h2>
      {subtitle && (
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground md:text-base">
          {subtitle}
        </p>
      )}
    </div>
  )
}
