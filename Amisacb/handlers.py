import datetime


def advert_image_handler(instance, filename, **kwargs):
	extension = f'{filename}'.split('.')[-1]
	filename = f'{instance.client_fullname}-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.{extension}'

	return filename
