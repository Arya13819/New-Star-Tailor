<?php

namespace App\Tailoring;

?>

@include('pages.marketing.' . $GLOBALS['locale'] . '.services-top')

<section id="catalogue" class="catalogue-section">
    <div class="catalogue-heading">
        <div>
            <p class="section-label">{{ raw_t('FIND YOUR NEXT FIT') }}</p>
            <h2>{{ raw_t('The tailoring edit.') }}</h2>
        </div>
        <p>{{ raw_t('Clear prices. Personal fit. Care in every stitch.') }}</p>
    </div>
    <div class="catalogue-toolbar">
        <nav class="category-filters" aria-label="{{ raw_t('Service categories') }}">

            @foreach (['ALL' => 'All services'] + CATEGORIES as $code => $label)
                @php
                    $count =
                        $code === 'ALL' ? count($all) : count(array_filter($all, fn($s) => $s['category'] === $code));
                @endphp
                @if (!$count && $code !== 'ALL')
                    @continue
                @endif
                <a class="category-chip {!! $category === $code ? 'is-selected' : '' !!}" {!! $category === $code ? 'aria-current="true"' : '' !!}
                    href="/services?{{ http_build_query(['category' => $code, 'q' => $search]) }}#catalogue">{{ raw_t($label) }}
                    <span>{{ $count }}</span></a>
            @endforeach
        </nav>
        <form class="catalogue-search" method="get" action="/services#catalogue"><input type="hidden" name="category"
                value="{{ $category }}"><label class="visually-hidden"
                for="service-search">{{ raw_t('Search services') }}</label><input type="search" id="service-search"
                name="q" value="{{ $search }}" maxlength="80"
                placeholder="{{ raw_t('Search services') }}"><button type="submit"
                aria-label="{{ raw_t('Search services') }}">⌕</button></form>
    </div>
    <div class="catalogue-results"><span>{{ count($services) }} {{ raw_t('Services') }}</span><a
            href="/services#catalogue">{{ raw_t('Clear filters') }} ×</a></div>
    <div class="service-grid">
        @foreach ($services as $s)
            @php
                $name = $GLOBALS['locale'] === 'hi' && $s['name_hi'] ? $s['name_hi'] : $s['name_en'];
            @endphp
            <article class="catalogue-card" data-service="{{ $s['code'] }}">
                <div class="catalogue-photo">
                    @if (isset(PHOTOS[$s['code']]))
                        {!! product_image(PHOTOS[$s['code']], $name) !!}
                    @else
                        <div class="service-placeholder"><img src="/static/img/brand-star.svg" alt=""
                                width="80" height="80"></div>
                    @endif
                    <span class="service-category">{{ raw_t(CATEGORIES[$s['category']]) }}</span>
                </div>
                <div class="catalogue-card-body">
                    <p class="service-caption">{{ raw_t('TAILORED TO YOU') }}</p>
                    <h3>{{ $name }}</h3>
                    <p class="service-description">
                        {{ $s['description'] ?: raw_t('Cut to your measurements. Finished with care.') }}</p>
                    <div class="service-price-row">
                        <div>
                            @if ($s['default_stitching_price'] !== null)
                                <strong
                                    class="service-price">{!! money($s['default_stitching_price']) !!}</strong><small>{{ raw_t('Stitching only') }}</small>
                            @else
                                <strong
                                    class="service-price service-quote">{{ raw_t('Let’s talk fit.') }}</strong><small>{{ raw_t('Please call for pricing') }}</small>
                            @endif

                        </div><a class="service-action"
                            href="{!! $s['default_stitching_price'] !== null ? '/order?service=' . (int) $s['id'] : 'tel:+91' . e(SHOP_PHONE) !!}">{{ raw_t($s['default_stitching_price'] !== null ? 'Order online' : 'Call the shop') }}
                            ↗</a>
                    </div>
                </div>
            </article>
        @endforeach

        @if (!$services)
            <div class="catalogue-empty">
                <h3>{{ raw_t('No matching services') }}</h3>
                <p>{{ raw_t('Try another search or explore the full collection.') }}</p><a class="btn btn-primary"
                    href="/services#catalogue">{{ raw_t('All services') }}</a>
            </div>
        @endif
    </div>
    <p class="catalogue-disclaimer">
        {{ raw_t('Stitching charges only — cloth is billed separately, whether you bring your own or the shop provides it.') }}
    </p>
</section>

@include('pages.marketing.' . $GLOBALS['locale'] . '.services-bottom')
