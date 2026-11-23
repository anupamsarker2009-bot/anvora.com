"""Build Anvora sub-pages from the rebranded homepage shell.
Usage: python -I pages.py <site dir>
Run after rebrand.py. Rewrites links in index.html and writes <route>/index.html pages.
"""
import re, sys, os, html

SITE = sys.argv[1]
home = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
E = lambda t: html.escape(t, quote=True)

# ------------------------------------------------------------------ link rewiring
ROUTES = {
    "/product/vault": "/services/brand-strategy",
    "/product/page-transition-course": "/services/performance-marketing",
    "/product/button-pack": "/services/social-media",
    "/product/icons": "/services/content-studio",
    "/product/community": "/services/seo-growth",
    "/showcase": "/approach",
    "/collection": "/example-plans",
    "/plans": "/pricing",
    "/plans/subscription?type=annual": "/contact?plan=starter",
    "/plans/team-subscription?type=annual": "/contact?plan=growth",
    "/login": "/contact",
    "/try": "/audit",
    "/updates": "/insights",
}
LABEL_ROUTES = {"Let's talk": "/contact", "Work with Anvora": "/contact", "Support": "/contact",
                "Client Login": "/contact", "Contact": "/contact"}

def rewire(s):
    def fix_a(m):
        tag, inner = m.group(1), m.group(2)
        if "sitemap__url" in tag:
            return m.group(0)
        label = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", inner)).split())
        hm = re.search(r'href="([^"]*)"', tag)
        href = hm.group(1) if hm else None
        new = None
        for k, v in LABEL_ROUTES.items():
            if label.startswith(k):
                new = v
        if new is None and href in ROUTES:
            new = ROUTES[href]
        if new is None and href and href.startswith("http"):
            new = "#"  # third-party sites from the original showcase/credits
        if new is not None and href is not None:
            tag = tag.replace(f'href="{href}"', f'href="{new}"', 1)
            tag = tag.replace(' data-barba-prevent=""', "").replace(' data-o-support="1"', "")
            tag = tag.replace(' target="_blank"', "")
        return f"<a{tag}>{inner}</a>"
    s = re.sub(r"<a\b([^>]*)>(.*?)</a>", fix_a, s, flags=re.S)
    # the "Web & Landing Pages" nav item was a disabled placeholder: make it a link
    s = re.sub(r'<li class="nav-bar__small-li is--inactive"><div data-disabled="" data-hover="" class="nav-bar__small-a is--inactive">(.*?</div></div>)</div></li>',
               r'<li class="nav-bar__small-li"><a data-hover="" href="/services/web-landing-pages" class="nav-bar__small-a w-inline-block">\1</a></li>',
               s, flags=re.S)
    # slack invite cover link from the original
    s = re.sub(r'<a href="#" class="cover-link w-inline-block"></a>', "", s)
    return s

home = rewire(home)

# showreel: Anvora's own video (audio track removed) for the preview loop and the full-screen player
REEL = "/videos/anvora-reel.mp4"
home = re.sub(r'data-video-src="[^"]*Osmo-V12-Reel[^"]*"', f'data-video-src="{REEL}"', home)
home = re.sub(r'data-player-src="https://vz-[^"]*playlist\.m3u8"', f'data-player-src="{REEL}" data-player-muted="true"', home)
home = home.replace(">00:48<", ">00:33<")
_js = os.path.join(SITE, "js", "55554.js")
_src = open(_js, encoding="utf-8").read()
_old = "T=!(!window.Hls||!Hls.isSupported()||q)"
if _old in _src:  # let the player play plain MP4 files instead of forcing HLS streaming
    open(_js, "w", encoding="utf-8", newline="").write(_src.replace(_old, "T=!(!window.Hls||!Hls.isSupported()||q||/\\.mp4(\\?|$)/i.test(c))", 1))

# Osmo's live resource counter -> static Anvora values
home = home.replace('<span data-vault-total="" class="nav-bar__big-span-number">000', '<span class="nav-bar__big-span-number">6')
home = home.replace('<div data-vault-total="" class="pricing-benefit__tag p-r">000', '<div class="pricing-benefit__tag p-r">✓')

home = home.replace('<li class="footer-link__col-li is--soon"><p class="p-m">Web &amp; Landing Pages</p>',
                    '<li class="footer-link__col-li"><a data-underline-link="" href="/services/web-landing-pages" class="p-m">Web &amp; Landing Pages</a>')

# footer column headings
home = home.replace('_col-top"><h4 class="h-xs">SEO &amp; Growth</h4>', '_col-top"><h4 class="h-xs">Company</h4>')
home = home.replace('_col-top"><h4 class="h-xs">Retainer</h4>', '_col-top"><h4 class="h-xs">Resources</h4>')

# free-audit banner: replace the Osmo dashboard screenshots with an Anvora audit-report mockup
def audit_mock(cls, theme):
    bars = [("Website & UX", 81), ("Paid ads", 58), ("SEO", 64), ("Social", 77), ("Email", 46)]
    rows = "".join(f'<div class="anv-am__bar"><span>{n}</span><i><b style="width:{v}%"></b></i><em>{v}</em></div>' for n, v in bars)
    ops = ["Fix conversion tracking on checkout", "Add 3 high-intent search campaigns", "Refresh ad creatives every 4 weeks", "Launch a welcome email flow"]
    li = "".join(f"<li><span>{i+1:02d}</span>{o}</li>" for i, o in enumerate(ops))
    return (f'<div class="{cls} anv-am anv-am--{theme}"><div class="anv-am__top"><strong>anvora</strong><span>Marketing audit · Sample report</span></div>'
            '<div class="anv-am__grid"><div class="anv-am__score"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="50" pathLength="100" class="t"/>'
            '<circle cx="60" cy="60" r="50" pathLength="100" class="v" stroke-dasharray="65 100"/></svg><div><b>65</b><span>/100</span></div>'
            f'<p>Overall marketing score</p></div><div class="anv-am__bars">{rows}</div>'
            f'<div class="anv-am__ops"><p>Top opportunities</p><ol>{li}</ol></div></div></div>')

home = re.sub(r'<img src="images/demo-vault-dark[^"]*"[^>]*class="(cover-image is--try-vault)">', lambda m: audit_mock(m.group(1), "dark"), home)
home = re.sub(r'<img src="images/demo-vault-light[^"]*"[^>]*class="(cover-image is--try-vault-light)">', lambda m: audit_mock(m.group(1), "light"), home)

# ------------------------------------------------------------------ shell pieces
def sec_start(cls):
    i = home.index(f'class="{cls}"')
    return home.rfind("<section", 0, i)

order = ["home-hero", "reel", "intro", "db", "product-slider", "info", "testimonial", "pricing-home", "made", "try-vault"]
starts = [sec_start(c) for c in order]
footer_start = home.rfind("<footer", 0, home.index('class="footer"'))
bounds = starts + [footer_start]
SECTION = {c: home[bounds[i]:bounds[i + 1]] for i, c in enumerate(order)}
PREFIX = home[:starts[0]]
SUFFIX = home[footer_start:]

