import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useConvexAuth, useQuery } from 'convex/react'
import { useAuthActions } from '@convex-dev/auth/react'
import { api } from '@convex/api'
import { Button } from '@/components/ui/button'
import { Logo } from '@/components/Logo'

function FullScreen({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-dvh items-center justify-center gradient-hero px-4">
      <div className="w-full max-w-sm text-center">{children}</div>
    </div>
  )
}

export function RequireAuth({ children }: { children: ReactNode }) {
  const { isLoading, isAuthenticated } = useConvexAuth()
  const location = useLocation()
  const me = useQuery(api.users.me, isAuthenticated ? {} : 'skip')
  const { signOut } = useAuthActions()

  if (isLoading) {
    return (
      <FullScreen>
        <Logo className="justify-center" />
        <p className="mt-4 text-sm text-muted-foreground">Loading…</p>
      </FullScreen>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace state={{ from: location.pathname }} />
  }

  if (me === undefined) {
    return (
      <FullScreen>
        <Logo className="justify-center" />
        <p className="mt-4 text-sm text-muted-foreground">Loading…</p>
      </FullScreen>
    )
  }

  if (me === null || me.role !== 'admin') {
    return (
      <FullScreen>
        <Logo className="justify-center" />
        <h1 className="mt-6 font-serif text-xl">Access pending</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          You are signed in{me?.email ? ` as ${me.email}` : ''}, but this account
          does not have staff access yet. Ask an existing admin to grant it from
          Settings → Staff access.
        </p>
        <Button
          variant="outline"
          className="mt-6"
          onClick={() => void signOut()}
        >
          Sign out
        </Button>
      </FullScreen>
    )
  }

  return <>{children}</>
}
