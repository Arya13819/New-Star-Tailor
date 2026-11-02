<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center">
    <div class="col-lg-8">
        <h1 class="h3 mb-4">{{ raw_t($title) }}</h1>
        <div class="card">
            <div class="card-body">
                <form method="post">{!! csrf_field() !!}
                    @if (!$service)
                        @php
                            field('code', 'Service code', 'text', null, true);
                        @endphp
                    @endif
                    @php
                        field('name_en', 'Name (English)', 'text', old('name_en', $service['name_en'] ?? ''), true);
                    @endphp
                    @php
                        field('name_hi', 'Name (Hindi)', 'text', old('name_hi', $service['name_hi'] ?? ''));
                    @endphp
                    @php
                        select_field(
                            'category',
                            'Category',
                            CATEGORIES,
                            old('category', $service['category'] ?? 'SHIRT'),
                        );
                    @endphp
                    @php
                        field(
                            'default_stitching_price',
                            'Stitching price (₹)',
                            'text',
                            old('default_stitching_price', $service['default_stitching_price'] ?? ''),
                        );
                    @endphp
                    @php
                        field('sort_order', 'Sort order', 'number', old('sort_order', $service['sort_order'] ?? 100));
                    @endphp
                    @php
                        textarea_field('description', 'Description', old('description', $service['description'] ?? ''));
                    @endphp
                    <label class="form-check mb-4"><input class="form-check-input" type="checkbox" name="is_active"
                            value="1" {!! old('is_active', $service['is_active'] ?? 1) ? 'checked' : '' !!}> {{ raw_t('Active') }}</label><button
                        class="btn btn-primary">{{ raw_t('Save') }}</button>
                </form>
            </div>
        </div>
    </div>
</div>
