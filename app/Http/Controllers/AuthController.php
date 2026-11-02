<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Tailoring\SessionState;
use DomainException;
use Illuminate\Support\Facades\Auth;
use Throwable;

use function App\Tailoring\actor;
use function App\Tailoring\audit;
use function App\Tailoring\cfg;
use function App\Tailoring\db;
use function App\Tailoring\fail;
use function App\Tailoring\flash;
use function App\Tailoring\go;
use function App\Tailoring\insert;
use function App\Tailoring\is_admin;
use function App\Tailoring\mobile_value;
use function App\Tailoring\now;
use function App\Tailoring\one;
use function App\Tailoring\password_value;
use function App\Tailoring\query;
use function App\Tailoring\rate_limit;
use function App\Tailoring\render;
use function App\Tailoring\stamps;
use function App\Tailoring\text_value;

class AuthController extends TailoringController
{
    protected function handle(string $path, bool $post): void
    {
        if ($path === '/setup') {
            if (strlen((string) cfg('setup_key', '')) < 32 || (int) one("SELECT COUNT(*) n FROM users WHERE role='ADMIN'")['n'] > 0) {
                fail(404);
            }
            if ($post) {
                rate_limit('setup', 5);
                if (! hash_equals((string) cfg('setup_key'), (string) (\request()->post()['setup_key'] ?? ''))) {
                    throw new DomainException('Invalid setup key.');
                }
                $password = password_value();
                if ($password !== (\request()->post()['confirm_password'] ?? '')) {
                    throw new DomainException('Passwords do not match.');
                }
                $email = strtolower(text_value('email', 190, true));
                if (! filter_var($email, FILTER_VALIDATE_EMAIL)) {
                    throw new DomainException('Enter a valid email.');
                }
                db()->beginTransaction();
                try {
                    // Shared DB lock also serializes simultaneous first-admin setup requests.
                    query('INSERT IGNORE INTO order_sequences (id,last_seq) VALUES (1,0)');
                    query('SELECT id FROM order_sequences WHERE id=1 FOR UPDATE')->fetch();
                    if ((int) one("SELECT COUNT(*) n FROM users WHERE role='ADMIN'")['n'] > 0) {
                        throw new DomainException('Setup has already been completed.');
                    }
                    $id = insert('users', ['name' => text_value('name', 120, true), 'email' => $email, 'mobile' => mobile_value(\request()->post()['mobile'] ?? ''), 'password_hash' => password_hash($password, PASSWORD_DEFAULT, ['cost' => 12]), 'role' => 'ADMIN', 'is_active' => 1, 'preferred_locale' => $GLOBALS['locale']] + stamps());
                    audit('user', $id, 'create_admin');
                    db()->commit();
                } catch (Throwable $e) {
                    if (db()->inTransaction()) {
                        db()->rollBack();
                    }throw $e;
                }
                flash('Admin account created. Sign in to continue.');
                go('/admin/login');
            }
            render('auth', ['title' => 'Create admin account', 'mode' => 'setup']);

            return;
        }
        if (in_array($path, ['/customer/login', '/admin/login', '/customer/register'], true)) {
            $register = $path === '/customer/register';
            $role = $path === '/admin/login' ? 'ADMIN' : 'CUSTOMER';
            if (actor()) {
                go(is_admin() ? '/admin/dashboard' : '/customer/dashboard');
            }
            if ($post) {
                rate_limit($register ? 'register' : 'login', 10);
                if ($register) {
                    $mobile = mobile_value(\request()->post()['mobile'] ?? '');
                    $password = password_value();
                    if ($password !== (\request()->post()['confirm_password'] ?? '')) {
                        throw new DomainException('Passwords do not match.');
                    }
                    if (one('SELECT id FROM users WHERE mobile=?', [$mobile])) {
                        throw new DomainException('An account with this mobile number already exists. Please sign in instead.');
                    }
                    $name = text_value('name', 120, true);
                    db()->beginTransaction();
                    try {
                        $id = insert('users', ['name' => $name, 'mobile' => $mobile, 'password_hash' => password_hash($password, PASSWORD_DEFAULT, ['cost' => 12]), 'role' => 'CUSTOMER', 'is_active' => 1, 'preferred_locale' => $GLOBALS['locale']] + stamps());
                        insert('customers', ['name' => $name, 'mobile' => $mobile, 'address' => text_value('address', 400), 'user_id' => $id, 'is_active' => 1] + stamps());
                        db()->commit();
                    } catch (Throwable $e) {
                        if (db()->inTransaction()) {
                            db()->rollBack();
                        }throw $e;
                    }
                    $user = one('SELECT * FROM users WHERE id=?', [$id]);
                } else {
                    $identifier = trim((string) (\request()->post()[$role === 'ADMIN' ? 'identifier' : 'mobile'] ?? ''));
                    $mobile = preg_replace('/\D/', '', $identifier);
                    if (strlen($mobile) === 12 && str_starts_with($mobile, '91')) {
                        $mobile = substr($mobile, 2);
                    }
                    $user = $role === 'ADMIN' ? one("SELECT * FROM users WHERE role='ADMIN' AND is_active=1 AND (email=? OR mobile=?) LIMIT 1", [strtolower($identifier), $mobile]) : one("SELECT * FROM users WHERE role='CUSTOMER' AND is_active=1 AND mobile=?", [$mobile]);
                    // A fixed dummy bcrypt hash keeps missing-account requests expensive too.
                    $hash = $user['password_hash'] ?? '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2uheWG/igi.';
                    if (! password_verify((string) (\request()->post()['password'] ?? ''), $hash) || ! $user) {
                        throw new DomainException('That email/mobile or password is not correct.');
                    }
                    query('UPDATE users SET last_login_at=?,updated_at=? WHERE id=?', [now(), now(), $user['id']]);
                }
                Auth::login(User::findOrFail($user['id']), isset(\request()->post()['remember']));
                \request()->session()->regenerate();
                if (! isset(\request()->query()['lang']) && in_array($user['preferred_locale'], ['en', 'hi'], true)) {
                    SessionState::$data['lang'] = $user['preferred_locale'];
                }unset(SessionState::$data['csrf'],SessionState::$data['old']);
                flash('Welcome back.');
                go($role === 'ADMIN' ? '/admin/dashboard' : '/customer/dashboard');
            }
            render('auth', ['title' => $register ? 'Create account' : ($role === 'ADMIN' ? 'Staff sign in' : 'Sign in'), 'mode' => $register ? 'register' : ($role === 'ADMIN' ? 'admin' : 'login')]);

            return;
        }
        if (in_array($path, ['/admin/logout', '/customer/logout'], true)) {
            if (! $post) {
                fail(405);
            }SessionState::$data = [];
            Auth::logout();
            \request()->session()->invalidate();
            \request()->session()->regenerateToken();
            go('/');
        }
        \App\Tailoring\fail();
    }
}
