<?php

namespace App\Tailoring;

?>
<h1 class="h3 mb-4">{{ raw_t('Notifications') }}</h1>
<div class="alert alert-info">
    {{ raw_t('SMS sending is not configured. Messages below are queued only and are not marked as sent.') }}</div>
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>{{ raw_t('Type') }}</th>
                        <th>{{ raw_t('Mobile number') }}</th>
                        <th>{{ raw_t('Message') }}</th>
                        <th>{{ raw_t('Status') }}</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($notifications as $n)
                        <tr>
                            <td>{{ $n['type'] }}</td>
                            <td>{{ $n['to_address'] }}</td>
                            <td>{{ $n['body'] }}</td>
                            <td>{{ $n['status'] }}</td>
                        </tr>
                    @endforeach

                    @if (!$notifications)
                        <tr>
                            <td colspan="4">{{ raw_t('No notifications yet.') }}</td>
                        </tr>
                    @endif
                </tbody>
            </table>
        </div>
    </div>
</div>
