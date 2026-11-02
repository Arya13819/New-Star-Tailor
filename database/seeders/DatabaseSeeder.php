<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        // Catalogue only: never create default accounts or overwrite shop prices.
        $defaults = [
            ['SHIRT', 'Shirt', 'शर्ट', 'SHIRT', null, 10],
            ['PANT', 'Pant', 'पैंट', 'PANT', null, 20],
            ['SHIRT_PANT_COMBO', 'Shirt + Pant Combo', 'शर्ट + पैंट सेट', 'SHIRT', '550.00', 30],
            ['POLICE_KHAAKI', 'Police Khaaki', 'पुलिस खाकी', 'POLICE', '700.00', 40],
            ['CRPF_KHAAKI', 'CRPF Khaaki', 'सीआरपीएफ खाकी', 'CRPF', '700.00', 50],
            ['CRPF_CHEETAH', 'CRPF Cheetah', 'सीआरपीएफ चीता', 'CRPF', '700.00', 60],
            ['CRPF_KHAAKI_DANGRI', 'CRPF Khaaki Dangri', 'सीआरपीएफ खाकी डंगरी', 'CRPF', null, 70],
            ['ARMY_PATTERN', 'Army Pattern', 'आर्मी पैटर्न', 'ARMY', null, 80],
            ['CHEETAH_US_PATTERN', 'Cheetah US Pattern', 'चीता यूएस पैटर्न', 'ARMY', '850.00', 90],
        ];
        foreach ($defaults as [$code,$name,$hindi,$category,$price,$sort]) {
            DB::table('services')->insertOrIgnore(['code' => $code, 'name_en' => $name, 'name_hi' => $hindi, 'category' => $category, 'default_stitching_price' => $price, 'sort_order' => $sort, 'is_active' => 1, 'created_at' => now(), 'updated_at' => now()]);
        }
    }
}
