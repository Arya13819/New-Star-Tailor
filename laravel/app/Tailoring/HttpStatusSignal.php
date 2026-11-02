<?php

namespace App\Tailoring;

final class HttpStatusSignal extends \RuntimeException
{
    public function __construct(public int $status)
    {
        parent::__construct('HTTP status');
    }
}
