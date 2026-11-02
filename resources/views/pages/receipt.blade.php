<?php

namespace App\Tailoring;

?>

@php
    $received = paid((int) $order['id']);
@endphp
<div class="print-area card receipt-card mx-auto php-receipt">
    <div class="receipt-header"><img src="/static/img/brand-star.svg" width="52" height="52" alt="">
        <div><strong class="receipt-shop-name">{{ SHOP_NAME }}</strong>
            <p class="receipt-shop-meta mb-0">{{ SHOP_ADDRESS }}<br>+91 {{ SHOP_PHONE }}</p>
        </div>
    </div>
    <div class="receipt-band">{{ raw_t('Order receipt') }} <span>{{ $order['order_number'] }}</span></div>
    <div class="receipt-body">
        <p>{{ $order['customer_name'] }} · {{ $order['customer_mobile'] }}</p>
        <p class="small">{{ raw_t('Status') }}: {{ $order['status'] }} · {{ raw_t('Confirmed delivery date') }}:
            {{ $order['confirmed_delivery_date'] ?: '—' }}</p>
        <div class="table-responsive">
            <table class="receipt-table">
                <thead>
                    <tr>
                        <th>{{ raw_t('Service') }}</th>
                        <th>{{ raw_t('Qty') }}</th>
                        <th class="text-end">{{ raw_t('Amount') }}</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($items as $item)
                        <tr>
                            <td>{{ $item['service_name_snapshot'] }}</td>
                            <td>{{ (int) $item['quantity'] }}</td>
                            <td class="text-end">{!! money($item['line_total']) !!}</td>
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
        <div class="receipt-totals">
            <div class="row-line"><span>{{ raw_t('Stitching') }}</span><span>{!! money($order['subtotal_stitching']) !!}</span></div>
            <div class="row-line"><span>{{ raw_t('Cloth') }}</span><span>{!! money($order['subtotal_material']) !!}</span></div>
            <div class="row-line grand"><span>{{ raw_t('Grand total') }}</span><span>{!! money($order['grand_total']) !!}</span>
            </div>
            <div class="row-line paid"><span>{{ raw_t('Paid (verified)') }}</span><span>{!! money(decimal($received)) !!}</span>
            </div>
            <div class="row-line balance"><span>{{ raw_t('Balance due') }}</span><span>{!! money(decimal(cents($order['grand_total']) - $received)) !!}</span>
            </div>
        </div>
        <p class="small text-secondary mt-4">{{ raw_t('Stitching and cloth, billed separately.') }}</p><button
            class="btn btn-primary no-print" data-print>{{ raw_t('Print receipt') }}</button>
    </div>
</div>
