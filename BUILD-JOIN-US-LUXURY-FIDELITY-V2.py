#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

PATCH_ID = "JOIN_US_LUXURY_FIDELITY_V2"
PATCH_MARKER = "TAM_JOIN_US_LUXURY_V2_FIDELITY"
REQUIRED_MARKERS = [
    "TAM_JOIN_US_WORDPRESS_FORCE_V1",
    "TAM_JOIN_US_LUXURY_V1",
    "https://careers.tamiyouzplaform.com/",
    "https://careers.tamiyouzplaform.com/api/v1/rakan/chat",
    "fetch('/join-us/notify.php'",
    "e.data.type === 'formSubmission'",
    'id="careersFrame"',
]

TEAM_ESRAA = "https://tamiyouzalrowad.com/wp-content/uploads/2019/07/14-thegem-person.jpg.webp"
TEAM_CAROLINE = "https://tamiyouzalrowad.com/wp-content/uploads/2023/12/17-thegem-person.jpg"
TEAM_RANA = "https://tamiyouzalrowad.com/wp-content/uploads/2024/04/%D8%B5%D9%88%D8%B1-09-thegem-person.jpg"
LOGO = "https://tamiyouzalrowad.com/wp-content/uploads/thegem/logos/logo_651908704a66443a544d00fe24e2d319_1x.png"

