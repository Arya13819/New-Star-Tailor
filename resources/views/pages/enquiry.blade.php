<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center">
    <div class="col-md-7">
        <p class="section-label text-center">{{ raw_t('Enquiry') }}</p>
        <h1 class="display-6 text-center mb-4">{{ raw_t('Send us an enquiry') }}</h1>
        <div class="card">
            <div class="card-body">
                <form method="post">{!! csrf_field() !!}
                    @php
                        field('name', 'Full name', 'text', null, true);
                    @endphp
                    @php
                        field('mobile', 'Mobile number', 'tel', null, true);
                    @endphp
                    @php
                        textarea_field('address', 'Address');
                    @endphp
                    @php
                        textarea_field('message', 'Message');
                    @endphp
                    <button class="btn btn-primary w-100">{{ raw_t('Send enquiry') }}</button>
                </form>
            </div>
        </div>
    </div>
</div>
