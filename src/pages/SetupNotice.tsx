import { Logo } from '@/components/Logo'

export function SetupNotice() {
  return (
    <div className="flex min-h-dvh items-center justify-center gradient-hero px-4">
      <div className="w-full max-w-lg rounded-xl border border-border bg-card p-8 shadow-warm">
        <Logo />
        <h1 className="mt-6 font-serif text-xl">Connect the backend</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          The app is built, but it needs a Convex deployment before it can run.
        </p>
        <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm">
          <li>
            Run <code className="rounded bg-secondary px-1.5 py-0.5">npx convex dev</code>{' '}
            and follow the prompts to create a project.
          </li>
          <li>
            That writes <code className="rounded bg-secondary px-1.5 py-0.5">VITE_CONVEX_URL</code>{' '}
            into <code className="rounded bg-secondary px-1.5 py-0.5">.env.local</code>.
          </li>
          <li>
            In another terminal run{' '}
            <code className="rounded bg-secondary px-1.5 py-0.5">npm run dev</code>.
          </li>
        </ol>
        <p className="mt-4 text-xs text-muted-foreground">
          See <code className="rounded bg-secondary px-1.5 py-0.5">README.md</code> for
          the full setup, including optional email (Resend) configuration.
        </p>
      </div>
    </div>
  )
}
