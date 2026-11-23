"""Rebrand the saved Osmo page into an Anvora marketing-agency site.
Usage: python -I rebrand.py <source index.html> <output index.html>
"""
import re, sys, html

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()

# ---------------------------------------------------------------- text map
# Exact text-node replacements (matched after html-unescape + strip).
T = {
    "Menu": "Menu", "Login": "Contact", "Join": "Let's talk",
    "Our Products": "Our Services",
    "The Vault": "Brand Strategy",
    "Page Transition Course": "Performance Marketing",
    "Button Pack": "Social Media",
    "Icon Library": "Content Studio",
    "Community": "SEO & Growth",
    "Easings": "Web & Landing Pages",
    "Osmo Showcase": "Our Approach",
    "Collection": "Example Plans",
    "Member Login": "Client Login",
    "Join Osmo": "Work with Anvora",
    "Learning": "Growing",
    "Demo: Try 20 Resources for Free": "Free: Get Your Marketing Audit",
    # hero
    "Dev Toolkit": "Marketing",
    "Built to Flex": "Built to Grow",
    "Platform packed with": "Agency fluent in",
    "Webflow": "Brand",
    "HTML": "Growth",
    "resources,": "strategy,",
    "icons": "content",
    "easings": "paid ads",
    "and\xa0a page transition": "and\xa0a data-driven",
    "course": "mindset",
    # hero cards / latest work
    "Mega Navigation (Directional Hover)": "Brand Identity Refresh",
    "3D Cards Tornado": "Social Launch Campaign",
    "Shutter Scroll Transition": "Paid Search Overhaul",
    "Radial Cards Slider (GSAP)": "Influencer Partnerships",
    "Product Hotspot Modal": "E-commerce Growth Sprint",
    "Number Odometer": "Conversion Rate Lift",
    "Step-by-step Timeline": "Go-to-Market Roadmap",
    "Animated Grid Overlay (Columns)": "Content Engine Setup",
    "Collage Focus Card on Hover": "Email Nurture Flows",
    "Osmo is an ever-growing platform": "Anvora is a full-service marketing company for ambitious brands. Strategy, creative and performance marketing under one roof, built around results you can actually measure.",
    "Osmo in use": "Anvora in action",
    "See what it can do!": "See what we can do!",
    "Join 3K+ others": "Now welcoming founding clients",
    "Created by": "Led by",
    "Dennis": "Creative", "Snellenberg": "Director",
    "Ilja": "Strategy", "van Eck": "Lead",
    "New Resource": "What we do",
    "Folder Tabs": "Product launch campaigns",
    "Sections & Layouts": "Social Media",
    "Sticker Effect on Click": "Rebrands & repositioning",
    "Gimmicks": "Branding",
    "Password Field": "Local SEO sprints",
    "Forms": "SEO",
    "Scaling Media on Scroll (Sticky)": "Paid social campaigns",
    "Scroll Animations": "Performance",
    "Scroll Ruler": "Newsletter & email flows",
    "Latest updates": "What we",
    "from Osmo": "can do for you",
    "New stuff is": "Ideas for",
    "added every week!": "every stage of growth!",
    # platform / services
    "The platform": "The agency",
    "( The Vault )": "( Our Approach )",
    "Built by two award-winning": "Built by strategists and creatives who live and breathe marketing, Anvora gives your brand the insight, campaigns, content and tools behind real growth. We plan, launch, measure and optimise, together with you.",
    "We built Osmo to help": "We built Anvora to help brands market smarter, faster, and better.",
    "About the Vault": "About our approach",
    "A growing toolkit for creative developers": "A complete growth partner for modern brands",
    "Access everything with a single membership:": "Everything you need in a single partnership:",
    "Buttons": "Social", "Icons": "Content",
    "Part of the": "Part of every", "Membership": "Retainer", "membership": "retainer",
    "Our ever-growing dashboard": "Positioning, messaging and visual identity that make your brand impossible to ignore.",
    "Learn how to create page transitions": "Paid search and social campaigns engineered for ROI, tracked down to the last click.",
    "100 fully accessible buttons": "Always-on social content and community management that keeps your audience engaged.",
    "Ready-to-paste easings": "Fast, conversion-focused websites and landing pages that turn clicks into customers.",
    "A uniform library of clean": "Photo, video and copywriting produced in-house, on brand and on schedule.",
    "Connect with the people who love": "Technical SEO, content and analytics that compound your organic growth month after month.",
    # why
    "Why Osmo?": "Why Anvora?",
    "Level up your game": "Level up your marketing with a team that cares about your growth as much as you do.",
    "Build faster and better": "Grow faster and smarter",
    "Our resources save you hours": "Our campaigns are built on research, not guesswork. Every plan is shaped around your goals, so you can focus on running your business while we drive the results.",
    "Speed up your process": "Launch with confidence",
    "These aren": "No cookie-cutter packages. Every strategy is built to be fast, flexible and measurable, so you can launch standout campaigns without trading quality for speed.",
    "A living and growing system": "Always optimising",
    "We keep adding new resources": "We test, learn and refine every week. Your marketing evolves with your business and your customers, so your growth never stands still.",
    "Osmo’s Global": "Anvora’s Global",
    # testimonials (PLACEHOLDERS - replace with real client reviews)
    "Osmo empowered me": "Anvora doubled our qualified leads in six months",
    "Dang Nguyen": "Client Name", "Head of Creative": "Head of Marketing, Company",
    "Thanks to Osmo": "Sample testimonial: Anvora took the time to understand our business before touching a single campaign. Within months our cost per lead dropped and our pipeline was fuller than ever. They feel like part of our own team.",
    "This gets the official GSAP": "The best marketing partner we have worked with.",
    "Cassie Evans": "Client Name", "Education GSAP": "Founder, Company",
    "Even if you know GSAP": "Sample testimonial: we had tried agencies before, but Anvora was the first to connect creative work directly to revenue. Clear reporting, honest advice and campaigns our customers actually talk about.",
    "One of a kind platform": "Our brand finally looks and sounds like us.",
    "Huy (by Huy)": "Client Name", "Designer & YT creator": "CEO, Company",
    "It's incredible to be able": "Sample testimonial: the rebrand Anvora delivered gave us the confidence to go after bigger clients. Everything from our website to our socials now tells one clear story.",
    "The creative developer's cheat code.": "Strategy, creative and ads, all in one place.",
    "Jordan Gilroy": "Client Name", "Web Designer": "Marketing Director, Company",
    "Osmo is a one-stop shop": "Sample testimonial: Anvora replaced three separate freelancers for us. One team, one plan, one monthly report, and noticeably better results across every channel.",
    "came across a few neat tricks": "“They spotted opportunities we had missed for years.”",
    "Jesper Landberg": "Client Name", "Creative Developer": "Growth Lead, Company",
    "Osmo Supply is a gem": "Sample testimonial: their SEO and content work doubled our organic traffic in under a year. Anvora is proactive, data-driven and genuinely great to work with.",
    "The Osmo Vault has been a great partner": "Anvora has been a great partner in growing our brand",
    "Victor Work": "Client Name", "VW Lab": "Owner, Company",
    "Osmo Supply has been a great partner": "Sample testimonial: from our first launch campaign to our latest product drop, Anvora has been with us every step. Smart people, sharp creative and results we can see.",
    # pricing (PLACEHOLDER numbers)
    "Everything you need in one membership": "Everything you need in one retainer",
    "per user": "per month", "1 user": "1 channel", "Solo": "Starter",
    "25": "1.5K", "20": "1.2K", "16": "2.4K",
    "Become a member": "Get started",
    "Vault Resources, added weekly": "Strategy, content & monthly reporting",
    "min 2 users": "multi-channel", "Team": "Growth",
    "Per person/month, billed": "Per month, billed",
    "Sign up your team": "Book a strategy call",
    "20% per user!": "20% on bundles!",
    # showcase (PLACEHOLDER client names)
    "Osmo": "Anvora",
    "Loopsii": "Northwind Coffee", "@stabondar": "@northwind",
    "Resources Used": "Channels Used",
    "Paaspop | 50 Years": "Lumen Festival", "@weareboring.nl": "@lumenfest",
    "Moisez | Portfolio": "Brightline Fitness", "@iammoisez": "@brightline",
    "Good Times Timer": "Kora Skincare", "@mateoszymkowicz": "@koraskin",
    "@achimrothe": "@harborco",
    "Finnian Sturdy": "Atlas Realty", "@finniansturdy": "@atlasrealty",
    "Chande Bootcamp": "Peak Academy", "@lenonguyen": "@peakacademy",
    "@kaixa.219": "@verdeliving",
    "BRND Club Website": "Mosaic Studio", "@antonievanpelt": "@mosaicstudio",
    "These folks": "These brands", "are talented": "are growing",
    "Explore showcase": "See our approach",
    # CTA / newsletter
    "Try for free": "Free audit",
    "Want a taste before you buy?": "Not sure where to start?",
    "Try the Osmo Demo Vault": "Get a free Anvora marketing audit",
    "Unlock the demo": "Claim your audit",
    "Try 20": "Free", "Resources for Free": "Marketing Audit",
    "Subscribe to the Osmo Newsletter": "Subscribe to the Anvora Newsletter",
    # footer
    "Product": "Services", "new": "new", "Showcase": "Our Approach",
    "About Osmo": "About Anvora", "Updates": "Insights",
    "2025": "2026", "osmo supply b.v.": "anvora marketing",
    "created by": "crafted by", "dennis": "the anvora", "ilja": "team",
    # about modal
    "A platform by...": "An agency by...",
    "Based in Netherlands and Belgium": "Anvora is a new, hands-on marketing company. We bring strategy, creative and performance marketing together, so growing brands get one partner, one clear plan and honest reporting on what works.",
    "Sites Pushed Live": "Core services", "120+": "6",
    "Site of the Day Awards": "Team for every channel", "38": "1",
}
# keys long enough to be treated as "starts with" matches
PREFIX = {k: v for k, v in T.items() if len(k) >= 10 and not k.startswith("@")}

