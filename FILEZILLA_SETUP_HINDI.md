# Ek folder se FileZilla upload

## Local folder — sirf yahi use karo

`/home/shyam/Documents/Work/newstartailor/`

## Server folder

`/domains/itgurujan.com/public_html/newstartailor/`

1. Current server folder ki files ka backup download karke rakho.
2. Local `newstartailor` ke **andar ki saari files aur folders** server ke upar
   wale folder mein upload karo. Extra `newstartailor/newstartailor` nesting mat banao.
3. Hidden `.env`, root `.htaccess`, `public/.htaccess` aur private directory
   `.htaccess` files bhi transfer karo. Failed transfers zero honi chahiye.
4. `vendor/` poora transfer karo; Composer server par chalana nahi hai.
5. Agar pichhle package ka root `assets/`, `static/`, `sw.js`,
   `.user.ini`, `robots.txt` ya `newstartailor-app/` server par maujood hai,
   backup ke baad un purane items ko hatao. Root `index.php` ko naye wale se replace karo. Naye project mein ye public files
   `public/` mein hain. Apni existing uploaded reference photos/storage ko delete
   mat karna; purane private storage ki photos ko naye `storage/app/private/references/`
   mein preserve karo. Existing `.env`/APP_KEY ko preserve karo.
6. Database pehle import ho chuka hai: SQL dobara import NAHI karna.
7. PHP 8.3.36, SSL aur HTTPS enabled rakho. `storage/` aur `bootstrap/cache/`
   writable hon (directories 755/775, files 644; 777 nahi).
8. Main site `https://newstartailor.itgurujan.com` kholo.
9. First admin ke liye `/setup` kholo; private `.env` ka `NST_SETUP_KEY` use karo.
   Admin pehle se hai toh `/admin/login` use karo.

## Final server layout

```text
/domains/itgurujan.com/public_html/newstartailor/
├── .env
├── .htaccess
├── index.php                  (shared-hosting entry point)
├── artisan
├── composer.json
├── composer.lock
├── app/
├── bootstrap/
├── config/
├── database/
├── public/
│   ├── index.php
│   ├── .htaccess
│   ├── static/
│   └── assets/
├── resources/views/
├── routes/
├── storage/
└── vendor/
```

Laravel views `resources/views` mein hain. Root `index.php` Laravel ke `public/index.php` ko load karta hai aur `.htaccess`
public assets ki location handle karta hai; browser URL mein `/public` add mat karo. Private source,
`.env` aur storage HTTP access se blocked hain. Uploaded photos Laravel's
authenticated routes se hi milti hain. `.htaccess` skip mat karna.

Database details `.env` mein set hain. Password/APP_KEY ko Git ya chat mein share
mat karna. Future uploads mein existing `.env`, `storage` aur photos preserve karo.

Check: `/services`, `/about`, `/contact`, `/customer/login`, `/healthz`.
Browser mein `/.env`, `/composer.lock`, `/vendor/autoload.php` aur
`/resources/views/layouts/app.blade.php` par 403 milna chahiye.
Agar 500/503 aaye toh private `storage/logs/laravel.log` dekho aur PHP extensions,
database credentials aur file permissions check karo; APP_DEBUG=false hi rakho.

Real payment gateway/SMS credentials configured nahi hain; online payments
manual verification aur notifications queue ke existing behavior par hain.
