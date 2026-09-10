import { Outlet } from 'react-router-dom'
import { RequireAuth } from '@/components/admin/RequireAuth'
import { AdminNav } from '@/components/admin/AdminNav'

export function AdminLayout() {
  return (
    <RequireAuth>
      <div className="min-h-dvh bg-background">
        <AdminNav />
        <main className="mx-auto max-w-7xl px-4 pt-6 pb-24 md:pb-10">
          <Outlet />
        </main>
      </div>
    </RequireAuth>
  )
}
