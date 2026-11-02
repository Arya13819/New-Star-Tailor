<?php

namespace App\Tailoring;

?>

@php
    $paidAmount = paid((int) $order['id']);
@endphp
@php
    $balance = cents($order['grand_total']) - $paidAmount;
@endphp

<div class="d-flex flex-wrap justify-content-between gap-3 mb-3">
    <div>
        <p class="section-label">{{ raw_t('Order details') }}</p>
        <h1 class="h3">{{ $order['order_number'] }}</h1>
        <p class="small text-secondary">{{ $order['customer_name'] }} · {{ $order['customer_mobile'] }}</p>
    </div>
    <div><a class="btn btn-outline-primary" href="/{!! $admin ? 'admin' : 'customer' !!}/orders/{{ (int) $order['id'] }}/receipt"
            target="_blank" rel="noopener">{{ raw_t('Print receipt') }}</a></div>
</div>

@php
    progress($order['status']);
@endphp

@if (!$order['advance_satisfied'])
    <div class="alert alert-warning">{{ raw_t('Advance not fully received yet.') }}
        {{ raw_t('Advance required') }}: {!! money($order['required_advance']) !!}.
        {{ raw_t('The order still proceeds; this is a reminder only.') }}</div>
@endif

<div class="row g-4">
    <div class="col-lg-7">
        <div class="card mb-4">
            <div class="card-body">
                <h2 class="h5">{{ raw_t('Items') }}</h2>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>{{ raw_t('Service') }}</th>
                                <th>{{ raw_t('Qty') }}</th>
                                <th>{{ raw_t('Stitching') }}</th>
                                <th>{{ raw_t('Cloth') }}</th>
                                <th>{{ raw_t('Amount') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach ($items as $item)
                                <tr>
                                    <td>{{ $item['service_name_snapshot'] }}</td>
                                    <td>{{ (int) $item['quantity'] }}</td>
                                    <td>{!! money($item['stitching_price']) !!}</td>
                                    <td>{!! money($item['material_price']) !!}</td>
                                    <td>{!! money($item['line_total']) !!}</td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
                <p class="small text-secondary">{{ raw_t('Confirmed delivery date') }}:
                    {{ $order['confirmed_delivery_date'] ?: '—' }}</p>
                @if ($order['notes'])
                    <p>{!! nl2br(e($order['notes'])) !!}</p>
                @endif

                @if ($order['self_measurement_acknowledged'])
                    <p class="small text-secondary">
                        {{ raw_t('Self-submitted measurement responsibility acknowledged.') }}
                        {{ $order['self_measurement_acknowledged_at'] }} UTC</p>
                @endif

                @foreach ($items as $item)
                    @if ($item['measurement_version_id'])
                        @php
                            $version = one('SELECT * FROM measurement_versions WHERE id=?', [
                                $item['measurement_version_id'],
                            ]);
                        @endphp

                        <details class="mb-3">
                            <summary>{{ $item['service_name_snapshot'] }} · {{ raw_t('Measurement version') }}
                                {{ (int) $version['version_number'] }}</summary>
                            <dl class="row small mt-3">
                                @foreach (MEASUREMENT_FIELDS as $key => $label)
                                    <dt class="col-6">{{ raw_t($label) }}</dt>
                                    <dd class="col-6">{{ $version[$key] ?? '—' }}</dd>
                                @endforeach

                            </dl>
                        </details>
                    @endif
                @endforeach

            </div>
        </div>

        @if ($images)
            <div class="card mb-4">
                <div class="card-body">
                    <h2 class="h5">{{ raw_t('Reference photos') }}</h2>
                    <div class="d-flex flex-wrap gap-3">
                        @foreach ($images as $image)
                            <a href="/{!! $admin ? 'admin' : 'customer' !!}/orders/{{ (int) $order['id'] }}/images/{{ (int) $image['id'] }}"
                                target="_blank" rel="noopener"><img class="php-reference"
                                    src="/{!! $admin ? 'admin' : 'customer' !!}/orders/{{ (int) $order['id'] }}/images/{{ (int) $image['id'] }}"
                                    alt="{{ raw_t('Reference photo') }}" width="120" height="120"
                                    loading="lazy"></a>
                        @endforeach
                    </div>
                </div>
            </div>
        @endif

        @if ($admin)
            <div class="card">
                <div class="card-body">
                    <h2 class="h5">{{ raw_t('Order details') }}</h2>
                    <form action="/admin/orders/{{ (int) $order['id'] }}/details" method="post">
                        {!! csrf_field() !!}
                        @php
                            select_field(
                                'priority',
                                'Priority',
                                ['NORMAL' => 'Normal', 'URGENT' => 'Urgent'],
                                $order['priority'],
                            );
                        @endphp
                        @php
                            field(
                                'confirmed_delivery_date',
                                'Confirmed delivery date',
                                'date',
                                $order['confirmed_delivery_date'],
                            );
                        @endphp
                        @php
                            textarea_field('notes', 'Notes', $order['notes']);
                        @endphp
                        <button class="btn btn-primary">{{ raw_t('Save details') }}</button>
                    </form>
                </div>
            </div>
        @endif

    </div>
    <div class="col-lg-5">
        <div class="card mb-4">
            <div class="card-body">
                <h2 class="h5 mb-3">{{ raw_t('Financial summary') }}</h2>
                <dl class="row">
                    <dt class="col-7">{{ raw_t('Grand total') }}</dt>
                    <dd class="col-5 text-end">{!! money($order['grand_total']) !!}</dd>
                    <dt class="col-7">{{ raw_t('Paid (verified)') }}</dt>
                    <dd class="col-5 text-end">{!! money(decimal($paidAmount)) !!}</dd>
                    <dt class="col-7">{{ raw_t('Balance due') }}</dt>
                    <dd class="col-5 text-end fw-bold">{!! money(decimal($balance)) !!}</dd>
                </dl>

                @if ($admin)
                    <h3 class="h6 mt-4">{{ raw_t('Status') }}</h3>
                    <form action="/admin/orders/{{ (int) $order['id'] }}/status" method="post"
                        class="d-flex flex-wrap gap-2">{!! csrf_field() !!}
                        @foreach (STATUSES as $status)
                            @if ($status === $order['status'])
                                @continue
                            @endif
                            <button class="btn btn-sm btn-outline-primary" name="status"
                                value="{{ $status }}">{{ $status }}</button>
                        @endforeach
                    </form>
                @endif

            </div>
        </div>

        @if ($admin && $balance > 0)
            <div class="card mb-4">
                <div class="card-body">
                    <h2 class="h5">{{ raw_t('Record a payment') }}</h2>
                    <form action="/admin/orders/{{ (int) $order['id'] }}/payment" method="post">
                        {!! csrf_field() !!}<input type="hidden" name="submission" value="{{ $submission }}">
                        @php
                            field('amount', 'Amount (₹)', 'text', null, true);
                        @endphp
                        @php
                            select_field('method', 'Method', ['CASH' => 'Cash', 'UPI' => 'UPI', 'ONLINE' => 'Online']);
                        @endphp
                        @php
                            field('transaction_reference', 'Payment reference');
                        @endphp
                        @php
                            textarea_field('note', 'Note');
                        @endphp
                        <button class="btn btn-primary w-100">{{ raw_t('Record payment') }}</button>
                    </form>
                </div>
            </div>
        @endif

        <div class="card">
            <div class="card-body">
                <h2 class="h5">{{ raw_t('Payment history') }}</h2>
                @foreach ($payments as $payment)
                    <div class="border-bottom py-3"><strong>{!! money($payment['amount']) !!}</strong> ·
                        {{ $payment['method'] }}<br><small class="text-secondary">{{ $payment['status'] }} ·
                            {{ $payment['created_at'] }} UTC</small><br><a
                            href="/{!! $admin ? 'admin' : 'customer' !!}/payments/{{ (int) $payment['id'] }}/receipt"
                            target="_blank" rel="noopener">{{ raw_t('Print receipt') }}</a></div>
                @endforeach

                @if (!$payments)
                    <p class="small text-secondary">{{ raw_t('No payments yet.') }}</p>
                @endif

            </div>
        </div>
    </div>
</div>
