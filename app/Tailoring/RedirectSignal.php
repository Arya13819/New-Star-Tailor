<?php

namespace App\Tailoring;

final class RedirectSignal extends \RuntimeException
{
    public function __construct(public string $path)
    {
        parent::__construct('Redirect');
    }
}
