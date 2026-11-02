<?php

namespace App\Tailoring;

?>
<div class="d-flex flex-wrap gap-3 justify-content-between align-items-center mb-4">
    <div>
        <p class="section-label">{{ raw_t($admin ? 'Shop dashboard' : 'My account') }}</p>
        <h1 class="h3">{{ raw_t($dashboard ? 'Welcome' : 'Orders') }}{!! $dashboard ? ', ' . e(actor()['name']) : '' !!}</h1>
    </div><a class="btn btn-primary" href="{!! $admin ? '/admin/orders/new' : '/order' !!}">{{ raw_t('New order') }} ↗</a>
</div>

@if ($admin)
    <form class="row g-2 mb-4" method="get">
        <div class="col-md-7"><label class="visually-hidden" for="order-search">{{ raw_t('Search') }}</label><input
                class="form-control" id="order-search" name="q" value="{{ \request()->query()['q'] ?? '' }}"
                placeholder="{{ raw_t('Search customer, mobile or order number…') }}"></div>
        <div class="col-md-3"><label class="visually-hidden" for="status-filter">{{ raw_t('Status') }}</label><select
                class="form-select" name="status" id="status-filter">
                <option value="">{{ raw_t('All statuses') }}</option>
                @foreach (STATUSES as $s)
                    <option {!! $s === (\request()->query()['status'] ?? '') ? 'selected' : '' !!}>{{ $s }}</option>
                @endforeach

            </select></div>
        <div class="col-md-2"><button class="btn btn-primary w-100">{{ raw_t('Search') }}</button></div>
    </form>
@endif

@if ($dashboard)
    @php
        $open = count(array_filter($orders, fn($o) => $o['status'] !== 'DELIVERED'));
    @endphp
    @php
        $due = array_sum(array_map(fn($o) => cents($o['grand_total']) - cents($o['paid']), $orders));
    @endphp
    <div class="row g-3 mb-4">
        <div class="col-6"><a href="/customer/orders?view=open" class="card text-decoration-none">
                <div class="card-body">
                    <p class="section-label">{{ raw_t('Open orders') }}</p><strong
                        class="h3">{{ $open }}</strong>
                </div>
            </a></div>
        <div class="col-6"><a href="/customer/payments" class="card text-decoration-none">
                <div class="card-body">
                    <p class="section-label">{{ raw_t('Balance due') }}</p><strong
                        class="h3">{!! money(decimal($due)) !!}</strong>
                </div>
            </a></div>
    </div>
@endif

@include('pages.order_table')
