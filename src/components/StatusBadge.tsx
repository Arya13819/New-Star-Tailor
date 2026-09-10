import { Badge } from '@/components/ui/badge'
import { useI18n } from '@/i18n'

type Status = 'new' | 'measurement' | 'ready' | 'delivered'

const VARIANT: Record<Status, 'secondary' | 'gold' | 'warning' | 'success'> = {
  new: 'secondary',
  measurement: 'warning',
  ready: 'gold',
  delivered: 'success',
}

export function StatusBadge({
  status,
  short = false,
}: {
  status: Status
  short?: boolean
}) {
  const { t } = useI18n()
  return (
    <Badge variant={VARIANT[status]}>
      {t(`status.${status}${short ? 'Short' : ''}`)}
    </Badge>
  )
}
