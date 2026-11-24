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

# social links
home = home.replace('<a href="#" target="_blank" aria-label="instagram"',
                    '<a href="https://www.instagram.com/thumbnailanvora/" target="_blank" rel="noopener" data-barba-prevent="" aria-label="instagram"')

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
home = re.sub(r'(>Support</a></li>)', r'\1<li class="footer-link__col-li"><a data-underline-link="" href="/brand" class="p-m">Brand Guidelines</a></li>', home, count=1)
home = home.replace('_col-top"><h4 class="h-xs">SEO &amp; Growth</h4>', '_col-top"><h4 class="h-xs">Company</h4>')
home = home.replace('_col-top"><h4 class="h-xs">Retainer</h4>', '_col-top"><h4 class="h-xs">Resources</h4>')

# ------------------------------------------------------------------ example approaches (by industry; not past clients)
A = lambda **k: k
APPROACHES = [
 A(slug="coffee-shop", short="Coffee Shop", name="Local coffee shop", cat="Local business", color="c-electric",
   goal="More regulars, every week",
   intro="How we would help an independent coffee shop turn passers-by into regulars, using local search, short-form video and a simple loyalty loop.",
   channels=["Google Business Profile", "Instagram & TikTok", "Loyalty & email"],
   situation=["Great coffee, but the shop barely shows up when people nearby search for “coffee near me”.",
              "Social posts are irregular and mostly photos of cups, so they get little reach.",
              "Lots of one-time visitors, with no easy way to bring them back."],
   audiences=[("Morning commuters", "Want speed and consistency. They decide in seconds, usually from Google Maps."),
              ("Remote workers", "Look for wifi, seats and plugs. They stay for hours and come back if they feel welcome."),
              ("Weekend locals", "Want a treat and a place to meet friends. Discover new spots on Instagram and TikTok.")],
   phases=[("Weeks 1–2", "Get found", "Fix the Google Business Profile: hours, menu, photos, categories and a plan for getting honest reviews."),
           ("Weeks 3–4", "Find the story", "Shoot a month of short videos in one morning: the roast, the team, the regulars, the signature drink."),
           ("Weeks 5–8", "Build the habit", "Launch a simple digital stamp card and a weekly email or SMS with one reason to visit."),
           ("Weeks 9–12", "Grow the reach", "Small, tightly targeted local ads around the shop, plus one collaboration with a nearby business.")],
   tactics=[("Google Maps first", "Most local coffee decisions start on a map, so the profile is treated like the shop window."),
            ("Weekly video series", "One recurring format, like “drink of the week”, that is easy to film and easy to recognise."),
            ("Review routine", "A small card at the till and a follow-up message that make leaving a review effortless."),
            ("Quiet-hour offers", "Offers aimed at the slowest hours of the day, so promotions fill empty seats instead of busy ones."),
            ("Local partnerships", "Cross-promotion with gyms, offices and shops within walking distance."),
            ("Loyalty that feels personal", "A stamp card plus a birthday drink, so regulars feel noticed.")],
   ad=("Sponsored · Within 2 km", "Your new morning stop is 3 minutes away", "Freshly roasted beans, fast service and the best flat white on the street. Show this ad for a free pastry with your first coffee.", "Get directions"),
   post=("Reel idea", "“From bean to cup in 30 seconds”: a fast, satisfying video of the morning roast, with the barista explaining today’s special."),
   offer=("Email subject line", "Your 5th coffee is on us this week ☕"),
   kpis=["Google Maps direction requests", "Calls and profile views", "Reviews per month", "Loyalty sign-ups", "Repeat visits"],
   services=["social-media", "seo-growth", "content-studio"]),

 A(slug="roofing-company", short="Roofing Company", name="Roofing company", cat="Home services", color="c-coral",
   goal="More quote requests from the right jobs",
   intro="How we would help a roofing company win more high-value quote requests in its service area, and stop relying only on word of mouth.",
   channels=["Google Search Ads", "Local SEO", "Before & after content"],
   situation=["Most work comes from referrals, so the pipeline goes quiet without warning.",
              "The website looks dated and doesn’t make it easy to request a quote from a phone.",
              "Competitors appear above them in Google when homeowners search after a storm."],
   audiences=[("Urgent repairs", "A leak or storm damage. They want someone fast and trustworthy, and usually call the first good result."),
              ("Planned replacements", "Older roofs. They compare three quotes and care about warranties, reviews and clear pricing."),
              ("Property managers", "Look after several buildings. They value reliability, reporting and fast response times.")],
   phases=[("Weeks 1–2", "Fix the foundations", "Set up call and form tracking, clean up the Google Business Profile and audit the current website."),
           ("Weeks 3–4", "Build the quote page", "A fast landing page with photos of real jobs, reviews, guarantees and a 3-step quote form."),
           ("Weeks 5–8", "Launch search ads", "High-intent search campaigns for repair and replacement terms, split by town in the service area."),
           ("Weeks 9–12", "Earn trust at scale", "A steady flow of before & after posts, review requests after every job and local SEO pages for each town.")],
   tactics=[("Intent-only keywords", "Ads target searches like “roof leak repair”, not broad terms that attract job seekers or DIY fans."),
            ("Emergency call extension", "A click-to-call button on every ad and page for urgent jobs."),
            ("Town-by-town pages", "Separate pages for each area served, so the business ranks where it actually works."),
            ("Before & after proof", "Photos from every job turned into posts, ads and website galleries."),
            ("Storm-ready campaigns", "Pre-built ads that can be switched on within an hour after severe weather."),
            ("Fast follow-up", "Missed calls and forms trigger an instant text, so leads don’t go to the next roofer.")],
   ad=("Ad · Search result", "Roof Leak? Same-Day Inspection", "Local, insured roofers. Free written quotes, clear pricing and a workmanship guarantee. Call now or book online in 60 seconds.", "Request a quote"),
   post=("Post idea", "A side-by-side before & after of a recent roof, with a 15-second clip of the crew explaining what was wrong and how it was fixed."),
   offer=("Landing page headline", "A roof you won’t have to think about for 25 years."),
   kpis=["Quote requests", "Cost per qualified lead", "Phone calls from ads", "Quote-to-job rate", "Google reviews"],
   services=["performance-marketing", "web-landing-pages", "seo-growth"]),

 A(slug="dental-clinic", short="Dental Clinic", name="Dental clinic", cat="Health & wellness", color="c-purple",
   goal="More new patients for high-value treatments",
   intro="How we would help a dental clinic attract new patients, especially for treatments like implants, aligners and whitening, while keeping the tone calm and trustworthy.",
   channels=["Google Search Ads", "Local SEO", "Email & reminders"],
   situation=["The diary is full of check-ups, but there are few enquiries for higher-value treatments.",
              "Many patients are nervous, and the website doesn’t speak to that.",
              "Online booking exists, but it is hard to find and drops people halfway through."],
   audiences=[("Nervous patients", "Have avoided the dentist for years. They need reassurance before they book."),
              ("Smile upgraders", "Interested in aligners or whitening. They research a lot and compare prices online."),
              ("Busy families", "Want one practice for everyone, with easy booking and evening appointments.")],
   phases=[("Weeks 1–2", "Listen and audit", "Review enquiries, the booking flow and patient reviews to understand what patients worry about."),
           ("Weeks 3–4", "Treatment pages", "Clear, friendly pages for each key treatment, with prices from, FAQs and a short video from the dentist."),
           ("Weeks 5–8", "Targeted search", "Search campaigns for treatment terms, sending people to the matching page with an easy consultation form."),
           ("Weeks 9–12", "Nurture and recall", "Email follow-ups for people who enquired but didn’t book, and reminders that bring existing patients back.")],
   tactics=[("Calm, human tone", "Real photos of the team and plain-language explanations instead of clinical jargon."),
            ("Transparent prices", "Showing “from” prices and payment plans upfront removes the biggest reason people don’t enquire."),
            ("Free consultation offer", "A low-pressure first step for high-value treatments."),
            ("Review strategy", "Asking happy patients for reviews at the right moment, in line with healthcare advertising rules."),
            ("Booking flow fixes", "Fewer steps and a mobile-friendly form so fewer people drop off."),
            ("Recall emails", "Friendly reminders that keep check-ups booked and the diary steady.")],
   ad=("Ad · Search result", "Clear Aligners · Free Consultation", "See your new smile before you start. Friendly local team, flexible payment plans and evening appointments.", "Book a free consult"),
   post=("Video idea", "“What actually happens at your first visit”: a calm walkthrough of the clinic, filmed from the patient’s point of view."),
   offer=("Email subject line", "Still thinking about straighter teeth? Here’s what it costs"),
   kpis=["Consultation bookings", "Cost per new patient", "Treatment enquiries", "Booking completion rate", "Recall bookings"],
   services=["performance-marketing", "seo-growth", "web-landing-pages"]),

 A(slug="plumbing-heating", short="Plumber & Heating", name="Plumbing & heating company", cat="Home services", color="c-dark",
   goal="A steady flow of booked jobs",
   intro="How we would help a plumbing and heating business fill its calendar with profitable jobs, from emergency call-outs to boiler installs.",
   channels=["Local Services & Search Ads", "Google Business Profile", "Service plans"],
   situation=["Busy in winter, quiet in summer, so income goes up and down all year.",
              "Most leads are small jobs, while boiler installs and bathroom refits are rare.",
              "Calls are missed when the team is on site, and those customers ring someone else."],
   audiences=[("Emergencies", "Burst pipe or no hot water. They want the fastest trustworthy option right now."),
              ("Planned upgrades", "New boiler or bathroom. They compare quotes and want clear prices and finance options."),
              ("Landlords", "Need safety checks and reliable repairs across several properties every year.")],
   phases=[("Weeks 1–2", "Stop losing leads", "Call tracking, a missed-call text-back and a cleaned-up Google Business Profile."),
           ("Weeks 3–4", "Split the services", "Separate pages and campaigns for emergencies, boiler installs and bathrooms, each with its own offer."),
           ("Weeks 5–8", "Launch and test", "Search and local service ads by job type, with budgets shifted toward the jobs that pay best."),
           ("Weeks 9–12", "Smooth the seasons", "An annual service plan, promoted to past customers by email and SMS before the busy season.")],
   tactics=[("Job-type campaigns", "Different ads and budgets for emergencies and installs, because their value is very different."),
            ("Missed-call text-back", "An automatic reply so the customer knows they will get a call back."),
            ("Finance messaging", "Monthly payment options shown upfront for big-ticket installs."),
            ("Service plan offer", "Recurring income from annual boiler services and landlord safety checks."),
            ("Review requests", "A text after every job asking for a review, with a direct link."),
            ("Seasonal timing", "Heating campaigns start before the first cold week, not after it.")],
   ad=("Ad · Search result", "Boiler Broken? Engineers Near You Today", "Gas Safe registered local engineers. Fixed call-out price, no hidden fees and 12-month guarantee on all repairs.", "Call now"),
   post=("Post idea", "“3 signs your boiler is about to give up”: a quick tip video from one of the engineers, ending with the annual service offer."),
   offer=("SMS to past customers", "Winter is coming. Book your boiler service now and get 10% off before 31 October."),
   kpis=["Booked jobs", "Cost per booked job", "Install enquiries", "Service plan sign-ups", "Missed calls recovered"],
   services=["performance-marketing", "seo-growth", "web-landing-pages"]),

 A(slug="hair-salon", short="Hair & Beauty Salon", name="Hair & beauty salon", cat="Local business", color="c-coral",
   goal="A fuller booking diary",
   intro="How we would help a salon fill quiet days, attract new clients who love its style and keep existing clients rebooking.",
   channels=["Instagram & TikTok", "Online booking", "Email & SMS"],
   situation=["Weekends are full, but Tuesdays and Wednesdays are often empty.",
              "Beautiful work, but the Instagram feed isn’t turning followers into bookings.",
              "Clients often forget to rebook, so the gap between visits keeps getting longer."],
   audiences=[("Style seekers", "Follow trends on Instagram and TikTok. They choose a salon by its portfolio."),
              ("Busy professionals", "Want easy online booking, lunchtime or evening slots and no surprises on price."),
              ("Special occasions", "Weddings, proms and events. They plan ahead and book for groups.")],
   phases=[("Weeks 1–2", "Make booking easy", "Booking links everywhere: Instagram bio, Google profile, website and every post."),
           ("Weeks 3–4", "Show the work", "A content plan built around transformations, stylist profiles and the salon experience."),
           ("Weeks 5–8", "Fill quiet days", "Midweek offers for new clients, promoted with small local ads to the right age group and area."),
           ("Weeks 9–12", "Keep them coming", "Automatic rebooking reminders and a referral reward for clients who bring a friend.")],
   tactics=[("Transformation reels", "Short before & after videos, the format that gets the most reach for salons."),
            ("Stylist spotlights", "Each stylist gets their own content, so clients connect with a person."),
            ("Midweek offers", "Discounts only on quiet days, so the busy days stay full price."),
            ("Rebooking reminders", "A message at the right time for each service, like 6 weeks after a colour."),
            ("Referral rewards", "A thank-you for clients who bring a friend, and a welcome for the friend."),
            ("Bridal packages", "A dedicated page and enquiry form for weddings and events.")],
   ad=("Sponsored · Instagram", "New in town? Your first colour is 20% off", "Lived-in blondes, glossy brunettes and cuts that grow out beautifully. Midweek appointments available.", "Book now"),
   post=("Reel idea", "A 15-second colour transformation set to a trending sound, with the stylist naming the exact shade in the caption."),
   offer=("SMS reminder", "Hi Sam, it’s been 6 weeks since your colour. Want your usual Thursday slot?"),
   kpis=["Online bookings", "Midweek fill rate", "New clients", "Rebooking rate", "Instagram profile clicks"],
   services=["social-media", "content-studio", "brand-strategy"]),

 A(slug="real-estate-agent", short="Real Estate Agent", name="Real estate agent", cat="Property", color="c-light",
   goal="More valuation requests from sellers",
   intro="How we would help a local real estate agent stand out in a crowded market and win more seller instructions.",
   channels=["Brand positioning", "Meta Ads", "Local content"],
   situation=["Every agent in the area looks and sounds the same, so sellers choose on fees.",
              "Listings get views, but few homeowners ask for a valuation.",
              "There is no system to stay in touch with people who might sell in a year or two."],
   audiences=[("Ready sellers", "Planning to sell soon. They want a confident valuation and an agent they trust."),
              ("Curious owners", "Not ready yet, but want to know what their home is worth."),
              ("Landlords & investors", "Looking for rental management, yield advice and off-market deals.")],
   phases=[("Weeks 1–2", "Find the difference", "Positioning work to define what makes this agent genuinely different, and how to say it."),
           ("Weeks 3–4", "Valuation funnel", "An instant online valuation tool and landing page, with a follow-up from a real agent."),
           ("Weeks 5–8", "Local visibility", "Ads to homeowners in target streets, plus a monthly local market video."),
           ("Weeks 9–12", "Long-term nurture", "A monthly email with local prices and sold homes, keeping the agent top of mind.")],
   tactics=[("Clear positioning", "One strong reason to choose this agent, used consistently across every touchpoint."),
            ("Instant valuation", "A low-effort first step that turns curious owners into leads."),
            ("Hyper-local content", "Street-level market updates that show real local knowledge."),
            ("Sold-home stories", "Each sale turned into a short case story with the seller’s permission."),
            ("Retargeting", "Gentle reminders for people who visited the valuation page but didn’t finish."),
            ("Agent personal brands", "Agents become familiar faces in the area through short video.")],
   ad=("Sponsored · Facebook", "What is your home worth in today’s market?", "Get a free, no-obligation valuation from a local expert who has sold on your street. Takes 2 minutes.", "Get my valuation"),
   post=("Video idea", "“What sold on your street this month”: a 45-second market update filmed walking through the neighbourhood."),
   offer=("Email subject line", "Homes near you sold 4% above asking last month"),
   kpis=["Valuation requests", "Cost per valuation", "Instructions won", "Email list growth", "Market-update views"],
   services=["brand-strategy", "performance-marketing", "content-studio"]),

 A(slug="law-firm", short="Law Firm", name="Small law firm", cat="Professional services", color="c-dark",
   goal="More qualified consultations",
   intro="How we would help a small law firm attract the right clients for its main practice areas, with a professional, trustworthy presence online.",
   channels=["SEO & content", "Google Search Ads", "Reviews & reputation"],
   situation=["Most enquiries are not a good fit, which wastes a lot of partner time.",
              "The website talks about the firm, not about the client’s problem.",
              "Search ads are expensive, and there is no clear idea of which ones bring clients."],
   audiences=[("People in a hard moment", "Facing a divorce, a dispute or a loss. They need clarity and empathy first."),
              ("Small business owners", "Need contracts, employment advice or help with a dispute. They value speed and fixed fees."),
              ("Referrers", "Accountants and other advisers who send clients when they trust the firm.")],
   phases=[("Weeks 1–2", "Focus", "Pick the 2–3 most valuable practice areas and define the ideal client for each."),
           ("Weeks 3–4", "Rewrite for clients", "Practice-area pages that explain the problem, the process and the costs in plain language."),
           ("Weeks 5–8", "Search, carefully", "A tightly controlled search campaign with intake questions that filter out poor-fit enquiries."),
           ("Weeks 9–12", "Build authority", "Helpful guides that answer common questions and rank in search over time.")],
   tactics=[("Plain-language pages", "Clients understand what will happen, how long it takes and what it may cost."),
            ("Qualifying intake form", "A few smart questions save hours of unsuitable consultations."),
            ("Fixed-fee offers", "Clear packages for common needs make it easier to say yes."),
            ("Helpful guides", "Answers to the questions people search for, written by the lawyers themselves."),
            ("Reputation management", "A steady, compliant process for collecting reviews."),
            ("Referral partner updates", "A short quarterly update to accountants and advisers who refer clients.")],
   ad=("Ad · Search result", "Employment Lawyer · Fixed-Fee First Call", "Unfairly dismissed? Speak to a specialist employment lawyer. Clear advice, fixed fees, no jargon.", "Book a consultation"),
   post=("LinkedIn idea", "A short post from a partner: “3 clauses every small business contract should have”, with a downloadable checklist."),
   offer=("Guide title", "Getting divorced: a step-by-step guide to the process and the costs"),
   kpis=["Qualified consultations", "Cost per qualified enquiry", "Consultation-to-client rate", "Organic traffic to guides", "Reviews"],
   services=["seo-growth", "performance-marketing", "web-landing-pages"]),

 A(slug="fitness-studio", short="Gym & Fitness Studio", name="Gym or fitness studio", cat="Health & wellness", color="c-electric",
   goal="More trial sign-ups that become members",
   intro="How we would help a gym or boutique fitness studio fill its classes with new members, and keep them coming back after the first month.",
   channels=["Meta Ads", "Landing page & funnel", "Community content"],
   situation=["A January rush, then sign-ups drop for the rest of the year.",
              "Free trials bring people in, but few of them become paying members.",
              "The studio has a great community that nobody outside can see."],
   audiences=[("Beginners", "Want to get fit but feel intimidated. They need to see people like them."),
              ("Switchers", "Already train elsewhere. They want better coaching, better classes or a better vibe."),
              ("Busy parents", "Short on time. They want quick, effective sessions at the right times.")],
   phases=[("Weeks 1–2", "Fix the funnel", "A simple trial landing page, a booking flow and tracking from ad to first class."),
           ("Weeks 3–4", "Show the community", "Content that features real members, coaches and the energy of a class."),
           ("Weeks 5–8", "Trial campaigns", "Ads for a clear trial offer, targeted to people within a short drive of the studio."),
           ("Weeks 9–12", "Trial to member", "A follow-up sequence of messages and a coach check-in during the trial period.")],
   tactics=[("One clear offer", "A single, easy trial offer instead of many confusing deals."),
            ("Member stories", "Real people sharing why they joined. The most convincing content for beginners."),
            ("Trial follow-up", "Messages before and after the first class so people actually show up and come back."),
            ("Local targeting", "Ads only to people who live or work close enough to train regularly."),
            ("Challenge campaigns", "A 6-week challenge to create a second January in spring and autumn."),
            ("Referral nights", "Members bring a friend for free, building the community from within.")],
   ad=("Sponsored · Instagram", "Your first week is free. No pressure.", "Small group classes, friendly coaches and a plan built around you. Beginners very welcome.", "Claim free week"),
   post=("Reel idea", "“Your first class, explained”: a coach walks through what happens, from the warm-up to the high-fives at the end."),
   offer=("Trial follow-up SMS", "Great work today, Alex! Same time Thursday? Here’s your next class link."),
   kpis=["Trial sign-ups", "Cost per trial", "Trial show-up rate", "Trial-to-member rate", "Member retention"],
   services=["performance-marketing", "web-landing-pages", "social-media"]),

 A(slug="online-clothing-brand", short="Online Clothing Brand", name="Online clothing brand", cat="E-commerce", color="c-purple",
   goal="Profitable growth in online sales",
   intro="How we would help a direct-to-consumer clothing brand grow sales while keeping ad costs under control and building a brand people remember.",
   channels=["Paid social", "Content studio", "Email & SMS flows"],
   situation=["Ad costs keep rising, and the same creatives have been running for months.",
              "Many people add to cart and leave without buying.",
              "Customers buy once and rarely come back for a second order."],
   audiences=[("Trend followers", "Discover brands on TikTok and Instagram. They buy on impulse when the creative is right."),
              ("Value seekers", "Love the style but wait for a reason to buy: a new drop, a bundle or a seasonal sale."),
              ("Loyal fans", "Already bought and love the fit. They are the best source of repeat sales and reviews.")],
   phases=[("Weeks 1–2", "Audit the numbers", "Check tracking, margins and which products and ads really make money."),
           ("Weeks 3–4", "Creative sprint", "A batch of new videos: try-ons, styling tips, creator content and product close-ups."),
           ("Weeks 5–8", "Structured testing", "Paid social campaigns that test hooks, formats and offers in a clear, repeatable way."),
           ("Weeks 9–12", "Retention engine", "Welcome, abandoned cart, post-purchase and win-back flows by email and SMS.")],
   tactics=[("Creative testing", "New ads every month, with clear tests to learn what actually sells."),
            ("Creator content", "Real people wearing the clothes. More trustworthy than studio shots."),
            ("Cart recovery", "A sequence of reminders for people who left items in their basket."),
            ("Drops and bundles", "Limited releases and outfit bundles that give people a reason to buy now."),
            ("Post-purchase flow", "Styling tips and fit questions that lead naturally to a second order."),
            ("Margin-aware budgets", "Ad spend is judged on profit, not just revenue.")],
   ad=("Sponsored · TikTok", "The trousers everyone keeps asking about", "Tailored fit, stretch fabric, 6 colours. Free returns for 30 days.", "Shop now"),
   post=("Video idea", "“1 pair of trousers, 5 outfits”: a creator styles the bestseller for work, weekend and evening in 20 seconds."),
   offer=("Abandoned cart email", "Still thinking it over? Your size is almost sold out"),
   kpis=["Return on ad spend", "Cost per acquisition", "Conversion rate", "Repeat purchase rate", "Email & SMS revenue"],
   services=["performance-marketing", "content-studio", "social-media"]),

 A(slug="saas-startup", short="B2B Software Startup", name="B2B software startup", cat="Technology", color="c-dark",
   goal="More demos with the right companies",
   intro="How we would help an early-stage B2B software company build a predictable pipeline of demos, without wasting budget on the wrong audience.",
   channels=["Positioning & website", "LinkedIn & Google Ads", "Content & SEO"],
   situation=["The product is strong, but the website explains features, not the problem it solves.",
              "Demo requests come in slowly, and many are from companies that are too small.",
              "Content is published now and then, without a clear goal."],
   audiences=[("The champion", "A manager who feels the problem every day and wants a better tool."),
              ("The decision maker", "A head of department or founder who cares about cost, risk and results."),
              ("The evaluator", "Someone in IT or operations who checks security, integrations and set-up time.")],
   phases=[("Weeks 1–2", "Positioning", "Customer interviews and a clear message: who it is for, the problem and why it is better."),
           ("Weeks 3–4", "Website & demo flow", "A rewritten homepage, use-case pages and a short demo form that qualifies leads."),
           ("Weeks 5–8", "Targeted paid", "LinkedIn ads to the right job titles and company sizes, plus search ads for problem-aware terms."),
           ("Weeks 9–12", "Content engine", "Comparison pages, practical guides and founder posts that build trust and search traffic.")],
   tactics=[("Problem-first messaging", "Lead with the pain the customer feels, then show the product as the answer."),
            ("Use-case pages", "A page for each type of team or industry, with relevant examples."),
            ("Qualifying demo form", "Company size and role questions, so sales time goes to the right leads."),
            ("Account targeting", "Ads shown only to companies that match the ideal customer profile."),
            ("Comparison content", "Honest “us vs. them” pages for people already comparing tools."),
            ("Founder-led LinkedIn", "Regular posts from the founder that share lessons and opinions.")],
   ad=("Sponsored · LinkedIn", "Your team spends 6 hours a week on reports. It could be 6 minutes.", "Connect your tools once and get automatic, always-up-to-date reports. Set up in a day.", "Book a demo"),
   post=("LinkedIn idea", "A founder post: “We interviewed 40 operations managers. Here are the 5 problems they all mentioned.”"),
   offer=("Landing page headline", "Reporting that runs itself, so your team can get back to real work."),
   kpis=["Qualified demos", "Cost per qualified demo", "Demo-to-customer rate", "Website conversion rate", "Organic sign-ups"],
   services=["brand-strategy", "performance-marketing", "seo-growth"]),

 A(slug="restaurant", short="Restaurant", name="Neighbourhood restaurant", cat="Local business", color="c-coral",
   goal="Fuller tables, especially midweek",
   intro="How we would help a neighbourhood restaurant fill tables on quiet nights, grow direct bookings and rely less on delivery apps.",
   channels=["Instagram & TikTok", "Google Business Profile", "Email & events"],
   situation=["Fridays and Saturdays are busy, but Monday to Wednesday is quiet.",
              "Delivery apps take a large cut of every online order.",
              "There is no guest list, so the restaurant can’t invite people back."],
   audiences=[("Date nights", "Want atmosphere and something special. They discover places on Instagram."),
              ("Groups & celebrations", "Birthdays and team dinners. They book ahead and need space and set menus."),
              ("Locals", "Live nearby. They come back often if there is a reason, like a weekly special.")],
   phases=[("Weeks 1–2", "Direct bookings", "Booking and ordering links front and centre on Google, Instagram and the website."),
           ("Weeks 3–4", "Food that sells", "A content day to film the kitchen, signature dishes and the room at its best."),
           ("Weeks 5–8", "Midweek reasons", "A recurring midweek event, like a set menu or chef’s table, promoted locally."),
           ("Weeks 9–12", "Guest list", "Wi-fi and booking sign-ups feed a monthly email with events and offers.")],
   tactics=[("Kitchen content", "Behind-the-scenes cooking videos that make people hungry."),
            ("Midweek events", "Something special on quiet nights, instead of discounts every day."),
            ("Direct ordering", "Your own ordering link, with a small reward for ordering direct."),
            ("Group booking page", "An easy way to enquire for birthdays, parties and team dinners."),
            ("Local food creators", "Inviting local food creators to try the menu and share honestly."),
            ("Guest email list", "A list the restaurant owns, used for events and seasonal menus.")],
   ad=("Sponsored · Instagram", "Tuesday is pasta night. £15 for two courses.", "Fresh pasta made every morning, a glass of house wine optional but encouraged. 10 minutes from you.", "Book a table"),
   post=("Reel idea", "“How we make 300 ravioli before lunch”: a fast, satisfying kitchen video ending with the plated dish."),
   offer=("Email subject line", "New autumn menu + a table for you this Wednesday?"),
   kpis=["Direct bookings", "Midweek covers", "Direct online orders", "Guest list growth", "Google Maps actions"],
   services=["social-media", "content-studio", "seo-growth"]),

 A(slug="wedding-photographer", short="Wedding Photographer", name="Wedding photographer", cat="Creative services", color="c-light",
   goal="More bookings from ideal couples",
   intro="How we would help a wedding photographer attract couples who love their style, and book further ahead with less back-and-forth.",
   channels=["Instagram & Pinterest", "SEO & venue pages", "Enquiry nurture"],
   situation=["Enquiries come in, but many are looking for the cheapest option.",
              "The portfolio is beautiful, but it doesn’t rank on Google for local venues.",
              "Couples ask the same questions by email, and many go quiet after the first reply."],
   audiences=[("Style-led couples", "Choose a photographer by the feel of their work, often on Instagram and Pinterest."),
              ("Venue searchers", "Already booked a venue and search for photographers who know it."),
              ("Planners & venues", "Recommend suppliers they trust to dozens of couples each year.")],
   phases=[("Weeks 1–2", "Sharpen the brand", "Define the style and the ideal couple, then make the website say it clearly."),
           ("Weeks 3–4", "Venue pages", "A blog post for each venue photographed, with real galleries and tips for that venue."),
           ("Weeks 5–8", "Social & Pinterest", "A consistent posting plan and Pinterest boards that send traffic for years."),
           ("Weeks 9–12", "Enquiry to booking", "A welcome guide with prices and FAQs, plus a friendly follow-up sequence.")],
   tactics=[("Clear style statement", "Saying exactly what kind of wedding and couple you love, so the right people enquire."),
            ("Venue SEO", "Ranking for “[venue] wedding photographer”, where couples already have a date and budget."),
            ("Pinterest as search", "Pins keep sending visitors long after they are posted."),
            ("Pricing guide", "A beautiful PDF with starting prices that filters out poor-fit enquiries."),
            ("Follow-up sequence", "Helpful emails that keep the conversation going without being pushy."),
            ("Supplier relationships", "Sharing images with venues and planners to earn recommendations.")],
   ad=("Pinterest · Pin", "Relaxed, natural wedding photos at The Old Barn", "A full real wedding at one of the county’s most loved venues, plus 5 tips for photos there.", "See the gallery"),
   post=("Post idea", "A carousel: “The 7 moments couples tell me they’re most glad I captured”, with one image for each moment."),
   offer=("Email subject line", "Your wedding guide is here (and the 3 questions to ask any photographer)"),
   kpis=["Enquiries from ideal couples", "Enquiry-to-booking rate", "Organic traffic to venue pages", "Pinterest clicks", "Referrals from venues"],
   services=["brand-strategy", "seo-growth", "social-media"]),
]
APPROACH_IDX = {a["slug"]: a for a in APPROACHES}

