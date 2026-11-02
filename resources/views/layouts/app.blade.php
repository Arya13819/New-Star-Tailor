<?php

namespace App\Tailoring;

?>

@php
    $path = parse_url(\request()->getRequestUri(), PHP_URL_PATH) ?: '/';
@endphp
@php
    $locale = $GLOBALS['locale'];
@endphp
@php
    $nonce = e($GLOBALS['nonce']);
@endphp
@php
    $title = $title ?? SHOP_NAME;
@endphp

<!doctype html>
<html lang="{{ $locale }}">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{{ $title }} — {{ SHOP_NAME }}</title>
    <meta name="description"
        content="{{ raw_t("Expert men's tailoring and uniform specialists in Neemuch, Madhya Pradesh.") }}">
    <link rel="canonical" href="{{ rtrim((string) cfg('app_url', 'https://newstartailor.itgurujan.com'), '/') . $path }}">
    <link rel="icon" href="/static/img/brand-star.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/static/img/icons/apple-touch-icon.png?v=6">
    <link rel="manifest" href="/static/manifest.webmanifest">
    <meta name="theme-color" content="#243c35">
    <meta property="og:title" content="{{ $title . ' — ' . SHOP_NAME }}">
    <meta property="og:type" content="website">
    <meta property="og:image"
        content="{{ rtrim((string) cfg('app_url', 'https://newstartailor.itgurujan.com'), '/') }}/static/img/icons/icon-512.png?v=6">
    <link rel="stylesheet" href="/static/vendor/bootstrap/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/theme.css?v=6">
    <link rel="stylesheet" href="/static/css/premium.css?v=6">
    <link rel="stylesheet" href="/assets/css/php-ui.css?v=1">

    @if (in_array($path, ['/about', '/services'], true))
        <link rel="stylesheet" href="/static/css/catalogue.css?v=6">
    @endif

    @if (in_array($path, ['/about', '/contact'], true))
        <link rel="stylesheet" href="/static/css/location.css?v=7">
    @endif

    <script nonce="{{ $nonce }}" type="application/ld+json">{!! json_encode(['@context' => 'https://schema.org', '@type' => 'ClothingStore', 'name' => SHOP_NAME, 'telephone' => '+91'.SHOP_PHONE, 'address' => SHOP_ADDRESS, 'geo' => ['@type' => 'GeoCoordinates', 'latitude' => LATITUDE, 'longitude' => LONGITUDE]], JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_UNESCAPED_UNICODE) !!}</script>
</head>

