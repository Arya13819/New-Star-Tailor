<?php

namespace App\Tailoring;

?>
<div class="card print-area php-receipt mx-auto">
    <div class="card-body"><img src="/static/img/brand-star.svg" width="52" height="52" alt="">
        <h1 class="h3 mt-3">{{ SHOP_NAME }}</h1>
        <p class="small text-secondary">{{ SHOP_ADDRESS }}<br>+91 {{ SHOP_PHONE }}</p>
        <hr>
        <h2 class="h4">{{ raw_t('Payment receipt') }} #{{ (int) $payment['id'] }}</h2>
        <p>{{ $payment['order_number'] }} · {{ $payment['customer_name'] }}</p><strong
            class="h2">{!! money($payment['amount']) !!}</strong>
        <dl class="row mt-4">
            <dt class="col-5">{{ raw_t('Method') }}</dt>
            <dd class="col-7">{{ $payment['method'] }}</dd>
            <dt class="col-5">{{ raw_t('Status') }}</dt>
            <dd class="col-7">{{ $payment['status'] }}</dd>
            <dt class="col-5">{{ raw_t('Payment reference') }}</dt>
            <dd class="col-7">{{ $payment['transaction_reference'] ?: '—' }}</dd>
            <dt class="col-5">{{ raw_t('Verified at') }}</dt>
            <dd class="col-7">{{ $payment['verified_at'] ?: '—' }} UTC</dd>
        </dl>
        @if ($payment['status'] !== 'VERIFIED')
            <p class="alert alert-warning">
                {{ raw_t('This payment has not been verified and is not counted as paid.') }}</p>
        @endif
        <button class="btn btn-primary no-print" data-print>{{ raw_t('Print receipt') }}</button>
    </div>
</div>
