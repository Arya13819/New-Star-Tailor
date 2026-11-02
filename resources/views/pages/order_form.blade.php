<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center">
    <div class="col-12 col-lg-9">
        <p class="section-label text-center">{{ raw_t('Order online') }}</p>
        <h1 class="display-6 text-center mb-4">{{ raw_t($title) }}</h1>

        @if (!$services)
            <div class="alert alert-warning">
                {{ raw_t('Online ordering is temporarily unavailable — please call the shop.') }}</div>
        @else
            <div class="card">
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data" id="online-order">{!! csrf_field() !!}<input
                            type="hidden" name="submission" value="{{ $submission }}">

                        @if ($admin)
                            @php
                                $options = ['' => 'Choose a customer'];
                            @endphp
                            @foreach ($customers as $c)
                                @php
                                    $options[$c['id']] = $c['name'] . ' · ' . $c['mobile'];
                                @endphp
                            @endforeach
                            @php
                                select_field(
                                    'customer_id',
                                    'Customer',
                                    $options,
                                    old('customer_id', \request()->query()['customer'] ?? ''),
                                );
                            @endphp
                            <p><a href="/admin/customers/new">{{ raw_t('New customer') }} ↗</a></p>

                            @if (!empty(\request()->query()['enquiry']))
                                <input type="hidden" name="enquiry_id"
                                    value="{{ (int) \request()->query()['enquiry'] }}">
                            @endif
                        @elseif(actor())
                            <div class="alert alert-light border"><strong>{{ actor()['name'] }}</strong> ·
                                {{ actor()['mobile'] }}</div>
                        @else
                            @php
                                field('name', 'Full name', 'text', null, true);
                            @endphp
                            @php
                                field('mobile', 'Mobile number', 'tel', null, true);
                            @endphp
                            @php
                                textarea_field('address', 'Address');
                            @endphp
                        @endif

                        <h2 class="h6 section-label mt-4">{{ raw_t('Services') }}</h2>
                        <div id="item-rows">

                            @php
                                $selectedIds = old('service_id', [(int) (\request()->query()['service'] ?? 0)]);
                            @endphp
                            @if (!is_array($selectedIds))
                                @php
                                    $selectedIds = [0];
                                @endphp
                            @endif
                            @php
                                $selectedIds = array_slice($selectedIds, 0, 20);
                            @endphp
                            @foreach ($selectedIds as $index => $selectedId)
                                <div class="php-item-row border-bottom pb-3 mb-3" data-row>
                                    <div><label class="form-label"
                                            for="service-{{ $index }}">{{ raw_t('Service') }}</label><select
                                            class="form-select" name="service_id[]" id="service-{{ $index }}"
                                            data-service required>
                                            <option value="">{{ raw_t('Choose a service') }}</option>
                                            @foreach ($services as $s)
                                                <option value="{{ (int) $s['id'] }}"
                                                    data-price="{{ $s['default_stitching_price'] ?? '' }}"
                                                    {!! (int) $selectedId === (int) $s['id'] ? 'selected' : '' !!}>
                                                    {{ $GLOBALS['locale'] === 'hi' && $s['name_hi'] ? $s['name_hi'] : $s['name_en'] }}
                                                    — {!! $s['default_stitching_price'] !== null ? money($s['default_stitching_price']) : t('Please call for pricing') !!}</option>
                                            @endforeach

                                        </select></div>
                                    <div><label class="form-label"
                                            for="qty-{{ $index }}">{{ raw_t('Qty') }}</label><input
                                            class="form-control" id="qty-{{ $index }}" type="number"
                                            name="quantity[]" value="{{ old('quantity', [])[$index] ?? 1 }}"
                                            min="1" max="99" required></div><button type="button"
                                        class="btn btn-outline-danger" data-remove
                                        aria-label="{{ raw_t('Remove service') }}">×</button>

                                    @if ($admin)
                                        <div><label class="form-label"
                                                for="stitch-{{ $index }}">{{ raw_t('Stitching price (₹)') }}</label><input
                                                class="form-control" data-stitch id="stitch-{{ $index }}"
                                                name="stitching_price[]" inputmode="decimal"
                                                value="{{ old('stitching_price', [])[$index] ?? '' }}" required></div>
                                        <div><label class="form-label"
                                                for="cloth-{{ $index }}">{{ raw_t('Cloth price (₹)') }}</label><input
                                                class="form-control" id="cloth-{{ $index }}"
                                                name="material_price[]" inputmode="decimal"
                                                value="{{ old('material_price', [])[$index] ?? '0' }}" required></div>
                                    @endif

                                </div>
                            @endforeach

                        </div>
                        <button type="button" class="btn btn-outline-secondary btn-sm mb-4"
                            id="add-item-row">{{ raw_t('+ Add another service') }}</button>

                        @php
                            select_field(
                                'fabric_source',
                                'Who provides the cloth?',
                                ['CUSTOMER' => 'Customer brings cloth', 'SHOP' => 'Shop provides cloth'],
                                'CUSTOMER',
                            );
                        @endphp

                        <p class="small text-secondary">
                            {{ raw_t('Stitching charges only — cloth is billed separately, whether you bring your own or the shop provides it.') }}
                            {{ raw_t('If the shop is providing the cloth, our staff will call you to discuss fabric options and confirm the material cost.') }}
                        </p>

                        @if ($admin)
                            @php
                                select_field(
                                    'priority',
                                    'Priority',
                                    ['NORMAL' => 'Normal', 'URGENT' => 'Urgent'],
                                    'NORMAL',
                                );
                            @endphp
                            @php
                                field('confirmed_delivery_date', 'Confirmed delivery date', 'date');
                            @endphp
                        @endif
                        @php
                            field('requested_delivery_date', 'Customer requested date', 'date');
                        @endphp
                        @php
                            textarea_field('notes', 'Notes');
                        @endphp

                        <h2 class="h6 section-label mt-4">{{ raw_t('Measurements') }}</h2><label
                            class="form-check mb-3"><input class="form-check-input" type="checkbox"
                                id="provide_measurements" name="provide_measurements" value="1"
                                {!! old('provide_measurements') ? 'checked' : '' !!}> {{ raw_t('Provide measurements (optional)') }}</label>
                        <fieldset id="measurement-fields" class="border rounded p-3 mb-4">
                            <legend class="float-none w-auto px-2 fs-6">{{ raw_t('Measurements') }}
                                ({{ raw_t('inches') }})</legend>
                            <div class="row">
                                @foreach (MEASUREMENT_FIELDS as $name => $label)
                                    <div class="col-6">
                                        @php
                                            field($name, $label, 'number');
                                        @endphp
                                    </div>
                                @endforeach
                            </div>
                            @php
                                select_field(
                                    'fitting_preference',
                                    'Fitting preference',
                                    ['NORMAL' => 'Normal', 'SLIM' => 'Slim', 'LOOSE' => 'Loose'],
                                    'NORMAL',
                                );
                            @endphp
                            @php
                                field('allowance', 'Allowance');
                            @endphp
                            @php
                                textarea_field('measurement_notes', 'Measurement notes');
                            @endphp
                            <label class="form-check"><input class="form-check-input" type="checkbox"
                                    name="measurement_ack" value="1" {!! old('measurement_ack') ? 'checked' : '' !!}>
                                {{ raw_t('I am responsible for the accuracy of the measurements I submit.') }}</label>
                        </fieldset>
                        <label for="reference_image" class="form-label">{{ raw_t('Reference photo') }} (JPG, PNG, WebP
                            · 8
                            MB)</label><input class="form-control mb-4" type="file" id="reference_image"
                            name="reference_image" accept="image/jpeg,image/png,image/webp">
                        <h2 class="h6 section-label">{{ raw_t('Payment') }}</h2>
                        <p class="small text-secondary">
                            {{ raw_t('Online payment references remain pending until staff verify them. This website does not collect card details.') }}
                        </p>

                        @php
                            field('payment_reference', 'Payment reference');
                        @endphp
                        @php
                            field('payment_amount', 'Payment amount (₹)', 'text', '0');
                        @endphp

                        <button class="btn btn-primary btn-lg w-100 mt-3">{{ raw_t('Place order') }}</button>
                    </form>
                </div>
            </div>
        @endif

    </div>
</div>
