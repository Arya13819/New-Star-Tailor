# Laravel website ko FileZilla se live kaise karein

Website: **https://newstartailor.itgurujan.com**
PHP: **8.3.36** — Laravel 13 ki minimum requirement 8.3 hai.

Is ZIP mein Laravel + `vendor` dependencies + website assets sab included hain.
Server par Composer, Node.js ya SSH command chalana zaroori nahi hai.

## 1. ZIP apne computer par extract karo

`New-Star-Tailor-Laravel-Hostinger.zip` extract karne par yeh milega:

```text
newstartailor-app/             <- private Laravel application + vendor + .env
public_html/newstartailor/     <- public website files + index.php + .htaccess
DATABASE_IMPORT.sql           <- MySQL/phpMyAdmin import file
START-HERE-HINDI.md            <- yeh instructions
```

ZIP mein is deployment ke liye fresh APP_KEY aur NST_SETUP_KEY private `.env`
mein generate kiye gaye hain. Yeh keys Git/source code mein nahi hain. ZIP aur
`.env` ko private rakho. Database password ya admin password supplied nahi hai.

## 2. Purani website ka backup lo

FileZilla se current `public_html/newstartailor` folder download karke backup rakho.
Agar existing database mein data hai toh phpMyAdmin se export bhi kar lo.
`health`, `themes` ya main `public_html/index.php` ko replace mat karo.

## 3. MySQL database banao aur SQL import karo

hPanel mein **Databases → MySQL Databases**:

1. Is website ke liye **naya empty database** aur database user banao.
2. Full prefixed database name aur username note karo, jaise
   `u990876325_nst` (actual naam hPanel se lena).
3. Us database ka phpMyAdmin kholo → **Import**.
4. Extracted ZIP ka `DATABASE_IMPORT.sql` choose karke import karo.

Is SQL mein services/prices aur required tables hain; koi admin/customer login ya
sample orders nahi hain. Existing database par full SQL dobara import mat karna.
Agar purana New Star Tailor database migrate karna hai toh pehle developer guide
padho aur backup rakho.

## 4. Private `.env` edit karo — upload se pehle

Computer par extracted `newstartailor-app/.env` text editor mein kholo. Sirf actual
MySQL values fill karo:

```dotenv
APP_ENV=production
APP_DEBUG=false
APP_URL=https://newstartailor.itgurujan.com

DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=u990876325_YOUR_DATABASE
DB_USERNAME=u990876325_YOUR_USER
DB_PASSWORD="YOUR_DATABASE_PASSWORD"

SESSION_DRIVER=file
SESSION_SECURE_COOKIE=true
CACHE_STORE=file
QUEUE_CONNECTION=sync
```

- DB_HOST ka actual hostname hPanel mein jo ho wahi use karo.
- DB password **database user ka password** hai, FTP ka password nahi.
- `APP_KEY` ko generated value par rehne do.
- `NST_SETUP_KEY` ki generated value note karo; admin banane ke liye chahiye.
- `.env` mein passwords/keys kisi ko chat mein mat bhejna.

## 5. FileZilla mein sahi do folders upload karo

Remote/server side par **itgurujan.com ke domain folder** tak jao:

`/home/u990876325/domains/itgurujan.com/`

FTP mein home folder chroot ho toh yeh `domains/itgurujan.com/` ya uske equivalent
path ke naam se dikh sakta hai. Final structure yeh hona chahiye:

```text
/home/u990876325/domains/itgurujan.com/
├── newstartailor-app/
│   ├── .env
│   ├── app/
│   ├── bootstrap/
│   ├── config/
│   ├── resources/
│   ├── storage/
│   └── vendor/
└── public_html/
    ├── health/                     (isko touch nahi karna)
    ├── themes/                     (isko touch nahi karna)
    └── newstartailor/
        ├── index.php
        ├── .htaccess
        ├── .user.ini
        ├── static/
        ├── assets/
        └── sw.js
```

**Upload order:**

1. Local `newstartailor-app` folder ko remote domain folder mein upload karo.
2. Local `public_html/newstartailor` ke **andar ki files** remote
   `public_html/newstartailor` mein upload karo.
3. FileZilla ke **Failed transfers** tab mein koi file pending nahi honi chahiye.
4. `.env` aur `.htaccess` upload honi chahiye. Hidden files dekhne ke liye
   FileZilla mein **Server → Force showing hidden files** check karo.
