ALLOWED_HOSTS = ["*"]

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    'census',
    'mixnet',
    'postproc',
    'store',
    'visualizer',
    'voting',
]

APIS = {
    'authentication': 'http://localhost:8080',
    'base': 'http://localhost:8080',
    'booth': 'http://localhost:8080',
    'census': 'http://localhost:8080',
    'mixnet': 'http://localhost:8080',
    'postproc': 'http://localhost:8080',
    'store': 'http://localhost:8080',
    'visualizer': 'http://localhost:8080',
    'voting': 'http://localhost:8080',
}

BASEURL = 'http://localhost:8080'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'decide2',
        'USER': 'decide',
        'PASSWORD': 'decide',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256