<?php

declare(strict_types=1);

namespace App\Tailoring;

use DateTimeImmutable;
use DateTimeZone;
use DomainException;
use Illuminate\Support\Facades\DB;
use PDO;
use PDOStatement;
use RuntimeException;

const SHOP_NAME = 'New Star Tailor';
const SHOP_ADDRESS = 'Old UCO Bank Gully, Near Patel Plaza, Tagore Marg, Neemuch, Madhya Pradesh, India';
const LATITUDE = '24.4570252';
const LONGITUDE = '74.870045';
const STATUSES = ['NEW', 'MEASUREMENT', 'READY', 'DELIVERED'];
const CATEGORIES = ['SHIRT' => 'Shirt', 'PANT' => 'Pant', 'POLICE' => 'Police', 'CRPF' => 'CRPF', 'ARMY' => 'Army'];
const PHOTOS = ['SHIRT' => 'shirt.jpg', 'PANT' => 'pant.jpg', 'SHIRT_PANT_COMBO' => 'shirt_pant_combo.jpg', 'POLICE_KHAAKI' => 'police_khaaki.jpg', 'CRPF_KHAAKI' => 'crpf_khaaki.jpg', 'CRPF_CHEETAH' => 'crpf_cheetah.jpg', 'CRPF_KHAAKI_DANGRI' => 'crpf_khaaki_dangri.jpg', 'ARMY_PATTERN' => 'army_pattern.jpg', 'CHEETAH_US_PATTERN' => 'cheetah_us_pattern.jpg'];
const MEASUREMENT_FIELDS = ['shirt_length' => 'Shirt length', 'shirt_chest' => 'Chest', 'shirt_shoulder' => 'Shoulder', 'shirt_sleeves' => 'Sleeves', 'shirt_neck' => 'Neck', 'pant_length' => 'Pant length', 'pant_waist' => 'Waist', 'pant_hips' => 'Hips', 'pant_mori' => 'Mori'];
function cfg(string $key, mixed $default = null): mixed
{
    return $GLOBALS['config'][$key] ?? $default;
}
function e(mixed $s): string
{
    return htmlspecialchars((string) ($s ?? ''), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function raw_t(string $s): string
{
    static $catalogue;
    $catalogue ??= array_merge(json_decode(file_get_contents(__DIR__.'/hi.json'), true) ?: [], json_decode(file_get_contents(__DIR__.'/php-hi.json'), true) ?: []);

    return $GLOBALS['locale'] === 'hi' ? ($catalogue[$s] ?? $s) : $s;
}
function t(string $s): string
{
    return e(raw_t($s));
}
function db(): PDO
{
    $GLOBALS['db'] = DB::connection()->getPdo();

    return $GLOBALS['db'];
}
function query(string $sql, array $args = []): PDOStatement
{
    $stmt = db()->prepare($sql);
    $stmt->execute($args);

    return $stmt;
}
function one(string $sql, array $args = []): ?array
{
    return query($sql, $args)->fetch() ?: null;
}
function rows(string $sql, array $args = []): array
{
    return query($sql, $args)->fetchAll();
}
function insert(string $table, array $data): int
{
    // Table and column names come exclusively from server code.
    $fields = array_keys($data);
    $marks = implode(',', array_fill(0, count($fields), '?'));
    query('INSERT INTO `'.$table.'` (`'.implode('`,`', $fields).'`) VALUES ('.$marks.')', array_values($data));

    return (int) db()->lastInsertId();
}
function now(): string
{
    return gmdate('Y-m-d H:i:s');
}
function stamps(): array
{
    return ['created_at' => now(), 'updated_at' => now()];
}
function actor(): ?array
{
    return $GLOBALS['user'];
}
function is_admin(): bool
{
    return actor() && actor()['role'] === 'ADMIN';
}
function need_role(string $role): void
{
    if (! actor()) {
        go($role === 'ADMIN' ? '/admin/login' : '/customer/login');
    } if (actor()['role'] !== $role) {
        fail(403);
    }
}
function fail(int $status = 404): never
{
    throw new HttpStatusSignal($status);
}
function go(string $path): never
{
    if (! str_starts_with($path, '/') || str_starts_with($path, '//') || preg_match('/[\r\n]/', $path)) {
        $path = '/';
    } throw new RedirectSignal($path);
}
function csrf(): string
{
    return \csrf_token();
}
function csrf_field(): string
{
    return (string) \csrf_field();
}
function validate_csrf(): void
{ /* Laravel's web middleware validates every POST. */
}
function flash(string $s, string $kind = 'success'): void
{
    SessionState::$data['flashes'][] = [$kind, $s];
}
function old(string $key, mixed $default = ''): mixed
{
    return SessionState::$data['old'][$key] ?? \request()->post()[$key] ?? $default;
}
function text_value(string $key, int $max = 400, bool $required = false): string
{
    $s = trim((string) (\request()->post()[$key] ?? ''));
    if (($required && $s === '') || (preg_match_all('/./us', $s) === false || preg_match_all('/./us', $s) > $max)) {
        throw new DomainException('Please check: '.$key);
    }

    return $s;
}
function mobile_value(mixed $value): string
{
    $v = preg_replace('/\D/', '', (string) $value);
    if (strlen($v) === 12 && str_starts_with($v, '91')) {
        $v = substr($v, 2);
    } if (! preg_match('/^[6-9][0-9]{9}$/D', $v)) {
        throw new DomainException('Enter a valid 10-digit mobile number.');
    }

    return $v;
}
function cents(mixed $value): int
{
    $s = trim((string) $value);
    if (! preg_match('/^(\d{1,8})(?:\.(\d{1,2}))?$/D', $s, $m)) {
        throw new DomainException('Enter a valid amount with at most two decimal places.');
    }

    return (int) $m[1] * 100 + (int) str_pad($m[2] ?? '', 2, '0');
}
function decimal(int $c): string
{
    if ($c < 0 || $c > 9999999999) {
        throw new DomainException('Amount is out of range.');
    }

    return intdiv($c, 100).'.'.str_pad((string) ($c % 100), 2, '0', STR_PAD_LEFT);
}
function money(mixed $decimal): string
{
    return '₹'.decimal(cents($decimal));
}
function choice(string $key, array $allowed, string $default = ''): string
{
    $value = (string) (\request()->post()[$key] ?? $default);
    if (! in_array($value, $allowed, true)) {
        throw new DomainException('Please choose a valid '.$key.'.');
    }

    return $value;
}
function date_value(string $key, bool $future = true): ?string
{
    $v = trim((string) (\request()->post()[$key] ?? ''));
    if ($v === '') {
        return null;
    } $d = DateTimeImmutable::createFromFormat('!Y-m-d', $v);
    if (! $d || $d->format('Y-m-d') !== $v || ($future && $v < (new DateTimeImmutable('now', new DateTimeZone('Asia/Kolkata')))->format('Y-m-d'))) {
        throw new DomainException('Please choose a valid date, today or later.');
    }

    return $v;
}
function rate_limit(string $scope, int $limit): void
{
    $bucket = hash_hmac('sha256', $scope.'|'.(\request()->ip() ?? 'unknown'), (string) cfg('app_key'));
    query('INSERT INTO php_rate_limits (bucket,window_start,attempts) VALUES (?,UNIX_TIMESTAMP(),1) ON DUPLICATE KEY UPDATE attempts=IF(window_start < UNIX_TIMESTAMP()-60,1,attempts+1),window_start=IF(window_start < UNIX_TIMESTAMP()-60,UNIX_TIMESTAMP(),window_start)', [$bucket]);
    $row = one('SELECT attempts FROM php_rate_limits WHERE bucket=?', [$bucket]);
    if ((int) $row['attempts'] > $limit) {
        set_status(429);
        throw new DomainException('Too many attempts. Please wait a minute.');
    }
    if (random_int(1, 100) === 1) {
        query('DELETE FROM php_rate_limits WHERE window_start < UNIX_TIMESTAMP()-86400');
    }
}
function audit(string $type, int $id, string $action, ?string $from = null, ?string $to = null): void
{
    insert('audit_logs', ['actor_user_id' => actor()['id'] ?? null, 'entity_type' => $type, 'entity_id' => $id, 'action' => $action, 'from_value' => $from, 'to_value' => $to, 'created_at' => now()]);
}
function notify(array $customer, array $order, string $type, string $body): void
{
    $locale = one('SELECT u.preferred_locale FROM customers c LEFT JOIN users u ON u.id=c.user_id WHERE c.id=?', [$customer['id']])['preferred_locale'] ?? 'en';
    if ($type === 'ORDER_CONFIRMATION') {
        $body = $locale === 'hi' ? 'नमस्ते! आपका ऑर्डर '.$order['order_number'].' कन्फर्म हो गया है। कुल '.money($order['grand_total']).'।' : 'Namaste! Aapka order '.$order['order_number'].' confirm ho gaya hai. Total '.money($order['grand_total']).'.';
    }
    if ($type === 'ORDER_READY') {
        $body = $locale === 'hi' ? 'आपका ऑर्डर '.$order['order_number'].' तैयार है। कृपया दुकान से ले जाएँ।' : 'Aapka order '.$order['order_number'].' taiyar hai. Kripya dukan se le jayein.';
    }
    insert('notifications', ['customer_id' => $customer['id'], 'order_id' => $order['id'], 'channel' => 'SMS', 'type' => $type, 'status' => 'SCHEDULED', 'to_address' => $customer['mobile'], 'body' => $body, 'scheduled_at' => now(), 'created_at' => now()]);
}
function paid(int $id): int
{
    return cents(one("SELECT COALESCE(SUM(amount),0) amount FROM payments WHERE order_id=? AND status='VERIFIED'", [$id])['amount']);
}
function authorized_order(int $id, bool $lock = false): array
{
    if (! actor()) {
        need_role('CUSTOMER');
    }
    $sql = 'SELECT o.*,c.name customer_name,c.mobile customer_mobile,c.address customer_address,c.user_id FROM orders o JOIN customers c ON c.id=o.customer_id WHERE o.id=?';
    $args = [$id];
    if (! is_admin()) {
        $sql .= ' AND c.user_id=?';
        $args[] = actor()['id'];
    }
    $order = one($sql.($lock ? ' FOR UPDATE' : ''), $args);
    if (! $order) {
        fail();
    }

    return $order;
}
function render(string $view, array $vars = []): void
{
    $content = \view('pages.'.str_replace('/', '.', $view), $vars)->render();
    echo \view('layouts.app', array_merge($vars, ['content' => $content]))->render();
}
function field(string $name, string $label, string $type = 'text', mixed $value = null, bool $required = false): void
{
    $val = $type === 'password' ? '' : ($value ?? old($name));
    echo '<div class="mb-3"><label class="form-label" for="'.e($name).'">'.t($label).'</label><input class="form-control" id="'.e($name).'" name="'.e($name).'" type="'.e($type).'" value="'.e($val).'" '.($required ? 'required ' : '').($type === 'password' ? 'minlength="8" maxlength="128" autocomplete="current-password" ' : '').($type === 'tel' ? 'inputmode="tel" autocomplete="tel" ' : '').($type === 'number' ? 'step="0.01" ' : ($type === 'date' ? '' : 'maxlength="400"')).' ></div>';
}
function select_field(string $name, string $label, array $options, mixed $value = null): void
{
    $value = $value ?? old($name);
    echo '<div class="mb-3"><label class="form-label" for="'.e($name).'">'.t($label).'</label><select class="form-select" name="'.e($name).'" id="'.e($name).'">';
    foreach ($options as $k => $v) {
        echo '<option value="'.e($k).'" '.((string) $value === (string) $k ? 'selected' : '').'>'.t((string) $v).'</option>';
    } echo '</select></div>';
}
function textarea_field(string $name, string $label, mixed $value = null): void
{
    echo '<div class="mb-3"><label class="form-label" for="'.e($name).'">'.t($label).'</label><textarea class="form-control" id="'.e($name).'" name="'.e($name).'" rows="3" maxlength="3000">'.e($value ?? old($name)).'</textarea></div>';
}
function product_image(string $file, string $alt, bool $eager = false): string
{
    $stem = pathinfo($file, PATHINFO_FILENAME);

    return '<picture><source type="image/webp" srcset="/static/img/optimized/'.e($stem).'-320.webp 320w, /static/img/optimized/'.e($stem).'-640.webp 640w" sizes="(max-width:575px) 85vw,(max-width:991px) 44vw,370px"><img src="/static/img/services/'.e($file).'" alt="'.e($alt).'" width="700" height="716" loading="'.($eager ? 'eager' : 'lazy').'" decoding="async"></picture>';
}
function progress(string $status): void
{
    $labels = ['Order confirmed', 'Measurement', 'Ready for collection', 'Delivered'];
    $current = array_search($status, STATUSES, true);
    echo '<ol class="order-progress" aria-label="'.t('Order progress').'">';
    foreach (STATUSES as $i => $step) {
        echo '<li class="'.($i < $current ? 'is-complete' : ($i === $current ? 'is-current' : '')).'" '.($i === $current ? 'aria-current="step"' : '').'><span class="progress-dot">'.($i < $current ? '✓' : $i + 1).'</span><span>'.t($labels[$i]).'</span></li>';
    } echo '</ol>';
}
function file_path(string $name): string
{
    $dir = (string) cfg('storage_dir');
    if ($dir === '') {
        throw new RuntimeException('Private storage is not configured.');
    } if (! is_dir($dir) && ! mkdir($dir, 0700, true) && ! is_dir($dir)) {
        throw new RuntimeException('Private storage unavailable.');
    } $base = realpath($dir);
    $public = realpath(\public_path());
    // Shared-hosting storage is protected by storage/.htaccess and root rules.
    $protectedStorage = $base === realpath(\storage_path('app/private/references'))
        && is_file(\storage_path('.htaccess'))
        && trim(file_get_contents(\storage_path('.htaccess'))) === 'Require all denied';
    if (! $protectedStorage && (preg_match('~(?:^|/)public_html(?:/|$)~', $base) || ($public && ($base === $public || str_starts_with($base, $public.DIRECTORY_SEPARATOR))))) {
        throw new RuntimeException('Storage must be outside the document root.');
    }

    return $base.DIRECTORY_SEPARATOR.$name;
}

function set_header(string $line, bool $replace = true, int $status = 0): void
{
    if (str_starts_with($line, 'Location:')) {
        go(trim(substr($line, 9)));
    }
    [$name,$value] = array_pad(explode(':', $line, 2), 2, '');
    $GLOBALS['response_headers'][$name] = trim($value);
    if ($status) {
        set_status($status);
    }
}
function set_status(?int $status = null): int
{
    if ($status !== null) {
        $GLOBALS['response_status'] = $status;
    }

    return $GLOBALS['response_status'] ?? 200;
}
