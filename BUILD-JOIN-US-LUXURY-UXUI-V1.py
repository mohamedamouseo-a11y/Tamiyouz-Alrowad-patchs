#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

SOURCE_MARKER = 'TAM_JOIN_US_WORDPRESS_FORCE_V1'
PATCH_MARKER = 'TAM_JOIN_US_LUXURY_V1'
REQUIRED_MARKERS = [
    SOURCE_MARKER,
    'https://careers.tamiyouzplaform.com/',
    'https://careers.tamiyouzplaform.com/api/v1/rakan/chat',
    "fetch('/join-us/notify.php'",
    "e.data.type === 'formSubmission'",
    "id=\"careersFrame\"",
]

LUXURY_CSS = r'''<style id="tamiyouz-join-us-luxury-v1">
:root{
  --lux-bg:#07131f;
  --lux-bg-2:#0a1827;
  --lux-panel:#0d1d2e;
  --lux-panel-2:#11243a;
  --lux-text:#f7f4ec;
  --lux-muted:#9aa9b8;
  --lux-gold:#e6b332;
  --lux-gold-2:#ffd765;
  --lux-gold-deep:#9b6d0a;
  --lux-line:rgba(230,179,50,.20);
  --lux-shadow:0 26px 80px rgba(0,0,0,.42);
  --lux-radius:26px;
}
html{scroll-behavior:smooth}
body{
  background:
    radial-gradient(900px 520px at 10% 16%,rgba(230,179,50,.07),transparent 65%),
    linear-gradient(180deg,#06111d 0%,#07131f 48%,#081724 100%);
  color:var(--lux-text);
}
body::before{
  content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  opacity:.25;
  z-index:-1;
  background-image:linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.018) 1px,transparent 1px);
  background-size:64px 64px;
  mask-image:linear-gradient(to bottom,black,transparent 78%);
}
.site-header{background:rgba(4,12,21,.52);backdrop-filter:blur(16px);border-bottom:1px solid rgba(255,255,255,.04)}
.site-header.scrolled{background:rgba(4,12,21,.92);border-bottom-color:var(--lux-line)}
.main-nav a{font-weight:600;letter-spacing:.01em}
.main-nav a:hover,.main-nav a.active{color:var(--lux-gold-2)}

.lux-page{overflow:hidden;background:transparent}
.lux-container{width:min(1180px,calc(100% - 40px));margin-inline:auto}
.lux-section{position:relative;padding:96px 0}
.lux-eyebrow{display:inline-flex;align-items:center;gap:10px;color:var(--lux-gold-2);font-size:12px;font-weight:800;letter-spacing:.24em;text-transform:uppercase}
.lux-eyebrow::before{content:"";width:34px;height:1px;background:linear-gradient(90deg,transparent,var(--lux-gold))}
.lux-title{font-size:clamp(32px,4.2vw,62px);line-height:1.18;font-weight:800;letter-spacing:-.03em;margin:16px 0 18px}
.lux-title .gold,.lux-section-title .gold{color:var(--lux-gold-2);text-shadow:0 0 30px rgba(230,179,50,.18)}
.lux-copy{font-size:clamp(14px,1.35vw,18px);line-height:2;color:#c4cdd6;max-width:680px}
.lux-section-head{text-align:center;max-width:760px;margin:0 auto 42px}
.lux-section-title{font-size:clamp(27px,3vw,42px);line-height:1.35;margin:10px 0 12px;color:#fff}
.lux-section-subtitle{color:var(--lux-muted);line-height:1.9;font-size:15px}

/* HERO */
.lux-hero{position:relative;min-height:740px;display:flex;align-items:center;margin-top:60px;isolation:isolate;background:#070f18}
.lux-hero-media{position:absolute;inset:0;z-index:-3;overflow:hidden}
.lux-hero-media video{width:100%;height:100%;object-fit:cover;filter:saturate(.75) contrast(1.08) brightness(.72);transform:scale(1.035)}
.lux-hero-media::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(4,11,18,.97) 0%,rgba(4,11,18,.78) 34%,rgba(4,11,18,.18) 66%,rgba(4,11,18,.58) 100%),linear-gradient(180deg,rgba(2,8,14,.18),rgba(6,17,29,.46) 72%,#07131f 100%)}
.lux-hero::before{content:"";position:absolute;width:380px;height:380px;border-radius:50%;right:-150px;top:90px;border:1px solid rgba(230,179,50,.18);box-shadow:0 0 90px rgba(230,179,50,.09);z-index:-1}
.lux-hero::after{content:"";position:absolute;left:-180px;bottom:-120px;width:520px;height:260px;border:1px solid rgba(230,179,50,.16);border-radius:50%;transform:rotate(-10deg);filter:drop-shadow(0 0 30px rgba(230,179,50,.08));z-index:-1}
.lux-hero-grid{display:grid;grid-template-columns:1.12fr .88fr;gap:70px;align-items:center;width:100%}
.lux-hero-content{padding:70px 0 140px}
.lux-hero h1{font-size:clamp(48px,6.5vw,92px);line-height:1.03;font-weight:300;letter-spacing:-.055em;margin:18px 0 24px;max-width:740px}
.lux-hero h1 strong{display:block;color:var(--lux-gold-2);font-weight:800;margin-top:4px}
.lux-hero-actions{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-top:32px}
.lux-btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:52px;padding:0 24px;border-radius:999px;text-decoration:none;font-weight:800;font-size:14px;transition:.28s ease;border:1px solid transparent}
.lux-btn-primary{background:linear-gradient(135deg,var(--lux-gold-2),#d79c15);color:#08131f;box-shadow:0 12px 34px rgba(230,179,50,.24)}
.lux-btn-primary:hover{transform:translateY(-2px);box-shadow:0 16px 42px rgba(230,179,50,.34);color:#08131f}
.lux-btn-ghost{border-color:rgba(255,255,255,.18);color:#fff;background:rgba(8,20,33,.36);backdrop-filter:blur(12px)}
.lux-btn-ghost:hover{border-color:var(--lux-gold);color:var(--lux-gold-2);transform:translateY(-2px)}
.lux-hero-note{justify-self:end;align-self:end;margin-bottom:150px;text-align:right;max-width:270px;padding:24px;border-right:1px solid var(--lux-gold);background:linear-gradient(90deg,transparent,rgba(230,179,50,.05));border-radius:0 18px 18px 0}
.lux-hero-note b{display:block;color:var(--lux-gold-2);font-size:20px;line-height:1.8}.lux-hero-note span{display:block;color:#8998a8;font-size:13px;line-height:1.8;margin-top:7px}

/* APPLICATION STAGE */
.lux-apply-stage{position:relative;margin-top:-116px;z-index:5;padding-bottom:32px}
.lux-apply-shell{width:min(930px,calc(100% - 30px));margin:0 auto;border:1px solid rgba(230,179,50,.28);border-radius:32px;background:linear-gradient(180deg,rgba(13,29,46,.98),rgba(8,22,36,.98));box-shadow:0 35px 90px rgba(0,0,0,.52),0 0 90px rgba(230,179,50,.07);overflow:hidden;position:relative}
.lux-apply-shell::before{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(115deg,transparent 0 42%,rgba(255,255,255,.035) 49%,transparent 56%)}
.lux-apply-head{text-align:center;padding:34px 28px 20px;border-bottom:1px solid rgba(230,179,50,.12);position:relative}
.lux-apply-head h2{font-size:clamp(24px,3vw,36px);color:var(--lux-gold-2);margin:0 0 7px}.lux-apply-head p{color:#8fa0b2;font-size:14px}
.lux-steps{display:flex;align-items:center;justify-content:center;gap:0;margin:24px auto 0;max-width:520px;direction:rtl}
.lux-step{display:flex;align-items:center;gap:8px;color:#7f8b99;font-size:11px;white-space:nowrap}.lux-step i{font-style:normal;width:27px;height:27px;border-radius:50%;display:grid;place-items:center;border:1px solid #435064;background:#19283b;color:#b9c4ce;font-weight:800}.lux-step.active{color:var(--lux-gold-2)}.lux-step.active i{background:var(--lux-gold);color:#07131f;border-color:var(--lux-gold)}.lux-step-line{height:1px;flex:1;min-width:44px;background:linear-gradient(90deg,#3b4757,rgba(230,179,50,.38));margin:0 10px}
.lux-iframe-mask{position:relative;overflow:hidden;background:#0b1a2a;min-height:760px}
.lux-iframe-mask::before{content:"";position:absolute;inset:0 0 auto;height:22px;background:linear-gradient(#0b1a2a,transparent);z-index:2;pointer-events:none}
.lux-iframe-mask iframe{display:block!important;width:100%!important;border:0!important;margin:-205px 0 -48px!important;min-height:980px!important;height:1080px;clip-path:none!important;background:#0b1a2a}
.lux-apply-trust{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid rgba(230,179,50,.12);background:rgba(5,15,25,.68)}
.lux-trust{padding:16px;text-align:center;border-left:1px solid rgba(255,255,255,.05);color:#aeb9c5;font-size:12px}.lux-trust:last-child{border-left:0}.lux-trust b{display:block;color:var(--lux-gold-2);font-size:14px;margin-bottom:3px}

/* STATS */
.lux-stats{padding:30px 0 0}.lux-stats-grid{display:grid;grid-template-columns:repeat(4,1fr);border-block:1px solid rgba(230,179,50,.12);background:rgba(10,25,40,.48);backdrop-filter:blur(10px)}
.lux-stat{text-align:center;padding:28px 16px;position:relative}.lux-stat:not(:last-child)::after{content:"";position:absolute;left:0;top:28%;height:44%;width:1px;background:rgba(255,255,255,.08)}.lux-stat strong{display:block;color:#fff;font-size:32px;letter-spacing:-.03em}.lux-stat strong span{color:var(--lux-gold-2)}.lux-stat small{color:#8999aa;font-size:12px}

/* CULTURE */
.lux-culture-grid{display:grid;grid-template-columns:.95fr 1.05fr;gap:34px;align-items:stretch}
.lux-culture-visual{min-height:500px;border-radius:var(--lux-radius);position:relative;overflow:hidden;border:1px solid rgba(230,179,50,.14);background:radial-gradient(circle at 30% 35%,rgba(230,179,50,.18),transparent 27%),linear-gradient(135deg,#11253a,#07131f 72%);box-shadow:var(--lux-shadow)}
.lux-culture-visual::before{content:"";position:absolute;inset:0;background:linear-gradient(135deg,transparent 0 45%,rgba(230,179,50,.08) 46%,transparent 47%),radial-gradient(circle at 68% 38%,rgba(255,255,255,.08),transparent 20%)}
.lux-culture-visual::after{content:"نصنع الفرق معًا";position:absolute;right:34px;bottom:34px;font-size:34px;line-height:1.4;color:#fff;font-weight:300;max-width:250px;border-right:2px solid var(--lux-gold);padding-right:18px;text-shadow:0 10px 30px #000}
.lux-culture-copy{padding:26px 0 10px}.lux-benefits{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:28px}.lux-benefit{border:1px solid rgba(230,179,50,.13);border-radius:18px;padding:20px;background:linear-gradient(145deg,rgba(18,38,59,.78),rgba(10,25,40,.72));transition:.28s ease}.lux-benefit:hover{transform:translateY(-4px);border-color:rgba(230,179,50,.38);box-shadow:0 14px 40px rgba(0,0,0,.24)}.lux-benefit-icon{width:40px;height:40px;border-radius:13px;display:grid;place-items:center;background:rgba(230,179,50,.12);border:1px solid rgba(230,179,50,.25);color:var(--lux-gold-2);margin-bottom:12px}.lux-benefit h3{font-size:15px;margin-bottom:6px}.lux-benefit p{color:#8d9dad;font-size:12px;line-height:1.8}

/* TALENT AREAS */
.lux-areas{background:linear-gradient(180deg,rgba(255,255,255,.01),rgba(230,179,50,.025),transparent)}
.lux-areas-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.lux-area-card{min-height:148px;padding:22px;border:1px solid rgba(230,179,50,.14);border-radius:19px;background:linear-gradient(150deg,rgba(17,36,56,.88),rgba(9,23,37,.88));position:relative;overflow:hidden;transition:.3s ease}.lux-area-card::before{content:"";position:absolute;right:-38px;top:-42px;width:110px;height:110px;border:1px solid rgba(230,179,50,.14);border-radius:50%}.lux-area-card:hover{transform:translateY(-5px);border-color:rgba(230,179,50,.42);box-shadow:0 18px 50px rgba(0,0,0,.24)}.lux-area-icon{color:var(--lux-gold-2);font-size:18px;margin-bottom:22px}.lux-area-card h3{font-size:15px;margin-bottom:6px}.lux-area-card p{color:#8393a4;font-size:11px}.lux-area-arrow{position:absolute;left:18px;bottom:18px;color:var(--lux-gold-2)}

/* JOURNEY */
.lux-journey-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.lux-journey-card{border:1px solid rgba(255,255,255,.07);border-radius:21px;padding:28px;background:linear-gradient(145deg,rgba(255,255,255,.035),rgba(255,255,255,.012));position:relative;overflow:hidden}.lux-journey-card::before{content:attr(data-step);position:absolute;left:18px;top:4px;font-size:76px;line-height:1;color:rgba(230,179,50,.055);font-weight:900}.lux-journey-card b{color:var(--lux-gold-2);display:block;margin-bottom:9px;font-size:16px}.lux-journey-card p{color:#9ba8b5;font-size:13px;line-height:1.9}

/* CTA */
.lux-cta{padding-top:36px;padding-bottom:100px}.lux-cta-card{min-height:260px;border-radius:28px;border:1px solid rgba(230,179,50,.22);background:radial-gradient(600px 250px at 50% 120%,rgba(230,179,50,.18),transparent 70%),linear-gradient(135deg,#12253a,#081724);box-shadow:var(--lux-shadow);display:grid;place-items:center;text-align:center;padding:40px;position:relative;overflow:hidden}.lux-cta-card::before,.lux-cta-card::after{content:"";position:absolute;width:420px;height:120px;border:1px solid rgba(230,179,50,.16);border-radius:50%;bottom:-90px}.lux-cta-card::before{left:-80px}.lux-cta-card::after{right:-80px}.lux-cta-card h2{font-size:clamp(28px,3.5vw,46px);margin-bottom:10px}.lux-cta-card p{color:#9aa9b8;margin-bottom:22px}

/* Motion */
.lux-reveal{opacity:0;transform:translateY(26px);transition:opacity .75s ease,transform .75s ease}.lux-reveal.is-visible{opacity:1;transform:none}.lux-delay-1{transition-delay:.08s}.lux-delay-2{transition-delay:.16s}.lux-delay-3{transition-delay:.24s}
.lux-focus:focus-visible,.lux-btn:focus-visible{outline:2px solid var(--lux-gold-2);outline-offset:4px}
.site-footer{background:#07131f;border-top:1px solid rgba(230,179,50,.14)}

@media(max-width:1024px){
  .lux-hero{min-height:680px}.lux-hero-grid{grid-template-columns:1fr;gap:10px}.lux-hero-content{padding:70px 0 160px}.lux-hero-note{display:none}.lux-culture-grid{grid-template-columns:1fr}.lux-culture-visual{min-height:390px}.lux-areas-grid{grid-template-columns:repeat(2,1fr)}.lux-apply-shell{width:min(850px,calc(100% - 28px))}
}
@media(max-width:720px){
  .lux-container{width:min(100% - 28px,1180px)}.lux-section{padding:70px 0}.lux-hero{min-height:650px}.lux-hero h1{font-size:48px}.lux-hero-content{padding-bottom:150px}.lux-hero-actions{align-items:stretch}.lux-btn{width:100%}.lux-apply-stage{margin-top:-92px}.lux-apply-shell{border-radius:22px}.lux-apply-head{padding-inline:16px}.lux-steps{transform:scale(.88);transform-origin:center}.lux-iframe-mask{min-height:800px}.lux-iframe-mask iframe{margin-top:-172px!important;min-height:1040px!important;height:1120px}.lux-apply-trust{grid-template-columns:repeat(2,1fr)}.lux-stats-grid{grid-template-columns:repeat(2,1fr)}.lux-stat:nth-child(2)::after{display:none}.lux-benefits{grid-template-columns:1fr}.lux-areas-grid{grid-template-columns:1fr}.lux-journey-grid{grid-template-columns:1fr}.lux-culture-visual{min-height:320px}.lux-culture-visual::after{font-size:26px;right:24px;bottom:24px}.lux-cta-card{padding:34px 22px}.lux-section-head{margin-bottom:30px}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.lux-reveal{opacity:1;transform:none;transition:none}.lux-btn,.lux-benefit,.lux-area-card{transition:none}.rakan-float-btn,.rakan-pulse-ring{animation:none!important}}
</style>'''