PAGE_CSS = """<style id="anv-pages">
img[src*="osmo-micrographic"],img[src*="cutout-new"],img[src*="/pf-"],.about-gallery{visibility:hidden!important}
.join-faces__image-row{display:none!important}
.anv-am{position:absolute;inset:0;width:100%;height:100%;padding:1.6em;display:flex;flex-direction:column;gap:1.2em;font-family:Haffer VF,Arial,sans-serif;overflow:hidden;border-radius:inherit}
.anv-am--dark{background:#1b1919;color:var(--color-light)}
.anv-am--light{background:var(--color-white);color:var(--color-dark)}
.anv-am__top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(128,128,128,.25);padding-bottom:1em}
.anv-am__top strong{font-size:1.4em;font-variation-settings:"wght" 700;letter-spacing:-.03em}
.anv-am__top span{font-family:Haffer Mono,Arial,sans-serif;font-size:.7em;text-transform:uppercase;opacity:.6}
.anv-am__grid{display:grid;grid-template-columns:.8fr 1.2fr;grid-template-rows:auto 1fr;gap:1em;flex:1}
.anv-am__score{position:relative;border-radius:.6em;background:var(--color-purple);color:#fff;padding:1em;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.6em}
.anv-am__score svg{width:7.5em;transform:rotate(-90deg)}
.anv-am__score circle{fill:none;stroke-width:10}.anv-am__score .t{stroke:rgba(255,255,255,.2)}.anv-am__score .v{stroke:var(--color-electric);stroke-linecap:round}
.anv-am__score>div{position:absolute;top:calc(50% - 1.6em);text-align:center}
.anv-am__score>div b{font-size:2.4em;letter-spacing:-.04em;font-weight:400}.anv-am__score>div span{opacity:.7}
.anv-am__score p{font-size:.8em;opacity:.85}
.anv-am__bars{display:flex;flex-direction:column;justify-content:center;gap:.8em;border-radius:.6em;padding:1em 1.2em;background:rgba(128,128,128,.1)}
.anv-am__bar{display:grid;grid-template-columns:6.5em 1fr 1.8em;align-items:center;gap:.8em;font-size:.8em}
.anv-am__bar i{height:.5em;border-radius:1em;background:rgba(128,128,128,.25);overflow:hidden}
.anv-am__bar b{display:block;height:100%;border-radius:1em;background:var(--color-electric)}
.anv-am--light .anv-am__bar b{background:var(--color-purple)}
.anv-am__bar em{font-style:normal;text-align:right;opacity:.7}
.anv-am__ops{grid-column:1/-1;border-radius:.6em;padding:1em 1.2em;background:rgba(128,128,128,.1)}
.anv-am__ops p{font-family:Haffer Mono,Arial,sans-serif;font-size:.7em;text-transform:uppercase;opacity:.6;margin-bottom:.8em}
.anv-am__ops ol{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:1fr 1fr;gap:.6em 1.2em;font-size:.85em}
.anv-am__ops li{display:flex;gap:.6em}.anv-am__ops li span{color:var(--color-purple);font-family:Haffer Mono,Arial,sans-serif}
.anv-am--dark .anv-am__ops li span{color:var(--color-electric)}
.anv-wrap{width:100%;max-width:92em;margin:0 auto;padding:0 var(--container-padding)}
.anv-sec{padding:var(--padding-s) 0;position:relative}
.anv-sec.is--dark{background:var(--color-neutral-800);color:var(--color-light)}
.anv-hero{padding:12.5em 0 var(--padding-s);text-align:center}
.anv-hero .h-xl{margin:.35em auto .3em;max-width:11em}
.anv-hero .p-l{max-width:34em;margin:0 auto;opacity:.75}
.anv-hero .button-row{justify-content:center;margin-top:var(--gap-xxl)}
.anv-row{display:flex;flex-wrap:wrap;gap:var(--gap-xs);align-items:center}
.anv-split{display:grid;grid-template-columns:1fr 1fr;gap:var(--gap-xxl);align-items:start}
.anv-split .p-l+.p-l{margin-top:1em}
.anv-muted{opacity:.6}
.anv-head{margin-bottom:var(--gap-xxl)}
.anv-head .eyebrow{margin-bottom:1.25em;opacity:.6}
.anv-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--gap-s)}
.anv-grid.is--2{grid-template-columns:repeat(2,1fr)}
.anv-card{background:var(--color-white);border-radius:.75em;padding:var(--gap-l);display:flex;flex-direction:column;gap:1em;min-height:15em}
.is--dark .anv-card{background:var(--color-neutral-700)}
.anv-card .eyebrow{opacity:.5}
.anv-card .p-m{opacity:.75;margin-top:auto}
.anv-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--gap-s);counter-reset:s}
.anv-step{border-top:1px solid currentColor;padding-top:var(--gap-m);display:flex;flex-direction:column;gap:.75em}
.anv-step .h-l{color:var(--color-electric)}
.anv-step .p-m{opacity:.7}
.anv-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--gap-s)}
.anv-stat{border-radius:.75em;padding:var(--gap-l);background:var(--color-purple);color:var(--color-white);display:flex;flex-direction:column;justify-content:space-between;min-height:14em}
.anv-stat:nth-child(2){background:var(--color-electric);color:var(--color-dark)}
.anv-stat:nth-child(3){background:var(--color-dark);color:var(--color-light)}
.anv-faq{border-top:1px solid var(--color-neutral-450)}
.anv-faq details{border-bottom:1px solid var(--color-neutral-450);padding:1.4em 0}
.anv-faq summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:1em;align-items:center}
.anv-faq summary::-webkit-details-marker{display:none}
.anv-faq summary:after{content:"+";font-size:1.6em;line-height:1;transition:transform .3s}
.anv-faq details[open] summary:after{transform:rotate(45deg)}
.anv-faq details .p-m{margin-top:1em;max-width:46em;opacity:.75}
.anv-faq-group+.anv-faq-group{margin-top:var(--padding-xs)}
.anv-case{display:grid;grid-template-columns:1fr 1.2fr;gap:var(--gap-s);background:var(--color-white);border-radius:1em;padding:var(--gap-s);scroll-margin-top:8em}
.anv-case+.anv-case{margin-top:var(--gap-s)}
.anv-case__visual{border-radius:.6em;min-height:22em;padding:var(--gap-l);display:flex;flex-direction:column;justify-content:space-between}
.anv-case__body{padding:var(--gap-m);display:flex;flex-direction:column;gap:1.25em}
.anv-case__body dl{display:grid;grid-template-columns:8em 1fr;gap:.9em 1.5em;margin:0}
.anv-case__body dt{font-family:Haffer Mono,Arial,sans-serif;font-size:.6875em;text-transform:uppercase;opacity:.5;padding-top:.35em}
.anv-case__body dd{margin:0}
.anv-tile{border-radius:.75em;padding:var(--gap-l);min-height:20em;display:flex;flex-direction:column;justify-content:space-between;color:inherit;text-decoration:none;transition:transform .4s cubic-bezier(.65,.05,0,1)}
.anv-tile:hover{transform:translateY(-.4em)}
.c-purple{background:var(--color-purple);color:var(--color-white)}
.c-electric{background:var(--color-electric);color:var(--color-dark)}
.c-coral{background:var(--color-coral);color:var(--color-white)}
.c-dark{background:var(--color-neutral-800);color:var(--color-light)}
.c-light{background:var(--color-neutral-300);color:var(--color-dark)}
.anv-table{width:100%;border-collapse:collapse;background:var(--color-white);border-radius:.75em;overflow:hidden}
.anv-table th,.anv-table td{padding:1.1em 1.4em;text-align:left;border-bottom:1px solid var(--color-neutral-300);font-size:1em}
.anv-table th{font-family:Haffer Mono,Arial,sans-serif;font-size:.75em;text-transform:uppercase;font-weight:400}
.anv-table td:not(:first-child),.anv-table th:not(:first-child){text-align:center}
.anv-form{background:var(--color-white);border-radius:1em;padding:var(--gap-l);display:grid;gap:var(--gap-s)}
.anv-form .anv-2{display:grid;grid-template-columns:1fr 1fr;gap:var(--gap-s)}
.anv-form label{display:flex;flex-direction:column;gap:.5em}
.anv-form label>span{font-family:Haffer Mono,Arial,sans-serif;font-size:.6875em;text-transform:uppercase;opacity:.6}
.anv-form input,.anv-form select,.anv-form textarea{font:inherit;font-size:1em;border:1px solid var(--color-neutral-450);background:var(--color-neutral-200);border-radius:.4em;padding:.85em 1em;color:var(--color-dark);width:100%}
.anv-form textarea{min-height:9em;resize:vertical}
.anv-form input:focus,.anv-form select:focus,.anv-form textarea:focus{outline:2px solid var(--color-purple);outline-offset:1px}
.anv-chips{display:flex;flex-wrap:wrap;gap:.5em}
.anv-chips label{flex-direction:row;align-items:center;gap:.5em;border:1px solid var(--color-neutral-450);border-radius:2em;padding:.55em 1em;cursor:pointer}
.anv-chips input{width:auto}
.anv-chips label:has(input:checked){background:var(--color-dark);color:var(--color-light);border-color:var(--color-dark)}
.anv-form button[type=submit]{font:inherit;border:0;cursor:pointer;background:var(--color-purple);color:#fff;border-radius:.4em;padding:1em 1.5em;font-size:1em;justify-self:start}
.anv-form button[type=submit]:hover{background:var(--color-dark)}
.anv-form__done{display:none;padding:var(--gap-l);border-radius:.6em;background:var(--color-electric)}
.anv-form.is--sent>*{display:none}.anv-form.is--sent .anv-form__done{display:block}
.anv-contact{display:grid;grid-template-columns:1.4fr 1fr;gap:var(--gap-s);align-items:start}
.anv-info{display:grid;gap:var(--gap-s)}
.anv-info .anv-card{min-height:0}
.anv-info a{color:inherit}
.anv-prose{max-width:46em;margin:0 auto}
.anv-prose h2{font-size:1.5em;letter-spacing:-.02em;margin:2em 0 .6em;font-weight:500}
.anv-prose p,.anv-prose li{font-size:1.0625em;line-height:1.55;opacity:.85}
.anv-prose ul{padding-left:1.2em}
.anv-prose p+p{margin-top:.8em}
.anv-note{border-radius:.6em;background:var(--color-electric);padding:1em 1.25em;font-size:.95em}
.anv-article .h-s{margin:.6em 0}
.anv-featured{display:grid;grid-template-columns:1.3fr 1fr;gap:var(--gap-s);margin-bottom:var(--gap-s)}
.anv-featured .anv-tile{min-height:26em}
@media (max-width:991px){.anv-grid,.anv-steps{grid-template-columns:repeat(2,1fr)}}
@media (max-width:767px){
 .anv-hero{padding-top:9em}
 .anv-card{min-height:0}.anv-card .p-m{margin-top:.5em}.anv-tile,.anv-stat{min-height:14em}
 .anv-split,.anv-grid,.anv-grid.is--2,.anv-steps,.anv-stats,.anv-case,.anv-contact,.anv-featured,.anv-form .anv-2{grid-template-columns:1fr}
 .anv-case__body dl{grid-template-columns:1fr}
 .anv-table th,.anv-table td{padding:.8em .6em;font-size:.85em}
}
</style>"""

