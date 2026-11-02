<?php

declare(strict_types=1);

namespace App\Tailoring;

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
function handle_request(string $path, callable $handler): void
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
    $handler($path, $post);
}
