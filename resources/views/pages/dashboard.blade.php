<?php

namespace App\Tailoring;

?>
<div class="d-flex flex-wrap gap-3 justify-content-between align-items-center mb-4">
    <div>
        <p class="section-label">{{ raw_t('Shop dashboard') }}</p>
        <h1 class="h3">{{ raw_t('Welcome') }}, {{ actor()['name'] }}</h1>
    </div><a href="/admin/orders/new" class="btn btn-primary">{{ raw_t('New order') }} ↗</a>
</div>
<form action="/admin/orders" method="get" class="d-flex gap-2 mb-4" role="search"><label class="visually-hidden"
        for="global-search">{{ raw_t('Search') }}</label><input class="form-control" id="global-search" name="q"
        placeholder="{{ raw_t('Search customer, mobile or order number…') }}"><button
        class="btn btn-primary">{{ raw_t('Search') }}</button></form>
<div class="row g-3 mb-4">
    @foreach ($counts as $status => $count)
        <div class="col-6 col-lg-3"><a class="card text-decoration-none"
                href="/admin/orders?status={{ $status }}">
                <div class="card-body">
                    <p class="section-label">{{ $status }}</p><strong class="h2">{{ $count }}</strong>
                </div>
            </a></div>
    @endforeach
</div>
<div class="card mb-4">
    <div class="card-body">
        <p class="section-label">{{ raw_t('Outstanding balance') }}</p><strong
            class="h2">{!! money($outstanding) !!}</strong>
        <div class="d-flex flex-wrap gap-2 mt-4"><a href="/admin/customers/new"
                class="btn btn-outline-primary">{{ raw_t('New customer') }}</a><a href="/admin/orders?view=today"
                class="btn btn-outline-primary">{{ raw_t("Today's deliveries") }}</a><a
                href="/admin/orders?view=overdue" class="btn btn-outline-primary">{{ raw_t('Overdue') }}</a><a
                href="/admin/orders?view=urgent" class="btn btn-outline-primary">{{ raw_t('Urgent') }}</a><a
                href="/admin/payments?status=PENDING"
                class="btn btn-outline-primary">{{ raw_t('Pending payments') }}</a></div>
    </div>
</div>
<h2 class="h5 mb-3">{{ raw_t('Recent orders') }}</h2>
@php
    $admin = true;
@endphp
@include('pages.order_table')