def map_text(raw):
    txt = html.unescape(raw)
    st = txt.strip()
    if not st:
        return raw
    new = T.get(st)
    if new is None:
        for k, v in PREFIX.items():
            if st.startswith(k) and len(st) > len(k) + 15:
                new = v
                break
    if new is None:
        return raw
    lead = txt[: len(txt) - len(txt.lstrip())]
    trail = txt[len(txt.rstrip()):]
    return lead + html.escape(new, quote=False) + trail

# ---------------------------------------------------------------- logos
def wordmark(vb_w, vb_h, cls, weight=600):
    fs = vb_h * 0.98
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {vb_w} {vb_h}" fill="none"{cls}>'
            f'<text x="0" y="{vb_h*0.86:.1f}" textLength="{vb_w}" lengthAdjust="spacingAndGlyphs" '
            f'font-family="Haffer, \'Haffer XH\', Arial, sans-serif" font-weight="{weight}" font-size="{fs:.1f}" '
            f'fill="currentColor" letter-spacing="-0.02em">anvora</text></svg>')

ANVORA_MARK = ("M712 2H1070C1112 2 1140 38 1128 75C1060 290 1000 480 920 670H1320A102 102 0 0 1 1422 772V1318H1135"
               "A305 305 0 0 1 830 1013V850C720 1060 600 1200 500 1298C488 1308 472 1312 455 1312H62C14 1312 -12 1248 18 1205"
               "C380 800 560 430 655 45C662 18 684 2 712 2Z")

