<?php

namespace App\Tailoring;

?>
<h1 class="h3 mb-4">{{ raw_t('Payments') }}</h1>
@if ($admin)
    <div class="d-flex gap-2 mb-4"><a class="btn btn-outline-primary"
            href="/admin/payments">{{ raw_t('All payments') }}</a><a class="btn btn-outline-primary"
            href="/admin/payments?status=PENDING">{{ raw_t('Pending payments') }}</a></div>
@endif
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table align-middle">
                <thead>
                    <tr>
                        <th>{{ raw_t('Order') }}</th>
                        <th>{{ raw_t('Amount') }}</th>
                        <th>{{ raw_t('Method') }}</th>
                        <th>{{ raw_t('Status') }}</th>
                        <th>{{ raw_t('Payment reference') }}</th>
                        <th>{{ raw_t('Receipt') }}</th>
                        @if ($admin)
                            <th>{{ raw_t('Action') }}</th>
                        @endif

                    </tr>
                </thead>
                <tbody>
                    @foreach ($payments as $payment)
                        <tr>
                            <td><a
                                    href="/{!! $admin ? 'admin' : 'customer' !!}/orders/{{ (int) $payment['order_id'] }}">{{ $payment['order_number'] }}</a>
                            </td>
                            <td>{!! money($payment['amount']) !!}</td>
                            <td>{{ $payment['method'] }}</td>
                            <td><span class="badge text-bg-{!! $payment['status'] === 'VERIFIED' ? 'success' : 'warning' !!}">{{ $payment['status'] }}</span>
                            </td>
                            <td>{{ $payment['transaction_reference'] ?: '—' }}</td>
                            <td><a href="/{!! $admin ? 'admin' : 'customer' !!}/payments/{{ (int) $payment['id'] }}/receipt"
                                    target="_blank" rel="noopener">{{ raw_t('Print receipt') }}</a></td>
                            @if ($admin)
                                <td>
                                    @if ($payment['status'] === 'PENDING')
                                        <form action="/admin/payments/{{ (int) $payment['id'] }}/verify"
                                            method="post">{!! csrf_field() !!}<label
                                                class="small d-block mb-2"><input type="checkbox" required>
                                                {{ raw_t('I have checked this payment.') }}</label><button
                                                class="btn btn-sm btn-primary">{{ raw_t('Verify payment') }}</button>
                                        </form>
                                    @endif
                                </td>
                            @endif

                        </tr>
                    @endforeach

                    @if (!$payments)
                        <tr>
                            <td colspan="7">{{ raw_t('No payments yet.') }}</td>
                        </tr>
                    @endif
                </tbody>
            </table>
        </div>
    </div>
</div>
