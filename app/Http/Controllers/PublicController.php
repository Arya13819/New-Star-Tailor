<?php

namespace App\Http\Controllers;

use const App\Tailoring\CATEGORIES;
use const App\Tailoring\SHOP_PHONE;

use Throwable;

use function App\Tailoring\db;
use function App\Tailoring\flash;
use function App\Tailoring\go;
use function App\Tailoring\insert;
use function App\Tailoring\mobile_value;
use function App\Tailoring\now;
use function App\Tailoring\one;
use function App\Tailoring\rate_limit;
use function App\Tailoring\render;
use function App\Tailoring\rows;
use function App\Tailoring\stamps;
use function App\Tailoring\text_value;

class PublicController extends TailoringController
{
    protected function handle(string $path, bool $post): void
    {
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
        \App\Tailoring\fail();
    }
}
