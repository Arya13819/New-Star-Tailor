<?php

namespace App\Tailoring;

?>
<h2 class="h4 mb-3">{{ raw_t('Measurements') }}</h2>
<p class="small text-secondary">
    {{ raw_t('Measurements are in inches. Previous versions remain unchanged for existing orders.') }}</p>

@foreach ($measurements as $i => $version)
    <details class="card mb-3" {!! $i === 0 ? 'open' : '' !!}>
        <summary class="card-body">{{ $version['name'] ?? '' }} · {{ raw_t('Version') }}
            {{ (int) $version['version_number'] }} · {{ $version['created_at'] }} UTC</summary>
        <div class="card-body pt-0">
            <dl class="row mb-0">
                @foreach (MEASUREMENT_FIELDS as $key => $label)
                    <dt class="col-6 col-md-3">{{ raw_t($label) }}</dt>
                    <dd class="col-6 col-md-3">{{ $version[$key] ?? '—' }}</dd>
                @endforeach
                <dt class="col-6">
                    {{ raw_t('Fitting preference') }}</dt>
                <dd class="col-6">{{ $version['fitting_preference'] ?: '—' }}</dd>
            </dl>
            <p class="small">{!! nl2br(e($version['notes'] ?? '')) !!}</p>
        </div>
    </details>
@endforeach

@if (!$measurements)
    <p class="text-secondary">{{ raw_t('No measurements yet.') }}</p>
@endif
