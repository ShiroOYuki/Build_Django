import os
import shutil
import subprocess

os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

def read_file(path):
    with open(path, "r", encoding="utf8") as f:
        return f.read()
    
def write_file(path, content):
    with open(path, "w", encoding="utf8") as f:
        f.write(content)
    
def init_django(path, proj):
    print("Creating virtual enviroment...")
    subprocess.run(["python", "-m", "venv", ".venv"])
    venv_python = os.path.join(path, ".venv", "Scripts", "python.exe" if os.name == "nt" else "python")
    
    print("Installing django...")
    subprocess.run([
        venv_python, "-m", "pip", "install", "django"], 
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )
    
    print("Initalization project...")
    subprocess.run(["django-admin", "startproject", proj, "."])
    return venv_python

def create_app(venv, app):
    print(f"Creating direcroty for django app: {app}")
    subprocess.run([venv, "manage.py", "startapp", app])
    
def edit_proj_settings(path, proj, app):
    print("Initalization project settings...")
    content = read_file(os.path.join(path, proj, "settings.py"))
    
    content = "import os\n" + content
    content = content.replace(
        "LANGUAGE_CODE = 'en-us'", 
        "LANGUAGE_CODE = 'zh-Hant'"
    )
    content = content.replace(
        "TIME_ZONE = 'UTC'", 
        "TIME_ZONE = 'Asia/Taipei'"
    )
    content = content.replace(
        "BASE_DIR = Path(__file__).resolve().parent.parent",
        (
            "BASE_DIR = Path(__file__).resolve().parent.parent\n"
            "STATIC_PATH = os.path.join(BASE_DIR, 'static')\n"
        )
    )
    content = content.replace(
        "'DIRS': [],",
        (
            "'DIRS': [\n"
            "\t\t\tSTATIC_PATH,\n"
            "\t\t\tos.path.join(STATIC_PATH, 'template'),\n"
            f"\t\t\tos.path.join(STATIC_PATH, '{app}'),\n"
            "\t\t],\n"
        )
    )
    
    if "USE_L10N = True" not in content:
        content += "\nUSE_L10N = True"
        
    if "STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]" not in content:
        content += "\nSTATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]"
    
    write_file(os.path.join(path, proj, "settings.py"), content)

def edit_proj_urls(path, proj, app):
    print("Initalization project urls reflection...")
    content = (
        "from django.contrib import admin\n"
        "from django.urls import path, include\n"
        "\n"
        "urlpatterns = [\n"
        f"    path('{app}/', include('{app}.urls')),\n"
        "    path('admin/', admin.site.urls),\n"
        "]"
    )
    
    write_file(os.path.join(path, proj, "urls.py"), content)
        
def edit_app_urls(path, app):
    print("Initalization app urls reflection...")
    content = (
        "from django.urls import path\n"
        "from . import views\n"
        "\n"
        "urlpatterns = [\n"
        "    path('', views.index, name='index'),\n"
        "]"
    )
    
    write_file(os.path.join(path, app, "urls.py"), content)
        
def edit_app_views(path, app):
    print("Initalization app HTML reflection...")
    content = (
        "from django.shortcuts import render\n"
        "from django.http.request import HttpRequest\n"
        "from django.http.response import HttpResponse\n"
        "\n"
        "# Create your views here.\n"
        "def index(request: HttpRequest):\n"
        f"    return render(request, 'index.html')\n"
    )
    
    write_file(os.path.join(path, app, "views.py"), content)
        
def create_static_files(ori_path, path, app):
    print("Creating static directorys...")
    dirs = [
        os.path.join(path, 'static'),
        os.path.join(path, 'static', 'fonts'),
        os.path.join(path, 'static', 'imgs'),
        os.path.join(path, 'static', 'template'),
        os.path.join(path, 'static', 'template', 'css'),
        os.path.join(path, 'static', 'template', 'js'),
        os.path.join(path, 'static', app),
        os.path.join(path, 'static', app, 'css'),
        os.path.join(path, 'static', app, 'js'),
    ]
    
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"  Created dicrectory: {d}")
    
    print("Creating template files...")
    elements = os.path.join(ori_path, "elements")
    copies = [
        (
            os.path.join(elements, 'template.html'), 
            os.path.join(path, 'static', 'template', 'template.html')
        ),
        (
            os.path.join(elements, "template.css"), 
            os.path.join(path, 'static', 'template', 'css', 'template.css')
        ),
        (
            os.path.join(elements, "template.js"), 
            os.path.join(path, 'static', 'template', 'js', 'template.js')
        ),
        (
            os.path.join(elements, "loading.js"), 
            os.path.join(path, 'static', 'template', 'js', 'loading.js')
        ),
        (
            os.path.join(elements, "loading.svg"), 
            os.path.join(path, 'static', 'imgs', 'loading.svg')
        ),
        (
            os.path.join(elements, 'app.html'), 
            os.path.join(path, 'static', app, f'{app}.html')
        ),
        (
            os.path.join(elements, "app.css"), 
            os.path.join(path, 'static', app, 'css', 'style.css')
        ),
        (
            os.path.join(elements, "app.js"), 
            os.path.join(path, 'static', app, 'js', f'{app}.js')
        )
    ]
    
    for file in copies:
        shutil.copyfile(file[0], file[1])
        print(f"  Created file: {file[1]}")

def edit_app_static_html(path, app):
    print(f"Editing HTML file for app: {app}")
    need_replace = [
        (
            '<link rel="stylesheet" href="/static/app/css/app.css">',
            f'<link rel="stylesheet" href="/static/{app}/css/style.css">'
        ),
        (
            '<script src="/static/app/js/app.js"></script>',
            f'<script src="/static/{app}/js/{app}.js"></script>'
        )
    ]
        
    content = read_file(os.path.join(path, 'static', app, f'{app}.html'))
    
    for r in need_replace:
        content = content.replace(r[0], r[1])
    
    write_file(os.path.join(path, 'static', app, 'index.html'), content)
    
def migrate(venv):
    print("Running 'manage.py migrate' command...")
    subprocess.run([venv, "manage.py", "migrate"])
    
def create_launch_file(path, proj):
    print("Creating 'run.bat'")
    content = (
        "@echo off\n"
        "call \".venv/Scripts/activate\"\n"
        "cls\n"
        "python manage.py runserver\n"
    )
    write_file(os.path.join(path, "run.bat"), content)

def main():
    ori_path = os.getcwd()
    path = os.path.abspath(input("Project path: ").strip())
    
    while path.endswith(("/", "\\")):
        path = path[:-1]
    
    proj = os.path.basename(path)
    app = input("App name: ").strip()
    print("="*10)
    
    if not os.path.isdir(path):
        os.makedirs(path)
    
    os.chdir(path)
    venv = init_django(path, proj)
    
    create_app(venv, app)
    create_static_files(ori_path, path, app)

    edit_proj_settings(path, proj, app)
    edit_proj_urls(path, proj, app)
    edit_app_urls(path, app)
    edit_app_views(path, app)
    edit_app_static_html(path, app)
    
    migrate(venv)
    create_launch_file(path, proj)

if __name__ == "__main__":
    main()

    