def mark(size, cls):
    # the Anvora logo mark (traced from the client's logo file), centred in a square box
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="-20 -73 1466 1466" fill="none"{cls}>'
            f'<path d="{ANVORA_MARK}" fill="currentColor"/></svg>')

def replace_svg(s, opener_re, builder):
    out, pos = [], 0
    for m in re.finditer(opener_re, s):
        if m.start() < pos:
            continue
        end = s.index("</svg>", m.start()) + 6
        cls_m = re.search(r'( class="[^"]*"| data-load-icon=""[^>]*?class="[^"]*")', m.group(0))
        extra = ""
        for a in re.findall(r' (?:class|data-load-icon)="[^"]*"', m.group(0)):
            extra += a
        out.append(s[pos:m.start()]); out.append(builder(extra)); pos = end
    out.append(s[pos:])
    return "".join(out)

s = replace_svg(s, r'<svg[^>]*viewBox="0 0 540 156"[^>]*>', lambda c: wordmark(540, 156, c))
def footer_wordmark(cls, vb="-4 0 1580 300"):
    # heavy uppercase wordmark, natural proportions (no glyph stretching), like the original
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="{vb}" fill="none"{cls}>'
            '<text x="0" y="292" font-family="\'Haffer VF\', \'Arial Black\', Arial, sans-serif" font-weight="900" '
            'font-size="400" letter-spacing="-20" fill="currentColor" style="font-variation-settings:\'wght\' 900">ANVORA</text></svg>')

