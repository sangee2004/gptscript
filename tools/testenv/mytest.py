import os

prompt = os.getenv('PROMPT')
env_var = os.environ['MY_ENV']

print(prompt)
print(env_var)
