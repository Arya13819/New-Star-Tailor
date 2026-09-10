import * as React from 'react'
import { en } from './en'
import { hi } from './hi'

export type Lang = 'en' | 'hi'

const DICTS: Record<Lang, Record<string, unknown>> = { en, hi }
const STORAGE_KEY = 'nst-lang'

type I18nContextValue = {
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: string, vars?: Record<string, string | number>) => string
}

const I18nContext = React.createContext<I18nContextValue | null>(null)

function lookup(dict: Record<string, unknown>, key: string): string | undefined {
  const parts = key.split('.')
  let node: unknown = dict
  for (const p of parts) {
    if (node && typeof node === 'object' && p in (node as object)) {
      node = (node as Record<string, unknown>)[p]
    } else {
      return undefined
    }
  }
  return typeof node === 'string' ? node : undefined
}

function interpolate(str: string, vars?: Record<string, string | number>) {
  if (!vars) return str
  return str.replace(/\{(\w+)\}/g, (_, k) =>
    k in vars ? String(vars[k]) : `{${k}}`,
  )
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = React.useState<Lang>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored === 'en' || stored === 'hi') return stored
    } catch {
      /* ignore */
    }
    return 'en'
  })

  React.useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  const setLang = React.useCallback((l: Lang) => {
    setLangState(l)
    try {
      localStorage.setItem(STORAGE_KEY, l)
    } catch {
      /* ignore */
    }
  }, [])

  const t = React.useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      const value =
        lookup(DICTS[lang], key) ?? lookup(DICTS.en, key) ?? key
      return interpolate(value, vars)
    },
    [lang],
  )

  const value = React.useMemo(
    () => ({ lang, setLang, t }),
    [lang, setLang, t],
  )

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n() {
  const ctx = React.useContext(I18nContext)
  if (!ctx) throw new Error('useI18n must be used within I18nProvider')
  return ctx
}

/** Pick a field by current language, falling back to the English field. */
export function useLocalized() {
  const { lang } = useI18n()
  return function localized<T extends Record<string, unknown>>(
    obj: T,
    baseKey: string,
  ): string {
    if (lang === 'hi') {
      const hiVal = obj[`${baseKey}Hi`]
      if (typeof hiVal === 'string' && hiVal.length > 0) return hiVal
    }
    const base = obj[baseKey]
    return typeof base === 'string' ? base : ''
  }
}
