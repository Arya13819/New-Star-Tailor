<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center"><div class="col-lg-8"><h1 class="h3 mb-4"><?= t($title)?></h1><div class="card"><div class="card-body"><form method="post"><?= csrf_field()?><?php if (! $service) {
    field('code', 'Service code', 'text', null, true);
}field('name_en', 'Name (English)', 'text', old('name_en', $service['name_en'] ?? ''), true);
field('name_hi', 'Name (Hindi)', 'text', old('name_hi', $service['name_hi'] ?? ''));
select_field('category', 'Category', CATEGORIES, old('category', $service['category'] ?? 'SHIRT'));
field('default_stitching_price', 'Stitching price (₹)', 'text', old('default_stitching_price', $service['default_stitching_price'] ?? ''));
field('sort_order', 'Sort order', 'number', old('sort_order', $service['sort_order'] ?? 100));
textarea_field('description', 'Description', old('description', $service['description'] ?? '')); ?><label class="form-check mb-4"><input class="form-check-input" type="checkbox" name="is_active" value="1" <?= old('is_active', $service['is_active'] ?? 1) ? 'checked' : ''?>> <?= t('Active')?></label><button class="btn btn-primary"><?= t('Save')?></button></form></div></div></div></div>
