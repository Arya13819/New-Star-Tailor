import { Toaster as Sonner, type ToasterProps } from 'sonner'
import { useTheme } from '@/components/theme-provider'

function Toaster(props: ToasterProps) {
  const { resolvedTheme } = useTheme()
  return (
    <Sonner
      theme={resolvedTheme}
      className="toaster group"
      position="top-center"
      toastOptions={{
        classNames: {
          toast:
            'group toast group-[.toaster]:bg-card group-[.toaster]:text-card-foreground group-[.toaster]:border-border group-[.toaster]:shadow-warm',
          description: 'group-[.toast]:text-muted-foreground',
          actionButton:
            'group-[.toast]:bg-primary group-[.toast]:text-primary-foreground',
          cancelButton:
            'group-[.toast]:bg-secondary group-[.toast]:text-secondary-foreground',
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
