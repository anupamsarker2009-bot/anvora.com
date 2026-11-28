# anvora.com

Website for **Anvora**, a full-service marketing company.

## Pages

| Page | Path |
| --- | --- |
| Home | `/` |
| Services | `/services/brand-strategy/`, `/services/performance-marketing/`, `/services/social-media/`, `/services/content-studio/`, `/services/seo-growth/`, `/services/web-landing-pages/` |
| Our Approach | `/approach/` |
| Example Plans | `/example-plans/` |
| Example Approaches (12 industries) | `/example-approaches/` and `/example-approaches/<industry>/` (coffee-shop, roofing-company, dental-clinic, plumbing-heating, hair-salon, real-estate-agent, law-firm, fitness-studio, online-clothing-brand, saas-startup, restaurant, wedding-photographer) |
| Pricing | `/pricing/` |
| Contact | `/contact/` |
| Free Audit | `/audit/` |
| Insights | `/insights/` |
| FAQs | `/faq/` |
| Brand Guidelines | `/brand/` |
| Social Media Posts (24 downloadable JPGs: 12 new, 12 posted) | `/social-media-posts/` |
| Instagram Stories (12 downloadable JPGs, 1080 × 1920) | `/instagram-stories/` |
| Scripts for Instagram (12 faceless Reel scripts, .txt downloads) | `/instagram-scripts/` |
| Storyboarding for SaaS (12 storyboards, 16:9 frames, private) | `/storyboarding-for-saas/` |
| Marketing Funnels (guide with examples and calculator, private) | `/marketing-funnels/` |
| Animation (flowing ribbons + gradient photo transition, video export, public) | `/animation/` |
| Greek Mythology (the full story, 14 parts, 95 chapters) | `/greek-mythology/` |
| Ownership (public: who owns Anvora) | `/ownership/` |
| Legal | `/legal/privacy-policy/`, `/legal/terms-and-conditions/`, `/legal/cookie-policy/`, `/legal/licensing-agreement/` |

## Run it on your computer

The site must be served from the root of a web address (links like `/pricing/` start with `/`).
With Python installed, open a terminal in this folder and run:

```
python -m http.server 8765
```

Then open http://localhost:8765

## Before going live

- Connect the contact and audit forms to a form service (search for `TODO` in the pages).
- Replace placeholder images, video and fonts that came from the original template.
- Replace the placeholder email, phone number and prices.
- Have the legal pages reviewed.

## Folder guide

- `index.html` and the page folders: the website
- `css/`, `js/`, `fonts/`, `images/`: styles, scripts, fonts and images
- `js/anvora-lock.js`: unlocks the private pages in the browser

## Private pages

Brand Guidelines, Social Media Posts, Instagram Stories, Scripts for Instagram, Storyboarding for SaaS, Marketing Funnels and Greek Mythology are password protected. Their content is encrypted (AES-256-GCM, key derived from the password with PBKDF2-SHA256), so it can't be read from the page source without the password. Once unlocked, other private pages open without asking again until the browser tab is closed.

The build scripts are kept outside this public repository, because they contain the private pages' text. The password is never stored in any file.
