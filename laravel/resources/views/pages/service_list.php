<?php

namespace App\Tailoring;

?>
<div class="d-flex flex-wrap justify-content-between gap-3 mb-4"><h1 class="h3"><?= t('Services & pricing')?></h1><a class="btn btn-primary" href="/admin/services/new"><?= t('New service')?></a></div><p class="text-secondary"><?= t('Changing a price affects new orders only. Existing orders keep their captured prices.')?></p><div class="card"><div class="card-body"><div class="table-responsive"><table class="table"><thead><tr><th><?= t('Service')?></th><th><?= t('Category')?></th><th><?= t('Stitching price (₹)')?></th><th><?= t('Status')?></th><th><?= t('Action')?></th></tr></thead><tbody><?php foreach ($services as $service) { ?><tr><td><?= e($service['name_en'])?><br><small class="text-secondary"><?= e($service['name_hi'])?></small></td><td><?= e($service['category'])?></td><td><?= $service['default_stitching_price'] !== null ? money($service['default_stitching_price']) : t('Not set')?></td><td><?= t($service['is_active'] ? 'Active' : 'Inactive')?></td><td><a href="/admin/services/<?= (int) $service['id']?>/edit"><?= t('Edit')?></a></td></tr><?php } ?></tbody></table></div></div></div>
