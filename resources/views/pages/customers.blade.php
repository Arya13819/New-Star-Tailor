<?php

namespace App\Tailoring;

?>
<div class="d-flex flex-wrap justify-content-between gap-3 mb-4">
    <h1 class="h3">{{ raw_t('Customers') }}</h1><a class="btn btn-primary"
        href="/admin/customers/new">{{ raw_t('New customer') }}</a>
</div>
<form method="get" class="d-flex gap-2 mb-4"><label class="visually-hidden"
        for="customer-search">{{ raw_t('Search') }}</label><input id="customer-search" class="form-control" name="q"
        value="{{ \request()->query()['q'] ?? '' }}" placeholder="{{ raw_t('Name or mobile') }}"><button
        class="btn btn-primary">{{ raw_t('Search') }}</button></form>
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>{{ raw_t('Name') }}</th>
                        <th>{{ raw_t('Mobile number') }}</th>
                        <th>{{ raw_t('Address') }}</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($customers as $customer)
                        <tr>
                            <td><a href="/admin/customers/{{ (int) $customer['id'] }}">{{ $customer['name'] }}</a></td>
                            <td>{{ $customer['mobile'] }}</td>
                            <td>{{ $customer['address'] }}</td>
                        </tr>
                    @endforeach

                    @if (!$customers)
                        <tr>
                            <td colspan="3">{{ raw_t('No customers yet.') }}</td>
                        </tr>
                    @endif
                </tbody>
            </table>
        </div>
    </div>
</div>