# footer: a column of example approaches (copied from the "Company" column so it gets the same accordion behaviour)
def _approach_col(m):
    col = m.group(0)
    items = "".join(f'<li class="footer-link__col-li"><a data-underline-link="" href="/example-approaches/{a["slug"]}" class="p-m">{E(a["short"])}</a></li>' for a in APPROACHES)
    items += '<li class="footer-link__col-li"><a data-underline-link="" href="/example-approaches" class="p-m">View all approaches →</a></li>'
    col = col.replace('<h4 class="h-xs">Company</h4>', '<h4 class="h-xs">Example Approaches</h4>')
    col = re.sub(r'<ul class="footer-link__col-ul">.*?</ul>', lambda _: f'<ul class="footer-link__col-ul">{items}</ul>', col, count=1, flags=re.S)
    return col + m.group(0)
home = re.sub(r'<div data-accordion-status="not-active" class="footer-link__col"><div data-hover="" data-accordion-toggle="" class="footer-link__col-top"><h4 class="h-xs">Company</h4>.*?</ul></div></div></div></div>',
              _approach_col, home, count=1, flags=re.S)


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
.anv-grid.is--4{grid-template-columns:repeat(4,1fr)}.anv-grid.is--6{grid-template-columns:repeat(6,1fr)}
.anv-pill{border:1px solid var(--color-neutral-450);border-radius:2em;padding:.55em 1.1em;font-size:.95em;color:inherit;text-decoration:none;transition:background .2s,color .2s}
.anv-pill:hover{background:var(--color-dark);color:var(--color-light)}
.anv-logo{border-radius:.75em;padding:var(--gap-l);min-height:17em;display:flex;flex-direction:column;justify-content:space-between;align-items:flex-start}
.anv-logo__mark{width:7em;align-self:center;margin:auto}
.anv-logo__wm{width:16em;margin:auto;align-self:center}
.anv-logo__lockup{display:flex;align-items:center;gap:1.1em;margin:auto;align-self:center}
.anv-logo__lockup span:first-child{width:4.2em;display:block}.anv-logo__lockup span:last-child{width:13em;display:block}
.anv-sw{all:unset;cursor:pointer;display:flex;flex-direction:column;background:var(--color-white);border-radius:.75em;overflow:hidden;transition:transform .3s}
.anv-sw:hover{transform:translateY(-.25em)}.anv-sw:focus-visible{outline:2px solid var(--color-purple);outline-offset:2px}
.anv-sw__chip{height:9em;display:flex;align-items:flex-end;padding:1em;transition:opacity .2s}
.anv-sw:not(.is--big) .anv-sw__chip{height:5em}
.anv-sw__chip .eyebrow{opacity:0;transition:opacity .2s}.anv-sw:hover .anv-sw__chip .eyebrow{opacity:.8}
.anv-sw.is--copied .anv-sw__chip .eyebrow{opacity:1}
.anv-sw__info{padding:1em 1.1em 1.2em;display:flex;flex-direction:column;gap:.4em}
.anv-sw__codes{display:flex;flex-direction:column;gap:.15em;font-family:Haffer Mono,Arial,sans-serif;font-size:.72em;text-transform:uppercase;opacity:.65}
.anv-ratio{display:flex;height:4.5em;border-radius:.75em;overflow:hidden;box-shadow:inset 0 0 0 1px var(--color-neutral-450)}
.anv-ratio i{font-style:normal;display:flex;align-items:flex-end;padding:.8em;font-family:Haffer Mono,Arial,sans-serif;font-size:.7em;text-transform:uppercase;white-space:nowrap;overflow:hidden}
.anv-pair{border-radius:.75em;padding:1.2em;min-height:9em;display:flex;flex-direction:column;justify-content:space-between;gap:.4em;box-shadow:inset 0 0 0 1px rgba(128,128,128,.2)}
.anv-font{background:var(--color-white);border-radius:.75em;padding:var(--gap-l);display:flex;flex-direction:column;gap:1em}
.anv-tscale{border-top:1px solid var(--color-neutral-450)}
.anv-ts{display:grid;grid-template-columns:14em 1fr;gap:var(--gap-l);align-items:center;padding:1.4em 0;border-bottom:1px solid var(--color-neutral-450);overflow:hidden}
.anv-ts__meta{display:flex;flex-direction:column;gap:.35em}
.anv-ts__sample{white-space:nowrap;overflow:hidden;text-overflow:clip}
.anv-btns{display:grid;gap:.6em}
.anv-btnrow>div:first-child{display:flex;align-items:center}
.anv-btnrow{display:grid;grid-template-columns:16em 1fr;gap:var(--gap-l);align-items:center;background:var(--color-white);border-radius:.75em;padding:1.2em 1.4em}
.anv-btnrow code,.anv-space code{font-family:Haffer Mono,Arial,sans-serif;font-size:.85em}
.anv-onDark{margin-top:var(--gap-s);background:var(--color-dark);color:var(--color-light);border-radius:.75em;padding:var(--gap-l)}
.anv-spacing{display:grid;gap:.55em}
.anv-space{display:grid;grid-template-columns:8.5em 4em 1fr;align-items:center;gap:1em}
.anv-space i{display:block;height:.9em;background:var(--color-purple);border-radius:.2em;max-width:100%}
.anv-do,.anv-dont{border-radius:.5em;padding:.9em 1em;display:flex;flex-direction:column;gap:.4em}
.anv-do{background:color-mix(in srgb,var(--color-electric) 35%,transparent)}
.anv-dont{background:color-mix(in srgb,var(--color-coral) 15%,transparent)}
.anv-dont p{text-decoration:line-through;text-decoration-color:var(--color-coral)}
.anv-voice .anv-card .p-m{margin-top:0}
.anv-motion{margin-top:var(--gap-l);height:3.5em;border-radius:2em;background:var(--color-neutral-700);position:relative;overflow:hidden}
.anv-motion i{position:absolute;top:.5em;left:.5em;width:2.5em;height:2.5em;border-radius:50%;background:var(--color-electric);animation:anvMove 2.4s cubic-bezier(.19,1,.22,1) infinite alternate}
@keyframes anvMove{to{left:calc(100% - 3em)}}
@media (max-width:991px){.anv-grid.is--4{grid-template-columns:repeat(2,1fr)}.anv-grid.is--6{grid-template-columns:repeat(3,1fr)}}
@media (max-width:767px){.anv-grid.is--4,.anv-grid.is--6{grid-template-columns:repeat(2,1fr)}.anv-ts,.anv-btnrow{grid-template-columns:1fr}.anv-ts__sample{font-size:min(var(--ts),2.6em)}.anv-space{grid-template-columns:7.5em 3.5em 1fr}}
@media (max-width:991px){.anv-grid,.anv-steps{grid-template-columns:repeat(2,1fr)}}
@media (max-width:767px){
 .anv-hero{padding-top:9em}
 .anv-card{min-height:0}.anv-card .p-m{margin-top:.5em}.anv-tile,.anv-stat{min-height:14em}
 .anv-split,.anv-grid,.anv-grid.is--2,.anv-steps,.anv-stats,.anv-case,.anv-contact,.anv-featured,.anv-form .anv-2{grid-template-columns:1fr}
 .anv-case__body dl{grid-template-columns:1fr}
 .anv-table th,.anv-table td{padding:.8em .6em;font-size:.85em}
}
.anv-arrow{font-size:1.6em;line-height:1;transition:transform .4s cubic-bezier(.65,.05,0,1)}.anv-tile:hover .anv-arrow{transform:translateX(.25em)}
.anv-glance{display:grid;grid-template-columns:1.25fr 1fr;gap:var(--gap-s)}
.anv-glance__goal{border-radius:1em;padding:var(--gap-l);min-height:24em;display:flex;flex-direction:column;justify-content:space-between}
.anv-glance__info{background:var(--color-white);border-radius:1em;padding:var(--gap-l);display:flex;flex-direction:column;justify-content:space-between;gap:var(--gap-l)}
.anv-glance__info dl{display:grid;grid-template-columns:9em 1fr;gap:1em 1.5em;margin:0}
.anv-glance__info dt{font-family:Haffer Mono,Arial,sans-serif;font-size:.6875em;text-transform:uppercase;opacity:.5;padding-top:.4em}
.anv-glance__info dd{margin:0;font-size:1.0625em}
.anv-chip{border:1px solid currentColor;border-radius:2em;padding:.45em 1em;font-size:.9em}
.anv-chal,.anv-kpis{list-style:none;margin:0;padding:0;border-top:1px solid var(--color-neutral-450)}
.anv-chal li,.anv-kpis li{display:grid;grid-template-columns:3.5em 1fr;gap:1em;padding:1.4em 0;border-bottom:1px solid var(--color-neutral-450);align-items:baseline}
.anv-chal li span,.anv-kpis li span{font-family:Haffer Mono,Arial,sans-serif;font-size:.75em;color:var(--color-purple)}
.anv-kpis li{font-size:1.25em;letter-spacing:-.01em}
.anv-phases .h-l{margin-top:-.2em}
.anv-mock{border-radius:.75em;padding:var(--gap-l);min-height:22em;display:flex;flex-direction:column;gap:1.2em}.anv-mock.is--white{background:var(--color-white)}
.anv-ad{border:1px solid var(--color-neutral-300);border-radius:.6em;padding:1.1em;display:flex;flex-direction:column;gap:.7em;margin-top:auto}
.anv-ad__top{display:flex;align-items:center;gap:.7em;font-size:.85em;line-height:1.2}
.anv-ad__top i{width:2.2em;height:2.2em;border-radius:50%;background:var(--color-purple);flex:none}
.anv-ad__top small{opacity:.55;font-size:.85em}
.anv-ad h4{font-size:1.2em;line-height:1.15;letter-spacing:-.02em;font-weight:500;margin:0}
.anv-ad p{font-size:.92em;opacity:.7;margin:0}
.anv-ad__cta{align-self:flex-start;background:var(--color-purple);color:#fff;border-radius:.4em;padding:.6em 1.1em;font-size:.85em}
.anv-mock__play{width:3.2em;height:3.2em;border-radius:50%;border:1px solid currentColor;display:flex;align-items:center;justify-content:center;font-size:.9em;margin-top:auto}
.anv-filters .anv-pill{font:inherit;background:none;cursor:pointer;color:inherit}
.anv-filters .anv-pill.is--on{background:var(--color-dark);color:var(--color-light);border-color:var(--color-dark)}
@media (min-width:992px){.footer-link__col{width:auto;max-width:none;flex:none}.footer-link__col-li>a,.footer-link__col-li>button,.footer-link__col-top h4{white-space:nowrap}}
.anv-fi{display:flex;flex-direction:column}.anv-fi>.anv-tile{flex:1}.anv-fi[hidden]{display:none}
@media (max-width:991px){.anv-glance{grid-template-columns:1fr}}
@media (max-width:767px){.anv-glance__goal{min-height:18em}.anv-glance__info dl{grid-template-columns:1fr;gap:.3em}.anv-glance__info dd{margin-bottom:.8em}.anv-kpis li{font-size:1.1em}}
</style>"""

FORM_JS = """<script id="anv-forms">
(function(){if(window.__anvForms)return;window.__anvForms=1;
document.addEventListener('submit',function(e){var f=e.target.closest&&e.target.closest('form.anv-form');if(!f)return;e.preventDefault();
if(!f.checkValidity()){f.reportValidity();return}
/* TODO: send the form data to your form service / CRM here */
f.classList.add('is--sent');},true);
function prefill(){var p=new URLSearchParams(location.search).get('plan');var s=document.querySelector('form.anv-form select[name=plan]');if(p&&s){s.value=p}}
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-copy]');if(!b)return;var v=b.getAttribute('data-copy');var done=function(){var l=b.querySelector('.anv-sw__chip .eyebrow');if(l){l.textContent='Copied '+v;setTimeout(function(){l.textContent='Copy'},1400)}b.classList.add('is--copied');setTimeout(function(){b.classList.remove('is--copied')},1400)};if(navigator.clipboard){navigator.clipboard.writeText(v).then(done,done)}else{done()}});
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-filter]');if(!b)return;var f=b.getAttribute('data-filter');b.parentNode.querySelectorAll('[data-filter]').forEach(function(x){x.classList.toggle('is--on',x===b)});document.querySelectorAll('.anv-fi').forEach(function(t){t.hidden=!(f==='all'||t.getAttribute('data-cat')===f)});if(window.ScrollTrigger)ScrollTrigger.refresh()});
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
                   [CALL(), btn("See detailed industry examples", "/example-approaches", "neutral-200")])
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

