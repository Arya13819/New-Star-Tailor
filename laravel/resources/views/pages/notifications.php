<?php

namespace App\Tailoring;

?>
<h1 class="h3 mb-4"><?= t('Notifications')?></h1><div class="alert alert-info"><?= t('SMS sending is not configured. Messages below are queued only and are not marked as sent.')?></div><div class="card"><div class="card-body"><div class="table-responsive"><table class="table"><thead><tr><th><?= t('Type')?></th><th><?= t('Mobile number')?></th><th><?= t('Message')?></th><th><?= t('Status')?></th></tr></thead><tbody><?php foreach ($notifications as $n) { ?><tr><td><?= e($n['type'])?></td><td><?= e($n['to_address'])?></td><td><?= e($n['body'])?></td><td><?= e($n['status'])?></td></tr><?php } ?><?php if (! $notifications) { ?><tr><td colspan="4"><?= t('No notifications yet.')?></td></tr><?php } ?></tbody></table></div></div></div>
