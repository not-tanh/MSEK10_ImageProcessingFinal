from PIL import Image


class Preprocessor:
    def __init__(self, image_size=128):
        self.image_size = image_size

    def __call__(self, input_images, **kwargs):
        if not input_images:
            return []
        # Inputs are img paths
        if type(input_images[0]) is str:
            images = [Image.open(path).resize((self.image_size, self.image_size)) for path in input_images]
        # Inputs are PIL images
        else:
            images = [image.resize((self.image_size, self.image_size)) for image in input_images]
        return images
