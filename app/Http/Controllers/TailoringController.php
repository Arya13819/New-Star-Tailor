<?php

namespace App\Http\Controllers;

use App\Tailoring\HttpStatusSignal;
use App\Tailoring\RedirectSignal;
use App\Tailoring\SessionState;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\Response;

use function App\Tailoring\flash;
use function App\Tailoring\handle_request;
use function App\Tailoring\render;

abstract class TailoringController extends Controller
{
    public function __invoke(Request $request): Response
    {
        SessionState::$data = $request->session()->get('tailoring', []);
        $GLOBALS['config'] = config('tailoring');
        $GLOBALS['db'] = null;
        $GLOBALS['response_headers'] = [];
        $GLOBALS['response_status'] = 200;
        $GLOBALS['nonce'] = base64_encode(random_bytes(18));
        $user = Auth::user();
        if ($user && ! $user->is_active) {
            Auth::logout();
            $request->session()->invalidate();
            $user = null;
        }
        $GLOBALS['user'] = $user?->toArray();
        if (in_array($request->query('lang'), ['en', 'hi'], true)) {
            SessionState::$data['lang'] = $request->query('lang');
            if ($user) {
                $user->preferred_locale = $request->query('lang');
                $user->save();
            }
        }
        $GLOBALS['locale'] = SessionState::$data['lang'] ?? 'en';
        if (! defined('App\\Tailoring\\SHOP_PHONE')) {
            define('App\\Tailoring\\SHOP_PHONE', config('tailoring.shop_phone', '9424035393'));
        }
        $path = $request->getPathInfo();
        ob_start();
        $redirect = null;
        try {
            handle_request($path, $this->handle(...));
        } catch (RedirectSignal $signal) {
            $redirect = $signal->path;
        } catch (HttpStatusSignal $signal) {
            $GLOBALS['response_status'] = $signal->status;
            render('message', ['title' => $signal->status === 404 ? 'Page not found' : 'Access denied', 'message' => 'The requested page is not available.']);
        } catch (\DomainException $error) {
            $this->rollback();
            if (($GLOBALS['response_status'] ?? 200) === 429) {
                render('message', ['title' => 'Please wait', 'message' => $error->getMessage()]);
            } elseif ($request->isMethod('POST')) {
                SessionState::$data['old'] = array_diff_key($request->post(), array_flip(['password', 'confirm_password', '_token', 'setup_key']));
                flash($error->getMessage(), 'danger');
                $redirect = $path;
                if (preg_match('~^/admin/orders/(\d+)/(?:status|payment|details)$~D', $path, $m)) {
                    $redirect = '/admin/orders/'.$m[1];
                } elseif (preg_match('~^/admin/payments/\d+/verify$~D', $path)) {
                    $redirect = '/admin/payments';
                } elseif (preg_match('~^/admin/enquiries/\d+/(?:status|convert)$~D', $path)) {
                    $redirect = '/admin/enquiries';
                }
            } else {
                $GLOBALS['response_status'] = 422;
                render('message', ['title' => 'Please check your request', 'message' => $error->getMessage()]);
            }
        } catch (\Throwable $error) {
            $this->rollback();
            $reference = bin2hex(random_bytes(4));
            Log::error('NST '.$reference, ['exception' => $error]);
            $GLOBALS['response_status'] = 503;
            render('message', ['title' => 'Temporarily unavailable', 'message' => 'Please contact the shop. Reference: '.$reference]);
        } finally {
            $request->session()->put('tailoring', SessionState::$data);
        }
        $body = ob_get_clean();

        return $redirect ? redirect()->to($redirect, 303) : response($body, $GLOBALS['response_status'], $GLOBALS['response_headers']);
    }

    abstract protected function handle(string $path, bool $post): void;

    private function rollback(): void
    {
        if (($GLOBALS['db'] ?? null) instanceof \PDO && $GLOBALS['db']->inTransaction()) {
            $GLOBALS['db']->rollBack();
        }
    }
}
