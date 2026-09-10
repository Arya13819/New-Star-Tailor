import { cn } from '@/lib/utils'

export function StitchDivider({ className }: { className?: string }) {
  return <hr className={cn('stitch-divider my-0', className)} aria-hidden="true" />
}
