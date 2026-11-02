<?php

namespace App\Tailoring;

?>
<h1 class="h3 mb-4"><?= t('New measurement version')?> — <?= e($customer['name'])?></h1><div class="card"><div class="card-body"><form method="post"><?= csrf_field()?><p class="small text-secondary"><?= t('Saving creates a new version. Previous orders keep their original measurements.')?></p><div class="row"><?php foreach (MEASUREMENT_FIELDS as $key => $label) { ?><div class="col-6 col-lg-4"><?php field($key, $label, 'number', old($key, $last[$key] ?? '')); ?></div><?php } ?></div><?php select_field('fitting_preference', 'Fitting preference', ['NORMAL' => 'Normal', 'SLIM' => 'Slim', 'LOOSE' => 'Loose'], old('fitting_preference', $last['fitting_preference'] ?? 'NORMAL'));
field('allowance', 'Allowance', 'text', old('allowance', $last['allowance'] ?? ''));
textarea_field('measurement_notes', 'Measurement notes', old('measurement_notes', $last['notes'] ?? ''));
textarea_field('alteration_notes', 'Alteration notes', old('alteration_notes', $last['alteration_notes'] ?? '')); ?><button class="btn btn-primary"><?= t('Save new version')?></button></form></div></div>
