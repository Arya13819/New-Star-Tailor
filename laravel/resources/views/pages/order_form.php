<?php

namespace App\Tailoring;

?>
<div class="row justify-content-center"><div class="col-12 col-lg-9"><p class="section-label text-center"><?= t('Order online')?></p><h1 class="display-6 text-center mb-4"><?= t($title)?></h1>
<?php if (! $services) { ?><div class="alert alert-warning"><?= t('Online ordering is temporarily unavailable — please call the shop.')?></div><?php } else { ?>
<div class="card"><div class="card-body"><form method="post" enctype="multipart/form-data" id="online-order"><?= csrf_field()?><input type="hidden" name="submission" value="<?= e($submission)?>">
<?php if ($admin) {
    $options = ['' => 'Choose a customer'];
    foreach ($customers as $c) {
        $options[$c['id']] = $c['name'].' · '.$c['mobile'];
    }select_field('customer_id', 'Customer', $options, old('customer_id', \request()->query()['customer'] ?? '')); ?><p><a href="/admin/customers/new"><?= t('New customer')?> ↗</a></p><?php if (! empty(\request()->query()['enquiry'])) { ?><input type="hidden" name="enquiry_id" value="<?= (int) \request()->query()['enquiry']?>"><?php } ?>
<?php } elseif (actor()) { ?><div class="alert alert-light border"><strong><?= e(actor()['name'])?></strong> · <?= e(actor()['mobile'])?></div><?php } else {
        field('name', 'Full name', 'text', null, true);
        field('mobile', 'Mobile number', 'tel', null, true);
        textarea_field('address', 'Address');
    } ?>
<h2 class="h6 section-label mt-4"><?= t('Services')?></h2>
<div id="item-rows">
<?php $selectedIds = old('service_id', [(int) (\request()->query()['service'] ?? 0)]);
    if (! is_array($selectedIds)) {
        $selectedIds = [0];
    }$selectedIds = array_slice($selectedIds, 0, 20);
    foreach ($selectedIds as $index => $selectedId) { ?>
<div class="php-item-row border-bottom pb-3 mb-3" data-row><div><label class="form-label" for="service-<?= $index?>"><?= t('Service')?></label><select class="form-select" name="service_id[]" id="service-<?= $index?>" data-service required><option value=""><?= t('Choose a service')?></option><?php foreach ($services as $s) { ?><option value="<?= (int) $s['id']?>" data-price="<?= e($s['default_stitching_price'] ?? '')?>" <?= ((int) $selectedId === (int) $s['id']) ? 'selected' : ''?>><?= e($GLOBALS['locale'] === 'hi' && $s['name_hi'] ? $s['name_hi'] : $s['name_en'])?> — <?= $s['default_stitching_price'] !== null ? money($s['default_stitching_price']) : t('Please call for pricing')?></option><?php } ?></select></div><div><label class="form-label" for="qty-<?= $index?>"><?= t('Qty')?></label><input class="form-control" id="qty-<?= $index?>" type="number" name="quantity[]" value="<?= e(old('quantity', [])[$index] ?? 1)?>" min="1" max="99" required></div><button type="button" class="btn btn-outline-danger" data-remove aria-label="<?= t('Remove service')?>">×</button>
<?php if ($admin) { ?><div><label class="form-label" for="stitch-<?= $index?>"><?= t('Stitching price (₹)')?></label><input class="form-control" data-stitch id="stitch-<?= $index?>" name="stitching_price[]" inputmode="decimal" value="<?= e(old('stitching_price', [])[$index] ?? '')?>" required></div><div><label class="form-label" for="cloth-<?= $index?>"><?= t('Cloth price (₹)')?></label><input class="form-control" id="cloth-<?= $index?>" name="material_price[]" inputmode="decimal" value="<?= e(old('material_price', [])[$index] ?? '0')?>" required></div><?php } ?>
</div><?php } ?></div>
<button type="button" class="btn btn-outline-secondary btn-sm mb-4" id="add-item-row"><?= t('+ Add another service')?></button>
<?php select_field('fabric_source', 'Who provides the cloth?', ['CUSTOMER' => 'Customer brings cloth', 'SHOP' => 'Shop provides cloth'], 'CUSTOMER'); ?>
<p class="small text-secondary"><?= t('Stitching charges only — cloth is billed separately, whether you bring your own or the shop provides it.')?> <?= t('If the shop is providing the cloth, our staff will call you to discuss fabric options and confirm the material cost.')?></p>
<?php if ($admin) {
    select_field('priority', 'Priority', ['NORMAL' => 'Normal', 'URGENT' => 'Urgent'], 'NORMAL');
    field('confirmed_delivery_date', 'Confirmed delivery date', 'date');
}field('requested_delivery_date', 'Customer requested date', 'date');
    textarea_field('notes', 'Notes'); ?>
<h2 class="h6 section-label mt-4"><?= t('Measurements')?></h2><label class="form-check mb-3"><input class="form-check-input" type="checkbox" id="provide_measurements" name="provide_measurements" value="1" <?= old('provide_measurements') ? 'checked' : ''?>> <?= t('Provide measurements (optional)')?></label>
<fieldset id="measurement-fields" class="border rounded p-3 mb-4"><legend class="float-none w-auto px-2 fs-6"><?= t('Measurements')?> (<?= t('inches')?>)</legend><div class="row"><?php foreach (MEASUREMENT_FIELDS as $name => $label) { ?><div class="col-6"><?php field($name, $label, 'number'); ?></div><?php } ?></div><?php select_field('fitting_preference', 'Fitting preference', ['NORMAL' => 'Normal', 'SLIM' => 'Slim', 'LOOSE' => 'Loose'], 'NORMAL');
    field('allowance', 'Allowance');
    textarea_field('measurement_notes', 'Measurement notes'); ?><label class="form-check"><input class="form-check-input" type="checkbox" name="measurement_ack" value="1" <?= old('measurement_ack') ? 'checked' : ''?>> <?= t('I am responsible for the accuracy of the measurements I submit.')?></label></fieldset>
<label for="reference_image" class="form-label"><?= t('Reference photo')?> (JPG, PNG, WebP · 8 MB)</label><input class="form-control mb-4" type="file" id="reference_image" name="reference_image" accept="image/jpeg,image/png,image/webp">
<h2 class="h6 section-label"><?= t('Payment')?></h2><p class="small text-secondary"><?= t('Online payment references remain pending until staff verify them. This website does not collect card details.')?></p>
<?php field('payment_reference', 'Payment reference');
    field('payment_amount', 'Payment amount (₹)', 'text', '0'); ?>
<button class="btn btn-primary btn-lg w-100 mt-3"><?= t('Place order')?></button></form></div></div><?php } ?></div></div>