FORM_JS = """<script id="anv-forms">
(function(){if(window.__anvForms)return;window.__anvForms=1;
document.addEventListener('submit',function(e){var f=e.target.closest&&e.target.closest('form.anv-form');if(!f)return;e.preventDefault();
if(!f.checkValidity()){f.reportValidity();return}
/* TODO: send the form data to your form service / CRM here */
f.classList.add('is--sent');},true);
function prefill(){var p=new URLSearchParams(location.search).get('plan');var s=document.querySelector('form.anv-form select[name=plan]');if(p&&s){s.value=p}}
document.addEventListener('DOMContentLoaded',prefill);window.addEventListener('popstate',prefill);setInterval(prefill,1500);
})();
</script>"""

# ------------------------------------------------------------------ components
def btn(label, href, variant="neutral-200"):
    l = E(label)
    return (f'<a data-button-rotate-hover="" class="button w-inline-block" data-size="" data-theme="" href="{href}" data-barba-p="" '
            f'data-button-rotate="" data-responsive="" data-shape=""><div data-wf--button-theme--variant="{variant}" class="button-bg"></div>'
            f'<div class="button-label__wrap"><div class="button-label"><span>{l}</span></div>'
            f'<div aria-hidden="true" class="button-label"><span>{l}</span></div></div></a>')

def tags(a, b):
    return ('<div class="tag-row"><div class="tag-row__line"></div><div class="button-row">'
            f'<div data-shape="" data-theme="" class="tag"><div data-wf--button-theme--variant="dark-10" class="button-bg"></div><span class="eyebrow is--relative">{E(a)}</span></div>'
            f'<div data-shape="round" data-theme="" class="tag"><div data-wf--button-theme--variant="dark-10" class="button-bg"></div><span class="eyebrow is--relative">{E(b)}</span></div>'
            '</div><div class="tag-row__line"></div></div>')

def hero(t1, t2, title, intro, buttons=()):
    b = f'<div class="button-row">{"".join(buttons)}</div>' if buttons else ""
    return (f'<section data-theme-section="light" class="anv-hero"><div class="anv-wrap">{tags(t1, t2)}'
            f'<h1 class="h-xl">{E(title)}</h1><p class="p-l">{E(intro)}</p>{b}</div></section>')

def head(eyebrow, title, sub=None):
    s = f'<p class="p-l anv-muted" style="max-width:34em;margin-top:1em">{E(sub)}</p>' if sub else ""
    return f'<div class="anv-head"><span class="eyebrow">{E(eyebrow)}</span><h2 class="h-l">{E(title)}</h2>{s}</div>'

def section(inner, dark=False):
    return (f'<section data-theme-section="{"dark" if dark else "light"}" class="anv-sec{" is--dark" if dark else ""}">'
            f'<div class="anv-wrap">{inner}</div></section>')

def split(eyebrow, title, paras):
    p = "".join(f'<p class="p-l">{E(x)}</p>' for x in paras)
    return section(f'<div class="anv-split"><div><span class="eyebrow anv-muted">{E(eyebrow)}</span>'
                   f'<h2 class="h-l" style="margin-top:.4em">{E(title)}</h2></div><div>{p}</div></div>')

