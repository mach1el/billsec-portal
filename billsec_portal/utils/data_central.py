import os
from django.db import ConnectionHandler

def get_data_central_connection():
  db_config = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('DC_DB_NAME'),
    'USER': os.getenv('DC_DB_USER'),
    'PASSWORD': os.getenv('DC_DB_PASSWORD'),
    'HOST': os.getenv('DC_DB_HOST'),
    'PORT': os.getenv('DC_DB_PORT', '5432'),
  }

  handler = ConnectionHandler(
    {
      'default': {'ENGINE': 'django.db.backends.postgresql'},
      'data_central': db_config
    }
  )
  return handler['data_central']
