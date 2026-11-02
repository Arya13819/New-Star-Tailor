<?php

namespace App\Tailoring;

?>
<div class="auth-shell row justify-content-center"><div class="col-12 col-md-6 col-lg-5"><div class="card auth-card"><div class="card-body p-4"><p class="section-label"><?= t('WELCOME TO NEW STAR TAILOR')?></p><h1 class="h3 mb-4"><?= t($title)?></h1><form method="post"><?= csrf_field()?>
<?php if ($mode === 'register' || $mode === 'setup') {
    field('name', 'Full name', 'text', null, true);
} ?>
<?php if ($mode === 'setup') {
    field('setup_key', 'Setup key', 'password', null, true);
    field('email', 'Email', 'email', null, true);
} ?>
<?php if ($mode === 'admin') {
    field('identifier', 'Email or mobile', 'text', null, true);
} else {
    field('mobile', 'Mobile number', 'tel', null, true);
} ?>
<?php if ($mode === 'register') {
    textarea_field('address', 'Address');
} ?>
<?php field('password', 'Password', 'password', null, true);
if (in_array($mode, ['register', 'setup'], true)) {
    field('confirm_password', 'Confirm password', 'password', null, true);
} else { ?><label class="form-check mb-3"><input class="form-check-input" type="checkbox" name="remember" value="1"> <?= t('Keep me signed in')?></label><?php } ?>
<button class="btn btn-primary btn-lg w-100"><?= t($title)?></button></form>
<?php if ($mode === 'login') { ?><p class="small text-center mt-4 mb-0"><?= t("Don't have an account?")?> <a href="/customer/register"><?= t('Create account')?></a></p><?php } elseif ($mode === 'register') { ?><p class="small text-center mt-4 mb-0"><a href="/customer/login"><?= t('Sign in')?></a></p><?php } ?>
</div></div></div></div>
