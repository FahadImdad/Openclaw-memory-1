# Lead Generation Tool — Complete Research

**Client:** Suleman  
**Requirement:** 15,000+ leads/month with Name, Email, Phone, Source, Status  
**Budget:** Client pays API costs directly

---

## 🎯 APPROACHES COMPARISON

### **APPROACH 1: B2B Database (Recommended)**
Pull verified contacts from existing databases with industry/job filters.

| Tool | Plan | Monthly Cost | Credits | Best For |
|------|------|-------------|---------|----------|
| **Snov.io** | Pro M | $189 | 20,000 | Best single-user value |
| **Hunter.io** | Growth | $104/mo (annual) | 10,000 | Email finder + sequences |
| **Apollo.io** | Professional | ~$99/user | 24K/year | Full database, but seat minimums |
| **Icypeas** | Varies | 3-10x cheaper | Varies | Cheapest email enrichment |

**Verdict:** Snov.io Pro M wins for 15K leads/month with 1 user.

---

### **APPROACH 2: LinkedIn Scraping + Email Finder**
Scrape LinkedIn profiles → enrich with email finder.

| Tool | Purpose | Cost |
|------|---------|------|
| **Phantombuster** | LinkedIn automation | ~$56-128/mo |
| **Snov.io Email Finder** | Find emails from names | Included in plan |
| **Hunter.io** | Find emails from domain | $34-104/mo |

**Pipeline:**
1. Scrape LinkedIn profiles with keywords (Phantombuster)
2. Pass name + company to Snov.io/Hunter
3. Get verified email
4. Store in Supabase

**Pros:** Higher intent (people actively posting)  
**Cons:** Lower volume, LinkedIn rate limits, legal grey area

---

### **APPROACH 3: Social Media Intent Scraping**
Find posts about needing services, then reach out.

| Platform | Scraper Option | Email Extraction |
|----------|----------------|------------------|
| Twitter/X | Apify Twitter Scraper ($0.25-5/1K) | ❌ Rarely in posts |
| Facebook | Apify FB Scraper | ❌ Rarely public |
| Instagram | Apify IG Scraper | ❌ Rarely public |
| Reddit | Apify Reddit Scraper | ❌ No emails |
| Google | SerpAPI / Google Search API | Links to websites only |

**The Problem:** Social posts don't include verified emails. You get:
- Post content ✓
- Username ✓
- Profile link ✓
- Email ❌ (need second step)

**Verdict:** Not practical for 15K verified emails/month.

---

### **APPROACH 4: Google Search + Website Scraping**
Search for intent queries → scrape contact pages.

**Pipeline:**
1. Search: "looking for book publisher" or "need website developer"
2. Get URLs (forum posts, business sites)
3. Scrape contact page for emails
4. Verify with email verifier

**Tools:**
- SerpAPI: $50/mo for 5K searches
- Apify Website Scraper: Pay per compute
- Hunter Email Verifier: 0.5 credit per verification

**Pros:** Can find real intent signals  
**Cons:** Very low hit rate, manual cleanup needed

---

### **APPROACH 5: Form/Contest Leads (Different Model)**
Run lead magnets (free ebooks, webinars) → collect emails directly.

**Not applicable** — client wants to find existing demand, not create it.

---

## 💰 DETAILED PRICING

### Snov.io (Recommended)
| Plan | Credits | Recipients | Price/mo |
|------|---------|------------|----------|
| Trial | 50 | 100 | Free |
| Starter | 1,000 | 5,000 | $39 |
| Pro S | 5,000 | 10,000 | $99 |
| **Pro M** | **20,000** | **30,000** | **$189** |
| Pro L | 50,000 | 50,000 | $369 |
| Pro XL | 100,000 | 100,000 | $738 |

**Credit Usage:**
- 1 credit = 1 email found OR 1 email verified
- Bulk operations included
- API access on paid plans

---

### Hunter.io
| Plan | Credits/mo | Price/mo (annual) |
|------|-----------|-------------------|
| Free | 50 | $0 |
| Starter | 2,000 | $34 |
| Growth | 10,000 | $104 |
| Scale | 25,000 | $209 |

**Credit Usage:**
- 1 credit = 1 email found
- 0.5 credit = 1 email verified

---

### Apollo.io
- Professional: $99/user/mo (24K credits/year) — needs 3 seat minimum for Organization
- Credits used for exports/reveals, not database access
- Unlimited records viewing, but export costs credits

**Warning:** Apollo's pricing is confusing. "Unlimited" plans have fair-use caps.

---

### Apify (Social Scrapers)
| Plan | Prepaid/mo | Compute Unit Cost |
|------|-----------|-------------------|
| Free | $5 | $0.30/CU |
| Starter | $29 | $0.30/CU |
| Scale | $199 | $0.25/CU |

**Actor Examples:**
- Twitter Scraper: ~$0.50-5 per 1K tweets
- LinkedIn Scraper: ~$1-3 per 1K profiles
- Facebook Scraper: ~$0.50-2 per 1K posts

---

### Lusha
- Credit-based: 1 email = 1 credit, 1 phone = 10 credits
- Free: 70 credits/mo
- Paid plans: Contact sales (expensive)

---

### Kaspr (Expensive)
- €0.20-0.35 per credit for add-ons
- Best for LinkedIn enrichment
- Not cost-effective for 15K/month

---

## ✅ FINAL RECOMMENDATION

### For 15K Leads/Month with Verified Emails:

**Primary: Snov.io Pro M @ $189/mo**
- 20,000 credits (enough for 15K finds + verification buffer)
- Full B2B database with filters
- REST API for integration
- Email verification included
- No seat minimum

### Build Stack:
```
┌─────────────────┐
│   Next.js UI    │ ← Fahad builds
├─────────────────┤
│   Snov.io API   │ ← $189/mo (client pays)
├─────────────────┤
│    Supabase     │ ← Free tier (dedup, storage)
├─────────────────┤
│     Vercel      │ ← Free hosting
└─────────────────┘
```

### Filters to Approximate "Intent":
Since social intent scraping isn't viable, use these B2B filters:
- **Job Titles:** Authors, Self-published writers, Small business owners, Startup founders
- **Industries:** Publishing, Professional services, E-commerce
- **Company Size:** 1-50 employees (likely need outsourced services)
- **Location:** US, UK, Canada, Australia
- **Technologies:** Outdated CMS (need web dev), No website (need web dev)

---

## 🚫 WHAT WON'T WORK

1. **Social media scraping → verified emails**: Posts don't contain emails
2. **15K high-intent leads from Twitter/FB**: Volume not achievable
3. **Scraping without verification**: High bounce rates, spam folders
4. **Phone numbers from social**: Almost never public

---

## 📋 NEXT STEPS FOR CLIENT

1. **Confirm approach:** B2B database (Snov.io) is the only scalable path
2. **Sign up for Snov.io Pro M** ($189/mo) — can start with trial
3. **Define target filters:** Job titles, industries, locations
4. **Fahad builds the tool:** Next.js + Snov.io API + Supabase
5. **Client pays:** $189/mo Snov.io + Fahad's $200-300 build fee

---

*Research completed: 2026-03-08*
