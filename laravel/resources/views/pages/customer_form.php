<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center"><div class="col-md-8"><h1 class="h3 mb-4"><?= t($title)?></h1><div class="card"><div class="card-body"><form method="post"><?= csrf_field()?><?php field('name', 'Full name', 'text', old('name', $customer['name'] ?? ''), true);
field('mobile', 'Mobile number', 'tel', old('mobile', $customer['mobile'] ?? ''), true);
textarea_field('address', 'Address', old('address', $customer['address'] ?? ''));
textarea_field('notes', 'Notes', old('notes', $customer['notes'] ?? '')); ?><button class="btn btn-primary"><?= t('Save')?></button></form></div></div></div></div>
