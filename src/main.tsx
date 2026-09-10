import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConvexReactClient } from 'convex/react'
import { ConvexAuthProvider } from '@convex-dev/auth/react'
import { ThemeProvider } from '@/components/theme-provider'
import { I18nProvider } from '@/i18n'
import { Toaster } from '@/components/ui/sonner'
import App from '@/App'
import { SetupNotice } from '@/pages/SetupNotice'
import './index.css'

const convexUrl = import.meta.env.VITE_CONVEX_URL as string | undefined

const root = createRoot(document.getElementById('root')!)

if (!convexUrl) {
  root.render(
    <StrictMode>
      <ThemeProvider>
        <I18nProvider>
          <SetupNotice />
        </I18nProvider>
      </ThemeProvider>
    </StrictMode>,
  )
} else {
  const convex = new ConvexReactClient(convexUrl)
  root.render(
    <StrictMode>
      <ConvexAuthProvider client={convex}>
        <ThemeProvider>
          <I18nProvider>
            <BrowserRouter>
              <App />
              <Toaster />
            </BrowserRouter>
          </I18nProvider>
        </ThemeProvider>
      </ConvexAuthProvider>
    </StrictMode>,
  )
}