# ------------------------------------------------------------------ brand guidelines
_mark_path = re.search(r' d="([^"]+)"', open(os.path.join(SITE, "images", "anvora-mark.svg"), encoding="utf-8").read()).group(1)
def MARK(color="currentColor", w="100%"):
    return f'<svg viewBox="0 0 1426 1320" width="{w}" aria-label="Anvora logo mark"><path fill="{color}" d="{_mark_path}"/></svg>'
_wm = re.search(r'<svg[^>]*class="nav-logo__wordmark-svg"[^>]*>.*?</svg>', home, flags=re.S)
WORDMARK = re.sub(r' class="[^"]*"', "", _wm.group(0)) if _wm else "<strong>anvora</strong>"

def _lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)
def rgb(h): return ", ".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))

BRAND_COLORS = [
    ("Anvora Purple", "#6840FF", "--color-purple", "Primary accent. Key actions, highlights, stat tiles."),
    ("Electric Lime", "#A1FF62", "--color-electric", "Energy accent. Main call-to-action buttons, numbers on dark."),
    ("Signal Coral", "#F84131", "--color-coral", "Use sparingly for urgency or a single highlight per page."),
    ("Ink", "#201D1D", "--color-dark", "Primary text and dark sections."),
    ("Paper", "#F4F4F4", "--color-light", "Default page background."),
    ("White", "#FFFFFF", "--color-white", "Cards, forms and surfaces on Paper."),
]
NEUTRALS = [("Neutral 300", "#EAEAEA", "--color-neutral-300"), ("Neutral 450", "#D8D8D8", "--color-neutral-450"),
            ("Neutral 500", "#817F7F", "--color-neutral-500"), ("Neutral 600", "#312E2E", "--color-neutral-600"),
            ("Neutral 700", "#2A2727", "--color-neutral-700"), ("Neutral 900", "#151313", "--color-neutral-900")]

