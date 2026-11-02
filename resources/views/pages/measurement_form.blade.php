<?php

namespace App\Tailoring;

?>
<h1 class="h3 mb-4">{{ raw_t('New measurement version') }} — {{ $customer['name'] }}</h1>
<div class="card">
    <div class="card-body">
        <form method="post">{!! csrf_field() !!}<p class="small text-secondary">
                {{ raw_t('Saving creates a new version. Previous orders keep their original measurements.') }}</p>
            <div class="row">
                @foreach (MEASUREMENT_FIELDS as $key => $label)
                    <div class="col-6 col-lg-4">
                        @php
                            field($key, $label, 'number', old($key, $last[$key] ?? ''));
                        @endphp
                    </div>
                @endforeach
            </div>
            @php
                select_field(
                    'fitting_preference',
                    'Fitting preference',
                    ['NORMAL' => 'Normal', 'SLIM' => 'Slim', 'LOOSE' => 'Loose'],
                    old('fitting_preference', $last['fitting_preference'] ?? 'NORMAL'),
                );
            @endphp
            @php
                field('allowance', 'Allowance', 'text', old('allowance', $last['allowance'] ?? ''));
            @endphp
            @php
                textarea_field(
                    'measurement_notes',
                    'Measurement notes',
                    old('measurement_notes', $last['notes'] ?? ''),
                );
            @endphp
            @php
                textarea_field(
                    'alteration_notes',
                    'Alteration notes',
                    old('alteration_notes', $last['alteration_notes'] ?? ''),
                );
            @endphp
            <button class="btn btn-primary">{{ raw_t('Save new version') }}</button>
        </form>
    </div>
</div>
