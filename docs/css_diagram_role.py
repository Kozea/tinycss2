"""
A Sphinx extension adding a 'css' role creating links to
the spec’s railroad diagrams.

"""

from docutils import nodes


def role_fn(_name, rawtext, text, lineno, inliner, options={}, content=()):
    ref = 'https://www.w3.org/TR/css-syntax-3/#%s-diagram' % text.replace(
        ' ', '-')
    if text.endswith(('-token', '-block')):
        text = '<%s>' % text
    ref = nodes.reference(rawtext, text, refuri=ref, **options)
    return [ref], []


def setup(app):
    app.add_role_to_domain('py', 'diagram', role_fn)
