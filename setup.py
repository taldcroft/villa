from setuptools import setup, find_packages

setup(name='villa',
      author='Tom Aldcroft',
      description='Watch the Villa via Raspberry Pi',
      author_email='taldcroft@gmail.com',
      version=0.2,
      zip_safe=False,
      packages=find_packages(),
      entry_points={'console_scripts': ['villa_web=villa.web:main',
                                        'villa_mon=villa.monitor:main',
                                        'villa_watch=villa.watch:main']},
      package_data={'villa': ['templates/*.html']},
)