LUXURY_MAIN = r'''<main class="lux-page" id="main-content">
  <!-- TAM_JOIN_US_LUXURY_V1 -->
  <section class="lux-hero" aria-labelledby="join-us-title">
    <div class="lux-hero-media" aria-hidden="true">
      <video autoplay muted loop playsinline preload="metadata" poster="https://tamiyouzalrowad.com/wp-content/uploads/thegem/logos/logo_651908704a66443a544d00fe24e2d319_1x.png">
        <source src="<?php echo esc_url(get_stylesheet_directory_uri() . '/assets/join-us/video-header.mp4?v=6'); ?>" type="video/mp4">
      </video>
    </div>
    <div class="lux-container lux-hero-grid">
      <div class="lux-hero-content lux-reveal is-visible">
        <span class="lux-eyebrow">BUILD A BRIGHTER TOMORROW</span>
        <h1 id="join-us-title">انضم إلى <strong>صُنّاع التميز</strong></h1>
        <p class="lux-copy">في تميز الرواد نؤمن أن أعظم الإنجازات تبدأ من أشخاص استثنائيين. انضم إلى بيئة تجمع الطموح والإبداع والتعلّم المستمر، واصنع معنا أثرًا يتجاوز حدود الوظيفة.</p>
        <div class="lux-hero-actions">
          <a class="lux-btn lux-btn-primary lux-focus" href="#apply-now"><span>اكتشف فرصتك معنا</span><span aria-hidden="true">←</span></a>
          <a class="lux-btn lux-btn-ghost lux-focus" href="#life-at-tamiyouz"><span aria-hidden="true">▶</span><span>اكتشف ثقافتنا</span></a>
        </div>
      </div>
      <aside class="lux-hero-note lux-reveal lux-delay-2" aria-label="رسالة التوظيف">
        <b>أشخاص مميزون يصنعون مستقبلاً أفضل.</b>
        <span>More than a job — a meaningful career journey.</span>
      </aside>
    </div>
  </section>

  <section class="lux-apply-stage" id="apply-now" aria-labelledby="apply-title">
    <div class="lux-apply-shell lux-reveal">
      <div class="lux-apply-head">
        <span class="lux-eyebrow">YOUR NEXT CHAPTER</span>
        <h2 id="apply-title">فرصتك تبدأ معنا اليوم</h2>
        <p>أكمل بياناتك المهنية بعناية، وفريقنا سيقوم بمراجعة طلبك.</p>
        <div class="lux-steps" aria-label="مراحل التقديم">
          <span class="lux-step active"><i>1</i>البيانات الشخصية</span><span class="lux-step-line"></span>
          <span class="lux-step"><i>2</i>الخبرات المهنية</span><span class="lux-step-line"></span>
          <span class="lux-step"><i>3</i>المراجعة</span>
        </div>
      </div>
      <div class="lux-iframe-mask">
        <iframe src="https://careers.tamiyouzplaform.com/"
                id="careersFrame"
                title="نموذج التقديم للوظائف - تميز الرواد"
                scrolling="yes"
                loading="eager"
                sandbox="allow-scripts allow-forms allow-same-origin allow-popups"
                allowfullscreen></iframe>
      </div>
      <div class="lux-apply-trust" aria-label="مزايا تجربة التقديم">
        <div class="lux-trust"><b>خصوصية</b>بياناتك محفوظة</div>
        <div class="lux-trust"><b>وضوح</b>خطوات تقديم مباشرة</div>
        <div class="lux-trust"><b>احترافية</b>مراجعة منظمة</div>
        <div class="lux-trust"><b>تواصل</b>متابعة من فريق الموارد البشرية</div>
      </div>
    </div>
  </section>

  <section class="lux-stats" aria-label="تميز الرواد بالأرقام">
    <div class="lux-stats-grid">
      <div class="lux-stat lux-reveal"><strong><span>+</span><span class="lux-count" data-count="5">5</span></strong><small>سنوات من التميز</small></div>
      <div class="lux-stat lux-reveal lux-delay-1"><strong><span>+</span><span class="lux-count" data-count="8">8</span></strong><small>تخصصات رقمية متكاملة</small></div>
      <div class="lux-stat lux-reveal lux-delay-2"><strong><span>+</span><span class="lux-count" data-count="50">50</span></strong><small>مشروعًا وفرصة للتعلّم</small></div>
      <div class="lux-stat lux-reveal lux-delay-3"><strong><span>+</span><span class="lux-count" data-count="100">100</span></strong><small>طموح يجمع فريقنا</small></div>
    </div>
  </section>

  <section class="lux-section" id="life-at-tamiyouz" aria-labelledby="why-title">
    <div class="lux-container lux-culture-grid">
      <div class="lux-culture-visual lux-reveal" role="img" aria-label="بيئة عمل تميز الرواد"></div>
      <div class="lux-culture-copy lux-reveal lux-delay-1">
        <span class="lux-eyebrow">LIFE AT TAMIYOUZ</span>
        <h2 class="lux-section-title" id="why-title">لماذا تنضم إلى <span class="gold">تميز الرواد؟</span></h2>
        <p class="lux-section-subtitle">لأنك لا تبحث عن وظيفة فقط، بل عن مساحة تتطور فيها، وتشارك أفكارك، وتعمل مع فريق يؤمن أن التميز عادة يومية.</p>
        <div class="lux-benefits">
          <article class="lux-benefit"><div class="lux-benefit-icon">✦</div><h3>بيئة محفزة</h3><p>مساحة عمل تقدّر المبادرة والأفكار الجديدة وتدعم التعاون الحقيقي.</p></article>
          <article class="lux-benefit"><div class="lux-benefit-icon">↗</div><h3>نمو مهني</h3><p>فرص مستمرة لتطوير مهاراتك من خلال مشاريع حقيقية وتحديات متنوعة.</p></article>
          <article class="lux-benefit"><div class="lux-benefit-icon">◎</div><h3>مشاريع مؤثرة</h3><p>اعمل على حلول رقمية ترتبط بأهداف واضحة وتترك أثرًا ملموسًا.</p></article>
          <article class="lux-benefit"><div class="lux-benefit-icon">⚖</div><h3>مرونة واتزان</h3><p>ثقافة تحترم جودة الإنجاز وتدعم تنظيم العمل بصورة صحية واحترافية.</p></article>
        </div>
      </div>
    </div>
  </section>

  <section class="lux-section lux-areas" aria-labelledby="areas-title">
    <div class="lux-container">
      <header class="lux-section-head lux-reveal">
        <span class="lux-eyebrow">TALENT AREAS</span>
        <h2 class="lux-section-title" id="areas-title">مجالات نبحث فيها عن <span class="gold">المواهب</span></h2>
        <p class="lux-section-subtitle">نرحب بأصحاب الخبرة والطموح في تخصصات التسويق والتقنية والإبداع الرقمي.</p>
      </header>
      <div class="lux-areas-grid">
        <article class="lux-area-card lux-reveal"><div class="lux-area-icon">◈</div><h3>التسويق الرقمي</h3><p>استراتيجية، أداء، حملات ونمو.</p><span class="lux-area-arrow">←</span></article>
        <article class="lux-area-card lux-reveal lux-delay-1"><div class="lux-area-icon">⌁</div><h3>تطوير وتصميم المواقع</h3><p>تجارب رقمية سريعة وفعالة.</p><span class="lux-area-arrow">←</span></article>
        <article class="lux-area-card lux-reveal lux-delay-2"><div class="lux-area-icon">▦</div><h3>تصميم الجرافيك والمحتوى</h3><p>هوية، محتوى بصري وموشن.</p><span class="lux-area-arrow">←</span></article>
        <article class="lux-area-card lux-reveal lux-delay-3"><div class="lux-area-icon">◎</div><h3>إدارة المشاريع والحسابات</h3><p>تنظيم، متابعة وتجربة عميل.</p><span class="lux-area-arrow">←</span></article>
      </div>
    </div>
  </section>

  <section class="lux-section" aria-labelledby="journey-title">
    <div class="lux-container">
      <header class="lux-section-head lux-reveal">
        <span class="lux-eyebrow">YOUR JOURNEY</span>
        <h2 class="lux-section-title" id="journey-title">رحلة واضحة من الطلب إلى <span class="gold">الانضمام</span></h2>
      </header>
      <div class="lux-journey-grid">
        <article class="lux-journey-card lux-reveal" data-step="01"><b>أرسل طلبك</b><p>شارك بياناتك وخبراتك وسيرتك الذاتية من خلال نموذج التقديم.</p></article>
        <article class="lux-journey-card lux-reveal lux-delay-1" data-step="02"><b>مراجعة ومقابلة</b><p>يقوم فريق الموارد البشرية بمراجعة الطلبات المناسبة والتواصل للخطوة التالية.</p></article>
        <article class="lux-journey-card lux-reveal lux-delay-2" data-step="03"><b>ابدأ رحلتك</b><p>عند اكتمال مراحل الاختيار، تبدأ تجربة جديدة مع فريق تميز الرواد.</p></article>
      </div>
    </div>
  </section>

  <section class="lux-cta">
    <div class="lux-container">
      <div class="lux-cta-card lux-reveal">
        <div>
          <span class="lux-eyebrow">MAKE YOUR MOVE</span>
          <h2>مستقبلك يبدأ بخطوة.</h2>
          <p>قد تكون هذه الخطوة بداية أفضل فصل في رحلتك المهنية.</p>
          <a class="lux-btn lux-btn-primary lux-focus" href="#apply-now">قدّم طلبك الآن <span aria-hidden="true">←</span></a>
        </div>
      </div>
    </div>
  </section>
</main>'''

