<?php

namespace App\Tailoring;

?>
<h1 class="h3 mb-4">{{ raw_t('Enquiries') }}</h1>
<div class="row g-3">
    @foreach ($enquiries as $enquiry)
        <div class="col-lg-6">
            <article class="card h-100">
                <div class="card-body"><span class="badge text-bg-secondary mb-3">{{ $enquiry['status'] }}</span>
                    <h2 class="h5">{{ $enquiry['name'] }}</h2><a
                        href="tel:+91{{ $enquiry['mobile'] }}">{{ $enquiry['mobile'] }}</a>
                    <p class="small mt-3">{!! nl2br(e($enquiry['message'])) !!}</p>
                    <p class="small text-secondary">{{ $enquiry['created_at'] }} UTC</p>
                    @if ($enquiry['converted_order_id'])
                        <a href="/admin/orders/{{ (int) $enquiry['converted_order_id'] }}">{{ raw_t('View order') }}</a>
                    @else
                        <form method="post" action="/admin/enquiries/{{ (int) $enquiry['id'] }}/status"
                            class="d-flex gap-2 mb-3">{!! csrf_field() !!}<label class="visually-hidden"
                                for="enquiry-{{ (int) $enquiry['id'] }}">{{ raw_t('Status') }}</label><select
                                class="form-select" id="enquiry-{{ (int) $enquiry['id'] }}" name="status">
                                @foreach (['NEW', 'CONTACTED', 'CLOSED'] as $s)
                                    <option {!! $enquiry['status'] === $s ? 'selected' : '' !!}>{{ $s }}</option>
                                @endforeach
                            </select><button class="btn btn-outline-primary">{{ raw_t('Save') }}</button></form>
                        <form method="post" action="/admin/enquiries/{{ (int) $enquiry['id'] }}/convert">
                            {!! csrf_field() !!}<button
                                class="btn btn-primary">{{ raw_t('Create order from enquiry') }}</button></form>
                    @endif

                </div>
            </article>
        </div>
    @endforeach

    @if (!$enquiries)
        <p class="text-secondary">{{ raw_t('No enquiries yet.') }}</p>
    @endif
</div>
