import datetime
from pathlib import Path
import environ
import firebase_admin
from firebase_admin import credentials

""" APPLICATION CONFIGURATIONS """

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    DEBUG=(bool, True)
)
environ.Env.read_env(BASE_DIR / '.env')

DEBUG = True
SECRET_KEY = env('SECRET_KEY')
ENVIRONMENT = env('ENVIRONMENT')
SITE_ID = int(env('SITE_ID'))

DOMAIN = env('DOMAIN')
PROTOCOL = env('PROTOCOL')
BASE_URL = f"{PROTOCOL}://{DOMAIN}"
ALLOWED_HOSTS = str(env('ALLOWED_HOSTS')).split(',')
CSRF_TRUSTED_ORIGINS = [f'{PROTOCOL}://{host}' for host in ALLOWED_HOSTS]
LOGOUT_REDIRECT_URL = '/accounts/cross-auth/'
LOGIN_REDIRECT_URL = '/accounts/cross-auth/'
GOOGLE_CALLBACK_ADDRESS = f"{BASE_URL}/accounts/google/login/callback/"
APPLE_CALLBACK_ADDRESS = f"{BASE_URL}/accounts/apple/login/callback/"

ROOT_URLCONF = 'root.urls'
AUTH_USER_MODEL = 'users.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

INSTALLED_APPS = [
    # DJANGO APPS
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # STARTER APPS
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'phonenumber_field',
    'django_ckeditor_5',
    'cities_light',

    # WEB APPS
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'fcm_django',

    # REST APPS
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'drf_yasg',

    # YOUR APPS
    'src.core.apps.CoreConfig',
    'src.services.users.apps.UsersConfig',
    'src.services.services.apps.ServicesConfig',
    'src.services.reporting.apps.ReportingConfig',
    'src.services.wallet.apps.WalletConfig',
    'src.services.finance.apps.FinanceAppConfig',
    'src.services.order.apps.OrderConfig',
    'src.services.dashboard.apps.DashboardConfig',
    'src.services.chat.apps.ChatConfig',
    'src.apps.stripe.apps.StripeConfig',

    # WEB APPS
    'src.web.website',
    'src.web.accounts',
    'src.apps.whisper.apps.WhisperConfig',

    # mailchimp
    'mailchimp_transactional',
]
# MAILCHIMP SETTINGS
MAILCHIMP_API_KEY = env('MAILCHIMP_API_KEY')
MAILCHIMP_FROM_EMAIL = env('MAILCHIMP_FROM_EMAIL')

MIDDLEWARE = [
    # DJANGO MIDDLEWARES
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]


# settings.py
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER')


# settings.py
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['en']  # Load English translations only
CITIES_LIGHT_INCLUDE_COUNTRIES = ['FR' ]  # Load data only for Pakistan and Turkey
CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPL', 'PPLA', 'PPLC']  # Include populated places and capitals


AUTHENTICATION_BACKENDS = (
    # DJANGO BACKENDS
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    # YOUR BACKENDS
)

REST_AUTH = {
    'REGISTER_SERIALIZER': 'src.api.auth.serializers.CustomRegisterSerializer',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'src.core.context_processors.application'
            ],
        },
    },
]

WSGI_APPLICATION = 'root.wsgi.application'

