import { Link } from 'react-router-dom'
import { useQuery } from 'convex/react'
import { api } from '@convex/api'
import { Logo } from '@/components/Logo'
import { StitchDivider } from '@/components/StitchDivider'
import { useI18n } from '@/i18n'
import { whatsappLink } from '@/lib/format'

export function PublicFooter() {
  const { t } = useI18n()
  const shop = useQuery(api.settings.getShop)

  return (
    <footer className="mt-20 gradient-navy text-white/80">
      <div className="mx-auto max-w-6xl px-4 py-14">
        <div className="grid gap-10 md:grid-cols-3">
          <div>
            <Logo tone="light" />
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-white/70">
              {t('landing.footerTagline')}
            </p>
          </div>

          <div className="text-sm">
            <p className="section-label mb-3">{t('nav.contact')}</p>
            <p className="text-white/80">{shop?.address}</p>
            <p className="mt-2 text-white/80">{shop?.phone}</p>
            <p className="mt-2 text-white/60">{shop?.hours}</p>
          </div>

          <div className="text-sm">
            <p className="section-label mb-3">{t('nav.services')}</p>
            <ul className="space-y-2">
              <li>
                <Link to="/services" className="hover:text-white">
                  {t('nav.services')}
                </Link>
              </li>
              <li>
                <Link to="/track-order" className="hover:text-white">
                  {t('nav.trackOrder')}
                </Link>
              </li>
              <li>
                <Link to="/enquiry" className="hover:text-white">
                  {t('nav.enquiry')}
                </Link>
              </li>
              <li>
                <a
                  href={whatsappLink(
                    shop?.whatsapp ?? '',
                    t('landing.whatsappMessage'),
                  )}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-white"
                >
                  WhatsApp
                </a>
              </li>
            </ul>
          </div>
        </div>

        <StitchDivider className="my-8 opacity-40" />

        <p className="text-xs text-white/50">
          © {new Date().getFullYear()} {t('common.appName')}.{' '}
          {t('landing.footerRights')}
        </p>
      </div>
    </footer>
  )
}
