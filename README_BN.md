# Telegram Auto Reaction Bot (বাংলা)

এই প্রকল্পটি Telegram চ্যানেলের নতুন পোস্টে এলোমেলো ❤️ 🔥 👍 😍 রিয়াকশন দেওয়ার জন্য Telegram Bot API ব্যবহার করে। GitHub Actions প্রতি ৫ মিনিটে চালু হয়ে জমে থাকা নতুন পোস্টগুলো পরীক্ষা করবে। এটি ২৪/৭ স্থায়ী সার্ভার নয়; সময়মতো রিয়াকশন নিশ্চিত নয়।

## ১) Telegram Bot তৈরি

1. Telegram-এ `@BotFather` খুলুন।
2. `/newbot` পাঠিয়ে নির্দেশনা অনুসরণ করুন।
3. BotFather যে bot token দেবে, সেটি গোপন রাখুন। কাউকে পাঠাবেন না।
4. আপনার চ্যানেলে বটকে **Administrator** করুন। অনুমতি দেওয়ার পরও যদি রিয়াকশন না হয়, চ্যানেলের Reaction Settings এবং Telegram API-এর ত্রুটি পরীক্ষা করুন।

## ২) API credential ও channel ID

1. `https://my.telegram.org` খুলে আপনার Telegram অ্যাকাউন্টে লগইন করুন।
2. **API development tools** থেকে `api_id` ও `api_hash` নিন—এই Bot API সংস্করণে এগুলো লাগে না; ভবিষ্যতে user-account পদ্ধতি ব্যবহার করলে প্রয়োজন হতে পারে।
3. চ্যানেল public হলে `CHANNEL_ID` হিসেবে `@YourChannelUsername` দিন। Private channel-এর numeric ID দরকার হলে Telegram থেকে সঠিক ID বের করুন; অনুমান করে লিখবেন না।

## ৩) GitHub repository তৈরি

1. GitHub অ্যাপে নতুন repository তৈরি করুন, যেমন `telegram-auto-reaction-bot`।
2. ZIP-এর ফাইলগুলো repository-এর root-এ upload/extract করুন। নিশ্চিত করুন `bot.py` root-এ এবং `.github/workflows/auto-reaction.yml` সঠিক জায়গায় আছে।
3. Repository-এর **Settings → Secrets and variables → Actions** খুলুন।

### Repository secrets তৈরি করুন

**Secrets → New repository secret**-এ নিচের তিনটি secret যোগ করুন:

- `BOT_TOKEN` — BotFather-এর token
- `CHANNEL_ID` — `@YourChannelUsername` অথবা সঠিক numeric channel ID
- `GH_TOKEN` — GitHub Personal Access Token (classic) অথবা fine-grained token, যার ওই repository-তে **Actions variables read/write** অনুমতি আছে

`GH_TOKEN` তৈরির সময় যত কম সম্ভব অনুমতি দিন। এটি repository variable `TELEGRAM_UPDATE_OFFSET` তৈরি/আপডেট করে যাতে একই পুরোনো পোস্ট বারবার প্রক্রিয়া না হয়। Token-টি কখনও কোডে লিখবেন না।

## ৪) Actions চালু করা

1. Repository-এর **Actions** tab খুলুন।
2. Workflow অনুমোদন/Enable করার বোতাম থাকলে সেটি চাপুন।
3. **Telegram Auto Reaction → Run workflow** চাপুন।
4. রান শেষ হলে লগ দেখুন। `Could not react` বা API error থাকলে সেটি অনুসারে বটের অনুমতি, channel ID ও reaction settings ঠিক করুন।

## গুরুত্বপূর্ণ সীমাবদ্ধতা

- GitHub Actions schedule প্রায়ই দেরি করতে পারে; পাঁচ মিনিট ঠিক সময়ের নিশ্চয়তা নয়।
- GitHub Actions স্থায়ী background process নয়। সত্যিকারের তাৎক্ষণিক ও নিরবচ্ছিন্ন বটের জন্য দীর্ঘসময় চলা host/VPS ব্যবহার করুন।
- BotFather token বা `GH_TOKEN` কারও সঙ্গে শেয়ার করবেন না। ভুল করে প্রকাশ করলে সঙ্গে সঙ্গে revoke/rotate করুন।
- প্রথমবার offset variable না থাকলে বট পুরোনো আপডেট এড়িয়ে শুরু করবে; এরপর নতুন channel post প্রক্রিয়া করবে।
- Bot API, channel permissions, অথবা channel-এর reaction settings রিয়াকশন প্রত্যাখ্যান করলে বট সেটি লগে দেখাবে; জোর করে বাইপাস করে না।
