from __future__ import unicode_literals, print_function

from pypugly.text import dedent


def test_django_integration(embed_data):
    import django
    import django.template
    from django.conf import settings
    from django.template.loader import get_template

    config = {
        'TEMPLATES': [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [
                    embed_data['includes']
                ],
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                        'django.core.context_processors.request'
                    ],
                    'loaders': [
                        (
                            'pypugly.django.Loader'
                        )
                    ],
                },
            }
        ]
    }
    settings.configure(**config)
    django.setup()

    t = get_template(embed_data['template.lang'])
    ctx = django.template.Context()
    result = t.render(ctx)

    assert result == dedent(
        '''
        <html>
            <head>
                <script src="alpha.js" />
            </head>
            <body>
                <h1>Hello, world!</h1>
            </body>
        </html>
        '''
    )
