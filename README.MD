# How to use

### Performance Management Tracker(PMT)
This application is designed to help city departments track and manage their performance metrics and initiatives.

## Root .env file format
```
EMAIL_HOST=YOUR_EMAIL_SMTP
EMAIL_PORT=SMPT_PORT
EMAIL_HOST_USER=YOUR_EMAIL_ADDRESS
EMAIL_HOST_PASSWORD=YOUR_EMAIL_PASSWORD
PERFORMANCE_OFFICER_EMAIL=OFFICER_EMAIL
```

## Deploy on IIS Server

- ```python -m venv venv```
- ```venv/scripts/activate```
- ```pip install -r requirements.txt```
- ```pip install wfastcgi` & `wfastcgi-enable```
- ```python manage.py runserver``` to test it locally

## FASTCGI Setting

```
WSGI_HANDLER: django.core.wsgi.get_wsgi_application()

DJANGO_SETTINGS_MODULE: crm.settings

PYTHONPATH: D:\www\performance_app
```

## Static files
```
python manage.py collectstatic --no-input
```

## Root web.config file
```
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
    </system.webServer>
    <location path="" overrideMode="Deny">
        <system.webServer>
        </system.webServer>
    </location>

<appSettings>
    <!-- Required settings -->
    <add key="WSGI_HANDLER" value="django.core.wsgi.get_wsgi_application()" />
    <!-- Your djangoname.settings -->
    <add key="DJANGO_SETTINGS_MODULE" value="crm.settings" />
    <!-- Your django path -->
    <add key="PYTHONPATH" value="D:\www\performance_app" /> 
    
  </appSettings>

    <location path="" overrideMode="Allow">
        <system.webServer>
        <handlers>
                <remove name="Performance_app_FastCGI" />
                <add name="Performance_app_FastCGI" path="*" verb="*" modules="FastCgiModule" scriptProcessor="D:\www\performance_app\venv\Scripts\python.exe|D:\www\performance_app\venv\Lib\site-packages\wfastcgi.py" resourceType="Unspecified" requireAccess="Script" />
        </handlers>
        </system.webServer>
    </location>
</configuration>
```
## Static folder web.config file
```
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <clear />      
      <add name="StaticFile" path="*" verb="*" modules="StaticFileModule" resourceType="File" requireAccess="Read" />
    </handlers>
  </system.webServer>
</configuration>
```
