<?php

use Illuminate\Foundation\Application;
use Illuminate\Http\Request;

define('LARAVEL_START', microtime(true));
// This index is uploaded to public_html/newstartailor. Laravel stays outside it.
$appPath = dirname(__DIR__, 2).'/newstartailor-app';
if (file_exists($maintenance = $appPath.'/storage/framework/maintenance.php')) {
    require $maintenance;
}
require $appPath.'/vendor/autoload.php';
/** @var Application $app */
$app = require_once $appPath.'/bootstrap/app.php';
$app->usePublicPath(__DIR__);
$app->handleRequest(Request::capture());
