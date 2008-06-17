google-app-engine-oil (gaeo) - A MVC web framework on Google AppEngine.

Authors: Lin-Chieh Shangkuan (Eric) <ericsk+gaeo@gmail.com>,
         Liang-Heng Chen (Gary) <xeonchen+gaeo@gmail.com>


== About

We want to create a simple framework that normalize the code layout
and coding style, so we developed this gaeo.


== License

gaeo is under Apache License 2.0. http://www.apache.org/licenses/LICENSE-2.0


== Install & Usage

1. In your $APP directory (the directory that contains app.yaml and main.py),
   type this command:

        svn co http://google-app-engine.googlecode.com/svn/trunk/gaeo gaeo

   or copy the ``gaeo'' directory to your $APP directory.

2. put your application code under $APP/application directory


3. If your application doesn't located in the $APP/application directory,
   please modify the *gaeo/dispatch/dispatcher.py* 's imports.

   For example, if your application is put in $APP/app directory, modify 
   the imports from:

        from application import controller
        from application import ...

   to:

        from app import controller
        from app import ...

   and don't forget to set *template_dir* of gaeo.Config in order to make 
   the gaeo's dispatcher know how to dispatch the requests. You can take
   the following sample code as the reference:

        import os
        import gaeo

        ...
        config = gaeo.Config()
        config.template_dir = os.path.join(
            os.path.dirname(__file__), 'application', 'templates')

4. For more tutorial, please view our QuickStart guide:
   http://code.google.com/p/google-app-engine-oil/wiki/QuickStart


== More Information

Project home
http://code.google.com/p/google-app-engine-oil/

Discussion Group
http://groups.google.com/group/google-app-engine-oil