V2_CSS = r'''
<style id="tamiyouz-join-us-luxury-v2-fidelity">
/* TAM_JOIN_US_LUXURY_V2_FIDELITY */
:root{
  --v2-gold:#f0bc35;
  --v2-gold-soft:#ffd86a;
  --v2-ink:#06111b;
  --v2-panel:#0b1b2a;
  --v2-line:rgba(240,188,53,.22);
}

/* Header: larger, calmer and closer to the premium reference */
.site-header{min-height:68px;background:linear-gradient(180deg,rgba(3,10,17,.92),rgba(3,10,17,.68));border-bottom:1px solid rgba(240,188,53,.10)}
.header-inner{min-height:68px;max-width:1500px;margin:0 auto;padding:0 22px;gap:10px}
.logo img{height:52px;filter:drop-shadow(0 0 14px rgba(240,188,53,.18))}
.main-nav{justify-content:center;gap:1px}
.main-nav a{font-size:11.5px;padding:9px 7px;color:#d8dee6}
.main-nav a.active{background:linear-gradient(135deg,rgba(240,188,53,.20),rgba(240,188,53,.06));border:1px solid rgba(240,188,53,.32);border-radius:999px;color:var(--v2-gold-soft)!important;padding-inline:13px}

/* Hero: stronger cinematic framing */
.lux-hero{min-height:790px;margin-top:68px;background:#050d15}
.lux-hero-media video{filter:saturate(.70) contrast(1.14) brightness(.61);transform:scale(1.08);animation:v2HeroDrift 16s ease-in-out infinite alternate}
.lux-hero-media::after{background:
  radial-gradient(680px 520px at 62% 38%,rgba(240,188,53,.12),transparent 62%),
  linear-gradient(90deg,rgba(3,9,15,.98) 0%,rgba(3,9,15,.88) 28%,rgba(3,9,15,.28) 59%,rgba(3,9,15,.66) 100%),
  linear-gradient(180deg,rgba(2,7,12,.08),rgba(5,15,24,.34) 64%,#07131f 100%)}
.lux-hero::before{width:520px;height:520px;right:-190px;top:70px;border-color:rgba(240,188,53,.22);box-shadow:0 0 130px rgba(240,188,53,.11)}
.lux-hero::after{left:-140px;bottom:-70px;width:610px;height:250px;border-color:rgba(240,188,53,.20)}
.lux-hero-grid{grid-template-columns:1.08fr .92fr;gap:52px}
.lux-hero-content{padding:72px 0 178px;position:relative;z-index:3}
.lux-hero h1{font-size:clamp(58px,7vw,104px);line-height:.98;max-width:770px;margin-top:22px;text-shadow:0 18px 50px rgba(0,0,0,.44)}
.lux-hero h1 strong{background:linear-gradient(180deg,#ffe184 0%,#f0bc35 48%,#c88412 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 8px 22px rgba(240,188,53,.22))}
.lux-copy{max-width:720px;color:#c6d0da;font-size:16px}
.lux-hero-actions{margin-top:28px}
.lux-hero-note{margin-bottom:142px;max-width:292px;border-right:2px solid var(--v2-gold);background:linear-gradient(90deg,transparent,rgba(240,188,53,.075));box-shadow:22px 0 80px rgba(240,188,53,.05)}
.lux-hero-crest{position:absolute;left:47%;top:46%;transform:translate(-50%,-50%);z-index:-1;width:min(41vw,540px);opacity:.25;filter:sepia(1) saturate(1.4) drop-shadow(0 0 42px rgba(240,188,53,.24));pointer-events:none}
.lux-hero-crest img{width:100%;height:auto;display:block;animation:v2CrestFloat 7s ease-in-out infinite}
.lux-hero-scroll{position:absolute;left:50%;bottom:102px;transform:translateX(-50%);z-index:4;color:#aab5c0;font-size:10px;letter-spacing:.18em;text-transform:uppercase;display:flex;align-items:center;gap:10px}
.lux-hero-scroll::after{content:"";width:42px;height:1px;background:linear-gradient(90deg,var(--v2-gold),transparent)}
@keyframes v2HeroDrift{from{transform:scale(1.08) translate3d(0,0,0)}to{transform:scale(1.13) translate3d(-1.2%,.7%,0)}}
@keyframes v2CrestFloat{0%,100%{transform:translateY(0) rotate(-1deg)}50%{transform:translateY(-14px) rotate(1deg)}}

/* Apply stage: reference-like floating shell + side storytelling */
.lux-apply-stage{margin-top:-148px;padding-bottom:20px;isolation:isolate}
.lux-apply-shell{width:min(980px,calc(100% - 34px));border-radius:30px;border-color:rgba(240,188,53,.34);background:linear-gradient(180deg,rgba(12,29,45,.985),rgba(6,20,33,.99));box-shadow:0 42px 110px rgba(0,0,0,.60),0 0 110px rgba(240,188,53,.08)}
.lux-apply-shell::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;box-shadow:inset 0 1px 0 rgba(255,255,255,.06),inset 0 0 70px rgba(240,188,53,.025)}
.lux-apply-head{padding:31px 28px 18px;background:radial-gradient(480px 120px at 50% 0,rgba(240,188,53,.10),transparent 72%)}
.lux-apply-head h2{font-size:34px;text-shadow:0 0 28px rgba(240,188,53,.18)}
.lux-iframe-mask{min-height:670px;background:#0a1a2a;overflow:hidden}
.lux-iframe-mask iframe{margin:-365px 0 -52px!important;min-height:1190px!important;height:1260px;background:#0a1a2a}
.lux-apply-trust{position:relative;z-index:4;background:rgba(4,14,23,.88)}
.lux-trust{padding:14px 12px}
.lux-apply-side{position:absolute;top:245px;width:190px;z-index:-1;padding:18px 16px;border:1px solid rgba(240,188,53,.20);background:linear-gradient(145deg,rgba(10,26,41,.88),rgba(5,17,28,.84));backdrop-filter:blur(14px);border-radius:18px;box-shadow:0 18px 55px rgba(0,0,0,.30);color:#93a4b4;font-size:11px;line-height:1.9}
.lux-apply-side b{display:block;color:var(--v2-gold-soft);font-size:15px;margin-bottom:7px}
.lux-apply-side::before{content:"";position:absolute;top:30px;width:74px;height:1px;background:linear-gradient(90deg,var(--v2-gold),transparent)}
.lux-apply-side-right{right:max(14px,calc(50% - 720px))}
.lux-apply-side-right::before{left:-55px}
.lux-apply-side-left{left:max(14px,calc(50% - 720px));text-align:left}
.lux-apply-side-left::before{right:-55px;transform:scaleX(-1)}

/* Stats: more visual authority */
.lux-stats{padding-top:16px}
.lux-stats-grid{max-width:1280px;margin:0 auto;border:1px solid rgba(240,188,53,.10);border-radius:0;background:linear-gradient(90deg,rgba(8,22,35,.82),rgba(11,28,43,.66),rgba(8,22,35,.82))}
.lux-stat{padding:25px 16px}
.lux-stat strong{font-size:36px}
.lux-stat small{font-size:11px;letter-spacing:.02em}
.lux-stat::before{display:block;margin:0 auto 7px;color:rgba(240,188,53,.72);font-size:13px}
.lux-stat:nth-child(1)::before{content:"✦"}.lux-stat:nth-child(2)::before{content:"◈"}.lux-stat:nth-child(3)::before{content:"↗"}.lux-stat:nth-child(4)::before{content:"◎"}

/* Culture: real current Tamiyouz team portraits rather than an abstract placeholder */
.lux-section{padding:84px 0}
.lux-culture-grid{gap:46px;align-items:center}
.lux-culture-visual{min-height:470px;background:#081724;display:grid;grid-template-columns:repeat(3,1fr);gap:0;box-shadow:0 32px 90px rgba(0,0,0,.42)}
.lux-culture-visual::before{z-index:2;background:linear-gradient(180deg,rgba(5,14,23,.04),rgba(5,14,23,.16) 52%,rgba(5,14,23,.86)),linear-gradient(90deg,rgba(240,188,53,.05),transparent)}
.lux-culture-visual::after{z-index:4;content:"نصنع الفرق معًا";font-size:31px}
.lux-culture-person{position:relative;overflow:hidden;min-height:470px}
.lux-culture-person img{width:100%;height:100%;object-fit:cover;object-position:center top;display:block;filter:saturate(.76) contrast(1.05) brightness(.82);transform:scale(1.03);transition:transform .7s ease,filter .5s ease}
.lux-culture-person:nth-child(2){transform:translateY(24px)}
.lux-culture-visual:hover .lux-culture-person img{transform:scale(1.08);filter:saturate(.92) contrast(1.07) brightness(.90)}

/* Areas: denser job-board-like visual hierarchy without fabricating vacancies */
.lux-areas-grid{grid-template-columns:repeat(3,1fr);gap:13px}
.lux-area-card{min-height:154px;padding:20px 21px}
.lux-area-card:nth-child(1),.lux-area-card:nth-child(4){background:linear-gradient(145deg,rgba(23,48,72,.92),rgba(7,22,35,.92))}
.lux-area-action{text-align:center;margin-top:25px}

/* Team cards: visually replaces the missing testimonial band without fake quotations */
.lux-team-band{padding-top:72px;padding-bottom:74px;background:linear-gradient(180deg,transparent,rgba(240,188,53,.018),transparent)}
.lux-team-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:34px}
.lux-team-card{display:grid;grid-template-columns:84px 1fr;gap:17px;align-items:center;padding:18px;border:1px solid rgba(240,188,53,.14);border-radius:21px;background:linear-gradient(145deg,rgba(16,35,54,.80),rgba(7,22,35,.88));box-shadow:0 18px 46px rgba(0,0,0,.22);transition:.3s ease}
.lux-team-card:hover{transform:translateY(-5px);border-color:rgba(240,188,53,.38)}
.lux-team-photo{width:84px;height:94px;border-radius:16px;overflow:hidden;border:1px solid rgba(240,188,53,.24);background:#102338}
.lux-team-photo img{width:100%;height:100%;object-fit:cover;object-position:center top;display:block}
.lux-team-meta small{display:block;color:var(--v2-gold-soft);font-size:9px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:5px}
.lux-team-meta h3{font-size:16px;margin:0 0 4px}.lux-team-meta p{color:#91a2b2;font-size:11px;margin:0;line-height:1.6}

/* Journey */
.lux-journey-card{min-height:160px;background:linear-gradient(145deg,rgba(255,255,255,.04),rgba(7,22,35,.74));border-color:rgba(240,188,53,.10)}
.lux-journey-card::after{content:"";position:absolute;inset:auto 24px 0;height:1px;background:linear-gradient(90deg,transparent,rgba(240,188,53,.38),transparent)}

/* CTA: more cinematic, with a lightweight CSS/SVG skyline layer */
.lux-cta{padding-top:18px;padding-bottom:90px}
.lux-cta-card{min-height:290px;background:radial-gradient(620px 220px at 50% 105%,rgba(240,188,53,.22),transparent 70%),linear-gradient(135deg,#11263a,#071521);overflow:hidden}
.lux-cta-card>div:not(.lux-cityline){position:relative;z-index:3}
.lux-cityline{position:absolute;inset:auto 0 0;height:118px;opacity:.24;color:var(--v2-gold);pointer-events:none}
.lux-cityline svg{width:100%;height:100%;display:block}

/* Footer tightening */
.site-footer{background:#06111b}.footer-inner{max-width:1240px}.footer-col h3{color:var(--v2-gold-soft)}

@media(max-width:1260px){.lux-apply-side{display:none}}
@media(max-width:1024px){
  .lux-hero{min-height:720px}.lux-hero-crest{left:68%;top:39%;width:min(56vw,470px)}.lux-hero-content{padding-bottom:170px}
  .lux-culture-visual{min-height:420px}.lux-culture-person{min-height:420px}.lux-team-grid{grid-template-columns:1fr}.lux-team-card{max-width:620px;width:100%;margin-inline:auto}.lux-areas-grid{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:720px){
  .site-header{min-height:60px}.header-inner{min-height:60px}.logo img{height:46px}.lux-hero{margin-top:60px;min-height:690px}.lux-hero h1{font-size:52px}.lux-hero-crest{left:50%;top:35%;width:82vw;opacity:.16}.lux-hero-scroll{display:none}
  .lux-apply-stage{margin-top:-96px}.lux-apply-head h2{font-size:27px}.lux-iframe-mask iframe{margin-top:-330px!important;min-height:1160px!important;height:1210px}.lux-iframe-mask{min-height:650px}
  .lux-culture-visual{min-height:360px;grid-template-columns:1fr 1fr}.lux-culture-person{min-height:360px}.lux-culture-person:nth-child(3){display:none}.lux-culture-person:nth-child(2){transform:none}
  .lux-areas-grid{grid-template-columns:1fr}.lux-team-card{grid-template-columns:72px 1fr}.lux-team-photo{width:72px;height:82px}.lux-section{padding:68px 0}
}
@media(prefers-reduced-motion:reduce){.lux-hero-media video,.lux-hero-crest img{animation:none!important}.lux-culture-person img,.lux-team-card{transition:none!important}}
</style>
'''

