<?php

namespace Tests\Unit;

use DomainException;
use PHPUnit\Framework\TestCase;

use function App\Tailoring\cents;
use function App\Tailoring\decimal;
use function App\Tailoring\money;

class CurrencyTest extends TestCase
{
    public function test_amounts_round_trip_without_floating_point(): void
    {
        $this->assertSame(55001, cents('550.01'));
        $this->assertSame('550.01', decimal(55001));
        $this->assertSame('₹550.01', money('550.01'));
        $this->assertSame('0.00', decimal(0));
    }

    public function test_fractional_paise_are_rejected(): void
    {
        $this->expectException(DomainException::class);
        cents('10.001');
    }

    public function test_negative_payments_are_rejected(): void
    {
        $this->expectException(DomainException::class);
        cents('-1.00');
    }

    public function test_database_amount_overflow_is_rejected(): void
    {
        $this->expectException(DomainException::class);
        decimal(10000000000);
    }
}
