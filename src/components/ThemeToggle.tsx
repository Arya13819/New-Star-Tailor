import { MoonIcon, SunIcon } from 'lucide-react'
import { useTheme } from '@/components/theme-provider'
import { cn } from '@/lib/utils'

export function ThemeToggle({ className }: { className?: string }) {
  const { resolvedTheme, toggle } = useTheme()
  return (
    <button
      type="button"
      onClick={toggle}
      aria-label="Toggle theme"
      className={cn(
        'inline-flex size-8 items-center justify-center rounded-full border border-border bg-card text-muted-foreground transition-colors hover:text-foreground',
        className,
      )}
    >
      {resolvedTheme === 'dark' ? (
        <SunIcon className="size-4" />
      ) : (
        <MoonIcon className="size-4" />
      )}
    </button>
  )
}
