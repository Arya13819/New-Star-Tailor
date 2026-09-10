export function formatCurrency(amount: number | null | undefined): string {
  const n = typeof amount === 'number' && !Number.isNaN(amount) ? amount : 0
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: n % 1 === 0 ? 0 : 2,
  }).format(n)
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat('en-IN').format(n)
}

export function formatDate(ts: number | null | undefined): string {
  if (!ts) return '—'
  return new Date(ts).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function formatDateTime(ts: number | null | undefined): string {
  if (!ts) return '—'
  return new Date(ts).toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function relativeDay(ts: number): string {
  const diff = Date.now() - ts
  const days = Math.floor(diff / (24 * 60 * 60 * 1000))
  if (days <= 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 30) return `${days} days ago`
  const months = Math.floor(days / 30)
  return months === 1 ? '1 month ago' : `${months} months ago`
}

export function initials(name: string): string {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase() ?? '')
    .join('')
}

export function whatsappLink(number: string, text?: string): string {
  const digits = number.replace(/\D/g, '')
  const q = text ? `?text=${encodeURIComponent(text)}` : ''
  return `https://wa.me/${digits}${q}`
}
