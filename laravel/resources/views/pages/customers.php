<?php

namespace App\Tailoring;

?>
<div class="d-flex flex-wrap justify-content-between gap-3 mb-4"><h1 class="h3"><?= t('Customers')?></h1><a class="btn btn-primary" href="/admin/customers/new"><?= t('New customer')?></a></div><form method="get" class="d-flex gap-2 mb-4"><label class="visually-hidden" for="customer-search"><?= t('Search')?></label><input id="customer-search" class="form-control" name="q" value="<?= e(\request()->query()['q'] ?? '')?>" placeholder="<?= t('Name or mobile')?>"><button class="btn btn-primary"><?= t('Search')?></button></form><div class="card"><div class="card-body"><div class="table-responsive"><table class="table"><thead><tr><th><?= t('Name')?></th><th><?= t('Mobile number')?></th><th><?= t('Address')?></th></tr></thead><tbody><?php foreach ($customers as $customer) { ?><tr><td><a href="/admin/customers/<?= (int) $customer['id']?>"><?= e($customer['name'])?></a></td><td><?= e($customer['mobile'])?></td><td><?= e($customer['address'])?></td></tr><?php } ?><?php if (! $customers) { ?><tr><td colspan="3"><?= t('No customers yet.')?></td></tr><?php } ?></tbody></table></div></div></div>