def cards(items, cols=3):
    c = "".join(f'<div class="anv-card"><span class="eyebrow">{i+1:02d}</span><h3 class="h-s">{E(t)}</h3><p class="p-m">{E(d)}</p></div>'
                for i, (t, d) in enumerate(items))
    return f'<div class="anv-grid{" is--2" if cols == 2 else ""}">{c}</div>'

def steps(items):
    return '<div class="anv-steps">' + "".join(
        f'<div class="anv-step"><span class="h-l">{i+1:02d}</span><h3 class="h-s">{E(t)}</h3><p class="p-m">{E(d)}</p></div>'
        for i, (t, d) in enumerate(items)) + "</div>"

def stats(items):
    return '<div class="anv-stats">' + "".join(
        f'<div class="anv-stat"><span class="eyebrow">{E(l)}</span><div><div class="h-xl">{E(n)}</div><p class="p-m">{E(d)}</p></div></div>'
        for n, l, d in items) + "</div>"

def faq(items, title=None):
    t = f'<h3 class="h-s" style="margin-bottom:.8em">{E(title)}</h3>' if title else ""
    return (f'<div class="anv-faq-group">{t}<div class="anv-faq">' + "".join(
        f'<details><summary class="h-xs">{E(q)}</summary><p class="p-m">{E(a)}</p></details>' for q, a in items) + "</div></div>")

def page(slug, title, desc, body, cta=True):
    s = PREFIX + body + (SECTION["try-vault"] if cta else "") + SUFFIX
    s = s.replace('data-barba-namespace="home"', f'data-barba-namespace="{slug}"', 1)
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)} | Anvora</title>", s, count=1, flags=re.S)
    s = re.sub(r'(<meta content=")[^"]*(" (?:name|property)="(?:og:|twitter:)?title")', lambda m: m.group(1) + E(title) + " | Anvora" + m.group(2), s)
    s = re.sub(r'(<meta content=")[^"]*(" (?:name|property)="(?:og:|twitter:)?description")', lambda m: m.group(1) + E(desc) + m.group(2), s)
    s = s.replace('aria-current="page" ', "").replace(" w--current", "")
    return finish(s)

def finish(s):
    if 'id="anv-pages"' not in s:
        stub = ('<script id="anv-stub">window.Outseta=window.Outseta||{on:function(){},getUser:function(){return Promise.resolve(null)},'
                'getJwtPayload:function(){return null}};</script>')
        s = s.replace("<head>", "<head>" + stub, 1)
        s = s.replace("</head>", PAGE_CSS + "</head>", 1)
    if 'id="anv-forms"' not in s:
        s = s.replace("</body>", FORM_JS + "</body>", 1)
    # root-absolute asset paths so pages work from sub-folders
    s = re.sub(r'(?<=[\s"\'(,])(css|js|images|fonts)/', r"/\1/", s)
    return s

