<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center">
    <div class="col-md-8">
        <h1 class="h3 mb-4">{{ raw_t($title) }}</h1>
        <div class="card">
            <div class="card-body">
                <form method="post">{!! csrf_field() !!}
                    @php
                        field('name', 'Full name', 'text', old('name', $customer['name'] ?? ''), true);
                    @endphp
                    @php
                        field('mobile', 'Mobile number', 'tel', old('mobile', $customer['mobile'] ?? ''), true);
                    @endphp
                    @php
                        textarea_field('address', 'Address', old('address', $customer['address'] ?? ''));
                    @endphp
                    @php
                        textarea_field('notes', 'Notes', old('notes', $customer['notes'] ?? ''));
                    @endphp
                    <button class="btn btn-primary">{{ raw_t('Save') }}</button>
                </form>
            </div>
        </div>
    </div>
</div>