def swatch(name, hx, var, use=None, big=True):
    fg = "#201D1D" if contrast(hx, "#201D1D") >= contrast(hx, "#FFFFFF") else "#FFFFFF"
    border = "box-shadow:inset 0 0 0 1px var(--color-neutral-450);" if hx in ("#FFFFFF", "#F4F4F4", "#EAEAEA") else ""
    u = f'<p class="p-s" style="opacity:.75;margin-top:.6em">{E(use)}</p>' if use else ""
    return (f'<button type="button" class="anv-sw{" is--big" if big else ""}" data-copy="{hx}" title="Click to copy {hx}">'
            f'<span class="anv-sw__chip" style="background:{hx};color:{fg};{border}"><span class="eyebrow">Copy</span></span>'
            f'<span class="anv-sw__info"><strong class="h-xs">{E(name)}</strong>'
            f'<span class="anv-sw__codes"><span>{hx}</span><span>RGB {rgb(hx)}</span><span>var({var})</span></span>{u}</span></button>')

def pair(bg, fg, label):
    r = contrast(bg, fg)
    grade = "AAA" if r >= 7 else "AA" if r >= 4.5 else "AA large" if r >= 3 else "Avoid"
    return (f'<div class="anv-pair" style="background:{bg};color:{fg}"><span class="h-s">Aa</span>'
            f'<span class="p-s">{E(label)}</span><span class="eyebrow">{r:.1f}:1 · {grade}</span></div>')

