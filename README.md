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
- `tools/`: the scripts used to generate the pages
