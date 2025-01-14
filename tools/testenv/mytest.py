import os

prompt = os.getenv('PROMPT')
env_var = os.environ['MY_ENV']

print("updated environment"+ ":" + prompt+ ":" +env_var)
