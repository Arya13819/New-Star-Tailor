"""Export the existing bilingual marketing design for Laravel PHP views.

Build-time only: run with the original Flask development environment.
Dynamic catalogue, authentication, order and payment pages remain PHP/database-backed.
"""
from pathlib import Path
import json
from jinja2 import ChoiceLoader, DictLoader
from flask import render_template
from babel.messages.pofile import read_po
from app import create_app
from app.extensions import db
from app.services.catalog_service import seed_defaults

ROOT=Path(__file__).resolve().parents[1]
app=create_app('testing')
app.jinja_loader=ChoiceLoader([DictLoader({'base.html':'{% block content %}{% endblock %}'}),app.jinja_loader])
with app.app_context():
    db.create_all()
    seed_defaults()
    from app.models.service import Service
    prices={s.code:s.default_stitching_price for s in Service.query.all()}
    for locale in ('en','hi'):
        dest=ROOT/'laravel/resources/views/pages/marketing'/locale
        dest.mkdir(parents=True,exist_ok=True)
        with app.test_request_context('/?lang='+locale):
            for page in ('index','about','contact','gallery','services'):
                if page=='gallery':
                    from app.routes.public.pages import GALLERY_PHOTOS
                    context={'photos':GALLERY_PHOTOS}
                elif page=='services':
                    from app.models.enums import ServiceCategory
                    from app.routes.public.services import CATEGORY_LABELS,SERVICE_IMAGES
                    services=Service.query.all()
                    context={'services':services,'categories':CATEGORY_LABELS,'category_counts':{c:sum(s.category==c for s in services) for c in ServiceCategory},'total_services':len(services),'selected_category':'ALL','search':'','service_images':SERVICE_IMAGES}
                else: context={'featured_prices':prices}
                html=render_template('public/'+page+'.html',**context)
                html=html.replace('9424035393','<?= e(SHOP_PHONE) ?>')
                if page=='index':
                    for code in ('SHIRT_PANT_COMBO','POLICE_KHAAKI','CRPF_CHEETAH'):
                        value=prices[code]
                        old=f'<span>₹{value:.2f}</span>'
                        new=f'''<?php if (isset($prices['{code}'])): ?><span><?= money($prices['{code}']) ?></span><?php endif ?>'''
                        html=html.replace(old,new,1)
                if page=='services':
                    (dest/'services-top.php').write_text('<?php namespace App\\Tailoring; ?>\n'+html.split('<section id="catalogue"')[0])
                    (dest/'services-bottom.php').write_text('<?php namespace App\\Tailoring; ?>\n'+'<section class="service-guidance"'+html.split('<section class="service-guidance"',1)[1])
                else:(dest/(('home' if page=='index' else page)+'.php')).write_text('<?php namespace App\\Tailoring; ?>\n'+html)
with (ROOT/'app/translations/hi/LC_MESSAGES/messages.po').open() as f:catalogue=read_po(f)
translations={m.id:m.string for m in catalogue if isinstance(m.id,str) and m.id and isinstance(m.string,str) and m.string}
(ROOT/'laravel/app/Tailoring/hi.json').write_text(json.dumps(translations,ensure_ascii=False,separators=(',',':'))+'\n')
print('PHP marketing templates exported in English and Hindi.')