def write(route, content):
    d = os.path.join(SITE, *route.strip("/").split("/"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n").write(content)
    print("wrote", route)

CALL = lambda: btn("Book a strategy call", "/contact", "electric")
PRICE = lambda: btn("See pricing", "/pricing", "neutral-200")

# ------------------------------------------------------------------ services
SERVICES = [
 dict(slug="brand-strategy", n="01", name="Brand Strategy",
  intro="Positioning, messaging and visual identity that make your brand impossible to ignore, and easy to choose.",
  why=("Clarity before campaigns", ["Great marketing starts with knowing exactly who you are, who you serve and why you are the better choice. Without that, every ad and every post works harder than it should.",
        "We dig into your market, your customers and your competitors, then turn what we learn into a brand that is sharp, consistent and built to grow."]),
  inc=[("Brand audit & research", "Customer interviews, competitor mapping and a clear picture of where your brand stands today."),
       ("Positioning & value proposition", "The space you own in your market, and the one sentence that explains why you win."),
       ("Messaging framework", "Key messages, proof points and a tone of voice your whole team can use."),
       ("Visual identity", "Logo, colour, typography and imagery direction that feels unmistakably you."),
       ("Brand guidelines", "A practical brand book so every touchpoint stays consistent."),
       ("Launch & rollout plan", "A step-by-step plan for bringing the new brand to market with impact.")],
  steps=[("Discover", "Workshops, research and audits to understand your business and audience."),
         ("Define", "Positioning, personality and messaging, agreed with your team."),
         ("Design", "Visual identity and key brand assets, refined through feedback rounds."),
         ("Deploy", "Guidelines, templates and a rollout plan so the brand lives everywhere.")],
  stats=[("4", "Phases", "A clear process from research to rollout."),
         ("3–6", "Weeks", "Typical timeline for a full brand strategy project."),
         ("1", "Brand book", "Everything your team needs, in one place.")],
  faq=[("Do you only work on new brands?", "No. We help new businesses build a brand from scratch and established companies refresh or reposition an existing one."),
       ("Is a logo included?", "Yes, visual identity work including logo design is part of the full brand strategy package. You can also book strategy only."),
       ("Who needs to be involved from our side?", "Usually a founder or marketing lead plus one or two key stakeholders for the workshops and feedback rounds.")]),
 dict(slug="performance-marketing", n="02", name="Performance Marketing",
  intro="Paid search and social campaigns engineered for ROI, tracked down to the last click.",
  why=("Every euro accountable", ["Ad platforms make it easy to spend money and hard to make it back. We build campaigns around your real business goals, not vanity metrics.",
        "From tracking setup to creative testing and budget allocation, we optimise every week so your spend keeps working harder."]),
  inc=[("Paid search", "Google and Microsoft Ads campaigns that capture people ready to buy."),
       ("Paid social", "Meta, LinkedIn and TikTok campaigns that reach the right audience at the right moment."),
       ("Creative testing", "Structured ad testing to find the messages and visuals that convert."),
       ("Conversion tracking", "Clean analytics and pixel setup so every result is measured correctly."),
       ("Budget optimisation", "Spend shifted weekly toward the channels and campaigns that perform."),
       ("Transparent reporting", "Clear dashboards and monthly reviews focused on revenue, leads and ROAS.")],
  steps=[("Audit", "We review your accounts, tracking and past results to find quick wins."),
         ("Plan", "Channel mix, audiences, budgets and KPIs agreed upfront."),
         ("Launch", "Campaigns built, creative produced and tracking verified."),
         ("Optimise", "Weekly testing and budget shifts, with monthly strategy reviews.")],
  stats=[("Weekly", "Optimisation", "Campaigns reviewed and improved every single week."),
         ("Monthly", "Reporting", "A clear report and a call to plan the next month."),
         ("100%", "Transparency", "Your ad accounts, your data, always visible to you.")],
  faq=[("Is ad spend included in your fee?", "No. Ad spend is paid directly to the platforms from your own accounts, so you keep full ownership and visibility."),
       ("What is the minimum ad budget?", "We recommend at least €1,500 per month in ad spend so campaigns can gather enough data to optimise."),
       ("How soon will we see results?", "Search campaigns often show results within weeks. Paid social usually needs 4 to 8 weeks of testing to reach its full potential.")]),
 dict(slug="social-media", n="03", name="Social Media",
  intro="Always-on social content and community management that keeps your audience engaged.",
  why=("Show up, consistently", ["Social media rewards brands that show up with something worth watching, every week. That takes strategy, creativity and a lot of consistency.",
        "We plan, create, publish and manage your channels so your brand stays visible and your community keeps growing."]),
  inc=[("Social strategy", "Channel choice, content pillars and goals tailored to your audience."),
       ("Content calendar", "A monthly plan of posts, stories and reels, approved before anything goes live."),
       ("Content creation", "Graphics, short-form video and captions made for each platform."),
       ("Community management", "Replies, comments and DMs handled in your brand's voice."),
       ("Influencer partnerships", "Finding, briefing and managing creators who fit your brand."),
       ("Analytics & insights", "Monthly reporting on reach, engagement and what to do next.")],
  steps=[("Strategy", "We define goals, audience, pillars and the channels that matter."),
         ("Create", "Our team produces a month of content ahead of time."),
         ("Publish", "Scheduled posting at the best times for each platform."),
         ("Engage & learn", "Community management plus monthly insights to sharpen the plan.")],
  stats=[("12–30", "Posts / month", "Depending on your package and channels."),
         ("3", "Platforms", "Typically managed per brand, such as Instagram, LinkedIn and TikTok."),
         ("Daily", "Community care", "Comments and messages answered every working day.")],
  faq=[("Which platforms do you manage?", "Instagram, TikTok, LinkedIn, Facebook, Pinterest and YouTube Shorts. We recommend focusing on the two or three that matter most for you."),
       ("Do we approve content before it goes live?", "Always. You receive the content calendar in advance and can request changes before anything is published."),
       ("Can you work with our in-house team?", "Yes. We can run everything, or support your team with strategy, content production or community management.")]),
 dict(slug="content-studio", n="04", name="Content Studio",
  intro="Photo, video and copywriting produced in-house, on brand and on schedule.",
  why=("Content that does a job", ["Every piece of content should earn its place: build trust, explain your product or drive action. Pretty is not enough.",
        "Our in-house studio plans and produces content around your goals, so you always have the right assets for every channel."]),
  inc=[("Copywriting", "Website copy, ads, emails and articles written to persuade."),
       ("Photography", "Product, lifestyle and team shoots that look like your brand."),
       ("Video production", "Brand films, short-form social video and ad creatives."),
       ("Motion & animation", "Animated graphics and explainers that make ideas easy to grasp."),
       ("Blog & long-form", "SEO-friendly articles, guides and case studies."),
       ("Email content", "Newsletters and automated flows that keep customers coming back.")],
  steps=[("Brief", "We agree goals, formats, channels and deadlines."),
         ("Concept", "Ideas, scripts and shot lists, approved before production."),
         ("Produce", "Shoots, writing and editing by our in-house team."),
         ("Deliver", "Final assets, sized and ready for every channel.")],
  stats=[("In-house", "Studio", "Writers, photographers, editors and designers under one roof."),
         ("48h", "Feedback rounds", "Typical turnaround for revisions on drafts."),
         ("All", "Formats", "Every asset delivered in the sizes each channel needs.")],
  faq=[("Do you shoot on location?", "Yes. We shoot in our studio or on location at your business, events or anywhere your story happens."),
       ("Who owns the content you create?", "Once the project is paid, you own the final assets and can use them across all of your channels."),
       ("Can we order content on a project basis?", "Yes. Content can be part of a monthly retainer or booked as a one-off project.")]),
 dict(slug="seo-growth", n="05", name="SEO & Growth",
  intro="Technical SEO, content and analytics that compound your organic growth month after month.",
  why=("Growth that compounds", ["Paid ads stop the moment you stop paying. Organic search keeps bringing in customers long after the work is done.",
        "We fix what holds your site back, create content people are searching for and build the authority that moves you up the rankings."]),
  inc=[("Technical SEO", "Site speed, indexing, structure and fixes that search engines love."),
       ("Keyword strategy", "The searches your customers actually make, prioritised by value."),
       ("On-page optimisation", "Titles, content and internal links tuned for every key page."),
       ("Content strategy", "A plan of articles and landing pages that capture demand."),
       ("Link building", "Earning quality mentions and links that build authority."),
       ("Analytics & CRO", "Tracking, dashboards and tests that turn traffic into customers.")],
  steps=[("Audit", "A full technical, content and competitor review of your site."),
         ("Roadmap", "A prioritised plan of fixes and opportunities."),
         ("Execute", "Monthly technical work, content and outreach."),
         ("Measure", "Rankings, traffic and conversions reported every month.")],
  stats=[("3–6", "Months", "Typical time before SEO results become clearly visible."),
         ("Monthly", "Reporting", "Rankings, traffic and leads in one clear report."),
         ("Long-term", "Value", "Organic traffic keeps working without paying per click.")],
  faq=[("How long does SEO take?", "Most sites see meaningful movement within three to six months, with results compounding from there."),
       ("Do you guarantee rankings?", "No honest agency can guarantee rankings. We commit to a clear plan, consistent work and transparent reporting."),
       ("Do you write the content too?", "Yes. Our content studio writes the articles and landing pages in your SEO plan.")]),
 dict(slug="web-landing-pages", n="06", name="Web & Landing Pages",
  intro="Fast, conversion-focused websites and landing pages that turn clicks into customers.",
  why=("Your best salesperson", ["Your website works around the clock. It should load fast, look great and guide every visitor toward taking action.",
        "We design and build websites and landing pages around your customers and your campaigns, then keep testing to improve them."]),
  inc=[("UX & wireframes", "Clear page structures built around what your visitors need."),
       ("Web design", "Distinctive design that matches your brand and builds trust."),
       ("Development", "Fast, responsive sites on Webflow, WordPress or Shopify."),
       ("Landing pages", "Campaign pages built to convert paid and organic traffic."),
       ("A/B testing", "Experiments on headlines, layouts and offers to lift conversions."),
       ("Care & maintenance", "Updates, monitoring and improvements after launch.")],
  steps=[("Plan", "Goals, sitemap, content and technical requirements."),
         ("Design", "Wireframes, then full designs for desktop and mobile."),
         ("Build", "Development, content entry, tracking and quality checks."),
         ("Launch & improve", "Go live, then test and optimise based on real data.")],
  stats=[("4–10", "Weeks", "Typical timeline for a full website build."),
         ("Mobile", "First", "Designed for the devices your customers really use."),
         ("Built-in", "Tracking", "Analytics and conversion tracking set up from day one.")],
  faq=[("Which platforms do you build on?", "Mostly Webflow, WordPress and Shopify. We will recommend the best fit for your goals and team."),
       ("Can you redesign our existing website?", "Yes. We can redesign and rebuild an existing site, or improve key pages first."),
       ("Can we edit the website ourselves?", "Yes. Every site we build comes with an easy-to-use editor and a short training session.")]),
]

for i, sv in enumerate(SERVICES):
    others = "".join(btn(o["name"], f'/services/{o["slug"]}', "neutral-300") for o in SERVICES if o is not sv)
    body = (hero(f'Service {sv["n"]}', "Anvora", sv["name"], sv["intro"], [CALL(), PRICE()])
            + split("Why it matters", sv["why"][0], sv["why"][1])
            + section(head("What's included", "Everything you need, handled.") + cards(sv["inc"]))
            + section(head("How we work", "A clear process, start to finish.") + steps(sv["steps"]), dark=True)
            + section(stats(sv["stats"]))
            + section(head("Questions", f'{sv["name"]} FAQs') + faq(sv["faq"]))
            + section(head("Explore more", "Other services") + f'<div class="anv-row">{others}</div>'))
    write(f'/services/{sv["slug"]}', page(sv["slug"], sv["name"], sv["intro"], body))

# ------------------------------------------------------------------ example plans (no past-client claims)
PLANS = [
 dict(id="local-cafe", name="Local café or restaurant", cat="Brand & Social", color="c-purple", goal="More regulars & online orders",
      ch="A loved local spot with an inconsistent look online and a quiet social presence.",
      ap="Sharpen the brand, then run a weekly short-form video series and local search ads around opening hours and menu highlights.",
      me="Google Maps actions, online orders, social reach and repeat customers."),
 dict(id="ecommerce-brand", name="E-commerce brand", cat="Content & Paid Social", color="c-electric", goal="Lower cost per sale",
      ch="Good products, but ad creatives that have stopped performing and rising ad costs.",
      ap="A monthly content sprint producing fresh product and UGC-style videos, tested in structured paid social campaigns.",
      me="Cost per acquisition, return on ad spend and conversion rate."),
 dict(id="fitness-studio", name="Gym or fitness studio", cat="Web & Local SEO", color="c-dark", goal="More trial sign-ups",
      ch="A slow website that doesn't show up when people nearby search for a gym or class.",
      ap="A fast, mobile-first landing page, local SEO for every location and a simple free-trial funnel.",
      me="Local rankings, trial sign-ups and trial-to-member conversion."),
 dict(id="online-store", name="Skincare or beauty brand", cat="Email & Retention", color="c-coral", goal="More repeat purchases",
      ch="Lots of first-time buyers, but few of them come back.",
      ap="Welcome, post-purchase and win-back email flows, plus content that teaches customers how to get the most from the products.",
      me="Repeat purchase rate, email revenue and customer lifetime value."),
 dict(id="real-estate", name="Real estate agency", cat="Brand Strategy", color="c-light", goal="More qualified leads",
      ch="A crowded market where every agency looks and sounds the same.",
      ap="Clear positioning, new messaging and a lead-generation funnel with valuation offers and retargeting.",
      me="Qualified leads, cost per lead and valuation requests."),
 dict(id="course-creator", name="Online course or coach", cat="Funnels & Growth", color="c-purple", goal="More enrolments",
      ch="Plenty of website visitors, but few of them ever enrol.",
      ap="A lead magnet, an automated email nurture sequence and dedicated landing pages for each course.",
      me="Email sign-ups, enrolments and revenue per visitor."),
]
EXAMPLE = '<span class="eyebrow anv-muted">Example plan · not a past client</span>'

def plan_tile(c):
    return (f'<a href="/example-plans#{c["id"]}" class="anv-tile {c["color"]}"><div class="anv-row" style="justify-content:space-between">'
            f'<span class="eyebrow">{E(c["cat"])}</span><span class="eyebrow">Example plan</span></div>'
            f'<div><span class="eyebrow" style="opacity:.6">Goal</span><div class="h-m" style="margin:.3em 0 .6em">{E(c["goal"])}</div>'
            f'<h3 class="h-xs">{E(c["name"])}</h3></div></a>')

def plan_block(c):
    return (f'<article class="anv-case" id="{c["id"]}"><div class="anv-case__visual {c["color"]}"><span class="eyebrow">{E(c["cat"])}</span>'
            f'<div><span class="eyebrow" style="opacity:.6">Goal</span><div class="h-l" style="margin-top:.3em">{E(c["goal"])}</div></div></div>'
            f'<div class="anv-case__body">{EXAMPLE}<h2 class="h-m">{E(c["name"])}</h2><dl>'
            f'<dt>Typical challenge</dt><dd class="p-m">{E(c["ch"])}</dd><dt>What we\'d do</dt><dd class="p-m">{E(c["ap"])}</dd>'
            f'<dt>What we\'d measure</dt><dd class="p-m">{E(c["me"])}</dd></dl></div></article>')

FOUNDING = section(
    '<div class="anv-split"><div><span class="eyebrow" style="opacity:.6">Founding clients</span>'
    '<h2 class="h-l" style="margin-top:.4em">Be one of our first clients</h2></div><div>'
    '<p class="p-l">Anvora is a new agency, and we are looking for a small number of founding clients to grow with.</p>'
    '<p class="p-l">Founding clients get a reduced rate and extra attention from day one. In return, we ask for honest feedback and, '
    'if you are happy with the results, permission to share them as one of our first case studies.</p>'
    f'<div class="button-row" style="margin-top:var(--gap-xxl)">{btn("Apply as a founding client", "/contact?plan=founding", "electric")}</div>'
    '</div></div>', dark=True)

approach_body = (hero("Our Approach", "How we work", "How we work", "Anvora is a new marketing company. Here is how we work, what you can expect from us and how we would approach your goals.",
                      [btn("See example plans", "/example-plans", "electric"), btn("Start a project", "/contact", "neutral-200")])
                 + section(head("Principles", "What you can expect from us") + cards([
                       ("Goals before tactics", "We start with your business goals and only then choose channels and campaigns."),
                       ("Your accounts, your data", "Ad accounts, analytics and content always belong to you, and you can see everything."),
                       ("Honest reporting", "Clear monthly reports in plain language, including what did not work."),
                       ("Test and learn", "We treat every campaign as an experiment and improve it every week."),
                       ("One partner", "Strategy, creative and performance under one roof, so nothing gets lost between agencies."),
                       ("Realistic promises", "We set honest expectations upfront. No guaranteed rankings or overnight miracles.")]))
                 + section(head("Process", "From first call to results") + steps([
                       ("Discover", "A free call and audit to understand your business, audience and goals."),
                       ("Plan", "A clear plan with channels, budget, timeline and the numbers we will track."),
                       ("Launch", "We build and launch your brand, content and campaigns."),
                       ("Improve", "Weekly optimisation and monthly reviews to keep results moving up.")]), dark=False)
                 + section(head("Example plans", "How we'd approach different businesses",
                                "These are examples of how we would plan for different types of businesses. They are not past client results.")
                           + f'<div class="anv-grid">{"".join(plan_tile(c) for c in PLANS)}</div>')
                 + FOUNDING)
write("/approach", page("approach", "Our Approach", "How Anvora works with clients.", approach_body))

plans_body = (hero("Example Plans", "Not past results", "Example plans", "How we would approach common goals for different types of businesses. Anvora is new, so these are example plans, not case studies of past clients.",
                   [CALL()])
              + section("".join(plan_block(c) for c in PLANS))
              + FOUNDING)
write("/example-plans", page("example-plans", "Example Plans", "Example marketing plans by Anvora.", plans_body))

# ------------------------------------------------------------------ pricing
def tick(v): return {"y": "✓", "n": "—"}.get(v, v)
ROWS = [("Channels managed", "1", "Up to 3", "Unlimited"), ("Strategy session", "Quarterly", "Monthly", "Weekly"),
        ("Content pieces / month", "Up to 12", "Up to 30", "Custom"), ("Paid ads management", "y", "y", "y"),
        ("SEO & content plan", "n", "y", "y"), ("Landing pages", "n", "1 / quarter", "Custom"),
        ("Reporting", "Monthly", "Monthly + dashboard", "Live dashboard"), ("Dedicated account lead", "n", "y", "y")]
table = ('<table class="anv-table"><thead><tr><th>Compare plans</th><th>Starter</th><th>Growth</th><th>Custom</th></tr></thead><tbody>'
         + "".join(f'<tr><td class="p-m">{E(r[0])}</td>' + "".join(f"<td class=\"p-m\">{E(tick(x))}</td>" for x in r[1:]) + "</tr>" for r in ROWS)
         + "</tbody></table>")
price_body = (hero("Pricing", "Retainers", "Simple pricing", "Flexible monthly retainers with no hidden fees. Pick a plan, or let us build one around your goals.",
                   [CALL()])
              + SECTION["pricing-home"]
              + section(head("Compare", "What's in each plan") + table)
              + section(head("Add-ons", "Need something extra?") + cards([
                    ("Brand strategy project", "A complete brand strategy and identity, delivered as a fixed-price project."),
                    ("Website build", "A new website or landing page set, quoted on scope."),
                    ("Content shoot", "A half or full day photo and video shoot with edited assets.")]))
              + section(head("Questions", "Pricing FAQs") + faq([
                    ("Is there a minimum contract?", "Retainers run on a quarterly or annual basis. Annual billing saves 20%."),
                    ("Is ad spend included?", "No. Ad spend is paid directly to the platforms from your own ad accounts."),
                    ("Can we change plans later?", "Yes. You can move up or down a plan at the end of any billing period."),
                    ("What does Custom include?", "Custom plans combine any of our services at the scale you need. Book a call and we will put together a proposal.")])))
write("/pricing", page("pricing", "Pricing", "Anvora marketing retainers and pricing.", price_body))

# ------------------------------------------------------------------ contact
SERVICE_CHIPS = "".join(f'<label><input type="checkbox" name="services" value="{E(s["name"])}"> {E(s["name"])}</label>' for s in SERVICES)
contact_form = (
    '<form class="anv-form" novalidate>'
    '<div class="anv-2"><label><span>Name *</span><input name="name" required autocomplete="name"></label>'
    '<label><span>Email *</span><input type="email" name="email" required autocomplete="email"></label></div>'
    '<div class="anv-2"><label><span>Company</span><input name="company" autocomplete="organization"></label>'
    '<label><span>Plan</span><select name="plan"><option value="">Not sure yet</option><option value="starter">Starter</option>'
    '<option value="growth">Growth</option><option value="custom">Custom</option><option value="founding">Founding client</option></select></label></div>'
    f'<label><span>What can we help with?</span><div class="anv-chips">{SERVICE_CHIPS}</div></label>'
    '<label><span>Monthly budget</span><select name="budget"><option>Under €2,000</option><option>€2,000 – €5,000</option>'
    '<option>€5,000 – €10,000</option><option>€10,000+</option></select></label>'
    '<label><span>Tell us about your goals *</span><textarea name="message" required></textarea></label>'
    '<button type="submit">Send message</button>'
    '<div class="anv-form__done"><h3 class="h-s">Thanks, we got your message!</h3><p class="p-m">We will get back to you within one working day.</p></div>'
    '</form>')
contact_info = ('<div class="anv-info">'
    '<div class="anv-card c-purple"><span class="eyebrow">Email</span><h3 class="h-s"><a href="mailto:hello@anvora.com">hello@anvora.com</a></h3><p class="p-m">We reply within one working day.</p></div>'
    '<div class="anv-card"><span class="eyebrow">Phone</span><h3 class="h-s">+00 000 000 000</h3><p class="p-m">Monday to Friday, 9:00 – 18:00.</p></div>'
    '<div class="anv-card c-electric"><span class="eyebrow">Prefer a call?</span><h3 class="h-s">Book a free 30-minute strategy call.</h3><p class="p-m">Mention it in your message and we will send you a few time slots.</p></div>'
    '</div>')
contact_body = (hero("Contact", "Let's talk", "Let's grow together", "Tell us a little about your business and goals. We will come back with ideas, not a sales pitch.")
                + section(f'<div class="anv-contact">{contact_form}{contact_info}</div>'))
write("/contact", page("contact", "Contact", "Get in touch with Anvora.", contact_body, cta=False))

# ------------------------------------------------------------------ free audit
audit_form = (
    '<form class="anv-form" novalidate>'
    '<div class="anv-2"><label><span>Name *</span><input name="name" required autocomplete="name"></label>'
    '<label><span>Email *</span><input type="email" name="email" required autocomplete="email"></label></div>'
    '<label><span>Website *</span><input type="url" name="website" placeholder="https://" required></label>'
    '<label><span>Main goal</span><select name="goal"><option>More leads</option><option>More online sales</option>'
    '<option>Stronger brand awareness</option><option>Better return on ad spend</option><option>Something else</option></select></label>'
    '<label><span>Anything we should know?</span><textarea name="message"></textarea></label>'
    '<button type="submit">Claim my free audit</button>'
    '<div class="anv-form__done"><h3 class="h-s">Your audit request is in!</h3><p class="p-m">We will send your personalised audit within 5 working days.</p></div>'
    '</form>')
audit_body = (hero("Free audit", "No strings attached", "Free marketing audit", "Find out what is holding your marketing back. We review your brand, website, ads, social and SEO, then send you a clear action plan.")
              + section(f'<div class="anv-contact">{audit_form}<div>{head("What you get", "A clear, honest review")}'
                        + cards([("Website & conversion", "Speed, UX and the biggest leaks in your funnel."),
                                 ("Ads & tracking", "Where your ad budget is working, and where it is wasted."),
                                 ("SEO & content", "Quick wins and the search opportunities you are missing."),
                                 ("Brand & social", "How your brand comes across, and how to stand out.")], cols=2) + "</div></div>")
              + section(head("How it works", "Three simple steps") + steps([
                    ("Tell us about you", "Fill in the short form with your website and goals."),
                    ("We dig in", "Our team reviews your marketing across every channel."),
                    ("Get your plan", "Receive a clear report and an optional call to walk through it."),
                    ("Act on it", "Use the plan yourself, or let Anvora put it into action.")]), dark=True))
write("/audit", page("audit", "Free Marketing Audit", "Get a free marketing audit from Anvora.", audit_body, cta=False))

# ------------------------------------------------------------------ insights
ARTICLES = [("Strategy", "7 min", "How to write a positioning statement that actually guides decisions", "A simple framework to define what makes your brand different, and use it every day.", "c-purple"),
            ("Performance", "5 min", "The 5 tracking mistakes that waste your ad budget", "Many ad accounts share the same tracking problems. Here is how to fix them.", "c-electric"),
            ("Social", "6 min", "Short-form video: a practical playbook for small teams", "How to plan, film and publish a month of video content in a single day.", "c-coral"),
            ("SEO", "8 min", "Local SEO checklist for businesses with multiple locations", "Everything you need to rank in every city you serve.", "c-dark"),
            ("Content", "4 min", "Why your website copy is not converting (and how to fix it)", "Five quick edits that make visitors more likely to take action.", "c-light"),
            ("Growth", "6 min", "Email flows every online business should have running", "The automated emails that keep earning while you sleep.", "c-purple"),
            ("Brand", "5 min", "When is it time to rebrand?", "Signs your brand is holding your business back, and what to do about it.", "c-electric"),
            ("Analytics", "6 min", "The only marketing dashboard you need", "Five numbers that tell you whether your marketing is working.", "c-coral")]
def art(a, big=False):
    cat, rt, t, ex, col = a
    return (f'<div class="anv-tile {col} anv-article"><div class="anv-row" style="justify-content:space-between"><span class="eyebrow">{E(cat)}</span>'
            f'<span class="eyebrow">{E(rt)} read</span></div><div><h3 class="{"h-m" if big else "h-s"}">{E(t)}</h3><p class="p-m">{E(ex)}</p></div></div>')
ins_body = (hero("Insights", "Playbooks", "Insights", "Practical marketing ideas and playbooks you can put to work in your own business.")
            + section(f'<div class="anv-featured">{art(ARTICLES[0], True)}{art(ARTICLES[1])}</div>'
                      f'<div class="anv-grid">{"".join(art(a) for a in ARTICLES[2:])}</div>'))
write("/insights", page("insights", "Insights", "Marketing insights from Anvora.", ins_body))

# ------------------------------------------------------------------ FAQ
faq_body = (hero("FAQs", "Good questions", "Frequently asked questions", "Everything you might want to know about working with Anvora. Can't find your answer? Just ask.",
                 [btn("Contact us", "/contact", "electric")])
            + section(
                faq([("What kind of businesses do you work with?", "Ambitious small and mid-sized businesses, from e-commerce and hospitality to B2B services. If you want to grow, we want to talk."),
                     ("How do we get started?", "Book a strategy call or claim a free audit. We will learn about your goals and propose a plan and budget."),
                     ("Who will we work with?", "A dedicated account lead plus specialists for each service, such as strategists, designers, writers and media buyers.")], "Working with us")
                + faq([("Do you offer all services separately?", "Yes. Every service can be booked on its own or combined into a retainer."),
                       ("Can you work alongside our in-house team?", "Absolutely. We can add capacity or expertise to your own team."),
                       ("Which ad platforms do you use?", "Google, Microsoft, Meta, LinkedIn, TikTok and Pinterest, depending on your audience.")], "Services")
                + faq([("How does pricing work?", "Most clients work with us on a monthly retainer. Larger one-off work such as a rebrand or website is quoted per project."),
                       ("Is there a long-term contract?", "Retainers are billed quarterly or annually. Annual billing saves 20%."),
                       ("Is ad spend included?", "No. Ad spend is paid directly to the ad platforms from accounts you own.")], "Pricing & contracts")
                + faq([("How will we know it is working?", "We agree clear KPIs at the start and report on them every month, in plain language."),
                       ("How soon can we expect results?", "Paid campaigns can show results within weeks; SEO and brand work build over months. We will set honest expectations upfront."),
                       ("Do we own our accounts and data?", "Yes. Ad accounts, analytics and content always belong to you.")], "Results & reporting")))
write("/faq", page("faq", "FAQs", "Frequently asked questions about Anvora.", faq_body))

# ------------------------------------------------------------------ legal (templates)
NOTE = '<p class="anv-note">This is a template. Please have it reviewed by a legal professional and add your company details before publishing.</p>'
LEGAL = {
 "privacy-policy": ("Privacy Policy", [
   ("Who we are", ["Anvora is a marketing company. This policy explains how we collect, use and protect your personal data when you use our website or services."]),
   ("What we collect", ["Information you give us, such as your name, email address, company and message when you fill in a form.", "Technical data such as your IP address, browser type and pages visited, collected through cookies and analytics tools."]),
   ("How we use your data", ["To reply to your enquiries and provide our services.", "To send our newsletter, if you subscribed. You can unsubscribe at any time.", "To understand and improve how our website is used."]),
   ("Sharing your data", ["We never sell your data. We only share it with trusted service providers who help us run our business, under appropriate agreements."]),
   ("Your rights", ["You can ask to access, correct or delete your personal data, or object to how we use it, by emailing hello@anvora.com."]),
   ("Contact", ["Questions about this policy? Email hello@anvora.com."])]),
 "terms-and-conditions": ("Terms & Conditions", [
   ("Introduction", ["These terms apply to the use of this website and to all services provided by Anvora, unless agreed otherwise in writing."]),
   ("Services", ["The scope, deliverables, timeline and fees for each project or retainer are set out in a proposal or agreement accepted by both parties."]),
   ("Payment", ["Invoices are payable within the term stated on the invoice. Retainers are billed in advance for each billing period."]),
   ("Intellectual property", ["Once paid in full, the client owns the final deliverables created for them. Anvora may show the work in its portfolio unless agreed otherwise."]),
   ("Liability", ["Anvora is not liable for indirect or consequential loss. Our total liability is limited to the fees paid for the relevant service."]),
   ("Changes", ["We may update these terms from time to time. The latest version is always published on this page."])]),
 "cookie-policy": ("Cookie Policy", [
   ("What are cookies?", ["Cookies are small text files stored on your device when you visit a website. They help the site work and help us understand how it is used."]),
   ("Cookies we use", ["Essential cookies that make the website work.", "Analytics cookies that help us improve the website (only with your consent).", "Marketing cookies that help us measure our advertising (only with your consent)."]),
   ("Managing cookies", ["You can change your cookie preferences at any time, or block cookies through your browser settings."]),
   ("Contact", ["Questions? Email hello@anvora.com."])]),
 "licensing-agreement": ("Licensing", [
   ("Ownership of work", ["After full payment, clients receive ownership of the final deliverables created specifically for them, including designs, copy, photos and videos."]),
   ("Third-party assets", ["Some work may include licensed fonts, stock imagery or music. These remain subject to their own licence terms, which we will share with you."]),
   ("Source files", ["Working and source files can be supplied on request, and may be subject to an additional fee if not included in the agreement."]),
   ("Portfolio use", ["Anvora may display completed work in its portfolio and case studies, unless the client asks us not to."])]),
}
for slug, (title, parts) in LEGAL.items():
    prose = NOTE + "".join(f"<h2>{E(h)}</h2>" + ("<ul>" + "".join(f"<li>{E(x)}</li>" for x in ps) + "</ul>" if len(ps) > 1 else f"<p>{E(ps[0])}</p>") for h, ps in parts)
    body = hero("Legal", "Last updated 2026", title, "How Anvora handles this topic, explained as clearly as possible.") + section(f'<div class="anv-prose">{prose}</div>')
    write(f"/legal/{slug}", page(slug, title, f"Anvora {title}.", body, cta=False))

# ------------------------------------------------------------------ homepage
home = home.replace(SECTION["testimonial"], "").replace(SECTION["made"], "")
def remove_div(s, opener):
    i = s.find(opener)
    if i < 0:
        return s
    depth, pos = 0, i
    for m in re.finditer(r"<(/?)div(?:\s[^>]*)?>", s[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return s[:i] + s[i + m.end():]
    return s
home = remove_div(home, '<div class="trustedby-wrap">')
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8", newline="\n").write(finish(home))
print("updated /index.html")
