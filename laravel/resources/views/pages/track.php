<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center"><div class="col-lg-7"><p class="section-label text-center"><?= t('Track your order')?></p><h1 class="display-6 text-center mb-3"><?= t('Check your order status')?></h1><p class="text-center text-secondary"><?= t('Enter the order number on your receipt and the mobile number used for your order.')?></p><div class="card mb-4"><div class="card-body"><form method="post"><?= csrf_field()?><?php field('order_number', 'Order number', 'text', null, true);
field('mobile', 'Mobile number', 'tel', null, true); ?><button class="btn btn-primary w-100"><?= t('Check status')?></button></form></div></div>
<?php if ($notFound) { ?><div class="alert alert-warning"><?= t('We could not find an order matching that order number and mobile number.')?></div><?php } ?>
<?php if ($result) {
    $paid = paid((int) $result['id']); ?><div class="card"><div class="card-body"><h2 class="h4"><?= e($result['order_number'])?></h2><span class="badge text-bg-secondary"><?= e($result['status'])?></span><?php progress($result['status']); ?><dl class="row"><dt class="col-7"><?= t('Grand total')?></dt><dd class="col-5 text-end"><?= money($result['grand_total'])?></dd><dt class="col-7"><?= t('Paid')?></dt><dd class="col-5 text-end"><?= money(decimal($paid))?></dd><dt class="col-7"><?= t('Balance due')?></dt><dd class="col-5 text-end"><?= money(decimal(cents($result['grand_total']) - $paid))?></dd></dl><?php if ($result['confirmed_delivery_date']) { ?><p class="small text-secondary"><?= t('Confirmed delivery date')?>: <?= e($result['confirmed_delivery_date'])?></p><?php } ?></div></div><?php } ?></div></div>
