# PyPUGly (temporary name) [![Build Status](https://travis-ci.org/zerotk/pypugly.svg)](https://travis-ci.org/zerotk/pypugly)

PuPUGly is an experiment to create the "perfect" HTML generation language and learn a little bit more about compilers.


## Syntax

The syntax is inspired on PUG (aka JADE) until it is not. I'm trying to make the language more consistent (from my point of view).

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
