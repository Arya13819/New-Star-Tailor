<?php

namespace App\Tailoring;

?>

<section class="tailor-hero" aria-labelledby="hero-title">
    <span class="hero-watermark" aria-hidden="true">NS</span>
    <span class="hero-orbit" aria-hidden="true"></span>
    <div class="hero-copy">
        <p class="section-label"><span class="tiny-rule"></span>MEN’S TAILORING · NEEMUCH</p>
        <h1 id="hero-title">A better fit.<br><em>A better you.</em></h1>
        <p class="hero-description">From your everyday shirt to the uniform you wear with pride. Discover clothing made
            to your measurements, with care in every stitch.</p>
        <div class="d-flex flex-wrap gap-3"><a class="btn btn-primary btn-lg" href="/order">Start your order <span
                    aria-hidden="true">↗</span></a><a class="btn btn-outline-primary btn-lg" href="/services">Explore
                services</a></div>
        <div class="hero-note"><span aria-hidden="true">✦</span>
            <div><strong>Your measurements. Your fit.</strong><small>Shirts, trousers & Police, CRPF and Army
                    uniforms</small></div>
        </div>
    </div>
    <div class="hero-visual" data-depth>
        <div class="hero-scene">
            <div class="hero-image-wrap">

                <picture>
                    <source type="image/webp"
                        srcset="/static/img/optimized/shirt_pant_combo-320.webp 320w, /static/img/optimized/shirt_pant_combo-640.webp 640w"
                        sizes="(max-width: 767px) 80vw, 480px">
                    <img src="/static/img/services/shirt_pant_combo.jpg"
                        alt="Blue shirt and navy trousers, neatly folded" class="" width="700" height="716"
                        loading="eager" decoding="async" fetchpriority="high">
                </picture>
                <span class="image-label">THE EVERYDAY COLLECTION</span>
            </div>
            <div class="hero-stamp"><span aria-hidden="true">✦</span><strong>Cut to fit.<br>Stitched to last.</strong>
            </div>
            <div class="fit-tag"><span class="fit-icon" aria-hidden="true">⌁</span>
                <div><strong>Made to measure</strong><small>A fit that feels like you.</small></div><span
                    class="fit-check" aria-hidden="true">✓</span>
            </div>
            <div class="measure-tape" aria-hidden="true">
                <span>10</span><span>20</span><span>30</span><span>40</span><span>50</span>
            </div>
        </div>
        <div class="hero-image-caption"><span>01 / EVERYDAY ESSENTIALS</span><a href="/gallery">View our work ↗</a>
        </div>
    </div>
</section>
<section class="promise-strip" aria-label="Our approach">
    <div><span class="promise-number">01</span>
        <div>
            <h2>Made to measure</h2>
            <p>A fit that feels like you.</p>
        </div>
    </div>
    <div><span class="promise-number">02</span>
        <div>
            <h2>Clear pricing</h2>
            <p>Stitching and cloth, billed separately.</p>
        </div>
    </div>
    <div><span class="promise-number">03</span>
        <div>
            <h2>Stay in the loop</h2>
            <p>Track your order, anytime.</p>
        </div>
    </div>