5. `storage` aur `bootstrap/cache` writable hone chahiye. Zaroorat ho toh folders
   ke permissions 755/775 rakho, files 644. 777 mat lagana.
6. hPanel mein is subdomain ka SSL aur Force HTTPS on rakho.

Agar FTP account sirf `public_html` tak restricted hai aur domain folder tak nahi
ja sakte, main FTP account use karo ya hPanel File Manager se private
`newstartailor-app` folder upload karo. Pura Laravel project public website folder
ke andar upload mat karna. Public index already is private path ke liye configured
hai; uska path badalne ki zaroorat nahi jab structure upar jaisa ho.

## 6. Admin account banao

Browser mein kholo:

`https://newstartailor.itgurujan.com/setup`

`.env` ka `NST_SETUP_KEY`, apna naam, email, mobile aur naya password enter karo.
Account banne ke baad setup page automatic lock ho jayega. Phir login:

`https://newstartailor.itgurujan.com/admin/login`

Admin banne ke baad `.env` mein `NST_SETUP_KEY=` blank kar sakte ho.
Koi default admin password nahi diya gaya hai.

## 7. Website check karo

- Main site: `https://newstartailor.itgurujan.com`
- Services: `/services`
- Customer signup: `/customer/register`
- Customer login: `/customer/login`
- Order tracking: `/track-order`
- About/Contact maps: `/about`, `/contact`
- Basic health: `/healthz`
- MySQL health: `/api/health`

Ek customer account aur test order banao. Admin se status update karo aur customer
tracking mein check karo. Cash/UPI payments record hote hi verified hain; online
references manually verify hone tak pending rehte hain. Real online gateway/SMS
provider abhi configured nahi hai.

`.env`, `vendor`, private photos aur app source website URL se download nahi hone
chahiye. Inki correct location public_html ke bahar hai.

## Agar problem aaye

- **404 on /setup or /services**: public folder aur `.htaccess` ki location check
  karo; extra nested `newstartailor/newstartailor` folder na ban gaya ho.
- **500 before homepage**: `vendor` poora upload hua hai ya nahi, PHP version aur
  extensions check karo. PHP mein Ctype, cURL, DOM, Fileinfo, Filter, Hash,
  Mbstring, OpenSSL, PDO MySQL, Session, Tokenizer aur XML enabled chahiye.
- **503 with reference number**: `.env` database settings aur SQL import check
  karo. Private `newstartailor-app/storage/logs/laravel.log` mein details milengi.
- **419**: HTTPS URL use karo, cookies allow karo aur page refresh karke form phir
  submit karo. Production mein secure cookies true rehni chahiye.
- **Write permission error**: `storage` aur `bootstrap/cache` folders writable karo.
- **Map blank**: internet connection aur browser content blockers check karo.

## Future updates

Code update karte waqt existing `.env` aur `storage` ka backup rakho aur unhe fresh
package se replace/delete mat karo. APP_KEY badalne se users ko phir login karna
pad sakta hai. MySQL aur `storage/app/private/references` dono ka backup chahiye.

## Existing database / developer notes

`database/php_extensions.sql` gives the extra port tables and remember token
column. Inspect before applying to an existing schema; do not blindly re-run an
ALTER for an existing column. The included Laravel migration checks existing
schema before adding missing structures. Existing bcrypt password hashes and
price/measurement snapshots are retained. Do not run the Flask, standalone PHP
and Laravel versions against the same live database at the same time.

This package is designed for a subdomain at `/`, not a URL subdirectory.
There is no need to upload the original Python virtualenv or install Node/Vite.
The frontend is server rendered and its CSS/JS/photo assets are included.

Official references:
- https://laravel.com/framework/docs/deployment
- https://www.hostinger.com/support/1884149-how-to-import-a-database-with-phpmyadmin-in-hostinger/
- https://www.hostinger.com/support/1884234-how-to-upload-backups-at-hostinger/

## Package verification

The Laravel HTTP/MySQL suite passed 112 checks; PHPUnit passed 6 tests with
9 assertions. Responsive browser checks passed at 320, 390, 768 and 1440 pixels,
including signup/login and mobile order submission. The final ZIP was extracted
into its actual two-folder deployment structure and tested with a fresh MySQL
import, first-admin setup, login and blocked private-file URLs.

Local runtime: PHP 8.4.27 with Composer locked to production PHP 8.3.36.
Hostinger PHP 8.3.36 and LiteSpeed/.htaccess execution still require the live
post-upload checks above; this archive has not been uploaded to your server.
