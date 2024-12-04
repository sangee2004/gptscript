import os

prompt = os.getenv('PROMPT_NEW')
env_var = os.environ['MY_ENV_NEW']

print(prompt+ ":" +env_var)