TYPE_SCALE = [("h-xxl", "Display XXL", "9.375em", "Haffer XH", "Hero statements"),
              ("h-xl", "Display XL", "7em", "Haffer XH", "Page titles"),
              ("h-l", "Heading L", "5em", "Haffer XH", "Section titles"),
              ("h-ml", "Heading ML", "3.875em", "Haffer XH", "Large callouts"),
              ("h-m", "Heading M", "2.5em", "Haffer XH", "Sub-sections"),
              ("h-s", "Heading S", "1.875em", "Haffer XH", "Card titles"),
              ("h-xs", "Heading XS", "1.25em", "Haffer VF", "Small titles, list headings"),
              ("p-l", "Body L", "1.1875em", "Haffer VF", "Intros and lead paragraphs"),
              ("p-m", "Body M", "1em", "Haffer VF", "Default body text"),
              ("p-s", "Body S", ".875em", "Haffer VF", "Captions and fine print"),
              ("eyebrow", "Label", ".6875em", "Haffer Mono", "Eyebrows, tags, metadata (uppercase)")]
type_rows = "".join(
    f'<div class="anv-ts"><div class="anv-ts__meta"><span class="eyebrow">{E(n)}</span><span class="p-s">.{c} · {s} · {E(f)}</span>'
    f'<span class="p-s anv-muted">{E(u)}</span></div><div class="{c} anv-ts__sample">Built to grow</div></div>'
    for c, n, s, f, u in TYPE_SCALE)

