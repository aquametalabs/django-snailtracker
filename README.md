# Django Snailtracker

## Introduction

Django Snailtracker is used to keep track of the history of individual records in your database. It will track updates, deletes and inserts and keep a diff of those records, when they changed and, if setup, who changed them.

## Installation

For more automatic installation of snailtracker, use pypi and `pip`.
`pip install django-snailtracker`

For a manual installation, you can clone the snailtracker repo and install it using python and setup.py.

    git clone git://github.com/aquameta/django-snailtracker.git
    python setup.py install

## Configuration

Snailtracker is just a Django app. Drop it into your `INSTALLED_APPS` tuple.

    INSTALLED_APPS = (
        ...
        'django_snailtracker',
        ...
    )

Sync your database...

    ./manage.py syncdb [--database=snailtracker]

Now you need to start tracking a model. In your apps models.py...

    import snailtracker


    class BlogPost(models.Model, snailtracker.models.Logger):

        snailtracker_exclude_fields = ('field_i_dont_care_about',)