LUXURY_JS = r'''<script id="tamiyouz-join-us-luxury-v1-js">
(function(){
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = document.querySelectorAll('.lux-reveal');
  if (reduce || !('IntersectionObserver' in window)) {
    items.forEach(function(el){ el.classList.add('is-visible'); });
  } else {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){ entry.target.classList.add('is-visible'); io.unobserve(entry.target); }
      });
    },{threshold:.12,rootMargin:'0px 0px -30px 0px'});
    items.forEach(function(el){ if(!el.classList.contains('is-visible')) io.observe(el); });
  }
  var counts = document.querySelectorAll('.lux-count');
  if(!reduce && 'IntersectionObserver' in window){
    var cio = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(!entry.isIntersecting) return;
        var el = entry.target, target = parseInt(el.getAttribute('data-count')||'0',10), start = 0, duration = 900, t0 = performance.now();
        function tick(now){ var p=Math.min(1,(now-t0)/duration); el.textContent=Math.round(target*(1-Math.pow(1-p,3))); if(p<1) requestAnimationFrame(tick); }
        requestAnimationFrame(tick); cio.unobserve(el);
      });
    },{threshold:.7});
    counts.forEach(function(el){ cio.observe(el); });
  }
})();
</script>'''

SEO_BLOCK = r'''<!-- Structured Data / Schema.org -->
  <script type="application/ld+json">
  {
    "@context":"https://schema.org",
    "@graph":[
      {
        "@type":"CollectionPage",
        "@id":"https://tamiyouzalrowad.com/join-us/#webpage",
        "url":"https://tamiyouzalrowad.com/join-us/",
        "name":"وظائف تميز الرواد | انضم لفريقنا",
        "description":"انضم إلى فريق تميز الرواد واكتشف فرص العمل في التسويق الرقمي والتقنية والإبداع.",
        "inLanguage":"ar",
        "isPartOf":{"@id":"https://tamiyouzalrowad.com/#website"},
        "about":{"@id":"https://tamiyouzalrowad.com/#organization"},
        "breadcrumb":{"@id":"https://tamiyouzalrowad.com/join-us/#breadcrumb"}
      },
      {
        "@type":"WebSite",
        "@id":"https://tamiyouzalrowad.com/#website",
        "url":"https://tamiyouzalrowad.com/",
        "name":"تميز الرواد",
        "inLanguage":"ar"
      },
      {
        "@type":"Organization",
        "@id":"https://tamiyouzalrowad.com/#organization",
        "name":"تميز الرواد",
        "alternateName":"Tamiyouz Al Rowad",
        "url":"https://tamiyouzalrowad.com/",
        "logo":{"@type":"ImageObject","url":"https://tamiyouzalrowad.com/wp-content/uploads/2024/05/28c37489c969625933a9e573e7aace35.png"},
        "sameAs":[
          "https://www.facebook.com/tamiyouzalrowad",
          "https://www.instagram.com/tamiyouzalrowad",
          "https://twitter.com/tamiyouzalrowad",
          "https://www.youtube.com/@tamiyouzalrowad",
          "https://www.linkedin.com/company/tamiyouzalrowad",
          "https://www.tiktok.com/@tamiyouzalrowad"
        ]
      },
      {
        "@type":"BreadcrumbList",
        "@id":"https://tamiyouzalrowad.com/join-us/#breadcrumb",
        "itemListElement":[
          {"@type":"ListItem","position":1,"name":"الرئيسية","item":"https://tamiyouzalrowad.com/"},
          {"@type":"ListItem","position":2,"name":"انضم لفريقنا","item":"https://tamiyouzalrowad.com/join-us/"}
        ]
      }
    ]
  }
  </script>'''


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def transform(source: str) -> str:
    missing = [m for m in REQUIRED_MARKERS if m not in source]
    if missing:
        raise SystemExit('SOURCE_GUARD_FAILED missing=' + json.dumps(missing, ensure_ascii=False))
    if PATCH_MARKER in source or 'tamiyouz-join-us-luxury-v1' in source:
        raise SystemExit('ALREADY_APPLIED')

    # Replace the old aggregated JobPosting schema with truthful page/organization/breadcrumb graph.
    schema_re = re.compile(r'<!-- Structured Data / Schema\.org -->\s*<script type="application/ld\+json">.*?</script>', re.S)
    source, schema_count = schema_re.subn(SEO_BLOCK, source, count=1)
    if schema_count != 1:
        raise SystemExit('SCHEMA_REPLACE_FAILED count=' + str(schema_count))

    # Insert override layer without disturbing the stable header/footer/integrations CSS.
    if '</head>' not in source:
        raise SystemExit('HEAD_END_NOT_FOUND')
    source = source.replace('</head>', LUXURY_CSS + '\n</head>', 1)

    # Replace only the page main presentation. Header, footer, Rakan, WhatsApp and postMessage scripts stay intact.
    main_re = re.compile(r'<main>.*?</main>', re.S)
    source, main_count = main_re.subn(lambda _m: LUXURY_MAIN, source, count=1)
    if main_count != 1:
        raise SystemExit('MAIN_REPLACE_FAILED count=' + str(main_count))

    if '</body>' not in source:
        raise SystemExit('BODY_END_NOT_FOUND')
    source = source.replace('</body>', LUXURY_JS + '\n</body>', 1)

    # Integration-preservation guards after transformation.
    post_missing = [m for m in REQUIRED_MARKERS if m not in source]
    if post_missing:
        raise SystemExit('POST_GUARD_FAILED missing=' + json.dumps(post_missing, ensure_ascii=False))
    if source.count(PATCH_MARKER) != 1:
        raise SystemExit('PATCH_MARKER_COUNT_INVALID')
    if source.count('id="careersFrame"') != 1:
        raise SystemExit('CAREERS_IFRAME_COUNT_INVALID')
    if source.count('https://careers.tamiyouzplaform.com/api/v1/rakan/chat') != 1:
        raise SystemExit('RAKAN_ENDPOINT_COUNT_INVALID')
    if source.count("fetch('/join-us/notify.php'") != 1:
        raise SystemExit('LEGACY_NOTIFY_HOOK_COUNT_INVALID')
    return source


