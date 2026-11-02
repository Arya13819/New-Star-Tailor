<?php

namespace App\Tailoring;

?>
<h1 class="h3 mb-4">{{ raw_t('Reports') }}</h1>
<form class="row g-2 mb-4" method="get">
    <div class="col-md-3">
        @php
            select_field(
                'period',
                'Period',
                ['today' => 'Today', 'week' => 'This week', 'month' => 'This month', 'custom' => 'Custom'],
                $period,
            );
        @endphp
    </div>
    <div class="col-md-3">
        @php
            field('from', 'From', 'date', \request()->query()['from'] ?? '');
        @endphp
    </div>
    <div class="col-md-3">
        @php
            field('to', 'To', 'date', \request()->query()['to'] ?? '');
        @endphp
    </div>
    <div class="col-md-3 align-self-center"><button class="btn btn-primary w-100">{{ raw_t('Apply') }}</button></div>
</form>
<div class="card mb-4">
    <div class="card-body">
        <p class="section-label">{{ raw_t('Revenue — verified payments only') }}</p><strong
            class="h2">{!! money(decimal($revenue)) !!}</strong>
        <p class="small text-secondary mt-2">
            {{ raw_t('Reporting dates use Asia/Kolkata. Timestamps are stored in UTC.') }}</p>
    </div>
</div>
<div class="card mb-4">
    <div class="card-body">
        <h2 class="h5">{{ raw_t('Order value by category') }}</h2>
        <p class="small text-secondary">{{ raw_t('These are order totals, not collected revenue.') }}</p>
        <dl class="row">
            @foreach ($categories as $c)
                <dt class="col-6">{{ $c['category'] }}</dt>
                <dd class="col-6 text-end">{!! money($c['total']) !!}</dd>
            @endforeach

        </dl>
    </div>
</div>
@php
    $admin = true;
@endphp
@include('pages.payments')
