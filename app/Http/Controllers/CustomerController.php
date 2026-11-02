<?php

namespace App\Http\Controllers;

use function App\Tailoring\actor;
use function App\Tailoring\need_role;
use function App\Tailoring\render;
use function App\Tailoring\rows;

class CustomerController extends TailoringController
{
    protected function handle(string $path, bool $post): void
    {
        if (str_starts_with($path, '/customer/')) {
            need_role('CUSTOMER');
            $uid = actor()['id'];
            if (in_array($path, ['/customer/dashboard', '/customer/orders'], true)) {
                $orders = rows("SELECT o.*,c.name customer_name,COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id AND p.status='VERIFIED'),0) paid FROM orders o JOIN customers c ON c.id=o.customer_id WHERE c.user_id=? ORDER BY o.created_at DESC,o.id DESC", [$uid]);
                if ((\request()->query()['view'] ?? '') === 'open') {
                    $orders = array_values(array_filter($orders, fn ($o) => $o['status'] !== 'DELIVERED'));
                }
                render('orders', ['title' => $path === '/customer/dashboard' ? 'My account' : 'My orders', 'orders' => $orders, 'admin' => false, 'dashboard' => $path === '/customer/dashboard']);

                return;
            }
            if ($path === '/customer/payments') {
                $payments = rows('SELECT p.*,o.order_number FROM payments p JOIN orders o ON o.id=p.order_id JOIN customers c ON c.id=p.customer_id WHERE c.user_id=? ORDER BY p.created_at DESC', [$uid]);
                render('payments', ['title' => 'Payments', 'payments' => $payments, 'admin' => false]);

                return;
            }
            if ($path === '/customer/measurements') {
                $profiles = rows('SELECT * FROM customers WHERE user_id=?', [$uid]);
                $measurements = rows('SELECT v.*,c.name FROM measurement_versions v JOIN measurements m ON m.id=v.measurement_id JOIN customers c ON c.id=m.customer_id WHERE c.user_id=? ORDER BY v.created_at DESC,v.id DESC', [$uid]);
                render('measurements', ['title' => 'Measurements', 'measurements' => $measurements]);

                return;
            }
        }
        \App\Tailoring\fail();
    }
}
