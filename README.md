# PyPUG (temporary name) [![Build Status](https://travis-ci.org/kaniabi/pypug.svg)](https://travis-ci.org/kaniabi/pypug)

PuPUG is an experiment to create the "perfect" HTML generation language and learn a little bit more about compilers.

The name is temporary... maybe PyPUGly?


## Syntax

I'm inspiring the syntax on PUG (aka JADE) until I'm not. I'm trying to make the language more consistent than JADE.

```
# Comments with '#'

# All code start with a dash (consistency).

# Define a variable like this:
-var name = 'PyPUGly'

# Define a function like this:
-def title(name):
  h1.title '{name}''

html(lang="en")
  head
    # All strings must be quoted. Only single-quotes are accepted (consistency).
    title 'This is {name}'
  body
    # Call a function like this:
    +title('PyPUGly')

    #container
      p 'Strings must be quoted.'
```


## TESTING

You py.test to test it

```console
$ PYTHONPATH=.:$PYTHONPATH py.test pypug
```
