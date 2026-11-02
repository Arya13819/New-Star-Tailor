<?php

namespace App\Tailoring;

?>
<div class="d-flex flex-wrap justify-content-between gap-3 mb-4">
    <h1 class="h3">{{ raw_t('Services & pricing') }}</h1><a class="btn btn-primary"
        href="/admin/services/new">{{ raw_t('New service') }}</a>
</div>
<p class="text-secondary">
    {{ raw_t('Changing a price affects new orders only. Existing orders keep their captured prices.') }}</p>
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>{{ raw_t('Service') }}</th>
                        <th>{{ raw_t('Category') }}</th>
                        <th>{{ raw_t('Stitching price (₹)') }}</th>
                        <th>{{ raw_t('Status') }}</th>
                        <th>{{ raw_t('Action') }}</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($services as $service)
                        <tr>
                            <td>{{ $service['name_en'] }}<br><small
                                    class="text-secondary">{{ $service['name_hi'] }}</small>
                            </td>
                            <td>{{ $service['category'] }}</td>
                            <td>{!! $service['default_stitching_price'] !== null ? money($service['default_stitching_price']) : t('Not set') !!}</td>
                            <td>{{ raw_t($service['is_active'] ? 'Active' : 'Inactive') }}</td>
                            <td><a href="/admin/services/{{ (int) $service['id'] }}/edit">{{ raw_t('Edit') }}</a></td>
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    </div>
</div>
