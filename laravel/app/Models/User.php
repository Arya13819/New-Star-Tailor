<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;

class User extends Authenticatable
{
    use HasFactory;

    protected $table = 'users';

    protected $guarded = ['id', 'role', 'is_active'];

    protected $hidden = ['password_hash', 'remember_token'];

    protected function casts(): array
    {
        return ['is_active' => 'boolean'];
    }

    public function getAuthPasswordName(): string
    {
        return 'password_hash';
    }
}
