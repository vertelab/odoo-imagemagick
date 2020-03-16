# odoo-imagemagick
advanced image management

This module requied a python library called Wand. Install Wand to your machine by using:

	$ sudo apt-get install libmagickwand-dev
	
	$ sudo pip3 install Wand


You need to specify recipes first in your database. By doing that, you can go to "Settings" -> "Configuration" -> "Image Recipe". You can find all Wand methods in http://docs.wand-py.org/en/0.4.1/index.html.
And wand document in https://media.readthedocs.org/pdf/wand/0.3-maintenance/wand.pdf

The module includes a http controller class which can take 6 different urls and return the processed image with your recipe.


Here's an example of how to specify a recipe and use it by controller:

You want to resize a photo to maximum size 300px*300px. Your recipe should be: image.transform(resize='300x300>'). Don't forget to publish your recipe after that.

And now you want to resize an employee image to that size by using this http route:

"/website/imagemagick/model/field/id/model("image.recipe"):recipe"

This route takes 4 parameters which are "model name", "field name", "record id", "recipe id"

In this case, you should get your first employee's image to maximum size 300px*300px by using url below:

http://localhost:8069/website/imagemagick/hr.employee/image/1/1
