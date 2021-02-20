## Avatar Field
Avatar Field is a simple Django field that helps you to add avatar icon beside name in choice for ForeignKey field.

  
Quick start
-----------
1. Add "avatar_field" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
    ...
    'avatar_field',
    ]

2. Use AvatarForeignKey instade of django normal ForeignKey and add image_field to tell the app what should use from the relation model 

    user = AvatarForeignKey("User", on_delete=models.CASCADE, image_field='picture')

3. Run `python manage.py makemigration` to create the migrations.
4. Run `python manage.py migrate` to reflact it on the database.

Now, all you need to go to the dashboard and see.