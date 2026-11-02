"""Build Laravel's complete FileZilla layout, with production vendor dependencies.

Only the upload archive gets newly generated APP_KEY/NST_SETUP_KEY values.
Never put this private archive in a public Git repository.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED,ZipInfo
import base64,secrets,json,os,shutil

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'laravel'
OUTPUT=ROOT.parent/'New-Star-Tailor-Laravel-Hostinger.zip'

def write_file(archive,source,name):archive.write(source,name)
def main():
    assert (APP/'vendor/autoload.php').is_file(),'Run Composer install --no-dev first.'
    shutil.copytree(ROOT/'app/static',APP/'public/static',dirs_exist_ok=True,ignore=shutil.ignore_patterns('uploads'))
    lock=json.loads((APP/'composer.lock').read_text())
    assert lock.get('platform-overrides',{}).get('php')=='8.3.36','Lock must target the production PHP version.'
    installed=json.loads((APP/'vendor/composer/installed.json').read_text())
    assert not installed.get('dev',True),'Run Composer install --no-dev before packaging.'
    framework=next(p['version'] for p in lock['packages'] if p['name']=='laravel/framework')
    production_env=(APP/'.env.example').read_text().replace('APP_KEY=\n','APP_KEY=base64:'+base64.b64encode(secrets.token_bytes(32)).decode()+'\n').replace('NST_SETUP_KEY=\n','NST_SETUP_KEY='+secrets.token_hex(32)+'\n')
    with ZipFile(OUTPUT,'w',ZIP_DEFLATED,compresslevel=7) as archive:
        for directory in ['app','bootstrap','config','database','resources','routes','vendor']:
            for source in sorted((APP/directory).rglob('*')):
                if not source.is_file():continue
                rel=source.relative_to(APP)
                if directory=='bootstrap' and 'cache' in rel.parts:continue
                if any(part in ['.git','node_modules'] for part in rel.parts):continue
                write_file(archive,source,'newstartailor-app/'+str(rel))
        for name in ['artisan','composer.json','composer.lock']:
            write_file(archive,APP/name,'newstartailor-app/'+name)
        archive.writestr('newstartailor-app/.env',production_env)
        archive.writestr('newstartailor-app/.htaccess','Require all denied\n')
        # Runtime folders are deliberately empty; no sessions, photos or logs ship.
        for folder in ['storage/logs','storage/app/private/references','storage/app/public','storage/framework/sessions','storage/framework/views','storage/framework/cache/data','storage/framework/cache/locks','bootstrap/cache']:
            archive.writestr('newstartailor-app/'+folder+'/.gitignore','*\n!.gitignore\n')
        for source in sorted((APP/'public').rglob('*')):
            if not source.is_file() or source.name=='index.php':continue
            write_file(archive,source,'public_html/newstartailor/'+str(source.relative_to(APP/'public')))
        write_file(archive,APP/'deployment/public-index.php','public_html/newstartailor/index.php')
        write_file(archive,APP/'database/new_star_tailor.sql','DATABASE_IMPORT.sql')
        write_file(archive,APP/'FILEZILLA_SETUP_HINDI.md','START-HERE-HINDI.md')
    with ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        names=archive.namelist()
        assert 'newstartailor-app/vendor/autoload.php' in names
        assert 'newstartailor-app/.env' in names
        assert 'public_html/newstartailor/index.php' in names
        assert not any(n.endswith(('.sqlite','.log')) or '/sessions/' in n and not n.endswith('.gitignore') for n in names)
        assert not any(n.startswith('public_html/newstartailor/.env') or n.startswith('public_html/newstartailor/vendor/') for n in names)
    os.chmod(OUTPUT,0o600)
    print(json.dumps({'archive':str(OUTPUT),'laravel':framework,'target_php':'8.3.36','bytes':OUTPUT.stat().st_size,'files':len(names),'vendor_included':True,'production_keys':'new per-build keys in private .env; no DB/admin password included'}))

if __name__=='__main__':main()