FONTS = [("Haffer XH", "Haffer XH,Arial,sans-serif", "Display", "Headlines and big statements. Tight letter-spacing (−0.03em to −0.06em), line-height around 1."),
         ("Haffer VF", "Haffer VF,Arial,sans-serif", "Text & UI", "Body copy, buttons and navigation. Variable font, weights 100–1000. Body uses about 420–430."),
         ("Haffer Mono", "Haffer Mono,Arial,sans-serif", "Labels", "Eyebrows, tags and data. Always uppercase at small sizes.")]
font_cards = "".join(
    f'<div class="anv-font"><span class="eyebrow anv-muted">{E(role)}</span><div style="font-family:{ff};font-size:6em;line-height:1;letter-spacing:-.04em">Aa</div>'
    f'<h3 class="h-s">{E(name)}</h3><p class="p-m anv-muted">{E(desc)}</p>'
    f'<p style="font-family:{ff};font-size:1.1em;line-height:1.5;word-break:break-all">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz<br>0123456789 € % &amp; @ ?</p></div>'
    for name, ff, role, desc in FONTS)

BTNS_LIGHT = [("Primary", "electric", "The main action on a page. One per view where possible."),
              ("Secondary", "purple", "Strong supporting actions."),
              ("Neutral", "neutral-200", "Low-emphasis actions, such as See pricing."),
              ("Dark", "neutral-800", "Actions on light cards that need weight."),
              ("Highlight", "coral", "Rare, attention-grabbing actions only.")]
btn_rows = "".join(f'<div class="anv-btnrow"><div class="anv-row">{btn(lbl, "#", v)}</div><div><strong class="p-m">{E(lbl)}</strong>'
                   f'<p class="p-s anv-muted">{E(d)} <code>variant="{v}"</code></p></div></div>' for lbl, v, d in BTNS_LIGHT)

SPACING = [("--gap-xxs", ".5em"), ("--gap-xs", ".75em"), ("--gap-s", "1em"), ("--gap-sm", "1.25em"), ("--gap-m", "1.5em"),
           ("--gap-l", "1.875em"), ("--gap-xl", "2em"), ("--gap-xxl", "2.5em"), ("--padding-xs", "3.75em"),
           ("--padding-s", "5em"), ("--padding-m", "7.5em"), ("--padding-l", "10em"), ("--padding-xl", "12.5em")]
space_rows = "".join(f'<div class="anv-space"><code>{t}</code><span class="p-s anv-muted">{v}</span><i style="width:var({t})"></i></div>' for t, v in SPACING)

VOICE = [("Clear over clever", "Say what we do and what it means for the client.", "We grow your leads with search and social ads.", "We leverage synergistic omnichannel paradigms."),
         ("Confident, not hype", "Back claims with process and numbers, never exaggeration.", "We test new ads every week and report what works.", "Guaranteed 10x results overnight!"),
         ("Honest", "Be upfront about what we know, what we don't, and what things cost.", "SEO usually takes three to six months to show results.", "Rank #1 on Google in days."),
         ("Human", "Write like a smart friend: warm, direct, short sentences.", "Tell us about your goals. We'll come back with ideas.", "Please submit your enquiry via the form below.")]
voice_cards = "".join(
    f'<div class="anv-card"><h3 class="h-s">{E(t)}</h3><p class="p-m">{E(d)}</p>'
    f'<div class="anv-do"><span class="eyebrow">Do</span><p class="p-m">{E(do)}</p></div>'
    f'<div class="anv-dont"><span class="eyebrow">Don\'t</span><p class="p-m">{E(dont)}</p></div></div>' for t, d, do, dont in VOICE)

def bsec(num, eyebrow, title, inner, dark=False, sub=None, sid=None):
    s = f'<p class="p-l anv-muted" style="max-width:36em;margin-top:1em">{E(sub)}</p>' if sub else ""
    return (f'<section id="{sid}" data-theme-section="{"dark" if dark else "light"}" class="anv-sec{" is--dark" if dark else ""}" style="scroll-margin-top:6em">'
            f'<div class="anv-wrap"><div class="anv-head"><span class="eyebrow">{num} — {E(eyebrow)}</span><h2 class="h-l">{E(title)}</h2>{s}</div>{inner}</div></section>')

TOC = [("logo", "Logo"), ("colour", "Colour"), ("type", "Typography"), ("buttons", "Buttons"), ("components", "Components"),
       ("spacing", "Spacing"), ("voice", "Tone of voice"), ("imagery", "Imagery & motion")]
toc = '<div class="anv-row" style="justify-content:center;margin-top:var(--gap-xxl)">' + "".join(
    f'<a href="#{i}" class="anv-pill" data-barba-prevent="">{E(t)}</a>' for i, t in TOC) + "</div>"

logo_sec = bsec("01", "Logo", "Our logo", (
    '<div class="anv-grid">'
    f'<div class="anv-logo c-light"><div class="anv-logo__mark">{MARK("#201D1D")}</div><span class="eyebrow">Mark on Paper</span></div>'
    f'<div class="anv-logo c-dark"><div class="anv-logo__mark">{MARK("#FFFFFF")}</div><span class="eyebrow">Mark on Ink</span></div>'
    f'<div class="anv-logo c-purple"><div class="anv-logo__mark">{MARK("#A1FF62")}</div><span class="eyebrow">Mark on Purple</span></div>'
    '</div>'
    f'<div class="anv-grid is--2" style="margin-top:var(--gap-s)"><div class="anv-logo c-light"><div class="anv-logo__wm" style="color:#201D1D">{WORDMARK}</div><span class="eyebrow">Wordmark</span></div>'
    f'<div class="anv-logo c-electric"><div class="anv-logo__lockup" style="color:#201D1D"><span>{MARK()}</span><span>{WORDMARK}</span></div><span class="eyebrow">Lockup: mark + wordmark</span></div></div>'
    '<div class="anv-grid" style="margin-top:var(--gap-s)">'
    '<div class="anv-card"><span class="eyebrow">Clear space</span><h3 class="h-s">Give it room</h3><p class="p-m">Keep empty space around the logo equal to at least half the height of the mark on every side.</p></div>'
    '<div class="anv-card"><span class="eyebrow">Minimum size</span><h3 class="h-s">Stay legible</h3><p class="p-m">Mark: at least 16px tall on screen (favicon). Wordmark: at least 80px wide.</p></div>'
    '<div class="anv-card"><span class="eyebrow">Don\'t</span><h3 class="h-s">Keep it intact</h3><p class="p-m">Don\'t stretch, rotate, outline, add shadows to, or recolour the logo outside the brand palette.</p></div>'
    '</div>'
    '<div class="anv-row" style="margin-top:var(--gap-l)">'
    f'{btn("Download mark (SVG)", "/images/anvora-mark.svg", "neutral-800")}{btn("Download favicon (SVG)", "/images/anvora-favicon.svg", "neutral-300")}</div>'),
    sid="logo")