s = replace_svg(s, r'<svg[^>]*viewBox="0 0 1768 297"[^>]*>', footer_wordmark)
s = replace_svg(s, r'<svg[^>]*viewBox="0 0 123 27"[^>]*>', lambda c: wordmark(123, 27, c))
s = replace_svg(s, r'<svg[^>]*viewBox="0 0 187 187"[^>]*class="nav-logo__icon-svg"[^>]*>', lambda c: mark(187, c))
s = replace_svg(s, r'<svg[^>]*viewBox="0 0 80 80"[^>]*class="home-hero__top-logo"[^>]*>', lambda c: mark(80, c))

# ---------------------------------------------------------------- head / tracking
DESC = "Anvora is a full-service marketing company: brand strategy, performance marketing, social media, content and SEO for ambitious brands."
TITLE = "Anvora - Marketing Built to Grow"
s = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", s, flags=re.S)
s = re.sub(r'(<meta content=")[^"]*(" (?:name|property)="(?:og:|twitter:)?title")', rf"\g<1>{TITLE}\2", s)
s = re.sub(r'(<meta content=")[^"]*(" (?:name|property)="(?:og:|twitter:)?description")', rf"\g<1>{DESC}\2", s)
s = re.sub(r'<meta content="google-site-verification[^>]*>', "", s)
s = re.sub(r'<link href="https://www\.osmo\.supply" rel="canonical">', "", s)
s = re.sub(r'<link rel="preconnect" href="https://config\.outseta\.com"[^>]*>', "", s)
# Osmo's analytics + membership (Outseta) wiring
s = re.sub(r'<script defer="" data-domain="osmo\.supply"[^>]*></script>', "", s)
s = re.sub(r'<script[^>]*>\s*var o_options.*?</script>', "", s, flags=re.S)
s = re.sub(r'<script src="js/outseta\.min\.js"[^>]*></script>', "", s)
# JSON-LD organisation
s = re.sub(r'<script type="application/ld\+json">.*?</script>',
           '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Anvora","description":"' + DESC + '"}</script>',
           s, count=1, flags=re.S)
s = s.replace('images/69012f298572037011bf87ea_osmo-icon-favicon.png', 'images/anvora-favicon.svg').replace('rel="shortcut icon" type="image/x-icon"', 'rel="icon" type="image/svg+xml"')
s = s.replace('images/69012f2e4a7dd6afaa4c04ab_osmo-icon-webclip.png', 'images/anvora-favicon.svg')

# attributes
ATTR = {"Ilja van Eck PNG": "Anvora team member", "Dennis Snellenberg PNG": "Anvora team member",
        "Osmo Supply Logo Icon": "Anvora logo"}
for k, v in ATTR.items():
    s = s.replace(f'"{k}"', f'"{v}"')
for k in ["Good Times Timer", "Chande Bootcamp", "Paaspop | 50 Years", "Moisez | Portfolio", "Loopsii", "Finnian Sturdy", "BRND Club Website", "Victor Work"]:
    s = s.replace(f'alt="{html.escape(k, quote=False)}"', f'alt="{html.escape(T[k])}"')


# social links / form / domain hooks still tied to Osmo
for u in ["https://www.linkedin.com/company/osmosupply/", "https://www.instagram.com/osmo.supply/", "https://twitter.com/osmosupply"]:
    s = s.replace(f'href="{u}"', 'href="#"')
s = s.replace('data-wf-domain="www.osmo.supply" ', '')
s = re.sub(r'<form method="get" data-mapping=.*?name="wf-form-Newsletter-Footer"', '<form method="get" name="wf-form-Newsletter-Footer"', s, flags=re.S)
s = s.replace(' data-o-email-form="1"', '')


# Anvora overrides: hide third-party client logos (add your own), widen price box
s = s.replace("</head>", "<style>.trustedby-wrap{display:none!important}.pricing-card__price-w{width:auto!important}</style></head>", 1)

# ---------------------------------------------------------------- text nodes
parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", s, flags=re.S | re.I)
for i in range(0, len(parts), 2):
    parts[i] = re.sub(r">([^<>]+)<", lambda m: ">" + map_text(m.group(1)) + "<", parts[i])
s = "".join(parts)

open(dst, "w", encoding="utf-8", newline="\n").write(s)

# report leftovers
t = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
left = sorted({html.unescape(m.group(1)).strip() for m in re.finditer(r">([^<>]+)<", t)} )
print("visible strings mentioning osmo/vault:", [x for x in left if re.search(r"osmo|vault|webflow|gsap", x, re.I)])
