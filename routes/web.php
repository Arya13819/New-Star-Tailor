<?php

use App\Http\Controllers\AdminController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\CustomerController;
use App\Http\Controllers\OrderController;
use App\Http\Controllers\PublicController;
use Illuminate\Support\Facades\Route;

foreach (['/', '/index.php', '/about', '/contact', '/gallery', '/services', '/healthz', '/api/health', '/robots.txt', '/sitemap.xml', '/sw.js'] as $path) {
    Route::get($path, PublicController::class);
}
foreach (['/setup', '/customer/login', '/customer/register', '/admin/login'] as $path) {
    Route::match(['GET', 'POST'], $path, AuthController::class);
}
Route::post('/api/payments/webhook', PublicController::class);
Route::match(['GET', 'POST'], '/order', OrderController::class);
Route::get('/order/success', OrderController::class);
foreach (['/enquiry', '/track-order'] as $path) {
    Route::match(['GET', 'POST'], $path, PublicController::class);
}
Route::middleware('role:CUSTOMER')->prefix('customer')->group(function () {
    foreach (['dashboard', 'orders', 'measurements', 'payments'] as $path) {
        Route::get($path, CustomerController::class);
    }
    Route::get('orders/{order}', OrderController::class)->whereNumber('order');
    Route::get('orders/{order}/receipt', OrderController::class)->whereNumber('order');
    Route::get('orders/{order}/images/{image}', OrderController::class)->whereNumber(['order', 'image']);
    Route::get('payments/{payment}/receipt', OrderController::class)->whereNumber('payment');
    Route::post('logout', AuthController::class);
});
Route::middleware('role:ADMIN')->prefix('admin')->group(function () {
    foreach (['dashboard', 'orders', 'customers', 'services', 'payments', 'enquiries', 'notifications', 'reports'] as $path) {
        Route::get($path, AdminController::class);
    }
    foreach (['customers/new', 'services/new'] as $path) {
        Route::match(['GET', 'POST'], $path, AdminController::class);
    }
    Route::match(['GET', 'POST'], 'orders/new', OrderController::class);
    Route::get('orders/{order}', OrderController::class)->whereNumber('order');
    Route::get('orders/{order}/receipt', OrderController::class)->whereNumber('order');
    Route::get('orders/{order}/images/{image}', OrderController::class)->whereNumber(['order', 'image']);
    foreach (['status', 'payment', 'details'] as $action) {
        Route::post('orders/{order}/'.$action, AdminController::class)->whereNumber('order');
    }
    Route::get('customers/{customer}', AdminController::class)->whereNumber('customer');
    foreach (['edit', 'measurements/new'] as $action) {
        Route::match(['GET', 'POST'], 'customers/{customer}/'.$action, AdminController::class)->whereNumber('customer');
    }
    Route::match(['GET', 'POST'], 'services/{service}/edit', AdminController::class)->whereNumber('service');
    Route::post('payments/{payment}/verify', AdminController::class)->whereNumber('payment');
    Route::get('payments/{payment}/receipt', AdminController::class)->whereNumber('payment');
    foreach (['status', 'convert'] as $action) {
        Route::post('enquiries/{enquiry}/'.$action, AdminController::class)->whereNumber('enquiry');
    }
    Route::post('logout', AuthController::class);
});
