<?php

namespace App\Tailoring;

?>
<div class="d-flex flex-wrap gap-3 justify-content-between align-items-center mb-4"><div><p class="section-label"><?= t($admin ? 'Shop dashboard' : 'My account')?></p><h1 class="h3"><?= t($dashboard ? 'Welcome' : 'Orders')?><?= $dashboard ? ', '.e(actor()['name']) : ''?></h1></div><a class="btn btn-primary" href="<?= $admin ? '/admin/orders/new' : '/order'?>"><?= t('New order')?> ↗</a></div>
<?php if ($admin) { ?><form class="row g-2 mb-4" method="get"><div class="col-md-7"><label class="visually-hidden" for="order-search"><?= t('Search')?></label><input class="form-control" id="order-search" name="q" value="<?= e(\request()->query()['q'] ?? '')?>" placeholder="<?= t('Search customer, mobile or order number…')?>"></div><div class="col-md-3"><label class="visually-hidden" for="status-filter"><?= t('Status')?></label><select class="form-select" name="status" id="status-filter"><option value=""><?= t('All statuses')?></option><?php foreach (STATUSES as $s) { ?><option <?= $s === (\request()->query()['status'] ?? '') ? 'selected' : ''?>><?= e($s)?></option><?php } ?></select></div><div class="col-md-2"><button class="btn btn-primary w-100"><?= t('Search')?></button></div></form><?php } ?>
<?php if ($dashboard) {
    $open = count(array_filter($orders, fn ($o) => $o['status'] !== 'DELIVERED'));
    $due = array_sum(array_map(fn ($o) => cents($o['grand_total']) - cents($o['paid']), $orders)); ?><div class="row g-3 mb-4"><div class="col-6"><a href="/customer/orders?view=open" class="card text-decoration-none"><div class="card-body"><p class="section-label"><?= t('Open orders')?></p><strong class="h3"><?= $open?></strong></div></a></div><div class="col-6"><a href="/customer/payments" class="card text-decoration-none"><div class="card-body"><p class="section-label"><?= t('Balance due')?></p><strong class="h3"><?= money(decimal($due))?></strong></div></a></div></div><?php } ?>
<?php require __DIR__.'/order_table.php'; ?>
