<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class SecurityHeaders
{
    public function handle(Request $request, Closure $next): Response
    {
        return self::apply($request, $next($request));
    }

    public static function apply(Request $request, Response $response): Response
    {
        $nonce = $GLOBALS['nonce'] ??= base64_encode(random_bytes(18));
        $map = in_array($request->path(), ['about', 'contact'], true) ? 'frame-src https://www.google.com https://maps.google.com; ' : '';
        if (! $response->headers->has('Content-Security-Policy')) {
            $response->headers->set('Content-Security-Policy', "default-src 'self'; script-src 'self' 'nonce-$nonce'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; ".$map."object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'");
        }
        $response->headers->set('X-Content-Type-Options', 'nosniff');
        $response->headers->set('X-Frame-Options', 'DENY');
        $response->headers->set('Referrer-Policy', 'strict-origin-when-cross-origin');
        $response->headers->set('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=()');
        if (! str_starts_with($request->path(), 'static/') && ! str_starts_with($request->path(), 'assets/')) {
            $response->headers->set('Cache-Control', 'private, no-store');
        }
        if (config('session.secure')) {
            $response->headers->set('Strict-Transport-Security', 'max-age=31536000');
        }

        return $response;
    }
}
