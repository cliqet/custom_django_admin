### Intro
 This project serves as the backend api as an alternative to Django's default admin and 
 can be used with any frontend framework. Most of the patterns used in Django's default admin 
 is used here such as customizing the add, edit forms or tables. The goal of this project is 
 to have the default Django admin that we have gotten used to but make it more flexible on 
 the frontend side.

### Frontend for Custom Django Admin
- [SolidJS](https://github.com/cliqet/solidjs_django_admin)

### Prerequisites
- Python 3.12.0
- Django 5.1.3
- Git
- Postgres >= 13
- Redis >= 7

### Integrations
- `Cloudflare`: Make sure you have an account with Cloudflare and create a turnstile widget. This is used for the login form.
- `SMTP2GO`: For email services. Make sure you have an API key. If you want a different provider, you can change the implementation. Feel free to customize and redesign the email templates used.

### Before starting
There is a current app registered named demo which you can use to see how the backend works. It has a model `DemoModel` that has all the fields that are supported and will give you a feel as to how to setup those fields. When you are about to start a project, just delete the demo folder and remove it from installed apps.

### Setting up the application in your local environment 
- Navigate to the `src` directory and install dependencies by running
```bash
pip install -r requirements.txt
```

### Setting up your configuration file
- Under the `/src` directory, create a file named `config.toml`. Copy the sample content located at the root directory `config_templates/config.example.toml`
- To ensure that your config.toml is complete and not have any missing variables, you can run from the root directory while your virtual environment is activated
```bash
python ./scripts/check_deploy.py
```
- Look for the database section and populate the variables in your `config.toml` file with your database credentials. This currently has postgres as the other option aside from sqlite so you may need to add your customizations for other db.
- Create a folder named `web_media` in the root directory of the project (where devops and src are), this will be the directory where all your uploaded files in the django admin will be placed for local development. 
- Under `application.media_root` in your config file, put the absolute path of the web_media directory you just created
- Under `application.static_root` in your config file, put the absolute path of the static folder you want to use for collecting static files when running `manage.py collectstatic`. `DO NOT` point this to the `static` directory under src directory. Note that you do not need this if you do not want to access the default Django admin.

### Setting up your signing keys for JWT
Since we are using token authentication, we need signing keys to sign the tokens. You can read more about it here
```bash
https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html#signing-key
```
Note that this keys directory can be anywhere in your machine if you are not using the docker setup. You just need to store the full path including the file names which need to be named exactly in the example in `config.example.toml`
The values can be set in `application.jwt_private_key` and `application.jwt_public_key`. In this example, we create a `keys` directory under the root directory and inside it
#### Generate a private key
```bash
openssl genpkey -algorithm RSA -out jwt_private.pem -pkeyopt rsa_keygen_bits:2048
```
#### Generate a public key from private key
```bash
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pub
```

### Setting up your database
- You may use either sqlite or postgres. All sqlites will be under the `sqlite_dbs` directory. If you prefer to use another db, you can create a new configuration for it in the config.toml file.


### Automated testing with pytest
To run pytest, make sure you set your environment variable for testing environment. In Unix, you can just run
```bash
export DJANGO_SETTINGS_MODULE=backend.settings.test
```
Then you can run
```bash
pytest
```
You can go back to dev settings by just removing the environment variable
```bash
unset DJANGO_SETTINGS_MODULE
```
or you can just set it to `backend.settings.base` which is the default if it is not set

#### Directories
Description of some of the directories in the repo.
- `devops`: This will contain all files related to deployments. It is divided into dev, other 
environments (staging, prod, etc) and libraries. For libraries, this will contain packages needed for certain functionalities if needed. It is separated into arm and amd for cross-platform needs.
- `config_templates`: This is where you can find templates for files that need to be customized based on the environment
- `docker_media_vol`: This is just for local development where uploaded media files would go to if using the docker setup.
- `keys`: This is where the public and private keys are stored which is used for signing tokens for our api.
- `scripts`: This is where you will find utility scripts such as running `manage.py` in a docker setup and a python script to validate config files.
- `src`: The django app source code
- `src.docs`: This is where a yml file is stored for api documentation that is used by drf spectacular.
- `src.logs`: This is where all log files go. It is separated by app and gunicorn. When using a docker setup, you can view gunicorn logs here.
- `src.media`: This is just a directory for storing media files when you are not using the docker setup. Everything here is gitignored so use this when you are not using the docker setup.
- `src.scripts`: This is where we can store scripts that allows us to have the context of the app. 
- `src.sqlite_dbs`: You can use this if you want to use sqlite as your db when developing. 
- `src.tests`: This is where all test files will be stored for pytest. 


### Setup using Docker

#### Setup your docker.env
Make sure you have a `docker.env` file in the root directory. Please refer to `config_templates/docker.env.example` for values needed.

#### Setup your docker.config.toml 
Under `src` directory, make sure you have a `docker.config.toml` file. This is the counterpart of `config.toml` but is meant for docker setup. The reason for the separation is to make it easy to switch between regular setup and docker setup since `config.toml` is ignored when running the docker setup. Please take note of required values for some variables when using the `docker.config.toml`.

#### Running the application
In the root directory, run the script
```bash
./devops/dev/deploy_dev.sh
```
and you should be able to access the application using `http://localhost:8000`

#### Utility scripts
You will be needing to run `manage.py` and `pytest` commands often. There is a `scripts` directory in the root directory that will allow you to run these commands without having to do docker commands anymore.
For example, to run `manage.py` commands, in the root directory, just run
```bash
./scripts/run_manage_py.sh
```
It will prompt you for what command you want to run.
To run pytest, use the 
```bash
./scripts/run_pytest.sh
```

### Deployment in servers
You can check if setup is okay by running the script in `scripts` directory `check_deploy.py`. Refer to instructions above.
Create a different deploy script using `deploy_dev.sh` as the guide and have one for staging, production and so on. Organize the devops directory according to your needs.

### API documentation
To learn more about the apis your frontend can consume, go to
```bash
<yourdomain>/api/schema/docs
```

### How to Use

### View existing demo apps and models
You can view all models under the django_admin_demo by setting the config `is_demo_mode` to `true`. You only need to set this to `false` and it will not show in the current admin. You may delete this app and models but take note that all tests use this so make sure to adjust the tests or completely delete the existing tests.

#### Creating a model and register in admin
We will use the demo app as our guide. First, create your model
```python
class DemoModel(BaseModel):
    serializer_classname = 'DemoModelSerializer'

    class ColorChoices(models.TextChoices):
        BLUE = ('Blue', 'Blue')
        RED = ('Red', 'Red')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name='Type')
    color = models.CharField(
        verbose_name='Color', 
        choices=ColorChoices.choices, 
        default=ColorChoices.BLUE,
        max_length=10
    )
    name = models.CharField(max_length=100, verbose_name='Name', unique=True)
    email = models.EmailField(
        validators=[EmailValidator(message='Please enter a valid email address')],
        help_text='Please enter a valid email address',
        verbose_name='Email'
    )
    ordering = models.PositiveIntegerField(verbose_name='Ordering', default=0)
    range_number = models.PositiveSmallIntegerField(
        verbose_name='Range Number',
        default=5,
        help_text='Enter a number from 5 to 10',
        validators=[
            MinValueValidator(limit_value=5, message='Min is 5'),
            MaxValueValidator(limit_value=10, message='Max is 10'),
        ]
    )
    amount = models.DecimalField(
        default=0.0, 
        decimal_places=2, 
        max_digits=10, 
        verbose_name='Amount',
        help_text='Max of 10 digits with format: 12345678.90',
        validators=[
            RegexValidator(regex=r'^\d{1,8}(\.\d{0,2})?$', message='Enter a valid amount (up to 8 digits before the decimal and 2 digits')
        ]
    )
    comment = models.TextField(verbose_name='Comment')
    is_active = models.BooleanField(verbose_name='Is Active', default=True)
    date = models.DateField(verbose_name='Date')
    time = models.TimeField(verbose_name='Time')
    last_log = models.DateTimeField(verbose_name='Last Log')
    classification = models.ManyToManyField(Classification, verbose_name='Classification')
    permissions = models.ManyToManyField(Permission, verbose_name='Permissions')
    file = models.FileField(verbose_name='File', help_text=build_filefield_helptext())
    image = models.ImageField(
        verbose_name='Image',
        help_text=build_filefield_helptext(['.jpg', '.jpeg', '.png'], 2)
    )
    metadata = models.JSONField(verbose_name='Metadata')
    html = HTMLField(verbose_name='HTML', help_text='Enter html')


    def __str__(self):
        return self.name
```
It inherits from `BaseModel`. Use this so that you do not need to add 
`created_at` and `updated_at` fields. 

All your models should have an `admin_serializer_classname` property and must have 
the corresponding serializer class defined in the `serializers.py` in the 
same app directory in order to dynamically serialize any model. Use the `AdminBaseModelSerializer`. Separate your admin serializers with your frontend facing website. Look at `django_admin_demo.admin` and `django_admin_demo.serializers` for examples.

```python
class DemoModelSerializer(AdminBaseModelSerializer):
    class Meta:
        model = DemoModel
        fields = '__all__'
```

Then in your `admin.py`, you should have a ModelAdmin for the model.
Use the `BaseModelAdmin`
```python
class DemoModelAdmin(BaseModelAdmin):
    ...
```

Once you register this with the model using `admin.site.register`,
your model will now be available on the frontend with its corresponding 
add, change and listview pages.

#### Model Fields 
For the list of all fields supported, you can view it at `create_post_body_model_serializer` 
in `django_admin.util_serializers`. Things to note about some fields:
- Setting `blank` to True will remove required validation on the frontend
- Use `validators` property to apply custom validation rules to fields
- Use `build_filefield_helptext` to create your help text for file and image fields 
as it creates the format so that validation is applied to both the frontend and the backend
- Special fields include ManyToManyField, JSONField and HTMLField. Look at DemoModel example.

#### Customizing the modeladmin

Just like with `admin.ModelAdmin`, `BaseModelAdmin` supports the same setup
for the frequently used properties. Below is an example of customizing a model admin for the model Type `DemoModelAdmin`

```python
class TypeAdmin(BaseModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    search_fields = ['name']
    custom_inlines = [DemoModelCustomInline, TypeCustomInline, CountryProfileCustomInline]
    extra_inlines = ['sample_extra']
    fieldsets = (
        ('Section 1', {
            'fields': ('name',),
        }),
    )
```

Notice that all  properties are just like in `admin.ModelAdmin` except 
for `custom_inlines`, `extra_inlines`, `custom_change_link` and `custom_actions`

1. `custom_inlines`: This is just like inlines except that it takes a special kind 
of tabularinline model `BaseCustomInline` which you need to inherit from when creating 
inlines (tables aside from the current model). You can refer to `django_admin.admin` for what 
properties are available. Below is an example of a custom inline
```python
class DemoModelCustomInline(BaseCustomInline):
    app_label = 'demo'
    model_name = 'demomodel'
    model_name_label = 'DemoModel'
    list_display = ['name', 'type', 'color', 'ordering', 'is_active', 'email']
    list_display_links = ['name']
    list_per_page = 5

    # Using the change_obj to show only those that are related to the change object
    def get_queryset(self, change_obj):
        return DemoModel.objects.filter(type=change_obj)
```

The difference between Django's inlines and BaseCustomInline is that with 
BaseCustomInline, you can have inlines that are `NOT RELATED` to the current model.
You can even have inlines of the same current model. It is up to you what inline 
you want to show as long as you have a registered model in the admin. If you want to show 
a table that is not related to the model, just override the `get_queryset()` method and 
return any model queryset.


2. `extra_inlines`: This property is to add additional content that 
you want to add when you are in the listview page of a model. The content 
can be anything you want and the strings in the list are just identifiers 
of what component you would render in order after the main table of the model 
and all the `custom_inlines`. Use this to show other components in the listview 
that is not table data. Use the `DynamicExtraInline` component in the frontend to 
setup the different components to render.

3. `custom_change_link`: This allows you to create a custom change link instead of the default generic link. By assigning a link here, this will be the assigned link which will be appended by the `/<pk>/change`. You need to handle your custom route in your frontend. This customization allows you to create a change form that can show not just the fields in the model.
```python
class CountryProfileAdmin(BaseModelAdmin):
    list_display = ['country', 'level', 'type', 'area']
    autocomplete_fields = ['country']
    custom_change_link = f'{DASHBOARD_URL_PREFIX}/custom-change/country-profile'
```

4. `custom_actions` - Instead of using `actions` like in the Django modeladmin, custom actions is the one used for adding different actions for the table. Looking at the example and default delete actions that come with `BaseModelAdmin`, you need to provide a list of dict with the following:
```python
custom_actions = [{
    'func': CUSTOM_ACTIONS.DELETE_LISTVIEW.value,
    'label': 'Delete selected records'
}]
```
The dict should have the `func` which is the identifier of the action and a `label` which is the one shown in the dropdown menu. You would need to provide a view if you would like to add more custom actions. Just follow the pattern used by the delete listview builtin function. Refer to `django_admin.actions` for more details.
There is a utility function `copy_record` that can dynamically copy records including related instances and handles recursive instances such as foreign keys to self. Refer to copy demo model action for how to use it to add copy actions to your models.


### Documenting the admin site
The documentation app provides a way to write documentation about the different models
in order for the admin to understand better the models. When a documentation record is 
created for a specific model, it will be accessible on the frontend under `/model-docs`

### Customizing the app list
Sometimes, you may want to have a specific add, listview or change forms for a specific model.
This is possible through configuring `django_admin.configuration` as shown below
```python
APP_LIST_CONFIG_OVERRIDE = {
    # The name of the app
    'demo': {
        'app_url': f'{DASHBOARD_URL_PREFIX}/custom',
        'models': {
            # The name of the model
            'Classification': {
                'admin_url': f'{DASHBOARD_URL_PREFIX}/custom/classification',
                'add_url': f'{DASHBOARD_URL_PREFIX}/custom/classification/customadd',
            },
            # You can add more models
        }
    },
    # You can add more apps
}
```

### Task Queue Workers
This also includes `django-rq` as it's current task queue worker which is used currently for emails. You can view the stats of your queue and access the failed queues and requeue or delete them.

### Reports
Allows you to query the db based using a GUI query builder or using raw SQL. Default permission is for superusers only. Queries can be saved.

### Other customizations
Set your preferred `DASHBOARD_URL_PREFIX` in django_admin.constants. You can also just 
build your own views and not use the generic views. This means you can also change the routes 
in the frontend and build your own components if you wish to. 