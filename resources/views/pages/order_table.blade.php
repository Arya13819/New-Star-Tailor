<?php

namespace App\Tailoring;

?>
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table align-middle">
                <thead>
                    <tr>
                        <th>{{ raw_t('Order') }}</th>
                        @if ($admin)
                            <th>{{ raw_t('Customer') }}</th>
                        @endif
                        <th>{{ raw_t('Status') }}</th>
                        <th>{{ raw_t('Delivery') }}</th>
                        <th class="text-end">{{ raw_t('Total') }}</th>
                        <th class="text-end">{{ raw_t('Balance due') }}</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($orders as $o)
                        <tr>
                            <td><a
                                    href="/{!! $admin ? 'admin' : 'customer' !!}/orders/{{ (int) $o['id'] }}">{{ $o['order_number'] }}</a>
                                @if ($o['priority'] === 'URGENT')
                                    <span class="badge text-bg-danger ms-2">{{ raw_t('Urgent') }}</span>
                                @endif
                            </td>

                            @if ($admin)
                                <td>{{ $o['customer_name'] ?? '' }}</td>
                            @endif
                            <td><span class="badge text-bg-secondary">{{ $o['status'] }}</span></td>
                            <td>{{ $o['confirmed_delivery_date'] ?: '—' }}</td>
                            <td class="text-end">{!! money($o['grand_total']) !!}</td>
                            <td class="text-end">{!! money(decimal(cents($o['grand_total']) - cents($o['paid']))) !!}</td>
                        </tr>
                    @endforeach

                    @if (!$orders)
                        <tr>
                            <td colspan="6" class="py-4 text-secondary">{{ raw_t('No orders yet.') }}</td>
                        </tr>
                    @endif
                </tbody>
            </table>
        </div>
        @if ($admin)
            <p class="small text-secondary mb-0">
                {{ raw_t('Showing up to 500 matching records. Use search and filters to narrow results.') }}</p>
        @endif

    </div>
</div>
