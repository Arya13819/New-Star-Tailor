<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class RequireRole
{
    public function handle(Request $request, Closure $next, string $role)
    {
        if (! Auth::check()) {
            return redirect($role === 'ADMIN' ? '/admin/login' : '/customer/login');
        }
        if (! Auth::user()->is_active) {
            Auth::logout();
            $request->session()->invalidate();

            return redirect('/customer/login');
        }
        abort_unless(Auth::user()->role === $role, 403);

        return $next($request);
    }
}
