from setuptools import setup, Extension

module = Extension(
    'simple_graphs',
    sources=['simple_graphs.cpp'],
    extra_compile_args=['-O3']
)

setup(
    name='simple_graphs',
    version='1.0',
    description='Ex2 - graphs in C++',
    ext_modules=[module]
)