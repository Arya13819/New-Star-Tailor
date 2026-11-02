<?php

namespace App\Tailoring;

?>
@php
    $hindi = $GLOBALS['locale'] === 'hi';
    $guide = $hindi
        ? [
            [
                '01',
                'हर दिन, आपका अंदाज़।',
                'ऑफिस की शर्ट से लेकर आरामदायक ट्राउज़र तक — अपनी पसंद और नाप के अनुसार सिलवाएँ।',
                '/services?category=SHIRT',
                'शर्ट की सिलाई देखें',
                'everyday',
            ],
            [
                '02',
                'वर्दी में भी सही फिट।',
                'पुलिस, CRPF और आर्मी यूनिफॉर्म की सिलाई के लिए हमारी सर्विसेज़ देखें।',
                '/services?category=POLICE',
                'यूनिफॉर्म देखें',
                'uniform',
            ],
            [
                '03',
                'अपना कपड़ा। अपनी पसंद।',
                'कपड़ा साथ लाएँ या दुकान पर विकल्प पूछें। कपड़े और सिलाई का खर्च अलग रहता है।',
                '/enquiry',
                'हमसे बात करें',
                'fabric',
            ],
        ]
        : [
            [
                '01',
                'Every day. Your way.',
                'From the office shirt to your favourite trousers. Made around your measurements and your routine.',
                '/services?category=SHIRT',
                'Explore shirts',
                'everyday',
            ],
            [
                '02',
                'Made for your duty.',
                'Thoughtful tailoring for Police, CRPF and Army uniforms. Find the service that fits your role.',
                '/services?category=POLICE',
                'Explore uniforms',
                'uniform',
            ],
            [
                '03',
                'Your fabric. Your choice.',
                'Bring your own cloth, or ask about options at the shop. Fabric and stitching are always billed separately.',
                '/enquiry',
                'Talk to the tailor',
                'fabric',
            ],
        ];
@endphp
<section class="fit-guide home-section" aria-labelledby="fit-guide-title">
    <div class="fit-guide-heading">
        <div>
            <p class="section-label">{{ $hindi ? 'आपके लिए बनाया गया' : 'THE ART OF A PERSONAL FIT' }}</p>
            <h2 id="fit-guide-title">{{ $hindi ? 'सिर्फ कपड़े नहीं।' : 'More than a garment.' }}<br>
                <em>{{ $hindi ? 'आपकी अपनी पहचान।' : 'Something that feels like you.' }}</em>
            </h2>
        </div>
        <p>{{ $hindi ? 'सही नाप, सोच-समझकर की गई कटिंग और हर सिलाई में ध्यान। आपकी अगली पसंद यहीं से शुरू होती है।' : 'Considered cuts. Personal measurements. Care in the finishing. Find a starting point for your next favourite fit.' }}
        </p>
    </div>
    <div class="fit-guide-grid">
        @foreach ($guide as [$number, $heading, $description, $url, $label, $swatch])
            <a class="fit-guide-card" href="{{ $url }}">
                <div class="fit-guide-card-top"><span>{{ $number }} / NEW STAR</span><span
                        class="fabric-swatch fabric-swatch--{{ $swatch }}" aria-hidden="true"></span></div>
                <h3>{{ $heading }}</h3>
                <p>{{ $description }}</p>
                <span class="fit-guide-link">{{ $label }} <span aria-hidden="true">↗</span></span>
            </a>
        @endforeach
    </div>
    <div class="fit-guide-footnote"><span
            aria-hidden="true">✦</span><span>{{ $hindi ? 'नीमच में मिलें। ऑनलाइन ऑर्डर करें। हर कदम पर साथ।' : 'Visit us in Neemuch. Order online. Keep track along the way.' }}</span><a
            href="/contact">{{ $hindi ? 'दुकान का पता' : 'Find the shop' }} ↗</a></div>
</section>
