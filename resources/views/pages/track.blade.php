<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center">
    <div class="col-lg-7">
        <p class="section-label text-center">{{ raw_t('Track your order') }}</p>
        <h1 class="display-6 text-center mb-3">{{ raw_t('Check your order status') }}</h1>
        <p class="text-center text-secondary">
            {{ raw_t('Enter the order number on your receipt and the mobile number used for your order.') }}</p>
        <div class="card mb-4">
            <div class="card-body">
                <form method="post">{!! csrf_field() !!}
                    @php
                        field('order_number', 'Order number', 'text', null, true);
                    @endphp
                    @php
                        field('mobile', 'Mobile number', 'tel', null, true);
                    @endphp
                    <button class="btn btn-primary w-100">{{ raw_t('Check status') }}</button>
                </form>
            </div>
        </div>

        @if ($notFound)
            <div class="alert alert-warning">
                {{ raw_t('We could not find an order matching that order number and mobile number.') }}</div>
        @endif

        @if ($result)
            @php
                $paid = paid((int) $result['id']);
            @endphp
            <div class="card">
                <div class="card-body">
                    <h2 class="h4">{{ $result['order_number'] }}</h2><span
                        class="badge text-bg-secondary">{{ $result['status'] }}</span>
                    @php
                        progress($result['status']);
                    @endphp
                    <dl class="row">
                        <dt class="col-7">{{ raw_t('Grand total') }}</dt>
                        <dd class="col-5 text-end">{!! money($result['grand_total']) !!}</dd>
                        <dt class="col-7">{{ raw_t('Paid') }}</dt>
                        <dd class="col-5 text-end">{!! money(decimal($paid)) !!}</dd>
                        <dt class="col-7">{{ raw_t('Balance due') }}</dt>
                        <dd class="col-5 text-end">{!! money(decimal(cents($result['grand_total']) - $paid)) !!}</dd>
                    </dl>
                    @if ($result['confirmed_delivery_date'])
                        <p class="small text-secondary">{{ raw_t('Confirmed delivery date') }}:
                            {{ $result['confirmed_delivery_date'] }}</p>
                    @endif

                </div>
            </div>
        @endif

    </div>
</div>
