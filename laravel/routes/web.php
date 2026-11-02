<?php

use App\Http\Controllers\TailoringController;
use Illuminate\Support\Facades\Route;

foreach (['/', '/index.php', '/about', '/contact', '/gallery', '/services', '/healthz', '/api/health', '/robots.txt', '/sitemap.xml', '/sw.js', '/order/success'] as $path) {
    Route::get($path, TailoringController::class);
}
foreach (['/setup', '/customer/login', '/customer/register', '/admin/login', '/order', '/enquiry', '/track-order'] as $path) {
    Route::match(['GET', 'POST'], $path, TailoringController::class);
}
Route::post('/api/payments/webhook', TailoringController::class);
Route::middleware('role:CUSTOMER')->prefix('customer')->group(function () {
    foreach (['dashboard', 'orders', 'measurements', 'payments'] as $path) {
        Route::get($path, TailoringController::class);
    }
    Route::get('orders/{order}', TailoringController::class)->whereNumber('order');
    Route::get('orders/{order}/receipt', TailoringController::class)->whereNumber('order');
    Route::get('orders/{order}/images/{image}', TailoringController::class)->whereNumber(['order', 'image']);
    Route::get('payments/{payment}/receipt', TailoringController::class)->whereNumber('payment');
    Route::post('logout', TailoringController::class);
});
Route::middleware('role:ADMIN')->prefix('admin')->group(function () {
    foreach (['dashboard', 'orders', 'customers', 'services', 'payments', 'enquiries', 'notifications', 'reports'] as $path) {
        Route::get($path, TailoringController::class);
    }
    foreach (['orders/new', 'customers/new', 'services/new'] as $path) {
        Route::match(['GET', 'POST'], $path, TailoringController::class);
    }
    Route::get('orders/{order}', TailoringController::class)->whereNumber('order');
    Route::get('orders/{order}/receipt', TailoringController::class)->whereNumber('order');
    Route::get('orders/{order}/images/{image}', TailoringController::class)->whereNumber(['order', 'image']);
    foreach (['status', 'payment', 'details'] as $action) {
        Route::post('orders/{order}/'.$action, TailoringController::class)->whereNumber('order');
    }
    Route::get('customers/{customer}', TailoringController::class)->whereNumber('customer');
    foreach (['edit', 'measurements/new'] as $action) {
        Route::match(['GET', 'POST'], 'customers/{customer}/'.$action, TailoringController::class)->whereNumber('customer');
    }
    Route::match(['GET', 'POST'], 'services/{service}/edit', TailoringController::class)->whereNumber('service');
    Route::post('payments/{payment}/verify', TailoringController::class)->whereNumber('payment');
    Route::get('payments/{payment}/receipt', TailoringController::class)->whereNumber('payment');
    foreach (['status', 'convert'] as $action) {
        Route::post('enquiries/{enquiry}/'.$action, TailoringController::class)->whereNumber('enquiry');
    }
    Route::post('logout', TailoringController::class);
});
