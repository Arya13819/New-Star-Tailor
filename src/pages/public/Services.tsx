import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery } from 'convex/react'
import { api } from '@convex/api'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Section, SectionHeader } from '@/components/public/Section'
import { StitchDivider } from '@/components/StitchDivider'
import { Skeleton } from '@/components/ui/skeleton'
import { useI18n, useLocalized } from '@/i18n'
import { formatCurrency } from '@/lib/format'
import { SERVICE_CATEGORIES } from '@/lib/constants'

export default function Services() {
  const { t } = useI18n()
  const localized = useLocalized()
  const services = useQuery(api.services.list, {})
  const seed = useMutation(api.services.seedIfEmpty)
  const [seeding, setSeeding] = useState(false)
  const triedRef = useRef(false)

  useEffect(() => {
    if (services && services.length === 0 && !triedRef.current) {
      triedRef.current = true
      setSeeding(true)
      seed({})
        .catch(() => undefined)
        .finally(() => setSeeding(false))
    }
  }, [services, seed])

  return (
    <>
      <div className="gradient-hero">
        <Section className="py-14 md:py-16">
          <SectionHeader title={t('services.title')} subtitle={t('services.subtitle')} />
        </Section>
      </div>

      <Section>
        {services === undefined || seeding ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-40 w-full" />
            ))}
          </div>
        ) : services.length === 0 ? (
          <div className="rounded-xl border border-border bg-card p-10 text-center shadow-warm">
            <p className="text-sm text-muted-foreground">{t('services.empty')}</p>
            <Button
              className="mt-4"
              variant="outline"
              onClick={() => {
                setSeeding(true)
                seed({}).finally(() => setSeeding(false))
              }}
            >
              {t('services.loadServices')}
            </Button>
          </div>
        ) : (
          <div className="space-y-14">
            {SERVICE_CATEGORIES.map((cat) => {
              const rows = services.filter((s) => s.category === cat)
              if (rows.length === 0) return null
              return (
                <div key={cat}>
                  <div className="flex items-center gap-3">
                    <h2 className="font-serif text-xl font-semibold">
                      {t(`category.${cat}`)}
                    </h2>
                    <StitchDivider className="flex-1" />
                  </div>
                  <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {rows.map((s) => (
                      <div
                        key={s._id}
                        className="hover-gold flex flex-col rounded-xl border border-border bg-card p-5 shadow-warm"
                      >
                        <h3 className="font-serif text-lg font-semibold">
                          {localized(s, 'name')}
                        </h3>
                        {s.description && (
                          <p className="mt-1.5 flex-1 text-sm text-muted-foreground">
                            {s.description}
                          </p>
                        )}
                        <div className="mt-4 flex items-end justify-between">
                          <div>
                            <p className="text-xs text-muted-foreground">
                              {t('services.stitchingFrom')}
                            </p>
                            <p className="font-serif text-lg font-semibold text-foreground">
                              {formatCurrency(s.defaultStitchingPrice)}
                            </p>
                          </div>
                          <Badge variant="outline">
                            {t('services.materialSeparate')}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}

            <div className="rounded-2xl gradient-navy px-6 py-10 text-center text-white">
              <p className="text-sm text-white/80">{t('services.subtitle')}</p>
              <Button asChild variant="gold" className="mt-4">
                <Link to="/enquiry">{t('services.enquireCta')}</Link>
              </Button>
            </div>
          </div>
        )}
      </Section>
    </>
  )
}
