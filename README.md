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

Supported controlers:

Controled url | Description
--- | --- 
 /imagemagick/<attachment_id>/id/<recipe_id>											| Used to fetch an attachment with an recipe using recipe id.																
 /imagemagick/<attachment_id>/ref/<recipe_ref>											| Used to fetch an attachment with an recipe using recipe external reference.												
 /imageurl/id/<recipe_id>?url=<image_url>												| Used to apply a recipe on a local image.																					
 /imageurl/ref/<recipe_ref>?url=<image_url>												| Used to apply a recipe on a local image.																					
 /imagefield/<model_name>/<field_name>/<obj_id>/ref/<recipe_ref>						| Used to fetch an arbitrary field from a model with a recipe using recipe id.												
 /imagefield/<model_name>/<field_name>/<obj_id>/id/<recipe_id>							| Used to fetch an arbitrary field from a model with a recipe using recipe external reference.								
 /imagefield/<model_name>/<field_name>/<obj_id>/ref/<recipe_ref>/image/<file_name>		| Used to fetch an arbitrary field from a model with a recipe. Intended to use a file name to ensure unique url.			
 /website/imagemagick/<model_name>/<field_name>/<obj_hash>/<recipe_id>					| Similar to the /imagefield/ controlers but designed to use a hash. Primarily meant to make it easier to manage caching.	

Variables:

Variable | Description | Expected type
--- | --- | ---
<attachment_id>			| id of an attachment. 								| Int			
<field_name>			| Technical name of the field on the model. 		| Str			
<file_name>				| Only used to make url unique.						| Str
<image_url>				| Path to the image. Only supports local paths.		| Str			
<model_name>			| Technical name of the model. 						| Str			
<obj_hash>				| Hash id of the object, also supports id. 			| Str or Int	
<obj_id>				| id of an object from selected model				| Int			
<recipe_id>				| id of an recipe									| Int			
<recipe_ref>			| External id of an recipe							| Str or Int	
