<?php

declare(strict_types=1);

namespace App\Tailoring;

use DomainException;
use finfo;
use Throwable;

function password_value(): string
{
    $password = (string) (\request()->post()['password'] ?? '');
    if (preg_match_all('/./us', $password) < 8 || strlen($password) > 72) {
        throw new DomainException('Password must be 8–72 bytes.');
    }

    return $password;
}
function save_customer(?int $id = null): int
{
    $data = ['name' => text_value('name', 120, true), 'mobile' => mobile_value(\request()->post()['mobile'] ?? ''), 'address' => text_value('address', 400), 'notes' => text_value('notes', 3000), 'updated_at' => now()];
    if ($id) {
        if (! one('SELECT id FROM customers WHERE id=?', [$id])) {
            fail();
        } query('UPDATE customers SET name=?,mobile=?,address=?,notes=?,updated_at=? WHERE id=?', [...array_values($data), $id]);
    } else {
        $data += ['is_active' => 1, 'created_at' => now()];
        $id = insert('customers', $data);
    }
    audit('customer', $id, 'save');

    return $id;
}
function add_measurement(int $customerId, string $source = 'SHOP'): int
{
    // Caller owns the transaction; the customer row serializes concurrent versions.
    query('SELECT id FROM customers WHERE id=? FOR UPDATE', [$customerId])->fetch();
    $measurement = one('SELECT * FROM measurements WHERE customer_id=?', [$customerId]);
    $measurementId = $measurement ? (int) $measurement['id'] : insert('measurements', ['customer_id' => $customerId] + stamps());
    $version = (int) (one('SELECT COALESCE(MAX(version_number),0) n FROM measurement_versions WHERE measurement_id=?', [$measurementId])['n']) + 1;
    $data = ['measurement_id' => $measurementId, 'version_number' => $version];
    foreach (MEASUREMENT_FIELDS as $key => $label) {
        $value = trim((string) (\request()->post()[$key] ?? ''));
        $number = $value === '' ? null : cents($value);
        if ($number !== null && ($number <= 0 || $number > 99999)) {
            throw new DomainException('Measurements must be greater than zero and at most 999.99 inches.');
        }
        $data[$key] = $number === null ? null : decimal($number);
    }
    $data += ['unit' => 'in', 'fitting_preference' => choice('fitting_preference', ['NORMAL', 'SLIM', 'LOOSE'], 'NORMAL'), 'allowance' => text_value('allowance', 120), 'notes' => text_value('measurement_notes', 3000), 'alteration_notes' => text_value('alteration_notes', 3000), 'source' => $source, 'created_by_id' => actor()['id'] ?? null, 'created_at' => now()];
    $id = insert('measurement_versions', $data);
    query('UPDATE measurements SET current_version_id=?,updated_at=? WHERE id=?', [$id, now(), $measurementId]);
    audit('measurement', $id, 'create_version', null, (string) $version);

    return $id;
}
function save_reference_image(int $orderId): ?string
{
    $file = \request()->file('reference_image');
    if (! $file) {
        return null;
    }
    if (! $file->isValid() || $file->getSize() > 8 * 1024 * 1024) {
        throw new DomainException('Upload a valid image smaller than 8 MB.');
    }
    $allowed = ['image/jpeg' => ['jpg', 'jpeg'], 'image/png' => ['png'], 'image/webp' => ['webp']];
    $mime = (new finfo(FILEINFO_MIME_TYPE))->file($file->getPathname());
    $extension = strtolower($file->getClientOriginalExtension());
    $size = @getimagesize($file->getPathname());
    if (! isset($allowed[$mime]) || ! in_array($extension, $allowed[$mime], true) || ! $size || ($size['mime'] ?? '') !== $mime || $size[0] * $size[1] > 50000000) {
        throw new DomainException('Only real JPG, PNG and WebP images are allowed.');
    }
    $name = bin2hex(random_bytes(20)).'.'.$extension;
    $path = file_path($name);
    $bytes = $file->getSize();
    $file->move(dirname($path), basename($path));
    chmod($path, 0600);
    try {
        insert('reference_images', ['order_id' => $orderId, 'file_name' => $name, 'storage_path' => $name, 'mime_type' => $mime, 'file_size' => $bytes, 'uploaded_by_id' => actor()['id'] ?? null, 'created_at' => now()]);
    } catch (Throwable $error) {
        @unlink($path);
        throw $error;
    }

    return $path;
}