def main():
    ap = argparse.ArgumentParser(description='Build Join Us Luxury UX/UI V1 from the current successful WordPress template.')
    ap.add_argument('--source', required=True, help='Current page-join-us.php')
    ap.add_argument('--output', required=True, help='Output transformed page-join-us.php')
    ap.add_argument('--manifest', help='Optional JSON manifest path')
    args = ap.parse_args()

    src_path = Path(args.source)
    out_path = Path(args.output)
    source = src_path.read_text(encoding='utf-8')
    result = transform(source)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result, encoding='utf-8')

    manifest = {
        'patch': 'JOIN_US_LUXURY_UXUI_V1',
        'source_path': str(src_path),
        'source_sha256': sha256_text(source),
        'output_path': str(out_path),
        'output_sha256': sha256_text(result),
        'source_marker': SOURCE_MARKER,
        'patch_marker': PATCH_MARKER,
        'careers_iframe_preserved': 'https://careers.tamiyouzplaform.com/' in result,
        'rakan_preserved': 'https://careers.tamiyouzplaform.com/api/v1/rakan/chat' in result,
        'form_submission_preserved': "e.data.type === 'formSubmission'" in result,
        'legacy_notify_hook_preserved': "fetch('/join-us/notify.php'" in result,
        'seo_schema': 'CollectionPage+WebSite+Organization+BreadcrumbList',
        'jobposting_schema_removed': '"@type": "JobPosting"' not in result and '"@type":"JobPosting"' not in result,
    }
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == '__main__':
    main()
