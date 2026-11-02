<?php

namespace App\Http\Controllers;

use App\Tailoring\SessionState;

use function App\Tailoring\actor;
use function App\Tailoring\authorized_order;
use function App\Tailoring\create_order;
use function App\Tailoring\fail;
use function App\Tailoring\file_path;
use function App\Tailoring\flash;
use function App\Tailoring\go;
use function App\Tailoring\need_role;
use function App\Tailoring\one;
use function App\Tailoring\rate_limit;
use function App\Tailoring\render;
use function App\Tailoring\rows;
use function App\Tailoring\set_header;
use function App\Tailoring\submission_token;

class OrderController extends TailoringController
{
    protected function handle(string $path, bool $post): void
    {
        if ($path === '/order' || $path === '/admin/orders/new') {
            $admin = $path === '/admin/orders/new';
            if ($admin) {
                need_role('ADMIN');
            }
            if ($post) {
                rate_limit('order', 10);
                $id = create_order($admin);
                flash('Order created.');
                go($admin ? '/admin/orders/'.$id : '/order/success');
            }
            $services = rows('SELECT * FROM services WHERE is_active=1'.($admin ? '' : ' AND default_stitching_price IS NOT NULL').' ORDER BY category,sort_order,id');
            $customers = $admin ? rows('SELECT id,name,mobile FROM customers WHERE is_active=1 ORDER BY name LIMIT 2000') : [];
            render('order_form', ['title' => $admin ? 'New order' : 'Place your order', 'services' => $services, 'customers' => $customers, 'admin' => $admin, 'submission' => submission_token('order')]);

            return;
        }
        if ($path === '/order/success') {
            if (empty(SessionState::$data['last_order'])) {
                fail();
            }$proof = SessionState::$data['last_order'];
            $order = one('SELECT o.* FROM orders o JOIN customers c ON c.id=o.customer_id WHERE o.id=? AND c.mobile=?', [$proof['id'], $proof['mobile']]);
            if (! $order) {
                fail();
            }render('order_success', ['title' => 'Order placed', 'order' => $order]);

            return;
        }
        if (preg_match('~^/(admin|customer)/orders/(\d+)(?:/(receipt|images/\d+))?$~D', $path, $m)) {
            need_role($m[1] === 'admin' ? 'ADMIN' : 'CUSTOMER');
            $order = authorized_order((int) $m[2]);
            if (isset($m[3]) && str_starts_with($m[3], 'images/')) {
                $image = one('SELECT * FROM reference_images WHERE id=? AND order_id=?', [(int) substr($m[3], 7), $order['id']]);
                if (! $image) {
                    fail();
                }$file = file_path(basename($image['file_name']));
                if (! is_file($file)) {
                    fail();
                }set_header('Content-Type: '.$image['mime_type']);
                set_header('Content-Disposition: inline; filename="'.basename($image['file_name']).'"');
                set_header('Cache-Control: private, no-store');
                set_header("Content-Security-Policy: default-src 'none'; sandbox");
                readfile($file);

                return;
            }
            $items = rows('SELECT * FROM order_items WHERE order_id=? ORDER BY id', [$order['id']]);
            $payments = rows('SELECT * FROM payments WHERE order_id=? ORDER BY created_at,id', [$order['id']]);
            $images = rows('SELECT id FROM reference_images WHERE order_id=?', [$order['id']]);
            render(isset($m[3]) ? 'receipt' : 'order_detail', ['title' => $order['order_number'], 'order' => $order, 'items' => $items, 'payments' => $payments, 'images' => $images, 'admin' => $m[1] === 'admin', 'submission' => submission_token('payment:'.$order['id'])]);

            return;
        }
        if (preg_match('~^/customer/payments/(\d+)/receipt$~D', $path, $m)) {
            need_role('CUSTOMER');
            $payment = one('SELECT p.*,o.order_number,c.name customer_name FROM payments p JOIN orders o ON o.id=p.order_id JOIN customers c ON c.id=p.customer_id WHERE p.id=? AND c.user_id=?', [(int) $m[1], actor()['id']]);
            if (! $payment) {
                fail();
            }render('payment_receipt', ['title' => 'Payment receipt', 'payment' => $payment]);

            return;
        }
        \App\Tailoring\fail();
    }
}