if ENVIRONMENT == 'server':
    DATABASES = {
        'default': {
            'ENGINE': env('DB_ENGINE'),
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASS'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

""" FIREBASE ------------------------------------------------------------------------------------------------------- """


FIREBASE_PROJECT_NAME = "Frent"
FIREBASE_PROJECT_ID = "frent-8368b"
FIREBASE_PROJECT_NUMBER = "233111883476"
FIREBASE_APP_NICK_NAME = "frent-web-app"
FIREBASE_APP_ID = "1:233111883476:web:1f91a9f07081cd34e03541"
FIREBASE_PRIVATE_KEY = "d1eb3d7d5907ca1cd7327d284625459a196d98e4"
FIREBASE_WEB_API_KEY = "AIzaSyDEvz2wHTjDttNMMmvU9LatBjzxwy_kejE"
FIREBASE_SERVICE_ACCOUNT = "firebase-adminsdk-fbsvc@frent-8368b.iam.gserviceaccount.com"
FIREBASE_FILE = "firebase.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_FILE)
    app = firebase_admin.initialize_app(cred)


# To learn more, visit the docs here:
# https://cloud.google.com/docs/authentication/getting-started>
GOOGLE_CLOUD_PROJECT = FIREBASE_PROJECT_ID
GOOGLE_APPLICATION_CREDENTIALS = FIREBASE_FILE

FCM_DJANGO_SETTINGS = {
    # an instance of firebase_admin.App to be used as default for all fcm-django requests
    # default: None (the default Firebase app)
    "DEFAULT_FIREBASE_APP": None,
    # default: _('FCM Django')
    "APP_VERBOSE_NAME": "[FCM Django]",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": False,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": True,
}

""" FIREBASE ------------------------------------------------------------------------------------------------------- """



""" INTERNATIONALIZATION --------------------------------------------------------------------------------"""
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_L10N = True
USE_TZ = True

""" EMAIL CONFIGURATION --------------------------------------------------------------------------------"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('EMAIL_PORT')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

""" RESIZER IMAGE --------------------------------------------------------------------------------"""
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
STATIC_ROOT = BASE_DIR / 'assets'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

""" RESIZER IMAGE --------------------------------------------------------------------------------"""
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {
    'JPEG': ".jpg",
    'PNG': ".png",
    'GIF': ".gif"
}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

""" ALL-AUTH SETUP --------------------------------------------------------------------------------"""
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

""" DEBUGGING TOOLS """

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'CLIENT_ID': '1021579594890-6m3kiukcsku6j5lpcv0293sjc3qq4830.apps.googleusercontent.com',
        'SECRET': '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',
        'SCOPE': ['profile', 'email', 'openid'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

""" MFA SETUP --------------------------------------------------------------------------------"""
MFA_ADAPTER = "allauth.mfa.adapter.DefaultMFAAdapter"

"""RESTAUTH SETUP --------------------------------------------------------------------------------"""
ACCOUNT_FORMS = {
    # 'login': 'src.web.accounts.forms.CustomLoginForm',
    'signup': 'src.web.accounts.forms.CustomSignUpForm',
}

"""  ACCOUNT ADAPTER Modify Login/Signup Redirect UR----------------------------------------------------"""
ACCOUNT_ADAPTER = "src.web.accounts.adapters.MyAccountAdapter"

""" PAYMENTS SETUP --------------------------------------------------------------------------------------------------"""
PAYMENTS_ENABLED = env('PAYMENTS_ENABLED')
if PAYMENTS_ENABLED:

    STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY_LIVE')
    STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY_LIVE')
    STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET_LIVE')

else:
    STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

"""       CKEDITOR SETUP --------------------------------------------------------------------------------"""
""" DJANGO-CKEDITOR-5 """
customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]

# CKEDITOR_5_CUSTOM_CSS = 'path_to.css'  # optional
# CKEDITOR_5_FILE_STORAGE = 'core.storage_backends.CKEditorAWSStorage'  # AWS
CKEDITOR_5_FILE_STORAGE = 'root.storage_backends.CKEditorLocalStorage'  # LOCAL

CKEDITOR_5_CONFIGS = {
    'default': {

        'toolbar': [
            'heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'imageUpload',
        ],

        'height': '100%',
        'width': '100%',
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': [
            'heading',
            '|', 'bold', 'italic', 'link', 'underline', 'strikethrough', 'code', 'subscript', 'superscript',
            'blockQuote',
            '|', 'outdent', 'indent', 'bulletedList', 'numberedList', 'todoList', 'insertTable',
            '|', 'fontSize', 'fontFamily', 'highlight', 'fontColor', 'fontBackgroundColor', 'removeFormat',
            '|', 'insertImage', 'imageUpload', 'mediaEmbed',
            '|', 'codeBlock', 'sourceEditing'
        ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}
