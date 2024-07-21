import boto3
from botocore.exceptions import ClientError
import json

from .base import *

secret_name = "prod-TaskLull-postgres"
region_name = "us-west-2"

# Create a Secrets Manager client
session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

try:
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
except ClientError as e:
    # For a list of exceptions thrown, see
    # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    raise e

secret = get_secret_value_response['SecretString']

secret_dict = json.loads(secret)
DJANGO_SECRET_KEY = secret_dict['DJANGO_SECRET_KEY']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = DJANGO_SECRET_KEY

ALLOWED_HOST_AWS = secret_dict['ALLOWED_EB_HOST']
ALLOWED_HOSTS = [ALLOWED_HOST_AWS]
ALLOWED_HOSTS += ['tasklull.com', 'www.tasklull.com', 'taskllul-env.eba-4mm238im.us-west-2.elasticbeanstalk.com']

secret_dict = json.loads(secret)
# Access values from the secret dictionary
db_user = secret_dict['username']
db_password = secret_dict['password']
db_host = secret_dict['host']
db_name = secret_dict['dbname']
db_port = secret_dict['port']
db_engine = secret_dict['engine']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': db_name,
        'USER': db_user,
        'PASSWORD': db_password,
        'HOST': db_host,  # Set to empty string for localhost.
        'PORT': db_port,  # Set to empty string for default.
    }
}
