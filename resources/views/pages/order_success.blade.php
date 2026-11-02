<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center">
    <div class="col-md-7">
        <div class="card text-center">
            <div class="card-body py-5">
                <p class="section-label">{{ raw_t('Order confirmed') }}</p>
                <h1 class="display-6 mb-3">{{ raw_t('Thank you!') }}</h1>
                <p>{{ raw_t('Your order number is') }}</p><strong
                    class="display-6 d-block mb-4">{{ $order['order_number'] }}</strong>
                <p>{{ raw_t('Please save this number — you can use it with your mobile number to track your order.') }}
                </p>
                <dl class="row my-4 text-start">
                    <dt class="col-7">{{ raw_t('Grand total') }}</dt>
                    <dd class="col-5 text-end">{!! money($order['grand_total']) !!}</dd>
                    <dt class="col-7">{{ raw_t('Advance required') }}</dt>
                    <dd class="col-5 text-end">{!! money($order['required_advance']) !!}</dd>
                </dl>
                @if ($order['fabric_source'] === 'SHOP')
                    <p class="small text-secondary">
                        {{ raw_t('Material cost will be confirmed by the shop separately.') }}</p>
                @endif
                <a class="btn btn-primary" href="/track-order">{{ raw_t('Track your order') }}</a>
            </div>
        </div>
    </div>
</div>
