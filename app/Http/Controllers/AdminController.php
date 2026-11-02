<?php

namespace App\Http\Controllers;

use const App\Tailoring\STATUSES;

use App\Tailoring\SessionState;
use DateTimeImmutable;
use DateTimeZone;
use DomainException;
use Throwable;

use function App\Tailoring\add_measurement;
use function App\Tailoring\add_payment;
use function App\Tailoring\audit;
use function App\Tailoring\authorized_order;
use function App\Tailoring\cents;
use function App\Tailoring\choice;
use function App\Tailoring\date_value;
use function App\Tailoring\db;
use function App\Tailoring\fail;
use function App\Tailoring\flash;
use function App\Tailoring\go;
use function App\Tailoring\insert;
use function App\Tailoring\need_role;
use function App\Tailoring\now;
use function App\Tailoring\one;
use function App\Tailoring\query;
use function App\Tailoring\render;
use function App\Tailoring\rows;
use function App\Tailoring\save_customer;
use function App\Tailoring\save_service;
use function App\Tailoring\stamps;
use function App\Tailoring\text_value;
use function App\Tailoring\update_status;
use function App\Tailoring\verify_payment;

class AdminController extends TailoringController
{
    protected function handle(string $path, bool $post): void
    {
        if (str_starts_with($path, '/admin/')) {
            need_role('ADMIN');
            if ($path === '/admin/dashboard') {
                $counts = array_fill_keys(STATUSES, 0);
                foreach (rows('SELECT status,COUNT(*) n FROM orders GROUP BY status') as $r) {
                    $counts[$r['status']] = (int) $r['n'];
                }
                $orders = rows("SELECT o.*,c.name customer_name,COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id AND p.status='VERIFIED'),0) paid FROM orders o JOIN customers c ON c.id=o.customer_id ORDER BY o.id DESC LIMIT 12");
                $outstanding = one("SELECT COALESCE(SUM(o.grand_total-COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id AND p.status='VERIFIED'),0)),0) total FROM orders o")['total'];
                render('dashboard', compact('counts', 'orders', 'outstanding') + ['title' => 'Dashboard']);

                return;
            }
            if ($path === '/admin/orders') {
                $where = [];
                $args = [];
                $search = trim((string) (\request()->query()['q'] ?? ''));
                $status = (string) (\request()->query()['status'] ?? '');
                if ($search !== '') {
                    $where[] = '(o.order_number LIKE ? OR c.name LIKE ? OR c.mobile LIKE ?)';
                    $arg = '%'.substr($search, 0, 120).'%';
                    $args = [$arg, $arg, $arg];
                }
                if (in_array($status, STATUSES, true)) {
                    $where[] = 'o.status=?';
                    $args[] = $status;
                }
                $view = \request()->query()['view'] ?? '';
                $today = (new DateTimeImmutable('now', new DateTimeZone('Asia/Kolkata')))->format('Y-m-d');
                if ($view === 'urgent') {
                    $where[] = "o.priority='URGENT' AND o.status<>'DELIVERED'";
                }
                if ($view === 'today') {
                    $where[] = "o.confirmed_delivery_date=? AND o.status<>'DELIVERED'";
                    $args[] = $today;
                }
                if ($view === 'overdue') {
                    $where[] = "o.confirmed_delivery_date<? AND o.status<>'DELIVERED'";
                    $args[] = $today;
                }
                $orders = rows("SELECT o.*,c.name customer_name,COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id AND p.status='VERIFIED'),0) paid FROM orders o JOIN customers c ON c.id=o.customer_id".($where ? ' WHERE '.implode(' AND ', $where) : '').' ORDER BY o.id DESC LIMIT 500', $args);
                render('orders', ['title' => 'Orders', 'orders' => $orders, 'admin' => true, 'dashboard' => false]);

                return;
            }
            if (preg_match('~^/admin/orders/(\d+)/(status|payment|details)$~D', $path, $m) && $post) {
                $id = (int) $m[1];
                if ($m[2] === 'status') {
                    update_status($id);
                } elseif ($m[2] === 'payment') {
                    add_payment($id);
                } else {
                    $order = authorized_order($id);
                    query('UPDATE orders SET priority=?,confirmed_delivery_date=?,notes=?,updated_at=? WHERE id=?', [choice('priority', ['NORMAL', 'URGENT'], 'NORMAL'), date_value('confirmed_delivery_date'), text_value('notes', 3000), now(), $id]);
                    audit('order', $id, 'update_details');
                }flash('Saved.');
                go('/admin/orders/'.$id);
            }
            if ($path === '/admin/customers') {
                $search = trim((string) (\request()->query()['q'] ?? ''));
                $customers = rows('SELECT * FROM customers'.($search !== '' ? ' WHERE name LIKE ? OR mobile LIKE ?' : '').' ORDER BY name LIMIT 500', $search !== '' ? ['%'.substr($search, 0, 120).'%', '%'.substr($search, 0, 120).'%'] : []);
                render('customers', ['title' => 'Customers', 'customers' => $customers]);

                return;
            }
            if ($path === '/admin/customers/new' || preg_match('~^/admin/customers/(\d+)(?:/(edit|measurements/new))?$~D', $path, $m)) {
                $id = isset($m[1]) ? (int) $m[1] : null;
                $customer = $id ? one('SELECT * FROM customers WHERE id=?', [$id]) : null;
                if ($id && ! $customer) {
                    fail();
                }$action = $m[2] ?? ($id ? 'view' : 'new');
                if ($post) {
                    if ($action === 'measurements/new') {
                        db()->beginTransaction();
                        try {
                            add_measurement($id);
                            db()->commit();
                        } catch (Throwable $e) {
                            if (db()->inTransaction()) {
                                db()->rollBack();
                            }throw $e;
                        }
                    } else {
                        $id = save_customer($id);
                    }flash('Saved.');
                    go('/admin/customers/'.$id);
                }
                if ($action === 'view') {
                    $orders = rows("SELECT o.*,COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id AND p.status='VERIFIED'),0) paid FROM orders o WHERE customer_id=? ORDER BY id DESC", [$id]);
                    $measurements = rows('SELECT v.* FROM measurement_versions v JOIN measurements m ON m.id=v.measurement_id WHERE m.customer_id=? ORDER BY v.version_number DESC', [$id]);
                    render('customer_detail', compact('customer', 'orders', 'measurements') + ['title' => $customer['name']]);
                } elseif ($action === 'measurements/new') {
                    $last = one('SELECT v.* FROM measurement_versions v JOIN measurements m ON m.current_version_id=v.id WHERE m.customer_id=?', [$id]);
                    render('measurement_form', ['title' => 'New measurement version', 'customer' => $customer, 'last' => $last ?? []]);
                } else {
                    render('customer_form', ['title' => $id ? 'Edit customer' : 'New customer', 'customer' => $customer ?? []]);
                }

                return;
            }
            if ($path === '/admin/services') {
                $services = rows('SELECT * FROM services ORDER BY category,sort_order');
                render('service_list', ['title' => 'Services', 'services' => $services]);

                return;
            }
            if ($path === '/admin/services/new' || preg_match('~^/admin/services/(\d+)/edit$~D', $path, $m)) {
                $id = isset($m[1]) ? (int) $m[1] : null;
                $service = $id ? one('SELECT * FROM services WHERE id=?', [$id]) : null;
                if ($id && ! $service) {
                    fail();
                }if ($post) {
                    save_service($id);
                    flash('Saved.');
                    go('/admin/services');
                }render('service_form', ['title' => $id ? 'Edit service' : 'New service', 'service' => $service ?? []]);

                return;
            }
            if ($path === '/admin/payments') {
                $payments = rows('SELECT p.*,o.order_number FROM payments p JOIN orders o ON o.id=p.order_id'.((\request()->query()['status'] ?? '') === 'PENDING' ? " WHERE p.status='PENDING'" : '').' ORDER BY p.created_at DESC,p.id DESC LIMIT 500');
                render('payments', ['title' => 'Payments', 'payments' => $payments, 'admin' => true]);

                return;
            }
            if (preg_match('~^/admin/payments/(\d+)/(verify|receipt)$~D', $path, $m)) {
                if ($m[2] === 'verify' && $post) {
                    verify_payment((int) $m[1]);
                    flash('Payment verified.');
                    go('/admin/payments');
                }if ($m[2] === 'receipt') {
                    $payment = one('SELECT p.*,o.order_number,c.name customer_name FROM payments p JOIN orders o ON o.id=p.order_id JOIN customers c ON c.id=p.customer_id WHERE p.id=?', [(int) $m[1]]);
                    if (! $payment) {
                        fail();
                    }render('payment_receipt', ['title' => 'Payment receipt', 'payment' => $payment]);

                    return;
                }
            }
            if ($path === '/admin/enquiries') {
                $enquiries = rows('SELECT * FROM enquiries ORDER BY created_at DESC,id DESC LIMIT 500');
                render('enquiries', ['title' => 'Enquiries', 'enquiries' => $enquiries]);

                return;
            }
            if (preg_match('~^/admin/enquiries/(\d+)/(status|convert)$~D', $path, $m) && $post) {
                $enquiry = one('SELECT * FROM enquiries WHERE id=?', [(int) $m[1]]);
                if (! $enquiry) {
                    fail();
                }if ($m[2] === 'status') {
                    $status = choice('status', ['NEW', 'CONTACTED', 'CLOSED']);
                    if ($enquiry['converted_order_id']) {
                        throw new DomainException('Converted enquiries keep their order link.');
                    }query('UPDATE enquiries SET status=?,updated_at=? WHERE id=?', [$status, now(), $enquiry['id']]);
                    audit('enquiry', (int) $enquiry['id'], 'status_change', $enquiry['status'], $status);
                } else {
                    if ($enquiry['converted_order_id']) {
                        go('/admin/orders/'.$enquiry['converted_order_id']);
                    }SessionState::$data['enquiry_to_convert'] = (int) $enquiry['id'];
                    $id = insert('customers', ['name' => $enquiry['name'], 'mobile' => $enquiry['mobile'], 'address' => $enquiry['address'], 'is_active' => 1] + stamps());
                    go('/admin/orders/new?customer='.$id.'&enquiry='.(int) $enquiry['id']);
                }flash('Saved.');
                go('/admin/enquiries');
            }
            if ($path === '/admin/notifications') {
                $notifications = rows('SELECT * FROM notifications ORDER BY created_at DESC,id DESC LIMIT 500');
                render('notifications', ['title' => 'Notifications', 'notifications' => $notifications]);

                return;
            }
            if ($path === '/admin/reports') {
                $tz = new DateTimeZone('Asia/Kolkata');
                $today = new DateTimeImmutable('today', $tz);
                $period = \request()->query()['period'] ?? 'month';
                $start = match ($period) {
                    'today' => $today,'week' => $today->modify('monday this week'),default => $today->modify('first day of this month')
                };
                $end = $today->modify('+1 day');
                if ($period === 'custom') {
                    foreach (['from', 'to'] as $k) {
                        $s = (string) (\request()->query()[$k] ?? '');
                        $d = DateTimeImmutable::createFromFormat('!Y-m-d', $s, $tz);
                        if (! $d || $d->format('Y-m-d') !== $s) {
                            throw new DomainException('Choose a valid report date range.');
                        }if ($k === 'from') {
                            $start = $d;
                        } else {
                            $end = $d->modify('+1 day');
                        }
                    }if ($end <= $start) {
                        throw new DomainException('Choose a valid report date range.');
                    }
                }
                $from = $start->setTimezone(new DateTimeZone('UTC'))->format('Y-m-d H:i:s');
                $to = $end->setTimezone(new DateTimeZone('UTC'))->format('Y-m-d H:i:s');
                $payments = rows("SELECT p.*,o.order_number FROM payments p JOIN orders o ON o.id=p.order_id WHERE p.status='VERIFIED' AND p.verified_at>=? AND p.verified_at<? ORDER BY p.verified_at DESC", [$from, $to]);
                $revenue = array_sum(array_map(fn ($p) => cents($p['amount']), $payments));
                $categories = rows('SELECT i.category_snapshot category,COALESCE(SUM(i.line_total),0) total FROM order_items i JOIN orders o ON o.id=i.order_id WHERE o.created_at>=? AND o.created_at<? GROUP BY i.category_snapshot', [$from, $to]);
                render('reports', compact('payments', 'revenue', 'categories', 'period') + ['title' => 'Reports']);

                return;
            }
        }
        \App\Tailoring\fail();
    }
}
