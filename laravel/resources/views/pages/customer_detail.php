<?php

namespace App\Tailoring;

?>
<div class="d-flex flex-wrap justify-content-between gap-3 mb-4"><div><h1 class="h3"><?= e($customer['name'])?></h1><p class="text-secondary"><?= e($customer['mobile'])?> · <?= e($customer['address'])?></p></div><div class="d-flex flex-wrap gap-2 align-self-start"><a class="btn btn-outline-primary" href="/admin/customers/<?= (int) $customer['id']?>/edit"><?= t('Edit customer')?></a><a class="btn btn-outline-primary" href="/admin/customers/<?= (int) $customer['id']?>/measurements/new"><?= t('New measurement version')?></a><a class="btn btn-primary" href="/admin/orders/new?customer=<?= (int) $customer['id']?>"><?= t('New order')?></a></div></div>
<h2 class="h5 mb-3"><?= t('Orders')?></h2><?php $admin = true;
require __DIR__.'/order_table.php'; ?>
<div class="mt-4"><?php require __DIR__.'/measurements.php'; ?></div>
