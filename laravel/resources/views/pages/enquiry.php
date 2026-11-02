<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center"><div class="col-md-7"><p class="section-label text-center"><?= t('Enquiry')?></p><h1 class="display-6 text-center mb-4"><?= t('Send us an enquiry')?></h1><div class="card"><div class="card-body"><form method="post"><?= csrf_field()?><?php field('name', 'Full name', 'text', null, true);
field('mobile', 'Mobile number', 'tel', null, true);
textarea_field('address', 'Address');
textarea_field('message', 'Message'); ?><button class="btn btn-primary w-100"><?= t('Send enquiry')?></button></form></div></div></div></div>
