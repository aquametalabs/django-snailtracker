# Django Snailtracker

## Introduction

Django Snailtracker is used to keep track of the history of individual
records in your database. It will track updates, deletes and inserts and
keep a diff of those records, when they changed and, if setup, who changed
them.

## Installation

For more automatic installation of snailtracker, use pypi and `pip`.
`pip install django-snailtracker`

For a manual installation, you can clone the snailtracker repo and install
it using python and setup.py.

    git clone git://github.com/aquameta/django-snailtracker.git
    python setup.py install

## Configuration

Snailtracker is just a Django app. Drop it into your `INSTALLED_APPS` tuple.

    INSTALLED_APPS = (
        ...
        'django_snailtracker',
        ...
    )

You also need to enable snailtracker by adding the following to your
settings.py:

    SNAILTRACKER_ENABLED = True

If you use Celery, you can offload the creation of snailtracker action objects
by enabling the following (this is recommended for applications that write
a lot of data to the database):

    SNAILTRACKER_OFFLOAD = True

Sync your database...

    python manage.py syncdb [--database=snailtracker]

Then migrate if you use South:

    python manage.py migrate django_snailtracker

## Usage

Registering models to be tracked by Snailtracker is a lot log registering
models to be used in the Django Admin. Start by creating a `snailtracker.py`
files in each app where you have models that you want to track.

The `snailtracker.py` file for a blog app would look like this:

    import django_snailtracker.utils
    
    from project.blogs.models import Blog, Post, Tag, Comment
    
    django_snailtracker.utils.register(Blog)
    django_snailtracker.utils.register(Post)
    django_snailtracker.utils.register(Tag)
    django_snailtracker.utils.register(Comment)