logo_sec = logo_sec.replace('href="/images/anvora-mark.svg"', 'href="/images/anvora-mark.svg" download data-barba-prevent=""').replace(
    'href="/images/anvora-favicon.svg"', 'href="/images/anvora-favicon.svg" download data-barba-prevent=""')

colour_sec = bsec("02", "Colour", "Colour palette", (
    f'<div class="anv-grid">{"".join(swatch(*c) for c in BRAND_COLORS)}</div>'
    f'<h3 class="h-s" style="margin:var(--padding-xs) 0 1em">Neutrals</h3><div class="anv-grid is--6">{"".join(swatch(n, h, v, big=False) for n, h, v in NEUTRALS)}</div>'
    '<h3 class="h-s" style="margin:var(--padding-xs) 0 1em">Balance</h3>'
    '<div class="anv-ratio"><i style="flex:60;background:var(--color-light);color:var(--color-dark)">Paper 60%</i>'
    '<i style="flex:25;background:var(--color-dark);color:var(--color-light)">Ink 25%</i><i style="flex:8;background:var(--color-purple);color:#fff">Purple 8%</i>'
    '<i style="flex:5;background:var(--color-electric);color:var(--color-dark)">Lime</i><i style="flex:2;background:var(--color-coral)"></i></div>'
    '<h3 class="h-s" style="margin:var(--padding-xs) 0 1em">Accessible pairings</h3>'
    '<div class="anv-grid is--4">'
    + pair("#F4F4F4", "#201D1D", "Ink on Paper") + pair("#201D1D", "#A1FF62", "Lime on Ink") + pair("#6840FF", "#FFFFFF", "White on Purple")
    + pair("#A1FF62", "#201D1D", "Ink on Lime") + pair("#201D1D", "#F4F4F4", "Paper on Ink") + pair("#F84131", "#FFFFFF", "White on Coral")
    + pair("#FFFFFF", "#6840FF", "Purple on White") + pair("#F4F4F4", "#817F7F", "Neutral 500 on Paper") + '</div>'
    '<p class="p-s anv-muted" style="margin-top:1em">Contrast ratios follow WCAG 2.1. AA needs 4.5:1 for body text, or 3:1 for large text (24px+, or 19px+ bold).</p>'),
    sub="Click any colour to copy its hex code.", sid="colour")

type_sec = bsec("03", "Typography", "Typography", (
    f'<div class="anv-grid">{font_cards}</div>'
    f'<h3 class="h-s" style="margin:var(--padding-xs) 0 1em">Type scale</h3><div class="anv-tscale">{type_rows}</div>'
    '<p class="p-s anv-muted" style="margin-top:1em">Sizes are in em, relative to the page\'s base size, which scales with the screen width. '
    'Haffer is a commercial typeface: make sure Anvora holds a web licence before launch.</p>'),
    sid="type")

buttons_sec = bsec("04", "Buttons", "Buttons", (
    f'<div class="anv-btns">{btn_rows}</div>'
    '<div class="anv-onDark"><span class="eyebrow">On dark backgrounds</span><div class="anv-row" style="margin-top:1em">'
    f'{btn("Primary", "#", "electric")}{btn("Secondary", "#", "purple")}{btn("Subtle", "#", "neutral-600")}{btn("Ghost", "#", "light-10")}</div></div>'
    '<div class="anv-grid" style="margin-top:var(--gap-s)">'
    '<div class="anv-card"><span class="eyebrow">Labels</span><h3 class="h-s">Start with a verb</h3><p class="p-m">Book a strategy call, See pricing, Claim your audit. Keep it to 1–4 words.</p></div>'
    '<div class="anv-card"><span class="eyebrow">Hierarchy</span><h3 class="h-s">One primary</h3><p class="p-m">Use one Primary (Lime) button per section, next to at most one Neutral button.</p></div>'
    '<div class="anv-card"><span class="eyebrow">Motion</span><h3 class="h-s">Rolling labels</h3><p class="p-m">On hover the label rolls up and is replaced by a copy of itself. Hover the buttons above to see it.</p></div>'
    '</div>').replace('href="#"', 'href="#buttons" data-barba-prevent=""'),
    sid="buttons")

comp_sec = bsec("05", "Components", "Components", (
    '<div class="anv-grid">'
    f'<div><span class="eyebrow anv-muted">Tags</span><div style="margin-top:1em">{tags("Service 01", "Anvora")}</div>'
    '<span class="eyebrow anv-muted" style="display:block;margin-top:2em">Eyebrow</span><span class="eyebrow" style="margin-top:1em">What we do</span></div>'
    '<div class="anv-card"><span class="eyebrow">01</span><h3 class="h-s">Card</h3><p class="p-m">White surface on Paper, 0.75em radius, generous padding. For services, features and principles.</p></div>'
    '<div class="anv-stat" style="min-height:0"><span class="eyebrow">Stat tile</span><div><div class="h-xl">6</div><p class="p-m">Core services. Purple, Lime and Ink tiles rotate.</p></div></div>'
    '</div>'
    '<div class="anv-grid is--2" style="margin-top:var(--gap-s)">'
    '<form class="anv-form" onsubmit="return false"><label><span>Form field</span><input placeholder="Your name"></label>'
    '<label><span>Select</span><select><option>Starter</option><option>Growth</option></select></label>'
    '<div class="anv-chips"><label><input type="checkbox" checked> Selected chip</label><label><input type="checkbox"> Chip</label></div></form>'
    '<div><span class="eyebrow anv-muted">FAQ item</span><div class="anv-faq" style="margin-top:1em"><details open><summary class="h-xs">How long does SEO take?</summary>'
    '<p class="p-m">Most sites see meaningful movement within three to six months.</p></details><details><summary class="h-xs">Is ad spend included?</summary>'
    '<p class="p-m">No, ad spend is paid directly to the platforms.</p></details></div></div></div>'),
    sid="components")

space_sec = bsec("06", "Spacing", "Spacing & shape", (
    f'<div class="anv-split"><div class="anv-spacing">{space_rows}</div><div class="anv-grid is--2">'
    '<div class="anv-card" style="border-radius:.4em"><span class="eyebrow">Radius S · .4em</span><p class="p-m">Inputs and small buttons.</p></div>'
    '<div class="anv-card" style="border-radius:.75em"><span class="eyebrow">Radius M · .75em</span><p class="p-m">Cards, tiles and swatches.</p></div>'
    '<div class="anv-card" style="border-radius:1em"><span class="eyebrow">Radius L · 1em</span><p class="p-m">Large panels and forms.</p></div>'
    '<div class="anv-card" style="border-radius:2em"><span class="eyebrow">Pill · 2em</span><p class="p-m">Chips, tags and the navigation bar.</p></div>'
    '</div></div>'),
    sub="Spacing uses tokens so every page breathes the same way. Use the smallest token that separates ideas clearly.", sid="spacing")

voice_sec = bsec("07", "Tone of voice", "How we sound", f'<div class="anv-grid is--2">{voice_cards}</div>', sid="voice")

img_sec = bsec("08", "Imagery & motion", "Imagery & motion", (
    '<div class="anv-grid">'
    '<div class="anv-card c-light"><span class="eyebrow">Photography</span><h3 class="h-s">Real and close</h3><p class="p-m">Real people, real products and real workspaces. Natural light, close crops, no generic stock handshakes.</p></div>'
    '<div class="anv-card c-light"><span class="eyebrow">Graphics</span><h3 class="h-s">Bold and simple</h3><p class="p-m">Flat colour blocks from the palette, big numbers and clean UI-style mockups. Avoid gradients and 3D effects.</p></div>'
    '<div class="anv-card c-light"><span class="eyebrow">Motion</span><h3 class="h-s">Fast, then soft</h3><p class="p-m">Movement starts quickly and eases out (expo.out), lasting about 0.6–1.2 seconds. Text reveals line by line.</p></div>'
    '</div>'
    '<div class="anv-motion"><i></i></div>'), dark=True, sid="imagery")

