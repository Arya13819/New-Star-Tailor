<?php

namespace App\Tailoring;

?>
<div class="auth-shell row justify-content-center">
    <div class="col-12 col-md-6 col-lg-5">
        <div class="card auth-card">
            <div class="card-body p-4">
                <p class="section-label">{{ raw_t('WELCOME TO NEW STAR TAILOR') }}</p>
                <h1 class="h3 mb-4">{{ raw_t($title) }}</h1>
                <form method="post">{!! csrf_field() !!}

                    @if ($mode === 'register' || $mode === 'setup')
                        @php
                            field('name', 'Full name', 'text', null, true);
                        @endphp
                    @endif

                    @if ($mode === 'setup')
                        @php
                            field('setup_key', 'Setup key', 'password', null, true);
                        @endphp
                        @php
                            field('email', 'Email', 'email', null, true);
                        @endphp
                    @endif

                    @if ($mode === 'admin')
                        @php
                            field('identifier', 'Email or mobile', 'text', null, true);
                        @endphp
                    @else
                        @php
                            field('mobile', 'Mobile number', 'tel', null, true);
                        @endphp
                    @endif

                    @if ($mode === 'register')
                        @php
                            textarea_field('address', 'Address');
                        @endphp
                    @endif

                    @php
                        field('password', 'Password', 'password', null, true);
                    @endphp
                    @if (in_array($mode, ['register', 'setup'], true))
                        @php
                            field('confirm_password', 'Confirm password', 'password', null, true);
                        @endphp
                    @else
                        <label class="form-check mb-3"><input class="form-check-input" type="checkbox" name="remember"
                                value="1"> {{ raw_t('Keep me signed in') }}</label>
                    @endif

                    <button class="btn btn-primary btn-lg w-100">{{ raw_t($title) }}</button>
                </form>

                @if ($mode === 'login')
                    <p class="small text-center mt-4 mb-0">{{ raw_t("Don't have an account?") }} <a
                            href="/customer/register">{{ raw_t('Create account') }}</a></p>
                @elseif($mode === 'register')
                    <p class="small text-center mt-4 mb-0"><a href="/customer/login">{{ raw_t('Sign in') }}</a></p>
                @endif

            </div>
        </div>
    </div>
</div>
