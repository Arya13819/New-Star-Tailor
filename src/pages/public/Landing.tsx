import { Link } from 'react-router-dom'
import { useQuery } from 'convex/react'
import { motion } from 'motion/react'
import {
  MessageCircleIcon,
  MapPinIcon,
  PhoneIcon,
  ClockIcon,
  ShirtIcon,
  RulerIcon,
  PackageCheckIcon,
  ShieldCheckIcon,
  HistoryIcon,
  ReceiptIndianRupeeIcon,
  CalendarClockIcon,
  ArrowRightIcon,
} from 'lucide-react'
import { api } from '@convex/api'
import { Button } from '@/components/ui/button'
import { Section, SectionHeader } from '@/components/public/Section'
import { StitchDivider } from '@/components/StitchDivider'
import { useI18n, useLocalized } from '@/i18n'
import { formatCurrency, whatsappLink } from '@/lib/format'

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.06, duration: 0.4 },
  }),
}

export default function Landing() {
  const { t } = useI18n()
  const localized = useLocalized()
  const shop = useQuery(api.settings.getShop)
  const services = useQuery(api.services.list, {})

  const featured = (services ?? []).slice(0, 6)

  return (
    <>
      {/* Hero */}
      <div className="gradient-hero">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-16 md:grid-cols-2 md:py-24">
          <motion.div
            initial="hidden"
            animate="show"
            variants={fadeUp}
            custom={0}
          >
            <p className="section-label">{t('landing.heroKicker')}</p>
            <h1 className="mt-3 font-serif text-3xl leading-tight font-semibold text-foreground md:text-5xl">
              {t('landing.heroTitle')}
            </h1>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground md:text-base">
              {t('landing.heroSubtitle')}
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Button asChild variant="gold" size="lg">
                <a
                  href={whatsappLink(
                    shop?.whatsapp ?? '',
                    t('landing.whatsappMessage'),
                  )}
                  target="_blank"
                  rel="noreferrer"
                >
                  <MessageCircleIcon className="size-4" />
                  {t('landing.heroCtaPrimary')}
                </a>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link to="/track-order">{t('landing.heroCtaSecondary')}</Link>
              </Button>
            </div>

            <dl className="mt-10 grid grid-cols-3 gap-4 border-t border-border pt-6">
              <div>
                <dt className="font-serif text-2xl font-semibold text-gold">25+</dt>
                <dd className="mt-1 text-xs text-muted-foreground">
                  {t('landing.heroStat1')}
                </dd>
              </div>
              <div>
                <dt className="font-serif text-2xl font-semibold text-gold">4</dt>
                <dd className="mt-1 text-xs text-muted-foreground">
                  {t('landing.heroStat2')}
                </dd>
              </div>
              <div>
                <dt className="font-serif text-2xl font-semibold text-gold">100%</dt>
                <dd className="mt-1 text-xs text-muted-foreground">
                  {t('landing.heroStat3')}
                </dd>
              </div>
            </dl>
          </motion.div>

          <motion.div
            initial="hidden"
            animate="show"
            variants={fadeUp}
            custom={1}
            className="relative"
          >
            <div className="texture-fabric absolute inset-0 rounded-2xl" />
            <div className="relative flex h-full flex-col justify-between rounded-2xl border border-border bg-card p-8 shadow-warm">
              <ShirtIcon className="size-10 text-gold" strokeWidth={1.4} />
              <div className="mt-8 space-y-4">
                {[
                  { icon: RulerIcon, label: t('landing.how2Title') },
                  { icon: ShieldCheckIcon, label: t('landing.why1Title') },
                  { icon: CalendarClockIcon, label: t('landing.why4Title') },
                ].map((row) => (
                  <div key={row.label} className="flex items-center gap-3">
                    <span className="inline-flex size-9 items-center justify-center rounded-full bg-gold/12 text-gold">
                      <row.icon className="size-4" />
                    </span>
                    <span className="text-sm font-medium text-foreground">
                      {row.label}
                    </span>
                  </div>
                ))}
              </div>
              <StitchDivider className="my-6" />
              <p className="text-xs text-muted-foreground">{shop?.hours}</p>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Services */}
      <Section>
        <SectionHeader
          kicker={t('landing.servicesKicker')}
          title={t('landing.servicesTitle')}
          subtitle={t('landing.servicesSubtitle')}
        />
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {featured.map((s, i) => (
            <motion.div
              key={s._id}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true, margin: '-40px' }}
              variants={fadeUp}
              custom={i}
              className="hover-gold rounded-xl border border-border bg-card p-5 shadow-warm"
            >
              <p className="section-label">{t(`category.${s.category}`)}</p>
              <h3 className="mt-2 font-serif text-lg font-semibold">
                {localized(s, 'name')}
              </h3>
              {s.description && (
                <p className="mt-1.5 text-sm text-muted-foreground">
                  {s.description}
                </p>
              )}
              <p className="mt-4 text-sm">
                <span className="text-muted-foreground">
                  {t('services.stitchingFrom')}{' '}
                </span>
                <span className="font-semibold text-foreground">
                  {formatCurrency(s.defaultStitchingPrice)}
                </span>
              </p>
            </motion.div>
          ))}
        </div>
        <div className="mt-8">
          <Button asChild variant="outline">
            <Link to="/services">
              {t('landing.servicesCta')}
              <ArrowRightIcon className="size-4" />
            </Link>
          </Button>
        </div>
      </Section>

      <StitchDivider />

      {/* How it works */}
      <Section>
        <SectionHeader
          kicker={t('landing.howKicker')}
          title={t('landing.howTitle')}
        />
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            { icon: ShirtIcon, title: t('landing.how1Title'), body: t('landing.how1Body') },
            { icon: RulerIcon, title: t('landing.how2Title'), body: t('landing.how2Body') },
            { icon: PackageCheckIcon, title: t('landing.how3Title'), body: t('landing.how3Body') },
          ].map((step, i) => (
            <motion.div
              key={step.title}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              variants={fadeUp}
              custom={i}
              className="relative rounded-xl border border-border bg-card p-6 shadow-warm"
            >
              <span className="font-serif text-sm font-semibold text-gold">
                0{i + 1}
              </span>
              <step.icon className="mt-3 size-8 text-navy dark:text-gold" strokeWidth={1.4} />
              <h3 className="mt-4 font-serif text-lg font-semibold">
                {step.title}
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">{step.body}</p>
            </motion.div>
          ))}
        </div>
      </Section>

      <StitchDivider />

      {/* Why choose us */}
      <Section>
        <SectionHeader
          kicker={t('landing.whyKicker')}
          title={t('landing.whyTitle')}
        />
        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          {[
            { icon: ShieldCheckIcon, title: t('landing.why1Title'), body: t('landing.why1Body') },
            { icon: HistoryIcon, title: t('landing.why2Title'), body: t('landing.why2Body') },
            { icon: ReceiptIndianRupeeIcon, title: t('landing.why3Title'), body: t('landing.why3Body') },
            { icon: CalendarClockIcon, title: t('landing.why4Title'), body: t('landing.why4Body') },
          ].map((row, i) => (
            <motion.div
              key={row.title}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              variants={fadeUp}
              custom={i}
              className="flex gap-4 rounded-xl border border-border bg-card p-5 shadow-warm"
            >
              <span className="inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-gold/12 text-gold">
                <row.icon className="size-5" />
              </span>
              <div>
                <h3 className="font-serif text-base font-semibold">{row.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{row.body}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </Section>

      {/* Contact / WhatsApp CTA */}
      <Section id="contact">
        <div className="overflow-hidden rounded-2xl gradient-navy px-6 py-12 text-white md:px-12">
          <div className="grid gap-8 md:grid-cols-2 md:items-center">
            <div>
              <p className="section-label">{t('landing.contactKicker')}</p>
              <h2 className="mt-2 font-serif text-2xl font-semibold md:text-3xl">
                {t('landing.contactTitle')}
              </h2>
              <div className="mt-6 space-y-3 text-sm text-white/80">
                <p className="flex items-center gap-3">
                  <MapPinIcon className="size-4 text-gold" />
                  {shop?.address}
                </p>
                <p className="flex items-center gap-3">
                  <PhoneIcon className="size-4 text-gold" />
                  {shop?.phone}
                </p>
                <p className="flex items-center gap-3">
                  <ClockIcon className="size-4 text-gold" />
                  {shop?.hours}
                </p>
              </div>
            </div>
            <div className="flex flex-col gap-3 md:items-end">
              <Button asChild variant="gold" size="lg">
                <a
                  href={whatsappLink(
                    shop?.whatsapp ?? '',
                    t('landing.whatsappMessage'),
                  )}
                  target="_blank"
                  rel="noreferrer"
                >
                  <MessageCircleIcon className="size-4" />
                  {t('landing.whatsappCta')}
                </a>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="border-white/30 bg-transparent text-white hover:bg-white/10 hover:text-white"
              >
                <Link to="/enquiry">{t('nav.enquiry')}</Link>
              </Button>
            </div>
          </div>
        </div>
      </Section>
    </>
  )
}
