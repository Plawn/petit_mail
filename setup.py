from setuptools import setup

with open('readme.md', 'r') as f :
    readme_content = f.read()

setup(
    name='petit_mail',
    version='0.1.1',
    description='An easy way to send templated emails using an HTTP interface',
    packages=['petit_mail'],
    url='https://github.com/Plawn/petit_mail',
    license='apache-2.0',
    author='Plawn',
    author_email='plawn.yay@gmail.com',
    long_description=readme_content,
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    install_requires=[
        'fastapi', 
        'uvicorn',
        'Jinja2',
        'premailer',
        'minio',
        'pyyaml',
        # To use Gmail api
        'google-api-python-client ',
        'google-auth-httplib2 ',
        'google-auth-oauthlib',
        'oauth2client',
    ],
)