brand_body = (hero("Brand", "Guidelines v1.0", "Brand guidelines",
                   "Everything you need to use the Anvora brand consistently: logo, colour, typography, buttons, components and tone of voice.")
              .replace("</div></section>", toc + "</div></section>", 1)
              + logo_sec + colour_sec + type_sec + buttons_sec + comp_sec + space_sec + voice_sec + img_sec)
write("/brand", page("brand", "Brand Guidelines", "The Anvora brand guidelines: logo, colours, fonts, buttons and tone of voice.", brand_body, cta=False))

# ------------------------------------------------------------------ example approach pages
SVC_NAME = {s["slug"]: s["name"] for s in SERVICES}
NOT_CLIENT = "Example approach · not a past client"

def approach_tile(a, big=False):
    return (f'<a href="/example-approaches/{a["slug"]}" class="anv-tile {a["color"]}"{" style=\"min-height:26em\"" if big else ""}>'
            f'<div class="anv-row" style="justify-content:space-between"><span class="eyebrow">{E(a["cat"])}</span><span class="eyebrow">Example approach</span></div>'
            f'<div><span class="eyebrow" style="opacity:.6">Goal</span><div class="h-m" style="margin:.3em 0 .6em">{E(a["goal"])}</div>'
            f'<div class="anv-row" style="justify-content:space-between;align-items:flex-end"><h3 class="h-xs">{E(a["name"])}</h3><span class="anv-arrow">→</span></div></div></a>')

def approach_page(a):
    i = APPROACHES.index(a)
    chips = "".join(f'<span class="anv-chip">{E(c)}</span>' for c in a["channels"])
    glance = section(
        f'<div class="anv-glance"><div class="anv-glance__goal {a["color"]}"><span class="eyebrow" style="opacity:.7">The goal</span>'
        f'<div><div class="h-l">{E(a["goal"])}</div><div class="anv-row" style="margin-top:1.4em">{chips}</div></div></div>'
        f'<div class="anv-glance__info"><dl>'
        f'<dt>Business type</dt><dd>{E(a["name"])}</dd>'
        f'<dt>Category</dt><dd>{E(a["cat"])}</dd>'
        f'<dt>Main channels</dt><dd>{E(", ".join(a["channels"]))}</dd>'
        f'<dt>First plan</dt><dd>90 days, reviewed every month</dd></dl>'
        f'<p class="anv-note">This is an example of how we would approach this type of business. It is not a past client, and the numbers we track depend on your starting point.</p>'
        f'</div></div>')
    chal = "".join(f'<li><span>{n+1:02d}</span><p class="p-l">{E(t)}</p></li>' for n, t in enumerate(a["situation"]))
    situation = section(f'<div class="anv-split"><div><span class="eyebrow anv-muted">The starting point</span>'
                        f'<h2 class="h-l" style="margin-top:.4em">Typical challenges</h2>'
                        f'<p class="p-l anv-muted" style="margin-top:1em;max-width:22em">What we often see with this type of business before marketing starts working.</p></div>'
                        f'<ol class="anv-chal">{chal}</ol></div>')
    aud = section(head("Audience", "Who we’d focus on") + cards(a["audiences"]), dark=True)
    ph = "".join(f'<div class="anv-step"><span class="eyebrow anv-muted">{E(w)}</span><span class="h-l">{n+1:02d}</span>'
                 f'<h3 class="h-s">{E(t)}</h3><p class="p-m">{E(d)}</p></div>' for n, (w, t, d) in enumerate(a["phases"]))
    plan = section(head("The plan", "The first 90 days", "A step-by-step plan. We review results every month and adjust as we learn.")
                   + f'<div class="anv-steps anv-phases">{ph}</div>')
    tac = section(head("Tactics", "What we’d do") + cards(a["tactics"]), dark=False)
    top, hl, txt, cta = a["ad"]
    fmt, idea = a["post"]
    olab, otxt = a["offer"]
    samples = section(head("Sample ideas", "What it could look like", "Example copy written for this page, to show the direction we would take.")
        + '<div class="anv-grid">'
        + f'<div class="anv-mock is--white"><span class="eyebrow anv-muted">Sample ad</span><div class="anv-ad"><div class="anv-ad__top"><i></i><span>Your business<br><small>{E(top)}</small></span></div>'
          f'<h4>{E(hl)}</h4><p>{E(txt)}</p><span class="anv-ad__cta">{E(cta)}</span></div></div>'
        + f'<div class="anv-mock {a["color"] if a["color"] not in ("c-light",) else "c-purple"}"><span class="eyebrow" style="opacity:.7">{E(fmt)}</span>'
          f'<div class="anv-mock__play">▶</div><p class="h-xs">{E(idea)}</p></div>'
        + f'<div class="anv-mock c-dark"><span class="eyebrow" style="opacity:.7">{E(olab)}</span><p class="h-s" style="margin-top:auto">“{E(otxt)}”</p></div>'
        + '</div>')
    kp = "".join(f'<li><span>{n+1:02d}</span>{E(k)}</li>' for n, k in enumerate(a["kpis"]))
    sv = "".join(f'<a class="anv-pill" href="/services/{s}" data-barba-p="">{E(SVC_NAME[s])} →</a>' for s in a["services"])
    measure = section(f'<div class="anv-split"><div><span class="eyebrow anv-muted">Measurement</span>'
                      f'<h2 class="h-l" style="margin-top:.4em">What we’d measure</h2>'
                      f'<p class="p-l anv-muted" style="margin-top:1em;max-width:24em">Clear numbers, reported every month in plain language, including what did not work.</p>'
                      f'<div style="margin-top:var(--gap-xxl)"><span class="eyebrow anv-muted">Services involved</span><div class="anv-row" style="margin-top:1em">{sv}</div></div></div>'
                      f'<ol class="anv-kpis">{kp}</ol></div>')
    more = [APPROACHES[(i + k) % len(APPROACHES)] for k in (1, 2, 3)]
    related = section(head("More examples", "Other example approaches")
                      + f'<div class="anv-grid">{"".join(approach_tile(m) for m in more)}</div>'
                      + f'<div class="button-row" style="margin-top:var(--gap-xxl);justify-content:center">{btn("View all approaches", "/example-approaches", "neutral-200")}</div>')
    body = (hero("Example approach", a["cat"], a["name"], a["intro"],
                 [btn("Start a similar project", "/contact", "electric"), btn("Get a free audit", "/audit", "neutral-200")])
            + glance + situation + aud + plan + tac + samples + measure + related)
    return page("approach-" + a["slug"], f'Marketing for a {a["name"][0].lower() + a["name"][1:]}' if not a["name"].startswith("B2B") else "Marketing for a B2B software startup",
                f'An example of how Anvora would approach marketing for a {a["name"].lower()}.', body)

for a in APPROACHES:
    write(f'/example-approaches/{a["slug"]}', approach_page(a))

_cats = []
for a in APPROACHES:
    if a["cat"] not in _cats: _cats.append(a["cat"])
filters = '<button class="anv-pill is--on" data-filter="all">All</button>' + "".join(
    f'<button class="anv-pill" data-filter="{E(c)}">{E(c)}</button>' for c in _cats)
grid = "".join(f'<div class="anv-fi" data-cat="{E(a["cat"])}">{approach_tile(a)}</div>' for a in APPROACHES)
ex_body = (hero("Example Approaches", f'{len(APPROACHES)} industries', "How we’d approach your business",
                "Step-by-step examples of how Anvora would plan marketing for different types of businesses, from a local coffee shop to a roofing company. These are examples, not past clients.",
                [CALL(), btn("Get a free audit", "/audit", "neutral-200")])
           + section(f'<div id="industries" style="scroll-margin-top:8em"></div>' + head("Industries", "Pick a business like yours")
                     + f'<div class="anv-row anv-filters" style="margin-bottom:var(--gap-l)">{filters}</div>'
                     + f'<div class="anv-grid">{grid}</div>')
           + section(head("Inside every approach", "What each example covers") + cards([
                 ("Typical challenges", "The problems we usually see with this type of business before marketing starts working."),
                 ("Who to reach", "The main customer groups, and what each of them needs to hear."),
                 ("A 90-day plan", "Four clear phases, from fixing the foundations to growing reach."),
                 ("Tactics", "The specific actions we would take, and why they fit this business."),
                 ("Sample ideas", "Example ads, posts and messages to show the direction we would take."),
                 ("What we’d measure", "The numbers that show whether the plan is working.")]), dark=True)
           + section(f'<div class="anv-split"><div><span class="eyebrow anv-muted">Don’t see yours?</span>'
                     f'<h2 class="h-l" style="margin-top:.4em">Every business is different</h2></div><div>'
                     f'<p class="p-l">These examples show how we think. Your plan will be built around your goals, your customers and your budget.</p>'
                     f'<p class="p-l">Tell us about your business and we will send you a short, honest view of where we would start.</p>'
                     f'<div class="button-row" style="margin-top:var(--gap-xxl)">{CALL()}{btn("Get a free audit", "/audit", "neutral-200")}</div></div></div>')
           + FOUNDING)
write("/example-approaches", page("example-approaches", "Example Approaches", "Examples of how Anvora would approach marketing for different types of businesses.", ex_body))

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