function create_order(bool $admin = false): int
{
    $nonce = (string) (\request()->post()['submission'] ?? '');
    if (! preg_match('/^[a-f0-9]{64}$/D', $nonce) || (SessionState::$data['submissions'][$nonce] ?? '') !== 'order') {
        throw new DomainException('This order form expired. Please open it again.');
    }
    $imagePath = null;
    db()->beginTransaction();
    try {
        // A unique key makes refresh/double-click submissions idempotent.
        query('INSERT IGNORE INTO php_submissions (token,order_id,created_at) VALUES (?,NULL,UTC_TIMESTAMP())', [$nonce]);
        $submission = one('SELECT order_id FROM php_submissions WHERE token=? FOR UPDATE', [$nonce]);
        if ($submission['order_id']) {
            db()->commit();

            return (int) $submission['order_id'];
        }
        $fabric = choice('fabric_source', ['CUSTOMER', 'SHOP'], 'CUSTOMER');
        if ($admin) {
            $customer = one('SELECT * FROM customers WHERE id=?', [(int) (\request()->post()['customer_id'] ?? 0)]);
            if (! $customer) {
                throw new DomainException('Select a customer.');
            }
        } elseif (actor() && actor()['role'] === 'CUSTOMER') {
            $customer = one('SELECT * FROM customers WHERE user_id=? ORDER BY id LIMIT 1', [actor()['id']]);
            if (! $customer) {
                throw new DomainException('Customer profile is unavailable. Please contact the shop.');
            }
        } else {
            $customerId = insert('customers', ['name' => text_value('name', 120, true), 'mobile' => mobile_value(\request()->post()['mobile'] ?? ''), 'address' => text_value('address', 400), 'is_active' => 1] + stamps());
            $customer = one('SELECT * FROM customers WHERE id=?', [$customerId]);
        }
        $measurementId = null;
        $ack = ! empty(\request()->post()['provide_measurements']);
        if ($ack) {
            if (empty(\request()->post()['measurement_ack'])) {
                throw new DomainException('Please accept responsibility for the accuracy of self-submitted measurements.');
            }
            $measurementId = add_measurement((int) $customer['id'], $admin ? 'SHOP' : 'CUSTOMER');
        } else {
            $measurementId = one('SELECT current_version_id FROM measurements WHERE customer_id=?', [$customer['id']])['current_version_id'] ?? null;
        }
        $serviceIds = \request()->post()['service_id'] ?? [];
        $quantities = \request()->post()['quantity'] ?? [];
        if (! is_array($serviceIds) || count($serviceIds) < 1 || count($serviceIds) > 20) {
            throw new DomainException('Choose between 1 and 20 services.');
        }
        $items = [];
        $stitching = 0;
        $material = 0;
        foreach ($serviceIds as $i => $serviceId) {
            $service = one('SELECT * FROM services WHERE id=? AND is_active=1'.($admin ? '' : ' AND default_stitching_price IS NOT NULL'), [(int) $serviceId]);
            if (! $service) {
                throw new DomainException('Choose an available service with a confirmed price.');
            }
            $quantity = filter_var($quantities[$i] ?? 0, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 99]]);
            if (! $quantity) {
                throw new DomainException('Quantity must be between 1 and 99.');
            }
            $price = $admin ? cents(\request()->post()['stitching_price'][$i] ?? $service['default_stitching_price']) : cents($service['default_stitching_price']);
            if ($price <= 0) {
                throw new DomainException('Stitching price must be greater than zero.');
            }
            $cloth = $admin && $fabric === 'SHOP' ? cents(\request()->post()['material_price'][$i] ?? '0') : 0;
            $line = ($price + $cloth) * $quantity;
            decimal($line);
            $stitching += $price * $quantity;
            $material += $cloth * $quantity;
            $items[] = ['service_id' => $service['id'], 'service_name_snapshot' => $service['name_en'], 'category_snapshot' => $service['category'], 'stitching_price' => decimal($price), 'material_price' => decimal($cloth), 'quantity' => $quantity, 'line_total' => decimal($line), 'measurement_version_id' => $measurementId];
        }
        $grand = $stitching + $material;
        decimal($grand);
        query('INSERT IGNORE INTO order_sequences (id,last_seq) VALUES (1,0)');
        $seq = (int) one('SELECT last_seq FROM order_sequences WHERE id=1 FOR UPDATE')['last_seq'] + 1;
        query('UPDATE order_sequences SET last_seq=? WHERE id=1', [$seq]);
        $number = 'NST-'.str_pad((string) $seq, 4, '0', STR_PAD_LEFT);
        $advance = $fabric === 'SHOP' ? $grand : intdiv($stitching + 1, 2);
        $order = ['order_number' => $number, 'customer_id' => $customer['id'], 'source' => $admin ? 'SHOP' : 'WEBSITE', 'status' => 'NEW', 'priority' => $admin ? choice('priority', ['NORMAL', 'URGENT'], 'NORMAL') : 'NORMAL', 'fabric_source' => $fabric, 'requested_delivery_date' => date_value('requested_delivery_date'), 'confirmed_delivery_date' => $admin ? date_value('confirmed_delivery_date') : null, 'subtotal_stitching' => decimal($stitching), 'subtotal_material' => decimal($material), 'grand_total' => decimal($grand), 'required_advance' => decimal($advance), 'advance_satisfied' => $advance === 0 ? 1 : 0, 'self_measurement_acknowledged' => $ack ? 1 : 0, 'self_measurement_acknowledged_at' => $ack ? now() : null, 'notes' => text_value('notes', 3000), 'created_by_id' => actor()['id'] ?? null, 'confirmed_at' => now()] + stamps();
        $id = insert('orders', $order);
        $order['id'] = $id;
        foreach ($items as $item) {
            insert('order_items', ['order_id' => $id] + $item);
        }
        $reference = text_value('payment_reference', 190);
        $amount = cents(\request()->post()['payment_amount'] ?? '0');
        if ($amount > 0) {
            if ($reference === '' || $amount > $grand) {
                throw new DomainException('Enter a payment reference and an amount no greater than the total.');
            }
            insert('payments', ['order_id' => $id, 'customer_id' => $customer['id'], 'amount' => decimal($amount), 'method' => 'ONLINE', 'status' => 'PENDING', 'provider' => 'manual', 'transaction_reference' => $reference, 'recorded_by_id' => actor()['id'] ?? null] + stamps());
        }
        $imagePath = save_reference_image($id);
        audit('order', $id, 'create', null, $number);
        notify($customer, $order, 'ORDER_CONFIRMATION', "Order $number confirmed. Total ".money(decimal($grand)).'. Please contact the shop for details.');
        if ($admin && ! empty(\request()->post()['enquiry_id'])) {
            $enquiryId = (int) \request()->post()['enquiry_id'];
            $enquiry = one('SELECT * FROM enquiries WHERE id=? FOR UPDATE', [$enquiryId]);
            if (! $enquiry || $enquiry['converted_order_id']) {
                throw new DomainException('This enquiry has already been converted or is unavailable.');
            }
            query("UPDATE enquiries SET status='CONVERTED',converted_order_id=?,converted_at=?,updated_at=? WHERE id=?", [$id, now(), now(), $enquiryId]);
            audit('enquiry', $enquiryId, 'convert', null, (string) $id);
        }
        query('UPDATE php_submissions SET order_id=? WHERE token=?', [$id, $nonce]);
        db()->commit();
        SessionState::$data['last_order'] = ['id' => $id, 'mobile' => $customer['mobile']];

        return $id;
    } catch (Throwable $e) {
        if (db()->inTransaction()) {
            db()->rollBack();
        } if ($imagePath) {
            @unlink($imagePath);
        } throw $e;
    }
}
function add_payment(int $orderId): void
{
    $nonce = (string) (\request()->post()['submission'] ?? '');
    if ((SessionState::$data['submissions'][$nonce] ?? '') !== 'payment:'.$orderId) {
        throw new DomainException('This payment form expired. Open the order again.');
    }
    db()->beginTransaction();
    try {
        query('INSERT IGNORE INTO php_submissions (token,order_id,created_at) VALUES (?,NULL,UTC_TIMESTAMP())', [$nonce]);
        $previous = one('SELECT order_id FROM php_submissions WHERE token=? FOR UPDATE', [$nonce]);
        if ($previous['order_id']) {
            db()->commit();

            return;
        }
        $order = authorized_order($orderId, true);
        $amount = cents(\request()->post()['amount'] ?? '0');
        $balance = cents($order['grand_total']) - paid($orderId);
        if ($amount <= 0 || $amount > $balance) {
            throw new DomainException('Payment must be greater than zero and cannot exceed the remaining balance.');
        }
        $method = choice('method', ['CASH', 'UPI', 'ONLINE']);
        $verified = $method !== 'ONLINE';
        $id = insert('payments', ['order_id' => $orderId, 'customer_id' => $order['customer_id'], 'amount' => decimal($amount), 'method' => $method, 'status' => $verified ? 'VERIFIED' : 'PENDING', 'provider' => 'manual', 'transaction_reference' => text_value('transaction_reference', 190), 'note' => text_value('note', 300), 'recorded_by_id' => actor()['id'], 'verified_by_id' => $verified ? actor()['id'] : null, 'verified_at' => $verified ? now() : null] + stamps());
        query('UPDATE orders SET advance_satisfied=?,updated_at=? WHERE id=?', [paid($orderId) >= cents($order['required_advance']) ? 1 : 0, now(), $orderId]);
        audit('payment', $id, 'record', null, $verified ? 'VERIFIED' : 'PENDING');
        query('UPDATE php_submissions SET order_id=? WHERE token=?', [$orderId, $nonce]);
        db()->commit();
    } catch (Throwable $e) {
        if (db()->inTransaction()) {
            db()->rollBack();
        } throw $e;
    }
}
function verify_payment(int $id): void
{
    $payment = one('SELECT * FROM payments WHERE id=?', [$id]);
    if (! $payment) {
        fail();
    }
    db()->beginTransaction();
    try {
        $order = authorized_order((int) $payment['order_id'], true);
        $payment = one('SELECT * FROM payments WHERE id=? FOR UPDATE', [$id]);
        if ($payment['status'] === 'PENDING') {
            if (paid((int) $order['id']) + cents($payment['amount']) > cents($order['grand_total'])) {
                throw new DomainException('Verifying this payment would overpay the order.');
            }
            query("UPDATE payments SET status='VERIFIED',verified_by_id=?,verified_at=?,updated_at=? WHERE id=?", [actor()['id'], now(), now(), $id]);
            query('UPDATE orders SET advance_satisfied=?,updated_at=? WHERE id=?', [paid((int) $order['id']) >= cents($order['required_advance']) ? 1 : 0, now(), $order['id']]);
            audit('payment', $id, 'verify', 'PENDING', 'VERIFIED');
        }
        db()->commit();
    } catch (Throwable $e) {
        if (db()->inTransaction()) {
            db()->rollBack();
        } throw $e;
    }
}
function update_status(int $id): void
{
    $status = choice('status', STATUSES);
    db()->beginTransaction();
    try {
        $order = authorized_order($id, true);
        query('UPDATE orders SET status=?,delivered_at=?,updated_at=? WHERE id=?', [$status, $status === 'DELIVERED' ? now() : null, now(), $id]);
        audit('order', $id, 'status_change', $order['status'], $status);
        if ($status === 'READY' && $order['status'] !== 'READY') {
            notify(['id' => $order['customer_id'], 'mobile' => $order['customer_mobile']], $order, 'ORDER_READY', 'Order '.$order['order_number'].' is ready for collection.');
        }
        db()->commit();
    } catch (Throwable $e) {
        if (db()->inTransaction()) {
            db()->rollBack();
        } throw $e;
    }
}
function save_service(?int $id): int
{
    $name = text_value('name_en', 120, true);
    $nameHi = text_value('name_hi', 120);
    $category = choice('category', array_keys(CATEGORIES));
    $price = trim((string) (\request()->post()['default_stitching_price'] ?? ''));
    if ($price !== '' && cents($price) <= 0) {
        throw new DomainException('Price must be greater than zero, or left unset.');
    }
    $data = ['name_en' => $name, 'name_hi' => $nameHi, 'category' => $category, 'default_stitching_price' => $price === '' ? null : decimal(cents($price)), 'is_active' => isset(\request()->post()['is_active']) ? 1 : 0, 'sort_order' => (int) (\request()->post()['sort_order'] ?? 100), 'description' => text_value('description', 300), 'updated_at' => now()];
    if ($id) {
        if (! one('SELECT id FROM services WHERE id=?', [$id])) {
            fail();
        } query('UPDATE services SET name_en=?,name_hi=?,category=?,default_stitching_price=?,is_active=?,sort_order=?,description=?,updated_at=? WHERE id=?', [...array_values($data), $id]);
    } else {
        $code = text_value('code', 40, true);
        if (! preg_match('/^[A-Z0-9_]{1,40}$/D', $code)) {
            throw new DomainException('Service code must use uppercase letters, digits or underscores.');
        } $id = insert('services', ['code' => $code] + $data + ['created_at' => now()]);
    }
    audit('service', $id, 'save');

    return $id;
}
