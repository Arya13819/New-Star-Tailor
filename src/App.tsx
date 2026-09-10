import { Routes, Route, Navigate } from 'react-router-dom'
import { ScrollToTop } from '@/components/ScrollToTop'
import { PublicLayout } from '@/layouts/PublicLayout'
import { AdminLayout } from '@/layouts/AdminLayout'

import Landing from '@/pages/public/Landing'
import Services from '@/pages/public/Services'
import TrackOrder from '@/pages/public/TrackOrder'
import Enquiry from '@/pages/public/Enquiry'
import Receipt from '@/pages/public/Receipt'
import AuthPage from '@/pages/auth/AuthPage'

import Dashboard from '@/pages/admin/Dashboard'
import Orders from '@/pages/admin/Orders'
import NewOrder from '@/pages/admin/NewOrder'
import OrderDetail from '@/pages/admin/OrderDetail'
import Customers from '@/pages/admin/Customers'
import CustomerDetail from '@/pages/admin/CustomerDetail'
import Payments from '@/pages/admin/Payments'
import Reports from '@/pages/admin/Reports'
import Settings from '@/pages/admin/Settings'

export default function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/services" element={<Services />} />
          <Route path="/track-order" element={<TrackOrder />} />
          <Route path="/enquiry" element={<Enquiry />} />
        </Route>

        <Route path="/receipt/:orderId" element={<Receipt />} />
        <Route path="/auth" element={<AuthPage />} />

        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="orders" element={<Orders />} />
          <Route path="orders/new" element={<NewOrder />} />
          <Route path="orders/:orderId" element={<OrderDetail />} />
          <Route path="customers" element={<Customers />} />
          <Route path="customers/:customerId" element={<CustomerDetail />} />
          <Route path="payments" element={<Payments />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}