TEAM_SECTION = f'''
  <section class="lux-team-band" aria-labelledby="team-title">
    <div class="lux-container">
      <header class="lux-section-head lux-reveal">
        <span class="lux-eyebrow">PEOPLE OF TAMIYOUZ</span>
        <h2 class="lux-section-title" id="team-title">وجوه من <span class="gold">فريقنا</span></h2>
        <p class="lux-section-subtitle">فريق متعدد التخصصات يجمع التسويق والتقنية والإبداع في بيئة واحدة.</p>
      </header>
      <div class="lux-team-grid">
        <article class="lux-team-card lux-reveal">
          <div class="lux-team-photo"><img src="{TEAM_ESRAA}" alt="إسراء - Growth Marketing & Analysis Director في تميز الرواد" loading="lazy" decoding="async"></div>
          <div class="lux-team-meta"><small>TAMIYOUZ TEAM</small><h3>Esraa</h3><p>Growth Marketing &amp; Analysis Director</p></div>
        </article>
        <article class="lux-team-card lux-reveal lux-delay-1">
          <div class="lux-team-photo"><img src="{TEAM_CAROLINE}" alt="Caroline - Art Director في تميز الرواد" loading="lazy" decoding="async"></div>
          <div class="lux-team-meta"><small>TAMIYOUZ TEAM</small><h3>Caroline</h3><p>Art Director</p></div>
        </article>
        <article class="lux-team-card lux-reveal lux-delay-2">
          <div class="lux-team-photo"><img src="{TEAM_RANA}" alt="Rana - Web & E-commerce Lead في تميز الرواد" loading="lazy" decoding="async"></div>
          <div class="lux-team-meta"><small>TAMIYOUZ TEAM</small><h3>Rana</h3><p>Web &amp; E-commerce Lead</p></div>
        </article>
      </div>
    </div>
  </section>

'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def transform(source: str) -> str:
    for marker in REQUIRED_MARKERS:
        if marker not in source:
            raise SystemExit(f"Required source marker missing: {marker}")
    if PATCH_MARKER in source:
        raise SystemExit("V2 fidelity marker already present; refusing duplicate application.")

    out = replace_once(
        source,
        "  <!-- TAM_JOIN_US_LUXURY_V1 -->",
        "  <!-- TAM_JOIN_US_LUXURY_V1 -->\n  <!-- TAM_JOIN_US_LUXURY_V2_FIDELITY -->",
        "v2 marker",
    )

    # Hero crest + scroll cue.
    hero_anchor = '''      </video>\n    </div>\n    <div class="lux-container lux-hero-grid">'''
    hero_new = f'''      </video>\n    </div>\n    <div class="lux-hero-crest" aria-hidden="true"><img src="{LOGO}" alt=""></div>\n    <div class="lux-container lux-hero-grid">'''
    out = replace_once(out, hero_anchor, hero_new, "hero crest anchor")
    out = replace_once(
        out,
        '''      </aside>\n    </div>\n  </section>\n\n  <section class="lux-apply-stage"''',
        '''      </aside>\n    </div>\n    <div class="lux-hero-scroll" aria-hidden="true">SCROLL TO DISCOVER</div>\n  </section>\n\n  <section class="lux-apply-stage"''',
        "hero scroll anchor",
    )

    # Side storytelling around the application shell.
    out = replace_once(
        out,
        '''  <section class="lux-apply-stage" id="apply-now" aria-labelledby="apply-title">\n    <div class="lux-apply-shell lux-reveal">''',
        '''  <section class="lux-apply-stage" id="apply-now" aria-labelledby="apply-title">\n    <aside class="lux-apply-side lux-apply-side-right" aria-hidden="true"><b>رحلة مهنية لها معنى</b>نبحث عن أشخاص يحبون التعلّم، ويتقنون العمل الجماعي، ويرون في كل مشروع فرصة لصناعة أثر.</aside>\n    <aside class="lux-apply-side lux-apply-side-left" aria-hidden="true"><b>ابدأ من هنا</b>خطوات واضحة، مراجعة منظمة، وتواصل مباشر مع فريق الموارد البشرية.</aside>\n    <div class="lux-apply-shell lux-reveal">''',
        "apply side notes",
    )

    # Let the parent page own the visible height; the existing resize postMessage remains intact.
    out = replace_once(out, '                scrolling="yes"', '                scrolling="no"', "iframe scrolling")
    out = replace_once(
        out,
        "        document.getElementById('careersFrame').style.height = e.data.height + 'px';",
        "        var frame = document.getElementById('careersFrame'); var postedHeight = parseInt(e.data.height, 10); if (frame && Number.isFinite(postedHeight)) { frame.style.height = Math.max(1190, postedHeight + 365) + 'px'; }",
        "iframe resize behavior",
    )

    # Replace abstract culture placeholder with current real team portraits already published on the site.
    culture_old = '''      <div class="lux-culture-visual lux-reveal" role="img" aria-label="بيئة عمل تميز الرواد"></div>'''
    culture_new = f'''      <div class="lux-culture-visual lux-reveal" role="group" aria-label="نماذج من فريق تميز الرواد">\n        <div class="lux-culture-person"><img src="{TEAM_ESRAA}" alt="إسراء من فريق تميز الرواد" loading="lazy" decoding="async"></div>\n        <div class="lux-culture-person"><img src="{TEAM_CAROLINE}" alt="Caroline من فريق تميز الرواد" loading="lazy" decoding="async"></div>\n        <div class="lux-culture-person"><img src="{TEAM_RANA}" alt="Rana من فريق تميز الرواد" loading="lazy" decoding="async"></div>\n      </div>'''
    out = replace_once(out, culture_old, culture_new, "culture visual")

    # Expand areas to six authentic capability tracks; do not claim these are currently-open vacancies.
    areas_old = '''      <div class="lux-areas-grid">\n        <article class="lux-area-card lux-reveal"><div class="lux-area-icon">◈</div><h3>التسويق الرقمي</h3><p>استراتيجية، أداء، حملات ونمو.</p><span class="lux-area-arrow">←</span></article>\n        <article class="lux-area-card lux-reveal lux-delay-1"><div class="lux-area-icon">⌁</div><h3>تطوير وتصميم المواقع</h3><p>تجارب رقمية سريعة وفعالة.</p><span class="lux-area-arrow">←</span></article>\n        <article class="lux-area-card lux-reveal lux-delay-2"><div class="lux-area-icon">▦</div><h3>تصميم الجرافيك والمحتوى</h3><p>هوية، محتوى بصري وموشن.</p><span class="lux-area-arrow">←</span></article>\n        <article class="lux-area-card lux-reveal lux-delay-3"><div class="lux-area-icon">◎</div><h3>إدارة المشاريع والحسابات</h3><p>تنظيم، متابعة وتجربة عميل.</p><span class="lux-area-arrow">←</span></article>\n      </div>'''
    areas_new = '''      <div class="lux-areas-grid">\n        <article class="lux-area-card lux-reveal"><div class="lux-area-icon">◈</div><h3>التسويق الرقمي والأداء</h3><p>استراتيجية، حملات، تحليل ونمو.</p><span class="lux-area-arrow">←</span></article>\n        <article class="lux-area-card lux-reveal lux-delay-1"><div class="lux-area-icon">⌁</div><h3>تطوير وتجربة المواقع</h3><p>Web، E-commerce وUX/UI.</p><span class="lux-area-arrow">←</span></article>\n        <article class="lux-area-card lux-reveal lux-delay-2"><div class="lux-area-icon">▦</div><h3>التصميم والمحتوى البصري</h3><p>Branding، Graphic وMotion.</p><span class="lux-area-arrow">←</span></article>\n        <article class="lux-area-card lux-reveal"><div class="lux-area-icon">◎</div><h3>السوشيال ميديا</h3><p>Content، Community وSMM.</p><span class="lux-area-arrow">←</span></article>\n        <article class="lux-area-card lux-reveal lux-delay-1"><div class="lux-area-icon">↗</div><h3>SEO والنمو العضوي</h3><p>بحث، محتوى وتحسين الظهور.</p><span class="lux-area-arrow">←</span></article>\n        <article class="lux-area-card lux-reveal lux-delay-2"><div class="lux-area-icon">✦</div><h3>إدارة المشاريع والحسابات</h3><p>تنظيم، متابعة وتجربة عميل.</p><span class="lux-area-arrow">←</span></article>\n      </div>\n      <div class="lux-area-action lux-reveal"><a class="lux-btn lux-btn-ghost lux-focus" href="#apply-now">استكشف مسارك وقدّم طلبك <span aria-hidden="true">←</span></a></div>'''
    out = replace_once(out, areas_old, areas_new, "areas grid")

    # Add authentic team band before the recruitment journey; no fabricated testimonials.
    journey_anchor = '  <section class="lux-section" aria-labelledby="journey-title">'
    out = replace_once(out, journey_anchor, TEAM_SECTION + journey_anchor, "team band")

    # Add lightweight skyline artwork to final CTA.
    cta_anchor = '''      <div class="lux-cta-card lux-reveal">\n        <div>'''
    cta_new = '''      <div class="lux-cta-card lux-reveal">\n        <div class="lux-cityline" aria-hidden="true"><svg viewBox="0 0 1200 140" preserveAspectRatio="none"><g fill="currentColor" opacity=".42"><rect x="20" y="92" width="48" height="48"/><rect x="78" y="72" width="38" height="68"/><rect x="126" y="104" width="70" height="36"/><rect x="214" y="82" width="56" height="58"/><rect x="285" y="55" width="42" height="85"/><rect x="342" y="94" width="72" height="46"/><rect x="430" y="64" width="36" height="76"/><rect x="479" y="88" width="86" height="52"/><rect x="580" y="42" width="40" height="98"/><rect x="634" y="76" width="65" height="64"/><rect x="718" y="58" width="44" height="82"/><rect x="778" y="96" width="76" height="44"/><rect x="868" y="68" width="34" height="72"/><rect x="918" y="86" width="70" height="54"/><rect x="1004" y="52" width="46" height="88"/><rect x="1065" y="78" width="54" height="62"/><rect x="1132" y="101" width="50" height="39"/></g><path d="M0 139H1200" stroke="currentColor" stroke-width="2" opacity=".7"/></svg></div>\n        <div>'''
    out = replace_once(out, cta_anchor, cta_new, "cta skyline")

    # Append the V2 override layer just before </head> so V1 remains recoverable and diffs stay surgical.
    if "</head>" not in out:
        raise SystemExit("Missing </head> anchor")
    out = out.rsplit("</head>", 1)[0] + V2_CSS + "\n</head>" + out.rsplit("</head>", 1)[1]

    # Post-transform invariants.
    invariants = {
        "v2_marker_once": out.count(PATCH_MARKER) == 2,  # HTML marker + CSS comment
        "v1_preserved": "TAM_JOIN_US_LUXURY_V1" in out,
        "force_preserved": "TAM_JOIN_US_WORDPRESS_FORCE_V1" in out,
        "careers_preserved": "https://careers.tamiyouzplaform.com/" in out,
        "rakan_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in out,
        "notify_preserved": "fetch('/join-us/notify.php'" in out,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in out,
        "iframe_present_once": out.count('id="careersFrame"') == 1,
        "team_band_present": 'id="team-title"' in out,
        "team_images_present": TEAM_ESRAA in out and TEAM_CAROLINE in out and TEAM_RANA in out,
        "culture_placeholder_removed": 'role="img" aria-label="بيئة عمل تميز الرواد"></div>' not in out,
        "scrollbar_removed": 'scrolling="yes"' not in out,
        "reduced_motion_preserved": "prefers-reduced-motion:reduce" in out,
        "collection_schema_preserved": '"@type":"CollectionPage"' in out,
        "jobposting_absent": '"@type": "JobPosting"' not in out and '"@type":"JobPosting"' not in out,
    }
    failed = [k for k, v in invariants.items() if not v]
    if failed:
        raise SystemExit("Post-transform guard failed: " + ", ".join(failed))
    return out, invariants


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest")
    args = ap.parse_args()

    source_path = Path(args.source)
    output_path = Path(args.output)
    source = source_path.read_text(encoding="utf-8")
    result, invariants = transform(source)
    output_path.write_text(result, encoding="utf-8")

    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "output_sha256": hashlib.sha256(result.encode()).hexdigest(),
        "files_changed": ["themes/thegem-elementor/page-join-us.php"],
        "design_focus": [
            "cinematic hero fidelity",
            "premium application shell and crop",
            "real team portrait culture visual",
            "six-track talent grid",
            "authentic team band without fabricated testimonials",
            "cinematic skyline CTA",
            "spacing and hierarchy tightening",
        ],
        "integrations_preserved": True,
        "seo_schema_preserved": True,
        "git_mutations_by_patch_runner": False,
        "invariants": invariants,
    }
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