</section>
<section class="home-section collection-section">
    <div class="section-heading">
        <div>
            <p class="section-label">THE RIGHT FIT FOR EVERY DAY</p>
            <h2>What can we stitch for you?</h2>
        </div><a class="text-link" href="/services">All services & pricing ↗</a>
    </div>
    <div class="collection-grid"><a class="collection-card" href="/services">
            <div class="collection-image">
                <picture>
                    <source type="image/webp"
                        srcset="/static/img/optimized/shirt_pant_combo-320.webp 320w, /static/img/optimized/shirt_pant_combo-640.webp 640w"
                        sizes="(max-width: 767px) calc(100vw - 44px), 380px">
                    <img src="/static/img/services/shirt_pant_combo.jpg" alt="Everyday essentials" class=""
                        width="700" height="716" loading="lazy" decoding="async">
                </picture><span class="collection-index" aria-hidden="true">01</span><span aria-hidden="true">↗</span>
            </div>
            <div class="collection-meta">
                <h3>Everyday essentials</h3>
                @if (isset($prices['SHIRT_PANT_COMBO']))
                    <span>{!! money($prices['SHIRT_PANT_COMBO']) !!}</span>
                @endif

            </div>
            <p>Shirts & trousers, made your way.</p>
        </a><a class="collection-card" href="/services">
            <div class="collection-image">
                <picture>
                    <source type="image/webp"
                        srcset="/static/img/optimized/police_khaaki-320.webp 320w, /static/img/optimized/police_khaaki-640.webp 640w"
                        sizes="(max-width: 767px) calc(100vw - 44px), 380px">
                    <img src="/static/img/services/police_khaaki.jpg" alt="Police uniforms" class=""
                        width="700" height="716" loading="lazy" decoding="async">
                </picture><span class="collection-index" aria-hidden="true">02</span><span aria-hidden="true">↗</span>
            </div>
            <div class="collection-meta">
                <h3>Police uniforms</h3>
                @if (isset($prices['POLICE_KHAAKI']))
                    <span>{!! money($prices['POLICE_KHAAKI']) !!}</span>
                @endif

            </div>
            <p>A sharp fit for the line of duty.</p>
        </a><a class="collection-card" href="/services">
            <div class="collection-image">
                <picture>
                    <source type="image/webp"
                        srcset="/static/img/optimized/crpf_cheetah-320.webp 320w, /static/img/optimized/crpf_cheetah-640.webp 640w"
                        sizes="(max-width: 767px) calc(100vw - 44px), 380px">
                    <img src="/static/img/services/crpf_cheetah.jpg" alt="CRPF uniforms" class="" width="700"
                        height="716" loading="lazy" decoding="async">
                </picture><span class="collection-index" aria-hidden="true">03</span><span
                    aria-hidden="true">↗</span>
            </div>
            <div class="collection-meta">
                <h3>CRPF uniforms</h3>
                @if (isset($prices['CRPF_CHEETAH']))
                    <span>{!! money($prices['CRPF_CHEETAH']) !!}</span>
                @endif

            </div>
            <p>Precision in every detail.</p>
        </a></div>
    <p class="pricing-note">Prices shown are for stitching only. Cloth is billed separately.</p>
</section>
<section class="craft-section home-section" aria-labelledby="craft-title">
    <div class="craft-visual"><span class="craft-outline" aria-hidden="true"></span>
        <div class="craft-photo">
            <picture>
                <source type="image/webp"
                    srcset="/static/img/optimized/shirt-320.webp 320w, /static/img/optimized/shirt-640.webp 640w"
                    sizes="(max-width: 767px) 80vw, 420px">
                <img src="/static/img/services/shirt.jpg" alt="Shirt" class="" width="700"
                    height="716" loading="lazy" decoding="async">
            </picture>
        </div><span class="craft-seal" aria-hidden="true"><img src="/static/img/brand-star.svg" alt=""
                width="45" height="45"></span>
    </div>
    <div class="craft-copy">
        <p class="section-label">CRAFTED AROUND YOU</p>
        <h2 id="craft-title">The details make<br><em>the difference.</em></h2>
        <p>Your measurements, your fabric, your personal style. We bring them together with thoughtful cutting and
            careful stitching.</p>
        <div class="craft-values">
            <div><span aria-hidden="true">01 /</span><strong>Your measurements. Your fit.</strong></div>
            <div><span aria-hidden="true">02 /</span><strong>Stitching and cloth, billed separately.</strong></div>
        </div><a class="text-link" href="/about">About us ↗</a>
    </div>
</section>
<section class="process-section home-section">
    <div>
        <p class="section-label">SIMPLE FROM START TO FINISH</p>
        <h2>Your next favourite fit,<br><em>in three easy steps.</em></h2><a class="text-link" href="/enquiry">Have a
            question? Let’s talk ↗</a>
    </div>
    <ol class="process-list">
        <li><span>01</span>
            <div>
                <h3>Choose your style</h3>
                <p>Pick everyday clothing or a uniform. Bring your fabric, or ask about cloth at the shop.</p>
            </div>
        </li>
        <li><span>02</span>
            <div>
                <h3>Make it yours</h3>
                <p>Visit us for measurements, or submit your measurements with your online order.</p>
            </div>
        </li>
        <li><span>03</span>
            <div>
                <h3>Leave the rest to us</h3>
                <p>Track your order online. Normal delivery is 10–15 days after confirmation; the shop confirms your
                    date.</p>
            </div>
        </li>
    </ol>
</section>
@include('partials.fit-guide')

<section class="tracking-banner">
    <div>
        <p class="section-label">ALREADY ORDERED?</p>
        <h2>Good things are taking shape.</h2>
        <p>Check your latest order status with your order number and mobile number.</p>
    </div><a class="btn btn-gold btn-lg" href="/track-order">Track your order ↗</a>
</section>
