<?php

namespace App\Tailoring;

?>
<div class="d-flex flex-wrap justify-content-between gap-3 mb-4">
    <div>
        <h1 class="h3">{{ $customer['name'] }}</h1>
        <p class="text-secondary">{{ $customer['mobile'] }} · {{ $customer['address'] }}</p>
    </div>
    <div class="d-flex flex-wrap gap-2 align-self-start"><a class="btn btn-outline-primary"
            href="/admin/customers/{{ (int) $customer['id'] }}/edit">{{ raw_t('Edit customer') }}</a><a
            class="btn btn-outline-primary"
            href="/admin/customers/{{ (int) $customer['id'] }}/measurements/new">{{ raw_t('New measurement version') }}</a><a
            class="btn btn-primary"
            href="/admin/orders/new?customer={{ (int) $customer['id'] }}">{{ raw_t('New order') }}</a></div>
</div>
<h2 class="h5 mb-3">{{ raw_t('Orders') }}</h2>
@php
    $admin = true;
@endphp
@include('pages.order_table')

<div class="mt-4">
    @include('pages.measurements')
</div>
