<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (! Schema::hasTable('users')) {
            DB::unprepared(file_get_contents(database_path('new_star_tailor.sql')));

            return;
        }
        if (! Schema::hasTable('php_submissions') || ! Schema::hasTable('php_rate_limits')) {
            $sql = file_get_contents(database_path('php_extensions.sql'));
            $sql = preg_replace('/ALTER TABLE users ADD COLUMN remember_token[^;]+;/', '', $sql);
            DB::unprepared($sql);
        }
        if (! Schema::hasColumn('users', 'remember_token')) {
            Schema::table('users', fn ($table) => $table->string('remember_token', 100)->nullable());
        }
    }

    public function down(): void
    {
        throw new RuntimeException('Business records are never removed by automatic rollback. Restore a verified database backup.');
    }
};