<body class="{!! $path === '/' ? 'home-page' : 'inner-page' !!}">
    <a class="skip-link" href="#main-content">{{ raw_t('Skip to content') }}</a>
    <div class="announcement no-print">
        <div class="container d-flex justify-content-between gap-3">
            <span>{{ raw_t('Made to measure. Made for you.') }}</span><a
                href="tel:+91{{ SHOP_PHONE }}">{{ raw_t('Neemuch') }} · +91 {{ SHOP_PHONE }}</a>
        </div>
    </div>
    <nav class="navbar navbar-expand-xl navbar-nst no-print" data-bs-theme="light"
        aria-label="{{ raw_t('Main navigation') }}">
        <div class="container"><a class="navbar-brand brand-lockup" href="/"><img class="shop-brand-mark"
                    src="/static/img/brand-star.svg" alt="" width="48"
                    height="48"><span><strong>{{ SHOP_NAME }}</strong><small>{{ raw_t('TAILORING & UNIFORMS') }}</small></span></a><button
                class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nstNav"
                aria-controls="nstNav" aria-expanded="false" aria-label="{{ raw_t('Menu') }}"><span
                    class="navbar-toggler-icon"></span></button>
            <div class="collapse navbar-collapse" id="nstNav">
                <ul class="navbar-nav mx-auto mb-2 mb-xl-0">
                    @foreach (['/' => 'Home', '/services' => 'Services', '/gallery' => 'Our work', '/about' => 'About', '/contact' => 'Contact'] as $href => $label)
                        <li class="nav-item"><a class="nav-link {!! $path === $href ? 'active' : '' !!}" {!! $path === $href ? 'aria-current="page"' : '' !!}
                                href="{{ $href }}">{{ raw_t($label) }}</a></li>
                    @endforeach
                </ul>
                <div class="nav-actions d-flex flex-wrap align-items-center gap-3"><a class="nav-track"
                        href="/track-order">{{ raw_t('Track order') }} ↗</a><a class="btn btn-primary btn-sm"
                        href="{!! actor() ? (is_admin() ? '/admin/dashboard' : '/customer/dashboard') : '/customer/login' !!}">{{ raw_t(actor() ? (is_admin() ? 'Dashboard' : 'My account') : 'Sign in') }}
                        ↗</a><a class="language-link"
                        href="{{ $path . '?' . http_build_query(array_merge(\request()->query(), ['lang' => $locale === 'hi' ? 'en' : 'hi'])) }}">{!! $locale === 'hi' ? 'English' : 'हिन्दी' !!}</a>
                </div>
            </div>
        </div>
    </nav>
    <main id="main-content" class="py-4">
        <div class="container">

            @foreach (SessionState::$data['flashes'] ?? [] as [$kind, $message])
                <div class="alert alert-{{ $kind }} no-print" role="alert">
                    {{ raw_t($message) }}</div>
            @endforeach
            @php
                unset(SessionState::$data['flashes']);
            @endphp

            @if (str_starts_with($path, '/admin/') && is_admin())
                <nav class="workspace-nav d-flex flex-wrap gap-2 mb-4 no-print"
                    aria-label="{{ raw_t('Shop management') }}">
                    @foreach (['dashboard' => 'Dashboard', 'orders' => 'Orders', 'customers' => 'Customers', 'services' => 'Services', 'payments' => 'Payments', 'enquiries' => 'Enquiries', 'notifications' => 'Notifications', 'reports' => 'Reports'] as $route => $name)
                        <a class="btn btn-sm {!! str_starts_with($path, '/admin/' . $route) ? 'btn-primary' : 'btn-outline-primary' !!}"
                            href="/admin/{{ $route }}">{{ raw_t($name) }}</a>
                    @endforeach
                    <form action="/admin/logout" method="post" class="ms-auto">{!! csrf_field() !!}<button
                            class="btn btn-sm btn-outline-secondary">{{ raw_t('Sign out') }}</button></form>
                </nav>
            @endif

            @if (str_starts_with($path, '/customer/') && actor() && !is_admin())
                <nav class="workspace-nav d-flex flex-wrap gap-2 mb-4 no-print">
                    @foreach (['dashboard' => 'My account', 'orders' => 'My orders', 'measurements' => 'Measurements', 'payments' => 'Payments'] as $route => $name)
                        <a class="btn btn-sm btn-outline-primary"
                            href="/customer/{{ $route }}">{{ raw_t($name) }}</a>
                    @endforeach
                    <form action="/customer/logout" method="post" class="ms-auto">{!! csrf_field() !!}<button
                            class="btn btn-sm btn-outline-secondary">{{ raw_t('Sign out') }}</button></form>
                </nav>
            @endif

            {!! $content !!}
        </div>
    </main>
    <footer class="site-footer no-print">
        <div class="container">
            <div class="row gy-4 footer-main">
                <div class="col-lg-5">
                    <p class="footer-brand"><img src="/static/img/brand-star.svg" alt="" width="38"
                            height="38">{{ SHOP_NAME }}</p>
                    <p class="footer-description">
                        {{ raw_t('Everyday essentials. Duty-ready uniforms. Thoughtfully stitched, just for you.') }}
                    </p><a href="tel:+91{{ SHOP_PHONE }}" class="footer-phone">+91 {{ SHOP_PHONE }} ↗</a>
                </div>
                <div class="col-6 col-lg-3">
                    <p class="footer-label">{{ raw_t('Explore') }}</p>
                    @foreach (['/services' => 'Services & pricing', '/gallery' => 'Our work', '/order' => 'Order online', '/enquiry' => 'Send us an enquiry', '/track-order' => 'Track your order'] as $href => $label)
                        <a href="{{ $href }}">{{ raw_t($label) }}</a>
                    @endforeach

                </div>
                <div class="col-6 col-lg-4">
                    <p class="footer-label">{{ raw_t('Visit the shop') }}</p>
                    <p>{{ SHOP_ADDRESS }}</p>
                    <p>{{ raw_t('Monday to Saturday, 10:00 AM – 8:00 PM') }}</p><a
                        href="https://www.google.com/maps/dir/?api=1&amp;destination={!! LATITUDE !!},{!! LONGITUDE !!}"
                        target="_blank" rel="noopener">{{ raw_t('Get directions') }} ↗</a>
                </div>
            </div>
            <div class="footer-bottom d-flex flex-wrap justify-content-between gap-3"><span>&copy;
                    {!! gmdate('Y') !!} {{ SHOP_NAME }}. {{ raw_t('All rights reserved.') }}</span><a
                    href="/admin/login">{{ raw_t('Staff sign in') }} ↗</a></div>
        </div>
    </footer>
    <script src="/static/vendor/bootstrap/bootstrap.bundle.min.js" defer></script>

    @if (str_ends_with($path, '/receipt'))
        <script src="/assets/js/print.js?v=1" defer></script>
    @endif

    @if ($path === '/')
        <script src="/static/js/premium.js?v=6" defer></script>
    @endif

    @if ($path === '/order' || $path === '/admin/orders/new')
        <script src="/assets/js/php-order.js?v=1" defer></script>
    @endif

    <script nonce="{{ $nonce }}">
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}));
        }
    </script>
</body>

</html>

@php
    unset(SessionState::$data['old']);
@endphp
