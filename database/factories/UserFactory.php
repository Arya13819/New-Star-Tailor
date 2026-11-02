<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class UserFactory extends Factory
{
    public function definition(): array
    {
        return ['name' => fake()->name(), 'email' => fake()->unique()->safeEmail(), 'mobile' => fake()->unique()->numerify('9#########'), 'password_hash' => Hash::make(Str::random(24)), 'role' => 'CUSTOMER', 'is_active' => true, 'preferred_locale' => 'en'];
    }
}
