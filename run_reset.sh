









python manage.py makemigrations
python manage.py migrate


# echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin123456')" | python manage.py shell
echo "from users.models import CustomUser; CustomUser.objects.create_superuser('admin', 'admin@gmail.com', 'admin123456')" | python manage.py shell


# python manage.py generate_dummy_data