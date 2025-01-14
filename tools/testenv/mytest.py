import os

prompt = os.getenv('PROMPT')
env_var = os.environ['MY_ENV']

print("updated environment for 1.0 setup"+ ":" + prompt+ ":" +env_var)
