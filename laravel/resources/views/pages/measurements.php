<?php

namespace App\Tailoring;

?>
<h2 class="h4 mb-3"><?= t('Measurements')?></h2><p class="small text-secondary"><?= t('Measurements are in inches. Previous versions remain unchanged for existing orders.')?></p>
<?php foreach ($measurements as $i => $version) { ?><details class="card mb-3" <?= $i === 0 ? 'open' : ''?>><summary class="card-body"><?= e($version['name'] ?? '')?> · <?= t('Version')?> <?= (int) $version['version_number']?> · <?= e($version['created_at'])?> UTC</summary><div class="card-body pt-0"><dl class="row mb-0"><?php foreach (MEASUREMENT_FIELDS as $key => $label) { ?><dt class="col-6 col-md-3"><?= t($label)?></dt><dd class="col-6 col-md-3"><?= e($version[$key] ?? '—')?></dd><?php } ?><dt class="col-6"><?= t('Fitting preference')?></dt><dd class="col-6"><?= e($version['fitting_preference'] ?: '—')?></dd></dl><p class="small"><?= nl2br(e($version['notes'] ?? ''))?></p></div></details><?php } ?><?php if (! $measurements) { ?><p class="text-secondary"><?= t('No measurements yet.')?></p><?php } ?>
