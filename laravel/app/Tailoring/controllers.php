<?php

declare(strict_types=1);

namespace App\Tailoring;

use App\Models\User;
use DateTimeImmutable;
use DateTimeZone;
use DomainException;
use Illuminate\Support\Facades\Auth;
use Throwable;

function submission_token(string $scope): string
{
    $token = bin2hex(random_bytes(32));
    SessionState::$data['submissions'] ??= [];
    if (count(SessionState::$data['submissions']) >= 50) {
        array_shift(SessionState::$data['submissions']);
    } SessionState::$data['submissions'][$token] = $scope;

    return $token;
}
function handle_request(string $path): void
{
    $post = \request()->method() === 'POST';
    if ($path === '/index.php') {
        go('/');
    }
    if (! in_array(\request()->method(), ['GET', 'HEAD', 'POST'], true)) {
        set_status(405);
        set_header('Allow: GET, HEAD, POST');

        return;
    }
    if ($path === '/api/payments/webhook' && $post) {
        set_status(501);
        set_header('Content-Type: application/json');
        echo '{"error":"Payment provider is not configured. No payment has been verified."}';

        return;
    }
    if ($post) {
        validate_csrf();
    }
    if ($path === '/healthz') {
        set_header('Content-Type: application/json');
        echo '{"status":"ok","service":"new-star-tailor-laravel"}';

        return;
    }
    if ($path === '/api/health') {
        set_header('Content-Type: application/json');
        try {
            query('SELECT 1');
            echo '{"status":"ok","database":true}';
        } catch (Throwable) {
            set_status(503);
            echo '{"status":"degraded","database":false}';
        }

        return;
    }
    if ($path === '/robots.txt') {
        set_header('Content-Type: text/plain');
        echo "User-agent: *\nDisallow: /admin\nDisallow: /customer\nDisallow: /setup\nDisallow: /src\nDisallow: /database\nDisallow: /api\nSitemap: ".rtrim((string) cfg('app_url'), '/')."/sitemap.xml\n";

        return;
    }
    if ($path === '/sitemap.xml') {
        set_header('Content-Type: application/xml');
        echo '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">';
        foreach (['/', '/services', '/gallery', '/about', '/contact'] as $p) {
            echo '<url><loc>'.e(rtrim((string) cfg('app_url'), '/').$p).'</loc></url>';
        }echo '</urlset>';

        return;
    }
    if ($path === '/sw.js') {
        set_header('Content-Type: application/javascript');
        set_header('Cache-Control: no-cache');
        set_header('Service-Worker-Allowed: /');
        readfile(\public_path('sw.js'));

        return;
    }
    if ($post && ! in_array($path, ['/setup', '/customer/register', '/customer/login', '/admin/login', '/admin/logout', '/customer/logout', '/order', '/enquiry', '/track-order'], true) && ! str_starts_with($path, '/admin/')) {
        fail(405);
    }
    if ($path === '/setup') {
        if (strlen((string) cfg('setup_key', '')) < 32 || (int) one("SELECT COUNT(*) n FROM users WHERE role='ADMIN'")['n'] > 0) {
            fail(404);
        }
        if ($post) {
            rate_limit('setup', 5);
            if (! hash_equals((string) cfg('setup_key'), (string) (\request()->post()['setup_key'] ?? ''))) {
                throw new DomainException('Invalid setup key.');
            }
            $password = password_value();
            if ($password !== (\request()->post()['confirm_password'] ?? '')) {
                throw new DomainException('Passwords do not match.');
            }
            $email = strtolower(text_value('email', 190, true));
            if (! filter_var($email, FILTER_VALIDATE_EMAIL)) {
                throw new DomainException('Enter a valid email.');
            }
            db()->beginTransaction();
            try {
                // Shared DB lock also serializes simultaneous first-admin setup requests.
                query('INSERT IGNORE INTO order_sequences (id,last_seq) VALUES (1,0)');
                query('SELECT id FROM order_sequences WHERE id=1 FOR UPDATE')->fetch();
                if ((int) one("SELECT COUNT(*) n FROM users WHERE role='ADMIN'")['n'] > 0) {
                    throw new DomainException('Setup has already been completed.');
                }
                $id = insert('users', ['name' => text_value('name', 120, true), 'email' => $email, 'mobile' => mobile_value(\request()->post()['mobile'] ?? ''), 'password_hash' => password_hash($password, PASSWORD_DEFAULT, ['cost' => 12]), 'role' => 'ADMIN', 'is_active' => 1, 'preferred_locale' => $GLOBALS['locale']] + stamps());
                audit('user', $id, 'create_admin');
                db()->commit();
            } catch (Throwable $e) {
                if (db()->inTransaction()) {
                    db()->rollBack();
                }throw $e;
            }
            flash('Admin account created. Sign in to continue.');
            go('/admin/login');
        }
        render('auth', ['title' => 'Create admin account', 'mode' => 'setup']);

        return;
    }
    if (in_array($path, ['/customer/login', '/admin/login', '/customer/register'], true)) {
        $register = $path === '/customer/register';
        $role = $path === '/admin/login' ? 'ADMIN' : 'CUSTOMER';
        if (actor()) {
            go(is_admin() ? '/admin/dashboard' : '/customer/dashboard');
        }
        if ($post) {
            rate_limit($register ? 'register' : 'login', 10);
            if ($register) {
                $mobile = mobile_value(\request()->post()['mobile'] ?? '');
                $password = password_value();
                if ($password !== (\request()->post()['confirm_password'] ?? '')) {
                    throw new DomainException('Passwords do not match.');
                }
                if (one('SELECT id FROM users WHERE mobile=?', [$mobile])) {
                    throw new DomainException('An account with this mobile number already exists. Please sign in instead.');
                }
                $name = text_value('name', 120, true);
                db()->beginTransaction();
                try {
                    $id = insert('users', ['name' => $name, 'mobile' => $mobile, 'password_hash' => password_hash($password, PASSWORD_DEFAULT, ['cost' => 12]), 'role' => 'CUSTOMER', 'is_active' => 1, 'preferred_locale' => $GLOBALS['locale']] + stamps());
                    insert('customers', ['name' => $name, 'mobile' => $mobile, 'address' => text_value('address', 400), 'user_id' => $id, 'is_active' => 1] + stamps());
                    db()->commit();
                } catch (Throwable $e) {
                    if (db()->inTransaction()) {
                        db()->rollBack();
                    }throw $e;
                }
                $user = one('SELECT * FROM users WHERE id=?', [$id]);
            } else {
                $identifier = trim((string) (\request()->post()[$role === 'ADMIN' ? 'identifier' : 'mobile'] ?? ''));
                $mobile = preg_replace('/\D/', '', $identifier);
                if (strlen($mobile) === 12 && str_starts_with($mobile, '91')) {
                    $mobile = substr($mobile, 2);
                }
                $user = $role === 'ADMIN' ? one("SELECT * FROM users WHERE role='ADMIN' AND is_active=1 AND (email=? OR mobile=?) LIMIT 1", [strtolower($identifier), $mobile]) : one("SELECT * FROM users WHERE role='CUSTOMER' AND is_active=1 AND mobile=?", [$mobile]);
                // A fixed dummy bcrypt hash keeps missing-account requests expensive too.
                $hash = $user['password_hash'] ?? '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2uheWG/igi.';
                if (! password_verify((string) (\request()->post()['password'] ?? ''), $hash) || ! $user) {
                    throw new DomainException('That email/mobile or password is not correct.');
                }
                query('UPDATE users SET last_login_at=?,updated_at=? WHERE id=?', [now(), now(), $user['id']]);
            }
            Auth::login(User::findOrFail($user['id']), isset(\request()->post()['remember']));
            \request()->session()->regenerate();
            if (! isset(\request()->query()['lang']) && in_array($user['preferred_locale'], ['en', 'hi'], true)) {
                SessionState::$data['lang'] = $user['preferred_locale'];
            }unset(SessionState::$data['csrf'],SessionState::$data['old']);
            flash('Welcome back.');
            go($role === 'ADMIN' ? '/admin/dashboard' : '/customer/dashboard');
        }
        render('auth', ['title' => $register ? 'Create account' : ($role === 'ADMIN' ? 'Staff sign in' : 'Sign in'), 'mode' => $register ? 'register' : ($role === 'ADMIN' ? 'admin' : 'login')]);

        return;
    }
    if (in_array($path, ['/admin/logout', '/customer/logout'], true)) {
        if (! $post) {
            fail(405);
        }SessionState::$data = [];
        Auth::logout();
        \request()->session()->invalidate();
        \request()->session()->regenerateToken();
        go('/');
    }
    if ($path === '/') {
        $prices = [];
        try {
            foreach (rows('SELECT code,default_stitching_price FROM services WHERE is_active=1 AND default_stitching_price IS NOT NULL') as $s) {
                $prices[$s['code']] = $s['default_stitching_price'];
            }
        } catch (Throwable $e) {
            error_log('NST PHP: storefront prices unavailable.');
        }
        render('marketing/'.$GLOBALS['locale'].'/home', ['prices' => $prices]);

        return;
    }
    if (in_array($path, ['/about', '/contact', '/gallery'], true)) {
        render('marketing/'.$GLOBALS['locale'].$path, ['title' => ucfirst(substr($path, 1))]);

        return;
    }
    if ($path === '/services') {
        $all = rows('SELECT * FROM services WHERE is_active=1 ORDER BY category,sort_order,id');
        $category = strtoupper((string) (\request()->query()['category'] ?? 'ALL'));
        if (! isset(CATEGORIES[$category])) {
            $category = 'ALL';
        }$search = trim(substr((string) (\request()->query()['q'] ?? ''), 0, 320));
        $services = array_values(array_filter($all, fn ($s) => ($category === 'ALL' || $s['category'] === $category) && ($search === '' || stripos(implode(' ', [$s['name_en'], $s['name_hi'] ?? '', $s['code'], $s['description'] ?? '']), $search) !== false)));
        render('services', compact('all', 'category', 'search', 'services') + ['title' => 'Services & pricing']);

        return;
    }
    if ($path === '/enquiry') {
        if ($post) {
            rate_limit('enquiry', 10);
            db()->beginTransaction();
            try {
                $id = insert('enquiries', ['name' => text_value('name', 120, true), 'mobile' => mobile_value(\request()->post()['mobile'] ?? ''), 'address' => text_value('address', 400), 'message' => text_value('message', 3000), 'status' => 'NEW'] + stamps());
                insert('notifications', ['channel' => 'SMS', 'type' => 'NEW_ENQUIRY', 'status' => 'SCHEDULED', 'to_address' => SHOP_PHONE, 'body' => 'New enquiry #'.$id.'. Please review in the staff dashboard.', 'created_at' => now(), 'scheduled_at' => now()]);
                db()->commit();
            } catch (Throwable $e) {
                if (db()->inTransaction()) {
                    db()->rollBack();
                }throw $e;
            }flash('Thank you. We have received your enquiry and will contact you soon.');
            go('/enquiry');
        }
        render('enquiry', ['title' => 'Send us an enquiry']);

        return;
    }
    if ($path === '/track-order') {
        $result = null;
        $notFound = false;
        if ($post) {
            rate_limit('tracking', 30);
            $number = strtoupper(text_value('order_number', 20, true));
            $mobile = mobile_value(\request()->post()['mobile'] ?? '');
            $result = one('SELECT o.id,o.order_number,o.status,o.grand_total,o.confirmed_delivery_date FROM orders o JOIN customers c ON c.id=o.customer_id WHERE o.order_number=? AND c.mobile=?', [$number, $mobile]);
            $notFound = ! $result;
        }
        render('track', ['title' => 'Track your order', 'result' => $result, 'notFound' => $notFound]);

        return;
    }
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
    fail();
}
