# -*- coding: utf-8 -*-
import os
import sys
from mock import Mock as MagicMock

class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()
MOCK_MODULES = ['k3', 'numpy', 'scipy', 'scipy.linalg', 'scipy.signal', 'core_k']
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)


basedir = os.path.split(__file__)[0]
idex_docs = basedir.split('\\').index('docs')
lpath_docs = basedir.split('\\')[:idex_docs]

lpath_docs.insert(1,'\\')
path_ = os.path.join( *lpath_docs)
path_src = os.path.join(path_, 'mediator')
sys.path.insert(0, path_)
sys.path.insert(0, path_src)
print(sys.path)

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'mediator'
copyright = '2022, other'
author = 'other'
release = '0.7.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser',
              'sphinx.ext.githubpages',
              'sphinx.ext.autodoc',
              'sphinx.ext.coverage',
              'sphinx.ext.napoleon',
              'sphinx.ext.viewcode']


napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True

templates_path = ['_templates']
#source_suffix = {
    #'.rst': 'restructuredtext',
    #'.txt': 'restructuredtext',
    #'.md': 'markdown',
#}
source_suffix = ['.rst', '.md']
exclude_patterns = []


myst_html_meta = {
    "description lang=en": "metadata description",
    "description lang=ru": "описание метаданных",
    "keywords": "Sphinx, MyST",
    "property=og:locale":  "ru_RU"
}
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
#html_theme = 'alabaster'
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']


html_theme_path = ["_themes", ]

highlight_options = {
  'default': {'stripall': True},
  'python': {'startinline': True},
}

latex_elements = {
  'extraclassoptions': ',openany,oneside'
}

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = "description"

# Don't show class signature with the class' name.
autodoc_class_signature = "separated"