from setuptools import setup

setup(name='villa',
      author='Tom Aldcroft',
      description='Watch the Villa via Raspberry Pi',
      author_email='taldcroft@gmail.com',
      version=0.1,
      zip_safe=False,
      packages=['villa'],
      entry_points={'console_scripts': ['villa_web=villa.web.main',
                                        'villa_mon=villa.monitor.main']},
)
